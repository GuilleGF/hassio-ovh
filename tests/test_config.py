"""Tests for configuration schema validation."""

from datetime import timedelta

import pytest
import voluptuous as vol

from custom_components.ovh import CONFIG_SCHEMA, DOMAIN


class TestConfigSchema:
    """Tests for CONFIG_SCHEMA validation."""

    def test_backward_compat_single_entry(self):
        """Old format without list should still be accepted."""
        config = {
            DOMAIN: {
                "domain": "host.ovh.net",
                "username": "user",
                "password": "pass",
            }
        }
        result = CONFIG_SCHEMA(config)
        assert len(result[DOMAIN]) == 1
        assert result[DOMAIN][0]["domain"] == "host.ovh.net"

    def test_list_single_entry(self):
        """List format with one entry."""
        config = {
            DOMAIN: [{"domain": "host.ovh.net", "username": "user", "password": "pass"}]
        }
        result = CONFIG_SCHEMA(config)
        assert len(result[DOMAIN]) == 1

    def test_list_multiple_entries(self):
        """Multiple entries with different credentials."""
        config = {
            DOMAIN: [
                {"domain": "host1.ovh.net", "username": "u1", "password": "p1"},
                {"domain": "host2.ovh.net", "username": "u2", "password": "p2"},
            ]
        }
        result = CONFIG_SCHEMA(config)
        assert len(result[DOMAIN]) == 2
        assert result[DOMAIN][0]["domain"] == "host1.ovh.net"
        assert result[DOMAIN][1]["domain"] == "host2.ovh.net"

    def test_missing_domain_raises(self):
        with pytest.raises(vol.Invalid):
            CONFIG_SCHEMA({DOMAIN: [{"username": "u", "password": "p"}]})

    def test_missing_username_raises(self):
        with pytest.raises(vol.Invalid):
            CONFIG_SCHEMA({DOMAIN: [{"domain": "host.ovh.net", "password": "p"}]})

    def test_missing_password_raises(self):
        with pytest.raises(vol.Invalid):
            CONFIG_SCHEMA({DOMAIN: [{"domain": "host.ovh.net", "username": "u"}]})

    def test_ipv6_defaults_to_false(self):
        config = {
            DOMAIN: [{"domain": "host.ovh.net", "username": "u", "password": "p"}]
        }
        result = CONFIG_SCHEMA(config)
        assert result[DOMAIN][0]["ipv6"] is False

    def test_ipv6_can_be_enabled(self):
        config = {
            DOMAIN: [
                {
                    "domain": "host.ovh.net",
                    "username": "u",
                    "password": "p",
                    "ipv6": True,
                }
            ]
        }
        result = CONFIG_SCHEMA(config)
        assert result[DOMAIN][0]["ipv6"] is True

    def test_scan_interval_defaults_to_15_minutes(self):
        config = {
            DOMAIN: [{"domain": "host.ovh.net", "username": "u", "password": "p"}]
        }
        result = CONFIG_SCHEMA(config)
        assert result[DOMAIN][0]["scan_interval"] == timedelta(minutes=15)

    def test_scan_interval_can_be_overridden(self):
        config = {
            DOMAIN: [
                {
                    "domain": "host.ovh.net",
                    "username": "u",
                    "password": "p",
                    "scan_interval": {"minutes": 30},
                }
            ]
        }
        result = CONFIG_SCHEMA(config)
        assert result[DOMAIN][0]["scan_interval"] == timedelta(minutes=30)
