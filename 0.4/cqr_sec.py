'''
Descriptions
    Run a simple count down to keep outlet state ON.

    Accept an adjustable parameter (seconds) to vary the delay.
    
    Parameters:
        count: in seconds (integer)
    
    Returns:
        Sucess | Failure

Notes
    This is a first draft to build a tiny feedback loop which can
    be optimized across RPi and daily fluctuations in temperature
    and humidity.

Dependencies
    1. Avoid empty tank i.e. pumping air.
    2. Given durations defined in ENV multiple subprocesses can run.
    3. No pre/post state checking to confirm OFF (default) vs ON.
    4. ...

Improvements
    - See above dependencies
    - ...
'''

# ----------------------------------------------------------------------
# Module(s).
# ----------------------------------------------------------------------
import subprocess, sys, time
from datetime import datetime

# ----------------------------------------------------------------------
# Import environment, data, and/or custom methods.
# ----------------------------------------------------------------------
import cqr_env
from cqr_pdu import pdu_curl, pdu_url

def simple_timer(count):

    # Log state change event.
    print(datetime.now(), f" Start non-blocking timer for {count} seconds...")

    # Count down before PDU outlet is turned off.
    while count > 0:
        if count % 5 == 0:
            print("\t", f"{count} seconds left...")
        time.sleep(1)
        count -= 1

    # Turn off PDU outlet.
    #OFF_OUTLET = pdu_curl(vendor={cqr_env.PDUS_SMARTLY[0]}, outlet={cqr_env.PDUS_SMARTLY[4]}, action="FALSE")
    OFF_OUTLET = pdu_url(protocol="SSH", outlet={cqr_env.PDUS_SMARTLY[4]}, action="FALSE")

if __name__ == "__main__":
    # Accept a count down integer from command line arguments.
    # When not valid, use 1 minute as a fallback count.
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 61
    simple_timer(count)
