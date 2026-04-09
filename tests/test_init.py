"""Tests for _get_external_ip and _update_ovh functions."""

from unittest.mock import AsyncMock

import aiohttp

from custom_components.ovh import (
    IP_RESOLVER_V4,
    IP_RESOLVER_V6,
    _get_external_ip,
    _update_ovh,
)


class TestGetExternalIp:
    """Tests for _get_external_ip."""

    async def test_returns_stripped_ipv4(self, mock_session):
        resp = AsyncMock()
        resp.text.return_value = "1.2.3.4\n"
        mock_session.get.return_value = resp

        ip = await _get_external_ip(mock_session)

        assert ip == "1.2.3.4"
        mock_session.get.assert_called_once_with(IP_RESOLVER_V4)

    async def test_uses_ipv6_resolver_when_flag_set(self, mock_session):
        resp = AsyncMock()
        resp.text.return_value = "2001:db8::1"
        mock_session.get.return_value = resp

        ip = await _get_external_ip(mock_session, ipv6=True)

        assert ip == "2001:db8::1"
        mock_session.get.assert_called_once_with(IP_RESOLVER_V6)

    async def test_returns_none_on_client_error(self, mock_session):
        mock_session.get.side_effect = aiohttp.ClientError()

        ip = await _get_external_ip(mock_session)

        assert ip is None

    async def test_returns_none_on_timeout(self, mock_session):
        mock_session.get.side_effect = TimeoutError()

        ip = await _get_external_ip(mock_session)

        assert ip is None


class TestUpdateOvh:
    """Tests for _update_ovh."""

    def _setup_responses(self, session, ip="1.2.3.4", ovh_body="good 1.2.3.4"):
        """Configure mock session to return IP then OVH response."""
        ip_resp = AsyncMock()
        ip_resp.text.return_value = ip
        ovh_resp = AsyncMock()
        ovh_resp.text.return_value = ovh_body
        session.get.side_effect = [ip_resp, ovh_resp]

    async def test_returns_true_on_good_response(self, mock_session):
        self._setup_responses(mock_session, ovh_body="good 1.2.3.4")

        result = await _update_ovh(mock_session, "host.ovh.net", "user", "pass")

        assert result is True

    async def test_returns_true_on_nochg_response(self, mock_session):
        self._setup_responses(mock_session, ovh_body="nochg 1.2.3.4")

        result = await _update_ovh(mock_session, "host.ovh.net", "user", "pass")

        assert result is True

    async def test_returns_false_when_ip_resolution_fails(self, mock_session):
        mock_session.get.side_effect = aiohttp.ClientError()

        result = await _update_ovh(mock_session, "host.ovh.net", "user", "pass")

        assert result is False

    async def test_returns_false_on_ovh_error(self, mock_session):
        self._setup_responses(mock_session, ovh_body="badauth")

        result = await _update_ovh(mock_session, "host.ovh.net", "user", "pass")

        assert result is False

    async def test_returns_false_on_ovh_client_error(self, mock_session):
        ip_resp = AsyncMock()
        ip_resp.text.return_value = "1.2.3.4"
        mock_session.get.side_effect = [ip_resp, aiohttp.ClientError()]

        result = await _update_ovh(mock_session, "host.ovh.net", "user", "pass")

        assert result is False

    async def test_returns_false_on_ovh_timeout(self, mock_session):
        ip_resp = AsyncMock()
        ip_resp.text.return_value = "1.2.3.4"
        mock_session.get.side_effect = [ip_resp, TimeoutError()]

        result = await _update_ovh(mock_session, "host.ovh.net", "user", "pass")

        assert result is False

    async def test_myip_param_included_in_ovh_url(self, mock_session):
        self._setup_responses(mock_session, ip="1.2.3.4")

        await _update_ovh(mock_session, "host.ovh.net", "user", "pass")

        ovh_url = mock_session.get.call_args_list[1][0][0]
        assert "myip=1.2.3.4" in ovh_url

    async def test_hostname_included_in_ovh_url(self, mock_session):
        self._setup_responses(mock_session)

        await _update_ovh(mock_session, "host.ovh.net", "user", "pass")

        ovh_url = mock_session.get.call_args_list[1][0][0]
        assert "hostname=host.ovh.net" in ovh_url

    async def test_uses_ipv6_resolver_when_flag_set(self, mock_session):
        self._setup_responses(mock_session, ip="2001:db8::1", ovh_body="good 2001:db8::1")

        await _update_ovh(mock_session, "host.ovh.net", "user", "pass", ipv6=True)

        ip_resolver_call = mock_session.get.call_args_list[0][0][0]
        assert ip_resolver_call == IP_RESOLVER_V6
