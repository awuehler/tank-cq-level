'''
Descriptions
    Run a simple count down to keep outlet state.

    Accept an adjustable parameter (seconds) to vary the delay.
    
    Parameters:
        count: in seconds (integer)
    
    Returns:
        Sucess | Failure

Notes
    This is a first draft to build a feedback loop which can
    be optimized across RPi and daily fluctuations in temperature
    and humidity.

Dependencies
    1. Avoid empty tank i.e. pumping air.
    2. ...

Improvements
    - ...
'''

# ----------------------------------------------------------------------
# Module(s).
# ----------------------------------------------------------------------
import subprocess, sys, time
from datetime import datetime

# ----------------------------------------------------------------------
# Import environment and data file(s).
# ----------------------------------------------------------------------
import cqr_env
import cqr_pdu

def simple_timer(count):
    print( datetime.now(), " : ", f"Start non-blocking timer for {count} seconds..." )
    while count > 0:
        print( "\t", f"{count} seconds left..." )
        time.sleep(1)
        count -= 1
    #print("Time's up!")
    PDU_TARGET   = f"https://{cqr_env.PDUS_SMARTLY[1]}/restapi/relay/outlets/7/state/"
    PDU_DIGEST   = f"{cqr_env.PDUS_SMARTLY[2]}:{cqr_env.PDUS_SMARTLY[3]}"
    PDU_RESPONSE = subprocess.run(['curl', '-k', '--digest', '--user', f"{PDU_DIGEST}", '-X', 'PUT', '-H', 'X-CSRF: x', '--data', 'value=false', f"{PDU_TARGET}"], text=True)

if __name__ == "__main__":
    # Accept a count down integer from command line arguments.
    # When missing, use 1 minute as a fallback count.
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 61
    simple_timer(count)
