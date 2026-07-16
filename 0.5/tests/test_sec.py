"""Tests for cqr_sec timer / outlet OFF behavior."""

from unittest.mock import patch

import pytest


def test_unknown_protocol_raises(reload_modules, pdu_calls):
    from dataclasses import replace

    cqr_env, _pdu, _get, cqr_sec = reload_modules()
    cqr_env.PDU = replace(cqr_env.PDU, protocol="protocol")

    with patch.object(cqr_sec.time, "sleep", return_value=None):
        with pytest.raises(ValueError, match="protocol"):
            cqr_sec.simple_timer(0)

    assert pdu_calls == []


def test_http_turns_outlet_off(reload_modules, pdu_calls):
    from dataclasses import replace

    cqr_env, _pdu, _get, cqr_sec = reload_modules()
    cqr_env.PDU = replace(cqr_env.PDU, protocol="http", outlet="7")

    with patch.object(cqr_sec.time, "sleep", return_value=None):
        cqr_sec.simple_timer(0)

    off_calls = [c for c in pdu_calls if str(c["kwargs"].get("action", "")).upper() == "FALSE"]
    assert len(off_calls) == 1
    assert off_calls[0]["kwargs"]["protocol"] == "http"


def test_off_failure_raises(reload_modules, pdu_calls):
    from dataclasses import replace

    def fail_off(kwargs):
        if str(kwargs.get("action", "")).upper() == "FALSE":
            return {"error": "Command failed"}
        return {"ok": True}

    cqr_env, _pdu, _get, cqr_sec = reload_modules(pdu_side_effect=fail_off)
    cqr_env.PDU = replace(cqr_env.PDU, protocol="http")

    with patch.object(cqr_sec.time, "sleep", return_value=None):
        with pytest.raises(RuntimeError, match="OFF failed"):
            cqr_sec.simple_timer(0)


def test_default_timer_count_uses_env(reload_modules):
    cqr_env, _pdu, _get, cqr_sec = reload_modules()
    cqr_env.PUMP_ON_DURATION_SEC = 42
    assert cqr_sec.default_timer_count() == 42
