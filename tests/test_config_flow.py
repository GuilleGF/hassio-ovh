"""Tests for OVH DynHost config flow."""

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.const import (
    CONF_DOMAIN,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)

from custom_components.ovh.config_flow import OVHConfigFlow, OVHOptionsFlow
from custom_components.ovh.const import CONF_IPV6, DEFAULT_INTERVAL


def _make_flow() -> OVHConfigFlow:
    """Return a flow instance with mocked HA methods."""
    flow = OVHConfigFlow()
    flow.async_set_unique_id = AsyncMock()
    flow._abort_if_unique_id_configured = MagicMock()
    flow.async_create_entry = MagicMock(
        return_value={"type": "create_entry", "title": "", "data": {}}
    )
    flow.async_show_form = MagicMock(return_value={"type": "form"})
    return flow


class TestOVHConfigFlowUser:
    """Tests for async_step_user."""

    async def test_shows_form_when_no_input(self):
        flow = _make_flow()
        result = await flow.async_step_user(None)
        flow.async_show_form.assert_called_once()
        assert flow.async_show_form.call_args.kwargs["step_id"] == "user"
        assert result["type"] == "form"

    async def test_creates_entry_with_valid_input(self):
        flow = _make_flow()
        await flow.async_step_user(
            {
                CONF_DOMAIN: "sub.example.com",
                CONF_USERNAME: "user",
                CONF_PASSWORD: "pass",
                CONF_IPV6: False,
            }
        )
        flow.async_set_unique_id.assert_called_once_with("sub.example.com")
        flow._abort_if_unique_id_configured.assert_called_once()
        call_kwargs = flow.async_create_entry.call_args
        assert call_kwargs.kwargs["title"] == "sub.example.com"
        assert call_kwargs.kwargs["data"][CONF_DOMAIN] == "sub.example.com"
        assert call_kwargs.kwargs["data"][CONF_USERNAME] == "user"
        assert call_kwargs.kwargs["data"][CONF_PASSWORD] == "pass"

    async def test_strips_and_lowercases_domain(self):
        flow = _make_flow()
        await flow.async_step_user(
            {
                CONF_DOMAIN: "  Sub.Example.COM  ",
                CONF_USERNAME: "u",
                CONF_PASSWORD: "p",
                CONF_IPV6: False,
            }
        )
        flow.async_set_unique_id.assert_called_once_with("sub.example.com")
        call_kwargs = flow.async_create_entry.call_args
        assert call_kwargs.kwargs["data"][CONF_DOMAIN] == "sub.example.com"

    async def test_strips_whitespace_from_credentials(self):
        flow = _make_flow()
        await flow.async_step_user(
            {
                CONF_DOMAIN: "sub.example.com",
                CONF_USERNAME: "  user  ",
                CONF_PASSWORD: "  pass  ",
                CONF_IPV6: False,
            }
        )
        call_kwargs = flow.async_create_entry.call_args
        assert call_kwargs.kwargs["data"][CONF_USERNAME] == "user"
        assert call_kwargs.kwargs["data"][CONF_PASSWORD] == "pass"

    async def test_ipv6_flag_stored_in_entry(self):
        flow = _make_flow()
        await flow.async_step_user(
            {
                CONF_DOMAIN: "sub.example.com",
                CONF_USERNAME: "u",
                CONF_PASSWORD: "p",
                CONF_IPV6: True,
            }
        )
        call_kwargs = flow.async_create_entry.call_args
        assert call_kwargs.kwargs["data"][CONF_IPV6] is True


class TestOVHConfigFlowImport:
    """Tests for async_step_import."""

    async def test_imports_yaml_entry(self):
        flow = _make_flow()
        await flow.async_step_import(
            {CONF_DOMAIN: "host.ovh.net", CONF_USERNAME: "u", CONF_PASSWORD: "p"}
        )
        flow.async_set_unique_id.assert_called_once_with("host.ovh.net")
        flow._abort_if_unique_id_configured.assert_called_once()
        call_kwargs = flow.async_create_entry.call_args
        assert call_kwargs.kwargs["data"][CONF_DOMAIN] == "host.ovh.net"

    async def test_import_preserves_scan_interval_in_options(self):
        flow = _make_flow()
        await flow.async_step_import(
            {
                CONF_DOMAIN: "host.ovh.net",
                CONF_USERNAME: "u",
                CONF_PASSWORD: "p",
                CONF_SCAN_INTERVAL: timedelta(minutes=30),
            }
        )
        call_kwargs = flow.async_create_entry.call_args
        assert call_kwargs.kwargs["options"][CONF_SCAN_INTERVAL] == 1800

    async def test_import_uses_default_interval_when_absent(self):
        flow = _make_flow()
        await flow.async_step_import(
            {CONF_DOMAIN: "host.ovh.net", CONF_USERNAME: "u", CONF_PASSWORD: "p"}
        )
        call_kwargs = flow.async_create_entry.call_args
        expected = int(DEFAULT_INTERVAL.total_seconds())
        assert call_kwargs.kwargs["options"][CONF_SCAN_INTERVAL] == expected

    async def test_import_aborts_if_already_configured(self):
        flow = _make_flow()
        flow._abort_if_unique_id_configured = MagicMock(
            side_effect=Exception("already_configured")
        )
        with pytest.raises(Exception, match="already_configured"):
            await flow.async_step_import(
                {CONF_DOMAIN: "host.ovh.net", CONF_USERNAME: "u", CONF_PASSWORD: "p"}
            )


class TestOVHOptionsFlow:
    """Tests for OVHOptionsFlow."""

    def _make_options_flow(self, data=None, options=None) -> OVHOptionsFlow:
        flow = OVHOptionsFlow()
        entry = MagicMock()
        entry.data = data or {CONF_IPV6: False}
        entry.options = options or {}
        type(flow).config_entry = property(lambda _: entry)
        flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})
        flow.async_show_form = MagicMock(return_value={"type": "form"})
        return flow

    async def test_shows_form_when_no_input(self):
        flow = self._make_options_flow()
        result = await flow.async_step_init(None)
        flow.async_show_form.assert_called_once()
        assert result["type"] == "form"

    async def test_saves_options_on_submit(self):
        flow = self._make_options_flow()
        result = await flow.async_step_init({CONF_IPV6: True, CONF_SCAN_INTERVAL: 600})
        flow.async_create_entry.assert_called_once_with(
            data={CONF_IPV6: True, CONF_SCAN_INTERVAL: 600}
        )
        assert result["type"] == "create_entry"

    async def test_prefills_current_ipv6_from_data(self):
        flow = self._make_options_flow(data={CONF_IPV6: True})
        await flow.async_step_init(None)
        flow.async_show_form.assert_called_once()

    async def test_prefills_interval_from_options(self):
        flow = self._make_options_flow(options={CONF_SCAN_INTERVAL: 600})
        await flow.async_step_init(None)
        flow.async_show_form.assert_called_once()
