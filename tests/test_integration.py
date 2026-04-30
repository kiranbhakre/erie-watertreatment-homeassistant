"""Live integration tests — require real Erie Connect credentials.

Set env vars before running:
    export ERIE_EMAIL="your@email.com"
    export ERIE_PASSWORD="yourpassword"
    pytest tests/test_integration.py -v -s
"""

import os
import pytest

from erie_connect.client import ErieConnect
from custom_components.erie_watertreatment.config_flow import _login_and_select_first_active_device


ERIE_EMAIL = os.environ.get("ERIE_EMAIL")
ERIE_PASSWORD = os.environ.get("ERIE_PASSWORD")

live = pytest.mark.skipif(
    not ERIE_EMAIL or not ERIE_PASSWORD,
    reason="ERIE_EMAIL and ERIE_PASSWORD env vars required for live tests",
)


@pytest.fixture(autouse=True)
def _allow_network(socket_enabled):
    """Re-enable real sockets for all tests in this module."""
    import socket as _socket
    from pytest_socket import _true_connect
    _socket.socket.connect = _true_connect


def _login():
    api = ErieConnect(ERIE_EMAIL, ERIE_PASSWORD)
    _login_and_select_first_active_device(api)
    return api


@live
@pytest.mark.enable_socket
def test_login_and_device_selection():
    api = _login()

    print(f"\n  Device : {api.device.name} (id={api.device.id})")

    assert api.device.id
    assert api.auth.access_token


@live
@pytest.mark.enable_socket
def test_water_usage():
    content = _login().info().content

    volume_liters = int(content["total_volume"].split()[0])

    print(f"\n  ---- Water Usage ----")
    print(f"  Total volume used : {volume_liters:,} L")
    print(f"  Last regeneration : {content['last_regeneration']}")
    print(f"  Regenerations     : {content['nr_regenerations']}")
    print(f"  Last maintenance  : {content['last_maintenance']}")

    assert volume_liters >= 0
    for key in ("last_regeneration", "nr_regenerations", "last_maintenance", "total_volume"):
        assert key in content, f"Missing key: {key}"


@live
@pytest.mark.enable_socket
def test_warnings():
    warnings = _login().dashboard().content.get("warnings", [])

    assert isinstance(warnings, list)

    print(f"\n  ---- Warnings ----")
    if warnings:
        print(f"  Active warnings ({len(warnings)}):")
        for w in warnings:
            print(f"    ⚠️  {w['description']}")
    else:
        print("  No active warnings")
