# TODO:
#   - Extend to include +1 vendor support
#   - Fail fast on unresolved host/credential placeholders at startup

"""Site-local runtime configuration for the tank CQ level controller."""

from dataclasses import dataclass

# ----------------------------------------------------------------------
# Hardware / timing seed values (document local pump & tank).
# ----------------------------------------------------------------------
PUMP_FEATURE = ["3.5 GPM", "45 PSI"]
TANK_FEATURE = ["3.0 GAL", "12 INCH"]

# Poll interval (sensor loop) and pump-on duration (timer subprocess), seconds.
POLL_INTERVAL_SEC = 37.29
PUMP_ON_DURATION_SEC = 61

# Extra stdout / verbose journal logging for sensor + PDU state.
BOOL_OUTPUTS = [True]

# BCM GPIO pin for the CQRobot optical level sensor.
GPIO_PIN = 18

# Subprocess timeout for curl/ssh PDU commands (seconds).
PDU_COMMAND_TIMEOUT_SEC = 30

# Digital Loggers PDUs commonly present self-signed TLS certificates.
# When True, curl uses -k (insecure skip-verify). Prefer pinning the device
# certificate (or installing a local CA) and setting this to False in production.
PDU_TLS_INSECURE = True


@dataclass(frozen=True)
class PduConfig:
    """Named PDU connection settings (replaces magic list indices)."""

    vendor: str
    host: str
    user: str
    password: str
    outlet: str
    protocol: str  # "http" or "ssh"


# Update host, credentials, outlet, and protocol for the local deployment.
PDU = PduConfig(
    vendor="DWL",
    host="192.168.XXX.YYY",
    user="userX",
    password="passY",
    outlet="7",
    protocol="http",
)

# Back-compat aliases used by older comments/docs; prefer POLL_INTERVAL_SEC /
# PUMP_ON_DURATION_SEC and PDU in new code.
TIME_CHECKED = [str(POLL_INTERVAL_SEC), str(PUMP_ON_DURATION_SEC)]
