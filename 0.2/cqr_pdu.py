'''
Descriptions
    Run a curl command and return its output.

    Auto-detects JSON responses and returns them as dicts.
    
    Parameters:
        command (list): The curl command and its arguments as a list.
                        Example: ["curl", "https://httpbin.org/get"]
    
    Returns:
        str | dict: Parsed JSON (dict) if response is valid JSON,
                    otherwise raw string.

Notes
    Example usage:
        response = run_curl(["curl", "https://httpbin.org/get"])
        print(response)

    Reference: https://www.digital-loggers.com/restapi.pdf

    Example: last outlet ON
    curl -s -k -X PUT -H "X-CSRF: x" -H "Accept: application/json" --data "value=true" --digest "https://<USER>:<PASS>@<IP>/restapi/relay/outlets/=7/state/"

    Example: last outlet OFF
    curl -s -k -X PUT -H "X-CSRF: x" -H "Accept: application/json" --data "value=false" --digest "https://<USER>:<PASS>@<IP>/restapi/relay/outlets/=7/state/"

    Example: last outlet STATE
    #curl -s -k -H "Accept: application/json" --digest "https://<USER>:<PASS>@<IP>/restapi/relay/outlets/=7/state/"

Dependencies
    1. URL construction is vendor specific.
    2. Initial PDU hardware is "Pro Switch" sold by Digital Loggers, Inc.
    3. Key feature is remote outlet ON/OFF cycling via Telnet, SSH, or HTTP/S
    4. ...

Improvements
    - Support +2 Smart PDU vendors
    - ...
'''

# ----------------------------------------------------------------------
# Module(s).
# ----------------------------------------------------------------------
import subprocess
import json

def run_curl(command: list):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout.strip()

        # Try auto-detect JSON.
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return output

    # Report command line problems.
    except subprocess.CalledProcessError as e:
        return {"error": "Curl command failed", "stderr": e.stderr}
