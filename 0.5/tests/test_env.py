"""Tests for cqr_env configuration."""

from dataclasses import fields


def test_pdu_config_is_named_dataclass():
    import cqr_env

    names = {f.name for f in fields(cqr_env.PduConfig)}
    assert names == {"vendor", "host", "user", "password", "outlet", "protocol"}
    assert cqr_env.PDU.vendor == "DWL"
    assert isinstance(cqr_env.POLL_INTERVAL_SEC, float)
    assert isinstance(cqr_env.PUMP_ON_DURATION_SEC, int)
    assert cqr_env.GPIO_PIN == 18
    assert cqr_env.PDU_COMMAND_TIMEOUT_SEC > 0
    assert isinstance(cqr_env.PDU_TLS_INSECURE, bool)


def test_time_checked_aliases_match_typed_constants():
    import cqr_env

    assert float(cqr_env.TIME_CHECKED[0]) == cqr_env.POLL_INTERVAL_SEC
    assert int(float(cqr_env.TIME_CHECKED[1])) == cqr_env.PUMP_ON_DURATION_SEC
