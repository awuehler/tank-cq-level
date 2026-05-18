#!/usr/bin/env python3

'''
Descriptions
    Third draft of program to monitor the binary output from a sensor.

    Turn on/off PDU outlet to activate an RV pump which drains a tank.

    Pump-on events will auto adjust given rate of fill per conditions.

Notes
    Design goal is to read the GPIO output continously to check for the
    water level within a condensation tank (any slow fill catch basin).

Dependencies
    Requires:
        1. CQ Robot Water Sensor
        2. Digital Web Loggers PDU
        3. RV Water Pump (tubing, values, ...)
        4. WiFi (between RPi & PDU)

Improvements
    - Define functions for each condition
    - Redirect from standard out to logfile
    - 
'''

# ----------------------------------------------------------------------
# Module(s).
# ----------------------------------------------------------------------
import RPi.GPIO as GPIO
from datetime import datetime
import subprocess, sys, time

# ----------------------------------------------------------------------
# Import environment and data file(s).
# ----------------------------------------------------------------------
import cqr_env
import cqr_pdu

# Define mode to use GPIO pin via BCM pin numbering.
GPIO.setmode(GPIO.BCM)
GPIO.setup(18,GPIO.IN)

def main():
    # Create always true loop.
    try:
        while True:
            # Read the RAW GPIO value (binary).
            CQR_VALUE = GPIO.input(18)
            
            # Session token.
            PDU_TARGET = f"https://{cqr_env.PDUS_SMARTLY[1]}/api/login"
            PDU_DIGEST = f"username={cqr_env.PDUS_SMARTLY[2]}&password={cqr_env.PDUS_SMARTLY[3]}"
            PDU_TOKENS = cqr_pdu.run_curl(["curl", "-s", "-k", "-X POST", "-H 'Accept: application/json'", "-H 'Content-Type: application/x-www-form-urlencoded'", "-d" f"{PDU_DIGEST}", f"{PDU_TARGET}"])
            #print( f"PDU Session State: {PDU_TOKENS}" )

            # Report tank condition.
            if CQR_VALUE == 0:
                # Do nothing.
                if cqr_env.BOOL_OUTPUTS[0] is True:
                    print( datetime.now(), " : ", f"{CQR_VALUE}: H2O level is below sensor" )
                    # TODO: heartbeat check system/process/wifi/pdu; ...
                    # Example: curl -s -k -H "Accept: application/json" --digest "https://<USER>:<PASS>@<IP>/restapi/relay/outlets/=<0-7>/state/"
                    # Example: curl -k --digest -u admin:admin -H "Accept: application/json" --digest 'http://192.168.156.109/restapi/relay/outlets/0/=name,physical_state/'
                    PDU_TARGET   = f"https://{cqr_env.PDUS_SMARTLY[1]}/restapi/relay/outlets/7/=name,physical_state/"
                    PDU_DIGEST   = f"{cqr_env.PDUS_SMARTLY[2]}:{cqr_env.PDUS_SMARTLY[3]}"
                    #PDU_RESPONSE = cqr_pdu.run_curl(["curl", "-s", "-k", "-X GET", "-H 'Accept: application/json'", "-u" f"{PDU_DIGEST}", "--digest", f"{PDU_TARGET}"])
                    PDU_RESPONSE = cqr_pdu.run_curl(["curl", "-s", "-k", "--digest", "-u" f"{PDU_DIGEST}", "-H 'Accept: application/json'", "--digest", f"{PDU_TARGET}"])
                    print( "\t", f"PDU Outlet State: {PDU_RESPONSE}" )
            elif CQR_VALUE == 1:
                # Do something.
                if cqr_env.BOOL_OUTPUTS[0] is True:
                    print( datetime.now(), " : ", f"{CQR_VALUE}: H2O level is at sensor" )
                    # TODO: get/set countdown timer; get/set PDU outlet state; ...
                    # Example: curl -s -k --digest --user admin:admin -X PUT -H "X-CSRF: x" --data "value=true" 'http://192.168.156.109/restapi/relay/outlets/7/state/'
                    PDU_TARGET   = f"https://{cqr_env.PDUS_SMARTLY[1]}/restapi/relay/outlets/7/state/"
                    PDU_DIGEST   = f"{cqr_env.PDUS_SMARTLY[2]}:{cqr_env.PDUS_SMARTLY[3]}"
                    PDU_RESPONSE = subprocess.run(['curl', '-k', '--digest', '--user', f"{PDU_DIGEST}", '-X', 'PUT', '-H', 'X-CSRF: x', '--data', 'value=true', f"{PDU_TARGET}"], text=True)
                    #print( f"PDU Outlet State: {PDU_RESPONSE}")
                    # This subprocess.Popen will run a process in the background without blocking.
                    process = subprocess.Popen([sys.executable, "cqr_sec.py", cqr_env.TIME_CHECKED[1]])

            else:
                # Do something else.
                if cqr_env.BOOL_OUTPUTS[0] is True:
                    print( datetime.now(), " : ", f"{CQR_VALUE}: Something is wrong with sensor" )
                    # TODO: check sensor; check system; restart process; restart system; ...

            # Delay interval.
            time.sleep( float(cqr_env.TIME_CHECKED[0]) )
    
    except KeyboardInterrupt:
        print( "\nProgram stopped by user input...\n" )
    finally:
        # Reset GPIO settings.
        GPIO.cleanup()

if __name__ == "__main__":
    """
        Setup to support both "shebang" and "import" code execution
        either as a script and/or imported into another module.
        Isolate all user defined file updates to this section.
    """
    # Optimize for local runtime environment: See cqr_env.py
    
    # Main function to access GPIO data generated by water sensor.
    main()
