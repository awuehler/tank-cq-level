'''
Descriptions
    PDUManager issues HTTP or SSH commands to a Digital Loggers smart PDU.

    Auto-detects JSON responses and returns them as dicts when possible.

Notes
    Reference: https://www.digital-loggers.com/restapi.pdf

    Example outlet ON (HTTP digest auth):
        curl -s -k -X PUT -H "X-CSRF: x" --data "value=true" --digest
        --user "<USER>:<PASS>"
        "https://<IP>/restapi/relay/outlets/<N>/state/"

    Example outlet OFF:
        ... --data "value=false" ...

    Example outlet STATE (name + physical_state):
        curl -s -k -H "Accept: application/json" --digest --user "<USER>:<PASS>"
        "https://<IP>/restapi/relay/outlets/<N>/=name,physical_state/"

    TLS:
        curl -k is controlled by cqr_env.PDU_TLS_INSECURE. Local PDUs often use
        self-signed certificates; leave insecure skip-verify enabled until a
        device certificate (or local CA) is pinned, then set PDU_TLS_INSECURE
        to False.

Dependencies
    1. URL construction is vendor specific (Digital Loggers Pro Switch first).
    2. Remote outlet ON/OFF via HTTP/S or SSH+local curl on the PDU.
'''

# ----------------------------------------------------------------------
# Module(s).
# ----------------------------------------------------------------------
import json
import logging
import subprocess

# ----------------------------------------------------------------------
# Import environment, data, and/or custom methods.
# ----------------------------------------------------------------------
import cqr_env

logger = logging.getLogger(__name__)


def pdu_ok(result) -> bool:
    """Return True when a PDU call did not report a command/timeout error."""
    if result is None:
        return False
    if isinstance(result, dict) and "error" in result:
        return False
    return True


class PDUManager:

    def run_curl(self, command: list, timeout: float | None = None):
        """Run curl/ssh with a hard timeout so a hung PDU cannot block forever."""
        if timeout is None:
            timeout = float(cqr_env.PDU_COMMAND_TIMEOUT_SEC)
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout,
            )
            output = result.stdout.strip()
            try:
                return json.loads(output)
            except json.JSONDecodeError:
                return output

        except subprocess.TimeoutExpired as e:
            logger.error(f"Command timed out after {timeout}s: {command[0]}")
            return {"error": "Command timed out", "timeout": timeout, "stderr": e.stderr}

        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed with exit code {e.returncode}. Stderr: {e.stderr}")
            return {"error": "Command failed", "stderr": e.stderr}


    def pdu_curl(self, vendor: str, outlet: str, action: str):
        '''
        Legacy wrapper: HTTP curl for PDU based on vendor, outlet, and action.

        TODO: Use vendor parameter to support additional smart PDU APIs.
        '''
        return self.pdu_url(protocol="http", outlet=outlet, action=action)


    def pdu_url(self, protocol: str, outlet: str | None = None, action: str = "get"):
        '''
        Execute a curl (or SSH-wrapped curl) command for the configured PDU.

        Args:
            protocol: "http" or "ssh".
            outlet: Outlet id; defaults to cqr_env.PDU.outlet when omitted/empty.
            action: "true", "false", or "get".
        '''
        action = action.lower()
        if action not in ["true", "false", "get"]:
            raise ValueError("Invalid action. Must be 'true', 'false', or 'get'...")

        pdu = cqr_env.PDU
        pdu_ip = pdu.host
        pdu_user = pdu.user
        pdu_pass = pdu.password
        pdu_outlet = outlet if outlet not in (None, "") else pdu.outlet
        pdu_digest = f"{pdu_user}:{pdu_pass}"
        tls_insecure = bool(cqr_env.PDU_TLS_INSECURE)
        # -k skips certificate verification for self-signed PDU certs when enabled.
        tls_args = ["-k"] if tls_insecure else []

        if action in ["true", "false"]:
            http_method = "PUT"
            target_path = f"/restapi/relay/outlets/{pdu_outlet}/state/"
            action_data = f"value={action}"
            headers = ["-H", "X-CSRF: x"]
        else:
            http_method = "GET"
            target_path = f"/restapi/relay/outlets/{pdu_outlet}/=name,physical_state/"
            action_data = ""
            headers = ["-H", "Accept: application/json", "-H", "X-CSRF: x"]

        # Bound curl's own transfer time in addition to subprocess timeout.
        max_time = ["--max-time", str(int(cqr_env.PDU_COMMAND_TIMEOUT_SEC))]

        if protocol.lower() == "http":
            target_url = f"https://{pdu_ip}{target_path}"
            args = (
                ["curl", "--silent"]
                + tls_args
                + max_time
                + ["--digest", "--user", pdu_digest, "-X", http_method]
                + headers
            )
            if action_data:
                args.extend(["--data", action_data])
            args.append(target_url)

        elif protocol.lower() == "ssh":
            # Requires a public key installed on the smart PDU.
            target_url = f"https://localhost{target_path}"
            pdu_public = f"{pdu_user}@{pdu_ip}"
            remote_tls = "-k " if tls_insecure else ""
            header_str = " ".join(
                f"{headers[i]} '{headers[i + 1]}'" for i in range(0, len(headers), 2)
            )
            data_str = f"--data {action_data}" if action_data else ""
            remote_curl = (
                f"curl -s {remote_tls}--max-time {int(cqr_env.PDU_COMMAND_TIMEOUT_SEC)} "
                f"--digest -u {pdu_digest} -X {http_method} {header_str} {data_str} "
                f"{target_url}"
            ).strip()
            args = [
                "ssh",
                "-o",
                "StrictHostKeyChecking=accept-new",
                "-o",
                f"ConnectTimeout={int(cqr_env.PDU_COMMAND_TIMEOUT_SEC)}",
                pdu_public,
                remote_curl,
            ]
        else:
            raise ValueError("Invalid protocol. Must be 'HTTP' or 'SSH'...")

        return self.run_curl(args)


_pdu_instance = PDUManager()

run_curl = _pdu_instance.run_curl
pdu_curl = _pdu_instance.pdu_curl
pdu_url  = _pdu_instance.pdu_url
