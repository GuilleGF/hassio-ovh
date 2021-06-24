"""Integrate with OVH Dynamic DNS service."""
import asyncio
from datetime import timedelta
import logging

import aiohttp
from aiohttp import BasicAuth
import async_timeout
import voluptuous as vol

from homeassistant.const import (
    CONF_DOMAIN,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONF_SCAN_INTERVAL
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_interval

_LOGGER = logging.getLogger(__name__)

DOMAIN = "ovh"

DEFAULT_INTERVAL = timedelta(minutes=10)

TIMEOUT = 10
UPDATE_URL = "https://www.ovh.com/nic/update"

OVH_ERRORS = {
    "nohost": "Hostname supplied does not exist under specified account",
    "badauth": "Invalid username password combination",
    "badagent": "Client disabled",
    "!donator": "An update request was sent with a feature that is not available",
    "abuse": "Username is blocked due to abuse",
}

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_DOMAIN): cv.string,
                vol.Required(CONF_USERNAME): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_INTERVAL): vol.All(
                    cv.time_period, cv.positive_timedelta
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

async def async_setup(hass, config):
    """Initialize the OVH component."""
    conf = config[DOMAIN]
    domains = conf.get(CONF_DOMAIN)
    user = conf.get(CONF_USERNAME)
    password = conf.get(CONF_PASSWORD)
    interval = conf.get(CONF_SCAN_INTERVAL)
    domains_list = domains.split(",")

    session = async_get_clientsession(hass)

    for domain in domains_list:
        result = await _update_ovh(hass, session, domain, user, password)
        if not result:
            return False

    async def update_domain_interval(now):
        """Update the OVH entry."""
        for domain in domains_list:
            await _update_ovh(hass, session, domain, user, password)

    async_track_time_interval(hass, update_domain_interval, interval)

    return True


async def _update_ovh(hass, session, domain, user, password):
    """Update OVH."""
    params = {"system": "dyndns", "hostname": domain}
    authentication = BasicAuth(user, password)

    try:
        with async_timeout.timeout(TIMEOUT):
            resp = await session.get(UPDATE_URL, params=params, auth=authentication)
            body = await resp.text()

            if body.startswith("good") or body.startswith("nochg"):
                _LOGGER.info("Updating OVH for domain: %s", domain)

                return True

            _LOGGER.warning("Updating OVH failed: %s => %s", domain, OVH_ERRORS[body.strip()])

    except aiohttp.ClientError:
        _LOGGER.warning("Can't connect to OVH API")

    except asyncio.TimeoutError:
        _LOGGER.warning("Timeout from OVH API for domain: %s", domain)

    return False
