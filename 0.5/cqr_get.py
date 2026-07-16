#!/usr/bin/env python3

'''
Descriptions
    A v0.5 of control program to monitor the binary sensor output.

    Turn ON/OFF PDU outlet to activate an RV pump which drains a tank.

    Pump-on events are adjustable given rate of fill per conditions.

Notes
    Design goal is to read the GPIO output continously to check for the
    water level within a condensation tank (any slow fill catch basin).

Dependencies
    Assumes Python 3.x.
    Requires:
        1. CQ Robot Water Sensor
        2. Digital Web Loggers PDU
        3. RV Water Pump (tubing, values, ...)
        4. WiFi (between RPi & PDU)

Improvements
    - ENV heartbeats & restarts: SYS, WiFi, PDU, DNS, etc.
    - Sensor debounce for droplet false positives
    - ...
'''

# ----------------------------------------------------------------------
# Module(s).
# ----------------------------------------------------------------------
import logging
import subprocess
import sys
import time
from pathlib import Path

# ----------------------------------------------------------------------
# Import environment, data, and/or custom methods.
# ----------------------------------------------------------------------
import cqr_env
from cqr_pdu import pdu_ok, pdu_url

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Directory containing this script (used for absolute cqr_sec.py path).
_SCRIPT_DIR = Path(__file__).resolve().parent
_TIMER_SCRIPT = _SCRIPT_DIR / "cqr_sec.py"

# Runtime loop state (initialized in main / tests).
poll_process = None
last_sensor = 0
timer_was_running = False
_gpio = None


def setup_gpio(pin: int | None = None):
    """Initialize BCM GPIO input. Called from main so imports stay hardware-free."""
    global _gpio
    import RPi.GPIO as GPIO

    pin = cqr_env.GPIO_PIN if pin is None else pin
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN)
    _gpio = GPIO
    return GPIO


def get_pdu_state():
    pdu = cqr_env.PDU
    return pdu_url(protocol=pdu.protocol, outlet=pdu.outlet, action="GET")


def start_pump_cycle():
    """Turn PDU outlet ON and spawn the non-blocking off-timer if ON succeeds."""
    global poll_process, timer_was_running

    pdu = cqr_env.PDU
    result = pdu_url(protocol=pdu.protocol, outlet=pdu.outlet, action="TRUE")
    if not pdu_ok(result):
        logging.error(f"PDU outlet ON failed; timer not started. result={result}")
        return False

    if cqr_env.BOOL_OUTPUTS[0]:
        state = get_pdu_state()
        logging.info(f"{pdu.outlet}: {state} (outlet power state)")

    poll_process = subprocess.Popen(
        [
            sys.executable,
            str(_TIMER_SCRIPT),
            str(int(cqr_env.PUMP_ON_DURATION_SEC)),
        ]
    )
    return True


def main():
    global poll_process, last_sensor, timer_was_running, _gpio

    gpio = _gpio if _gpio is not None else setup_gpio()
    logging.info("Starting water sensor monitoring loop.")

    try:
        while True:
            cqr_value = gpio.input(cqr_env.GPIO_PIN)
            timer_running = poll_process is not None and poll_process.poll() is None
            timer_finished = timer_was_running and not timer_running

            if cqr_value == 0:
                if cqr_env.BOOL_OUTPUTS[0]:
                    logging.info(f"CQRobot: {cqr_value} (H2O level below sensor)")
                    state = get_pdu_state()
                    logging.info(f"{cqr_env.PDU.outlet}: {state} (outlet power state)")

            elif cqr_value == 1:
                if cqr_env.BOOL_OUTPUTS[0]:
                    logging.info(f"CQRobot: {cqr_value} (H2O level at sensor)")

                rising_edge = last_sensor == 0
                should_start = (not timer_running) and (rising_edge or timer_finished)

                if should_start:
                    if start_pump_cycle():
                        timer_running = True

            else:
                logging.error(f"{cqr_value}: Unexpected sensor reading.")
                # TODO: Implement recovery logic (e.g., reset GPIO/alert)
                break

            last_sensor = cqr_value
            timer_was_running = timer_running
            time.sleep(float(cqr_env.POLL_INTERVAL_SEC))

    except KeyboardInterrupt:
        logging.info("Program stopped by user.")
    finally:
        if _gpio is not None:
            _gpio.cleanup()
            _gpio = None


if __name__ == "__main__":
    setup_gpio()
    try:
        pdu = cqr_env.PDU
        result = pdu_url(protocol=pdu.protocol, outlet=pdu.outlet, action="FALSE")
        if not pdu_ok(result):
            logging.error(f"Failed to bootstrap PDU state OFF: {result}")
    except Exception as e:
        logging.error(f"Failed to bootstrap PDU state: {e}")

    main()
