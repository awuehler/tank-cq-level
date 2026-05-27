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
    - Define functions for each condition
    - Add priori state change awareness
    - ENV heartbeats & restarts: SYS, WiFi, PDU, DNS, etc.
    - ...
'''

# ----------------------------------------------------------------------
# Module(s).
# ----------------------------------------------------------------------
import RPi.GPIO as GPIO
import subprocess
import sys
import time
import logging

# Configure logging to system journal.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ----------------------------------------------------------------------
# Import environment, data, and/or custom methods.
# ----------------------------------------------------------------------
import cqr_env
from cqr_pdu import pdu_url

# Define mode to use GPIO pin via BCM pin numbering.
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN)

def get_pdu_state():
    # Helper to fetch PDU status.
    return pdu_url(protocol=cqr_env.PDUS_SMARTLY[5], outlet=cqr_env.PDUS_SMARTLY[4], action="GET")

def main():
    logging.info("Starting water sensor monitoring loop.")
    
    try:
        while True:
            # Read the RAW GPIO value (binary).
            cqr_value = GPIO.input(18)

            if cqr_env.BOOL_OUTPUTS[0]:
                if cqr_value == 0:
                    logging.info(f"CQRobot: {cqr_value} (H2O level below sensor)")
                    state = get_pdu_state()
                    logging.info(f"{cqr_env.PDUS_SMARTLY[4]}: {state} (outlet power state)")

                elif cqr_value == 1:
                    logging.info(f"CQRobot: {cqr_value} (H2O level at sensor)")
                    
                    # Trigger PDU state change.
                    pdu_url(protocol=cqr_env.PDUS_SMARTLY[5], outlet=cqr_env.PDUS_SMARTLY[4], action="TRUE")
                    
                    # Log state and trigger timer.
                    state = get_pdu_state()
                    logging.info(f"{cqr_env.PDUS_SMARTLY[4]}: {state} (outlet power state)")
                    
                    # Call non-blocking timer.
                    subprocess.Popen([sys.executable, "cqr_sec.py", cqr_env.TIME_CHECKED[1]])
                
                else:
                    logging.error(f"{cqr_value}: Unexpected sensor reading.")
                    # TODO: Implement recovery logic (e.g., reset GPIO/alert)
                    break

            time.sleep(float(cqr_env.TIME_CHECKED[0]))
    
    except KeyboardInterrupt:
        logging.info("Program stopped by user.")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    # Bootstrap: Ensure outlet is OFF on startup.
    try:
        pdu_url(protocol=cqr_env.PDUS_SMARTLY[5], outlet=cqr_env.PDUS_SMARTLY[4], action="FALSE")
    except Exception as e:
        logging.error(f"Failed to bootstrap PDU state: {e}")
        
    main()
