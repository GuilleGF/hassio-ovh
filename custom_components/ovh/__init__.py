"""Integrate with OVH Dynamic DNS service."""

import logging
from datetime import timedelta

import aiohttp
import async_timeout
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
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

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ovh"
CONF_IPV6 = "ipv6"

DEFAULT_INTERVAL = timedelta(minutes=15)

TIMEOUT = 30
HOST = "dns.eu.ovhapis.com/nic/update"
IP_RESOLVER_V4 = "https://api4.ipify.org"
IP_RESOLVER_V6 = "https://api6.ipify.org"

OVH_ERRORS = {
    "nohost": "Hostname supplied does not exist under specified account",
    "badauth": "Invalid username password combination",
    "badagent": "Client disabled",
    "!donator": "An update request was sent with a feature that is not available",
    "abuse": "Username is blocked due to abuse",
}

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
    """Initialize the OVH component."""
    session = async_get_clientsession(hass)

    for entry in config[DOMAIN]:
        domain = entry[CONF_DOMAIN].strip()
        user = entry[CONF_USERNAME].strip()
        password = entry[CONF_PASSWORD].strip()
        ipv6 = entry[CONF_IPV6]
        interval = entry[CONF_SCAN_INTERVAL]

        await _update_ovh(session, domain, user, password, ipv6=ipv6)

        async def update_domain_interval(
            now, _domain=domain, _user=user, _password=password, _ipv6=ipv6
        ):
            """Update the OVH entry."""
            await _update_ovh(session, _domain, _user, _password, ipv6=_ipv6)

        async_track_time_interval(hass, update_domain_interval, interval)

    return True


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
