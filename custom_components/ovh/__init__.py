"""Integrate with OVH Dynamic DNS service."""
import asyncio
from datetime import timedelta
import logging

import aiohttp
from aiohttp.hdrs import USER_AGENT
from aiohttp import BasicAuth
import voluptuous as vol

from homeassistant.const import CONF_DOMAIN, CONF_PASSWORD, CONF_TIMEOUT, CONF_USERNAME
from homeassistant.helpers.aiohttp_client import SERVER_SOFTWARE
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ovh"

# We should set a dedicated address for the user agent.
EMAIL = "hello@home-assistant.io"

INTERVAL = timedelta(minutes=5)

OVH_ERRORS = {
    "nohost": "Hostname supplied does not exist under specified account",
    "badauth": "Invalid username password combination",
    "badagent": "Client disabled",
    "!donator": "An update request was sent with a feature that is not available",
    "abuse": "Username is blocked due to abuse",
}

UPDATE_URL = "https://www.ovh.com/nic/update"
IP_URL = "https://api.ipify.org"
HA_USER_AGENT = f"{SERVER_SOFTWARE} {EMAIL}"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_DOMAIN): cv.string,
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Initialize the OVH component."""
    domain = config[DOMAIN].get(CONF_DOMAIN)
    user = config[DOMAIN].get(CONF_USERNAME)
    password = config[DOMAIN].get(CONF_PASSWORD)

    session = hass.helpers.aiohttp_client.async_get_clientsession()

    ip = await _get_public_ip(session)

    if not ip:
        return False

    result = await _update_ovh(session, domain, ip, user, password)

    if not result:
        return False

    async def update_domain_interval(now):
        """Update the OVH entry."""
        await _update_ovh(session, domain, ip, user, password)

    hass.helpers.event.async_track_time_interval(update_domain_interval, INTERVAL)

    return True


async def _get_public_ip(session):
    try:
        async with session.get(IP_URL) as ip_resp:
            ip = await ip_resp.text()

            _LOGGER.info("Public IP: {}".format(ip))

            return ip

    except aiohttp.ClientError:
        _LOGGER.warning("Can't connect to ipify API")

    return False


async def _update_ovh(session, domain, ip, user, password):
    """Update OVH."""
    url = UPDATE_URL
    params = {"myip": ip, "system": "dyndns", "hostname": domain}
    headers = {USER_AGENT: HA_USER_AGENT}
    authentication = BasicAuth(user, password)

    try:
        async with session.get(url, params=params, headers=headers, auth=authentication) as resp:
            body = await resp.text()

            if body.startswith("good") or body.startswith("nochg"):
                return True

            _LOGGER.warning(
                "Updating OVH failed: %s => %s", domain, OVH_ERRORS[body.strip()]
            )

    except aiohttp.ClientError:
        _LOGGER.warning("Can't connect to OVH API")

    return False
