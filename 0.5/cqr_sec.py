'''
Descriptions
    Run a simple count down to keep outlet state ON.

    Accept an adjustable parameter (seconds) to vary the delay.
    
    Parameters:
        count: in seconds (integer)
    
    Returns:
        Sucess | Failure

Notes
    This is a basic feedback loop which can be optimized as per the
    local conditions each RPi controller detects given the daily
    fluctuations in temperature and humidity.

Dependencies
    1. Avoid empty tank i.e. pumping air.
    2. Given duration defined in ENV, multiple subprocesses can start.
    3. No pre/post state checking to confirm OFF (default) vs ON.
    4. ...

Improvements
    - Reduce the number of above dependencies
    - ...
'''

# ----------------------------------------------------------------------
# Module(s).
# ----------------------------------------------------------------------
import logging, sys, time
from datetime import datetime

# ----------------------------------------------------------------------
# Import environment, data, and/or custom methods.
# ----------------------------------------------------------------------
import cqr_env
from cqr_pdu import pdu_curl, pdu_url

# Configure journal logging replacing print statements for state changes.
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def simple_timer(count):
    # Log state change event.
    logging.info(f"Start non-blocking timer for {count} seconds...")

    # Run a count down before PDU outlet is turned off.
    while count > 0:
        if count % 5 == 0:
            print(f"\t {count} seconds left...")
        time.sleep(1)
        count -= 1

    # Assign list items to variables for better readability.
    protocol_info = cqr_env.PDUS_SMARTLY[5].lower()
    vendor_info   = cqr_env.PDUS_SMARTLY[0]
    outlet_info   = cqr_env.PDUS_SMARTLY[4]

    # Turn off PDU outlet given default protocol.
    if protocol_info == "http":
        try:
            OFF_OUTLET = pdu_curl(vendor=vendor_info, outlet=outlet_info, action="FALSE")
            #logging.info("PDU outlet turned off via HTTP successfully.")
        except Exception as e:
            # NOTE: Replace 'Exception' with specific HTTP request errors if possible
            logging.error(f"Error executing pdu_curl: {e}")

    elif protocol_info == "ssh":
        try:
            OFF_OUTLET = pdu_url(protocol="SSH", outlet=outlet_info, action="FALSE")
            #logging.info("PDU outlet turned off via SSH successfully.")
        except Exception as e:
            # NOTE: Replace 'Exception' with specific SSH connection errors if possible
            logging.error(f"Error executing pdu_url: {e}")

if __name__ == "__main__":
    # Accept a count down integer from command line arguments.
    # When not valid, use 61 seconds as a fallback count.
    try:
        count = int(sys.argv[1]) if len(sys.argv) > 1 else 61
    except ValueError:
        logging.warning("Invalid input provided for timer count. Falling back to default: 61 seconds.")
        count = 61

    simple_timer(count)
