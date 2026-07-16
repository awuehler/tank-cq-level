"""Tests for cqr_get control loop behavior."""

from pathlib import Path
from unittest.mock import MagicMock, patch


def _sleep_interrupt_after(n):
    state = {"i": 0}

    def _sleep(_seconds):
        state["i"] += 1
        if state["i"] >= n:
            raise KeyboardInterrupt

    return _sleep


def test_gpio_not_initialized_at_import(reload_modules, fake_gpio_module):
    cqr_env, _pdu, cqr_get, _sec = reload_modules()
    # Import/reload must not call setmode/setup; only setup_gpio() should.
    fake_gpio_module.setmode.assert_not_called()
    fake_gpio_module.setup.assert_not_called()
    cqr_get.setup_gpio(cqr_env.GPIO_PIN)
    fake_gpio_module.setmode.assert_called_once()
    fake_gpio_module.setup.assert_called_once()


def test_control_runs_when_debug_off(reload_modules, pdu_calls, fake_gpio_module):
    cqr_env, _pdu, cqr_get, _sec = reload_modules()
    cqr_env.BOOL_OUTPUTS = [False]
    cqr_env.POLL_INTERVAL_SEC = 0.01
    fake_gpio_module.input.side_effect = [1]
    fake_proc = MagicMock()
    fake_proc.poll.return_value = 0
    cqr_get._gpio = fake_gpio_module

    with (
        patch.object(cqr_get.subprocess, "Popen", return_value=fake_proc) as popen,
        patch.object(cqr_get.time, "sleep", side_effect=KeyboardInterrupt),
    ):
        cqr_get.main()

    on_calls = [c for c in pdu_calls if str(c["kwargs"].get("action", "")).upper() == "TRUE"]
    assert on_calls
    assert popen.call_count == 1
    timer_path = Path(popen.call_args.args[0][1])
    assert timer_path.name == "cqr_sec.py"
    assert timer_path.is_absolute()


def test_on_failure_skips_timer(reload_modules, pdu_calls, fake_gpio_module):
    def fail_on_true(kwargs):
        if str(kwargs.get("action", "")).upper() == "TRUE":
            return {"error": "Command failed"}
        return {"ok": True}

    cqr_env, _pdu, cqr_get, _sec = reload_modules(pdu_side_effect=fail_on_true)
    cqr_env.BOOL_OUTPUTS = [False]
    cqr_env.POLL_INTERVAL_SEC = 0.01
    fake_gpio_module.input.side_effect = [1]
    cqr_get._gpio = fake_gpio_module

    with (
        patch.object(cqr_get.subprocess, "Popen") as popen,
        patch.object(cqr_get.time, "sleep", side_effect=KeyboardInterrupt),
    ):
        cqr_get.main()

    assert popen.call_count == 0
    assert any(c["result"].get("error") for c in pdu_calls)


def test_sustained_high_is_edge_triggered(reload_modules, pdu_calls, fake_gpio_module):
    cqr_env, _pdu, cqr_get, _sec = reload_modules()
    cqr_env.BOOL_OUTPUTS = [False]
    cqr_env.POLL_INTERVAL_SEC = 0.01
    fake_gpio_module.input.side_effect = [0, 1, 1, 1, 1]
    fake_proc = MagicMock()
    fake_proc.poll.return_value = None
    cqr_get._gpio = fake_gpio_module
    cqr_get.last_sensor = 0

    with (
        patch.object(cqr_get.subprocess, "Popen", return_value=fake_proc) as popen,
        patch.object(cqr_get.time, "sleep", side_effect=_sleep_interrupt_after(5)),
    ):
        cqr_get.main()

    on_calls = [c for c in pdu_calls if str(c["kwargs"].get("action", "")).upper() == "TRUE"]
    assert len(on_calls) == 1
    assert popen.call_count == 1


def test_rearms_after_off_if_still_high(reload_modules, pdu_calls, fake_gpio_module):
    cqr_env, _pdu, cqr_get, _sec = reload_modules()
    cqr_env.BOOL_OUTPUTS = [False]
    cqr_env.POLL_INTERVAL_SEC = 0.01
    fake_gpio_module.input.side_effect = [1, 1, 1, 1, 1]
    proc = MagicMock()
    proc.poll.side_effect = [None, None, 0, 0, 0]
    cqr_get._gpio = fake_gpio_module
    cqr_get.last_sensor = 0

    with (
        patch.object(cqr_get.subprocess, "Popen", return_value=proc) as popen,
        patch.object(cqr_get.time, "sleep", side_effect=_sleep_interrupt_after(5)),
    ):
        cqr_get.main()

    on_calls = [c for c in pdu_calls if str(c["kwargs"].get("action", "")).upper() == "TRUE"]
    assert len(on_calls) >= 2
    assert popen.call_count >= 2
