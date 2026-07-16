'''
Descriptions
    Run a simple countdown to keep the PDU outlet ON, then turn it OFF.

    Accept an adjustable parameter (seconds) to vary the delay.

Parameters
    count: pump-on duration in seconds (integer)

Returns
    None on success; raises on invalid protocol or failed OFF.

Notes
    Duration is chosen for local fill rate / humidity so the pump clears
    water without running dry for long. cqr_get spawns at most one timer
    process at a time (edge-triggered ON + poll guard). This script still
    verifies the OFF result so a failed PDU call is not silent.

Dependencies
    1. Avoid extended empty-tank pumping (tune PUMP_ON_DURATION_SEC).
    2. Parent process (cqr_get) owns single-timer concurrency.
    3. OFF success is checked via pdu_ok; failures raise after logging.
'''

# ----------------------------------------------------------------------
# Module(s).
# ----------------------------------------------------------------------
import logging
import sys
import time

# ----------------------------------------------------------------------
# Import environment, data, and/or custom methods.
# ----------------------------------------------------------------------
import cqr_env
from cqr_pdu import pdu_ok, pdu_url

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def simple_timer(count):
    logging.info(f"Start non-blocking timer for {count} seconds...")

    while count > 0:
        if count % 5 == 0:
            logging.info(f"{count} seconds left...")
        time.sleep(1)
        count -= 1

    pdu = cqr_env.PDU
    protocol_info = pdu.protocol.lower()
    outlet_info = pdu.outlet

    if protocol_info not in ("http", "ssh"):
        msg = (
            f"Invalid PDU protocol {protocol_info!r}; "
            "expected 'http' or 'ssh'. Refusing to leave outlet ON."
        )
        logging.error(msg)
        raise ValueError(msg)

    try:
        result = pdu_url(protocol=protocol_info, outlet=outlet_info, action="FALSE")
        if not pdu_ok(result):
            msg = f"PDU outlet OFF failed via {protocol_info}: {result}"
            logging.error(msg)
            raise RuntimeError(msg)
        logging.info(f"PDU outlet turned off via {protocol_info.upper()}.")
    except Exception as e:
        logging.error(f"Error turning PDU outlet off via {protocol_info}: {e}")
        raise


def default_timer_count() -> int:
    """Pump-on duration from env; used when argv is missing or invalid."""
    return int(cqr_env.PUMP_ON_DURATION_SEC)


if __name__ == "__main__":
    fallback = default_timer_count()
    try:
        count = int(sys.argv[1]) if len(sys.argv) > 1 else fallback
    except ValueError:
        logging.warning(
            f"Invalid input for timer count. Falling back to PUMP_ON_DURATION_SEC={fallback}."
        )
        count = fallback

    simple_timer(count)
