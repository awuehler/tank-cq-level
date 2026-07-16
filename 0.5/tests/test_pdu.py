"""Tests for cqr_pdu helpers and subprocess behavior."""

from unittest.mock import MagicMock, patch

import pytest


def test_pdu_ok_detects_error_dicts():
    import cqr_pdu

    assert cqr_pdu.pdu_ok({"physical_state": True}) is True
    assert cqr_pdu.pdu_ok("true") is True
    assert cqr_pdu.pdu_ok(None) is False
    assert cqr_pdu.pdu_ok({"error": "Command failed"}) is False


def test_run_curl_applies_timeout():
    import cqr_pdu

    manager = cqr_pdu.PDUManager()
    completed = MagicMock()
    completed.stdout = '{"ok": true}'
    completed.stderr = ""

    with patch("cqr_pdu.subprocess.run", return_value=completed) as run:
        result = manager.run_curl(["curl", "https://example.test"], timeout=12)

    assert result == {"ok": True}
    assert run.call_args.kwargs["timeout"] == 12


def test_run_curl_timeout_returns_error_dict():
    import subprocess

    import cqr_pdu

    manager = cqr_pdu.PDUManager()
    with patch(
        "cqr_pdu.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd=["curl"], timeout=5),
    ):
        result = manager.run_curl(["curl", "https://example.test"], timeout=5)

    assert isinstance(result, dict)
    assert result["error"] == "Command timed out"
    assert cqr_pdu.pdu_ok(result) is False


def test_pdu_url_uses_outlet_argument_and_tls_flag():
    import cqr_env
    import cqr_pdu

    manager = cqr_pdu.PDUManager()
    captured = {}
    original_tls = cqr_env.PDU_TLS_INSECURE

    def fake_run(args, timeout=None):
        captured["args"] = list(args)
        captured["timeout"] = timeout
        return "true"

    manager.run_curl = fake_run  # type: ignore[method-assign]
    try:
        cqr_env.PDU_TLS_INSECURE = True
        manager.pdu_url(protocol="http", outlet="3", action="TRUE")
        assert "/restapi/relay/outlets/3/state/" in captured["args"][-1]
        assert "-k" in captured["args"]
        assert "--max-time" in captured["args"]

        cqr_env.PDU_TLS_INSECURE = False
        manager.pdu_url(protocol="http", outlet="3", action="FALSE")
        assert "-k" not in captured["args"]
    finally:
        cqr_env.PDU_TLS_INSECURE = original_tls


def test_pdu_url_rejects_bad_protocol():
    import importlib

    import cqr_pdu

    importlib.reload(cqr_pdu)
    with pytest.raises(ValueError, match="protocol"):
        cqr_pdu.PDUManager().pdu_url(protocol="ftp", outlet="7", action="GET")
