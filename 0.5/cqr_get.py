#!/usr/bin/env python3

'''
Descriptions
    A v0.3 draft of program to monitor the binary output from a sensor.

    Turn ON/OFF PDU outlet to activate an RV pump which drains a tank.

    Pump-on events will auto adjust given rate of fill per conditions.

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
    - Redirect from standard out to logfile
    - Exceptions handling and a priori state change awareness
    - ENV heartbeats & restarts: SYS, WiFi, PDU, DNS, etc.
    - Add additional try statements for each curl or ssh subprocess call
    - Clean-up code in support of protocol options
    - Update configuration to set default protocol
    - ...
'''

'''
# ----------------------------------------------------------------------
# Module(s).
# ----------------------------------------------------------------------
import RPi.GPIO as GPIO
from datetime import datetime
import ast, subprocess, sys, time

# ----------------------------------------------------------------------
# Import environment, data, and/or custom methods.
# ----------------------------------------------------------------------
import cqr_env
from cqr_pdu import run_curl, pdu_curl, pdu_url

# Define mode to use GPIO pin via BCM pin numbering.
GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.IN)

def main():
    # Create always true loop.
    try:
        while True:

            # Read the RAW GPIO value (binary).
            CQR_VALUE = GPIO.input(18)

            # Report tank condition.
            if CQR_VALUE == 0:
                # Do nothing.
                if cqr_env.BOOL_OUTPUTS[0] is True:
                    # Log current sensor and PDU states.
                    print(datetime.now(), " CQRobot:", f"{CQR_VALUE} (H2O level below sensor)  ", end="")
                    PDU_TARGET  = f"https://{cqr_env.PDUS_SMARTLY[1]}/restapi/relay/outlets/{cqr_env.PDUS_SMARTLY[4]}/=name,physical_state/"
                    PDU_DIGEST  = f"{cqr_env.PDUS_SMARTLY[2]}:{cqr_env.PDUS_SMARTLY[3]}"
                    #PDU_RETURN  = run_curl(["curl", "--silent", "-k", "--digest", "--user", f"{PDU_DIGEST}", "-H 'Accept: application/json'", "--digest", f"{PDU_TARGET}"])
                    PDU_RETURN  = pdu_url(protocol="SSH", outlet={cqr_env.PDUS_SMARTLY[4]}, action="GET")
                    print(f"{cqr_env.PDUS_SMARTLY[0]}:", f"{PDU_RETURN} (outlet power state)", flush=True)

            elif CQR_VALUE == 1:
                # Do something.
                if cqr_env.BOOL_OUTPUTS[0] is True:
                    # Sensor event triggers PDU outlet state change.
                    print(datetime.now(), " CQRobot:", f"{CQR_VALUE} (H2O level is at sensor)  ", end="")
                    PDU_TARGET  = f"https://{cqr_env.PDUS_SMARTLY[1]}/restapi/relay/outlets/{cqr_env.PDUS_SMARTLY[4]}/state/"
                    PDU_DIGEST  = f"{cqr_env.PDUS_SMARTLY[2]}:{cqr_env.PDUS_SMARTLY[3]}"
                    #ON_OUTLET   = pdu_curl(vendor={cqr_env.PDUS_SMARTLY[0]}, outlet={cqr_env.PDUS_SMARTLY[4]}, action="TRUE")
                    ON_OUTLET   = pdu_url(protocol="SSH", outlet={cqr_env.PDUS_SMARTLY[4]}, action="TRUE")
                    # Log PDU outlet state change.
                    PDU_TARGET  = f"https://{cqr_env.PDUS_SMARTLY[1]}/restapi/relay/outlets/{cqr_env.PDUS_SMARTLY[4]}/=name,physical_state/"
                    #PDU_RETURN  = run_curl(["curl", "--silent", "-k", "--digest", "--user", f"{PDU_DIGEST}", "-H 'Accept: application/json'", "--digest", f"{PDU_TARGET}"])
                    PDU_RETURN  = pdu_url(protocol="SSH", outlet={cqr_env.PDUS_SMARTLY[4]}, action="GET")
                    print(f"{cqr_env.PDUS_SMARTLY[0]}:", f"{PDU_RETURN} (outlet power state)", flush=True)

                # TODO: Convert the CompletedProcess object from subprocess.run to string
                # TODO: Add condition check for previously running sub process(es)

                    # Call a non-blocking method to run a count down timer.
                    TIMER_PROCESS = subprocess.Popen([sys.executable, "cqr_sec.py", cqr_env.TIME_CHECKED[1]])
            else:
                # Do something else.
                if cqr_env.BOOL_OUTPUTS[0] is True:
                    print(datetime.now(), " : ", f"{CQR_VALUE}: Something is wrong with sensor")

                # TODO: Power cycle RPi or reset GPIO pin(s) or Pager Duty alert or ...
                # Reset GPIO settings.
                GPIO.cleanup()

            # Delay interval.
            time.sleep(float(cqr_env.TIME_CHECKED[0]))
    
    except KeyboardInterrupt:
        print("\nProgram stopped by user input...\n")
    finally:
        # Reset GPIO settings.
        GPIO.cleanup()

if __name__ == "__main__":
    """
        Setup to support both "shebang" and "import" code execution
        either as a script and/or imported into another module.
        Isolate all user defined file updates to this section.
    """
    # Turn off PDU outlet to RV pump...
    # i.e. a pre-check bootstrap given unknown runtime conditions.
    #OFF_OUTLET = pdu_curl(vendor={cqr_env.PDUS_SMARTLY[0]}, outlet={cqr_env.PDUS_SMARTLY[4]}, action="FALSE")
    #OFF_OUTLET = pdu_url(protocol="SSH", outlet={cqr_env.PDUS_SMARTLY[4]}, action="FALSE")
    if {cqr_env.PDUS_SMARTLY[5]}.lower() == "http":
        OFF_OUTLET = pdu_curl(vendor={cqr_env.PDUS_SMARTLY[0]}, outlet={cqr_env.PDUS_SMARTLY[4]}, action="FALSE")
    elif {cqr_env.PDUS_SMARTLY[5]}.lower() == "ssh":
        OFF_OUTLET = pdu_url(protocol="SSH", outlet={cqr_env.PDUS_SMARTLY[4]}, action="FALSE")

    # Main function to access GPIO data generated by water sensor.
    main()
'''

# ----------------------------------------------------------------------
# Module(s).
# ----------------------------------------------------------------------
import RPi.GPIO as GPIO
import subprocess
import sys
import time
import logging

# Configure logging
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
    """Helper to fetch PDU status."""
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
