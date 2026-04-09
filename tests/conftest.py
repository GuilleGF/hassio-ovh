"""Shared fixtures for OVH tests."""

from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def mock_session():
    """Mock aiohttp client session."""
    return AsyncMock()


@pytest.fixture
def mock_ip_response():
    """Mock response returning an IPv4 address."""
    resp = AsyncMock()
    resp.text.return_value = "1.2.3.4"
    return resp


@pytest.fixture
def mock_ovh_good_response():
    """Mock OVH response for a successful update."""
    resp = AsyncMock()
    resp.text.return_value = "good 1.2.3.4"
    return resp
