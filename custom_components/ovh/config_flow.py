"""Config flow for OVH DynHost integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import (
    CONF_DOMAIN,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)
from homeassistant.core import callback

from .const import CONF_IPV6, DEFAULT_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)

_STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DOMAIN): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_IPV6, default=False): bool,
    }
)


class OVHConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OVH DynHost."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        if user_input is not None:
            domain = user_input[CONF_DOMAIN].strip().lower()
            await self.async_set_unique_id(domain)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=domain,
                data={
                    CONF_DOMAIN: domain,
                    CONF_USERNAME: user_input[CONF_USERNAME].strip(),
                    CONF_PASSWORD: user_input[CONF_PASSWORD].strip(),
                    CONF_IPV6: user_input[CONF_IPV6],
                },
            )

        return self.async_show_form(step_id="user", data_schema=_STEP_USER_SCHEMA)

    async def async_step_import(
        self, import_data: dict[str, Any]
    ) -> config_entries.ConfigFlowResult:
        """Handle import from YAML configuration."""
        domain = import_data[CONF_DOMAIN].strip().lower()
        await self.async_set_unique_id(domain)
        self._abort_if_unique_id_configured()
        _LOGGER.info("Importing OVH DynHost entry for domain: %s", domain)
        raw_interval = import_data.get(CONF_SCAN_INTERVAL, DEFAULT_INTERVAL)
        return self.async_create_entry(
            title=domain,
            data={
                CONF_DOMAIN: domain,
                CONF_USERNAME: import_data[CONF_USERNAME].strip(),
                CONF_PASSWORD: import_data[CONF_PASSWORD].strip(),
                CONF_IPV6: import_data.get(CONF_IPV6, False),
            },
            options={
                CONF_SCAN_INTERVAL: int(raw_interval.total_seconds()),
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,  # noqa: ARG004
    ) -> OVHOptionsFlow:
        """Create the options flow."""
        return OVHOptionsFlow()


class OVHOptionsFlow(config_entries.OptionsFlow):
    """Handle options for OVH DynHost."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current_ipv6 = self.config_entry.data.get(CONF_IPV6, False)
        current_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, int(DEFAULT_INTERVAL.total_seconds())
        )

        schema = vol.Schema(
            {
                vol.Optional(CONF_IPV6, default=current_ipv6): bool,
                vol.Optional(CONF_SCAN_INTERVAL, default=current_interval): vol.All(
                    int, vol.Range(min=60)
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
