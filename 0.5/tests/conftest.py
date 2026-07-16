"""Shared fixtures for 0.5 unit tests (GPIO/PDU mocked; no hardware)."""

from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture
def pdu_calls():
    return []


@pytest.fixture
def fake_gpio_module():
    """Install a fake RPi.GPIO before cqr_get touches hardware."""
    gpio_pkg = types.ModuleType("RPi")
    gpio = types.ModuleType("RPi.GPIO")
    gpio.BCM = 11
    gpio.IN = 1
    gpio.setmode = MagicMock()
    gpio.setup = MagicMock()
    gpio.input = MagicMock(return_value=0)
    gpio.cleanup = MagicMock()
    sys.modules["RPi"] = gpio_pkg
    sys.modules["RPi.GPIO"] = gpio
    yield gpio
    sys.modules.pop("RPi.GPIO", None)
    sys.modules.pop("RPi", None)


@pytest.fixture
def reload_modules(pdu_calls, fake_gpio_module):
    """Reload 0.5 modules with a mocked pdu_url and fake GPIO available."""

    def _reload(*, pdu_side_effect=None):
        for name in ("cqr_get", "cqr_sec", "cqr_pdu", "cqr_env"):
            sys.modules.pop(name, None)

        import cqr_env

        importlib.reload(cqr_env)

        # Patch pdu layer after env is loaded.
        import cqr_pdu

        importlib.reload(cqr_pdu)

        def _pdu_url(**kwargs):
            if pdu_side_effect is not None:
                result = pdu_side_effect(kwargs)
            else:
                result = {"ok": True}
            pdu_calls.append({"kwargs": kwargs, "result": result})
            return result

        cqr_pdu.pdu_url = _pdu_url
        cqr_pdu.pdu_ok = cqr_pdu.pdu_ok

        import cqr_get
        import cqr_sec

        importlib.reload(cqr_get)
        importlib.reload(cqr_sec)
        # Re-bind after reload (reload re-imports original pdu_url).
        cqr_get.pdu_url = _pdu_url
        cqr_sec.pdu_url = _pdu_url
        cqr_get.pdu_ok = cqr_pdu.pdu_ok
        cqr_sec.pdu_ok = cqr_pdu.pdu_ok

        cqr_get.poll_process = None
        cqr_get.last_sensor = 0
        cqr_get.timer_was_running = False
        cqr_get._gpio = None

        return cqr_env, cqr_pdu, cqr_get, cqr_sec

    return _reload
