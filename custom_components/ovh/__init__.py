"""Integrate with OVH Dynamic DNS service."""

import logging
from datetime import timedelta

import aiohttp
import async_timeout
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    CONF_DOMAIN,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_IPV6,
    DEFAULT_INTERVAL,
    DOMAIN,
    HOST,
    IP_RESOLVER_V4,
    IP_RESOLVER_V6,
    OVH_ERRORS,
    TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)

ENTRY_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DOMAIN): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_IPV6, default=False): cv.boolean,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_INTERVAL): vol.All(
            cv.time_period, cv.positive_timedelta
        ),
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(cv.ensure_list, [ENTRY_SCHEMA]),
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Initialize the OVH component from YAML (imports entries for UI management)."""
    if DOMAIN not in config:
        return True

    for entry_cfg in config[DOMAIN]:
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data=entry_cfg,
            )
        )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OVH DynHost from a config entry."""
    session = async_get_clientsession(hass)

    domain = entry.data[CONF_DOMAIN].strip()
    user = entry.data[CONF_USERNAME].strip()
    password = entry.data[CONF_PASSWORD].strip()
    ipv6 = entry.options.get(CONF_IPV6, entry.data.get(CONF_IPV6, False))
    raw_interval = entry.options.get(
        CONF_SCAN_INTERVAL, int(DEFAULT_INTERVAL.total_seconds())
    )
    interval = timedelta(seconds=raw_interval)

    await _update_ovh(session, domain, user, password, ipv6=ipv6)

    async def update_domain_interval(
        now, _domain=domain, _user=user, _password=password, _ipv6=ipv6
    ):
        """Update the OVH entry."""
        await _update_ovh(session, _domain, _user, _password, ipv6=_ipv6)

    unsub = async_track_time_interval(hass, update_domain_interval, interval)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = unsub

    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry and cancel the periodic update."""
    unsub = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if unsub is not None:
        unsub()
    return True


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def _get_external_ip(session, *, ipv6: bool = False):
    """Get current external IP address."""
    resolver = IP_RESOLVER_V6 if ipv6 else IP_RESOLVER_V4
    try:
        async with async_timeout.timeout(TIMEOUT):
            resp = await session.get(resolver)
            return (await resp.text()).strip()
    except aiohttp.ClientError:
        _LOGGER.warning("Can't reach IP resolver: %s", resolver)
    except TimeoutError:
        _LOGGER.warning("Timeout reaching IP resolver: %s", resolver)
    return None


async def _update_ovh(session, domain, user, password, *, ipv6: bool = False):
    """Update OVH."""
    ip = await _get_external_ip(session, ipv6=ipv6)
    if ip is None:
        _LOGGER.warning("Skipping OVH update for %s: could not resolve IP", domain)
        return False

    try:
        url = f"https://{user}:{password}@{HOST}?system=dyndns&hostname={domain}&myip={ip}"
        async with async_timeout.timeout(TIMEOUT):
            resp = await session.get(url)
            body = await resp.text()

            if body.startswith(("good", "nochg")):
                _LOGGER.info("Updating OVH for domain: %s", domain)
                return True

            _LOGGER.warning(
                "Updating OVH failed: %s => %s",
                domain,
                OVH_ERRORS[body.strip()],
            )

    except aiohttp.ClientError:
        _LOGGER.warning("Can't connect to OVH API for domain: %s", domain)

    except TimeoutError:
        _LOGGER.warning("Timeout from OVH API for domain: %s", domain)

    return False
