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
        curl -s -k -H "Accept: application/json" --digest "https://<USER>:<PASS>@<IP>/restapi/relay/outlets/=7/state/"
    Example: reference
        curl -s -k -H "Accept: application/json" --digest "https://<USER>:<PASS>@<IP>/restapi/relay/outlets/=<0-7>/state/"
    Example: key values
        curl -k --digest -u admin:admin -H "Accept: application/json" --digest 'http://192.168.156.109/restapi/relay/outlets/0/=name,physical_state/'
    Example: authentication
        curl -s -k --digest --user admin:admin -X PUT -H "X-CSRF: x" --data "value=true" 'http://192.168.156.109/restapi/relay/outlets/7/state/'

    # PDU session token.
    #PDU_TARGET = f"https://{cqr_env.PDUS_SMARTLY[1]}/api/login"
    #PDU_DIGEST = f"username={cqr_env.PDUS_SMARTLY[2]}&password={cqr_env.PDUS_SMARTLY[3]}"
    #PDU_TOKENS = cqr_pdu.run_curl(["curl", "-s", "-k", "-X POST", "-H 'Accept: application/json'", "-H 'Content-Type: application/x-www-form-urlencoded'", "-d" f"{PDU_DIGEST}", f"{PDU_TARGET}"])
    #print( f"PDU Session State: {PDU_TOKENS}" 

Dependencies
    1. URL construction is vendor specific.
    2. Initial PDU hardware is "Pro Switch" sold by Digital Loggers, Inc.
    3. Key feature is remote outlet ON/OFF cycling via Telnet, SSH, or HTTP/S
    4. ...

Improvements
    - Support +2 Smart PDU vendors
    - Clean-up support for both HTTP (i.e. curl) and SSH protocol access
    - ...
'''

'''
# ----------------------------------------------------------------------
# Module(s).
# ----------------------------------------------------------------------
import json, subprocess

# ----------------------------------------------------------------------
# Import environment, data, and/or custom methods.
# ----------------------------------------------------------------------
import cqr_env

# Define a PDU class.
class PDUManager:

    # Basic CLI subprocess support.
    def run_curl(self, command: list):
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

    # Vendor specific PDU API calls.
    def pdu_curl(self, vendor: str, outlet: str, action: str):
        '''
        Executes a curl command for PDU based on vendor, outlet, and action.
        
        Args:
            vendor (str): The vendor name.
            outlet (str): The specific outlet identifier.
            action (str): 'set' (triggers PUT) or 'get' (triggers POST).
        '''

        # TODO: Use vendor parameter to support additonal smart PDU APIs.
        # TODO: Update cqr_env to support 2nd or additional PDU models.

        # Determine the HTTP method based on the input action.
        if action.lower() == "false":
            HTTP_METHOD = "PUT"
            PDU_TARGET  = f"https://{cqr_env.PDUS_SMARTLY[1]}/restapi/relay/outlets/{cqr_env.PDUS_SMARTLY[4]}/state/"
            PDU_DIGEST  = f"{cqr_env.PDUS_SMARTLY[2]}:{cqr_env.PDUS_SMARTLY[3]}"
            args = [
                'curl', '--silent', '-k',
                '--digest', '--user', f"{PDU_DIGEST}", 
                '-X', HTTP_METHOD, 
                '-H', 'X-CSRF: x', 
                '--data', 'value=false', f"{PDU_TARGET}"
            ]
        elif action.lower() == "true":
            HTTP_METHOD = "PUT"
            PDU_TARGET  = f"https://{cqr_env.PDUS_SMARTLY[1]}/restapi/relay/outlets/{cqr_env.PDUS_SMARTLY[4]}/state/"
            PDU_DIGEST  = f"{cqr_env.PDUS_SMARTLY[2]}:{cqr_env.PDUS_SMARTLY[3]}"
            args = [
                'curl', '--silent', '-k',
                '--digest', '--user', f"{PDU_DIGEST}", 
                '-X', HTTP_METHOD, 
                '-H', 'X-CSRF: x', 
                '--data', 'value=true', f"{PDU_TARGET}"
            ]
        elif action.lower() == "get":
            HTTP_METHOD = "POST"
            PDU_TARGET  = f"https://{cqr_env.PDUS_SMARTLY[1]}/restapi/relay/outlets/{cqr_env.PDUS_SMARTLY[4]}/=name,physical_state/"
            PDU_DIGEST  = f"{cqr_env.PDUS_SMARTLY[2]}:{cqr_env.PDUS_SMARTLY[3]}"
            args = [
                'curl', '--silent', '-k',
                '--digest', '--user', f"{PDU_DIGEST}", 
                "-H 'Accept: application/json'", 
                '--digest', f"{PDU_TARGET}"
            ]
        else:
            raise ValueError("Invalid action. Must be 'true' or 'false' or 'get'...")

        # Execute subprocess.run to invoke system call for curl.
        try:
            result = subprocess.run(
                args,
                capture_output=True, # Captures stdout and stderr
                text=True,           # Returns output as strings instead of bytes
                check=True           # Raises CalledProcessError if the command fails
            )
            
            # Return the standard output.
            return result.stdout.strip()
            
        except subprocess.CalledProcessError as e:
            print(f"Curl command failed with exit code {e.returncode}")
            print(f"Error output: {e.stderr}")
            return None

    # Vendor specific PDU API calls.
    def pdu_url(self, protocol: str, outlet: str, action: str):
        '''
        Executes a curl command for PDU based on vendor, outlet, and action.
        
        Args:
            protocol (str): HTTP/S or SSH.
            outlet (str): The specific outlet identifier.
            action (str): 'set' (triggers PUT) or 'get' (triggers POST).
        '''

        if protocol.lower() == "http":
            # Determine the HTTP method based on the input action.
            if action.lower() == "false":
                HTTP_METHOD = "PUT"
                PDU_TARGET  = f"https://{cqr_env.PDUS_SMARTLY[1]}/restapi/relay/outlets/{cqr_env.PDUS_SMARTLY[4]}/state/"
                PDU_DIGEST  = f"{cqr_env.PDUS_SMARTLY[2]}:{cqr_env.PDUS_SMARTLY[3]}"
                args = [
                    'curl', '--silent', '-k', 
                    '--digest', '--user', f"{PDU_DIGEST}", 
                    '-X', HTTP_METHOD, 
                    '-H', 'X-CSRF: x', 
                    '--data', 'value=false', f"{PDU_TARGET}"
                ]
            elif action.lower() == "true":
                HTTP_METHOD = "PUT"
                PDU_TARGET  = f"https://{cqr_env.PDUS_SMARTLY[1]}/restapi/relay/outlets/{cqr_env.PDUS_SMARTLY[4]}/state/"
                PDU_DIGEST  = f"{cqr_env.PDUS_SMARTLY[2]}:{cqr_env.PDUS_SMARTLY[3]}"
                args = [
                    'curl', '--silent', '-k', 
                    '--digest', '--user', f"{PDU_DIGEST}", 
                    '-X', HTTP_METHOD, 
                    '-H', 'X-CSRF: x', 
                    '--data', 'value=true', f"{PDU_TARGET}"
                ]
            elif action.lower() == "get":
                HTTP_METHOD = "POST"
                PDU_TARGET  = f"https://{cqr_env.PDUS_SMARTLY[1]}/restapi/relay/outlets/{cqr_env.PDUS_SMARTLY[4]}/=name,physical_state/"
                PDU_DIGEST  = f"{cqr_env.PDUS_SMARTLY[2]}:{cqr_env.PDUS_SMARTLY[3]}"
                args = [
                    'curl', '--silent', '-k', 
                    '--digest', '--user', f"{PDU_DIGEST}", 
                    "-H 'Accept: application/json'", 
                    '--digest', f"{PDU_TARGET}"
                ]
            else:
                raise ValueError("Invalid action. Must be 'true' or 'false' or 'get'...")
        elif protocol.lower() == "ssh":
            # Determine the remote SSH command (HTTP method) based on the input action.
            # NOTE: Requires Public Key installed on smart PDU.
            if action.lower() == "false":
                HTTP_METHOD = "PUT"
                PDU_PUBLIC  = f"{cqr_env.PDUS_SMARTLY[2]}@{cqr_env.PDUS_SMARTLY[1]}"
                PDU_TARGET  = f"https://localhost/restapi/relay/outlets/{cqr_env.PDUS_SMARTLY[4]}/state/"
                PDU_DIGEST  = f"{cqr_env.PDUS_SMARTLY[2]}:{cqr_env.PDUS_SMARTLY[3]}"
                PDU_REMOTE  = f"curl -s -k --digest -u {PDU_DIGEST} -X {HTTP_METHOD} -H 'X-CSRF: x' --data value=false {PDU_TARGET}"
                args = [
                    'ssh', '-o', 'StrictHostKeyChecking=accept-new',
                    f"{PDU_PUBLIC}", f"{PDU_REMOTE}"
                ]
            elif action.lower() == "true":
                HTTP_METHOD = "PUT"
                PDU_PUBLIC  = f"{cqr_env.PDUS_SMARTLY[2]}@{cqr_env.PDUS_SMARTLY[1]}"
                PDU_TARGET  = f"https://localhost/restapi/relay/outlets/{cqr_env.PDUS_SMARTLY[4]}/state/"
                PDU_DIGEST  = f"{cqr_env.PDUS_SMARTLY[2]}:{cqr_env.PDUS_SMARTLY[3]}"
                PDU_REMOTE  = f"curl -s -k --digest -u {PDU_DIGEST} -X {HTTP_METHOD} -H 'X-CSRF: x' --data value=true {PDU_TARGET}"
                args = [
                    'ssh', '-o', 'StrictHostKeyChecking=accept-new',
                    f"{PDU_PUBLIC}", f"{PDU_REMOTE}"
                ]
            elif action.lower() == "get":
                HTTP_METHOD = "POST"
                PDU_PUBLIC  = f"{cqr_env.PDUS_SMARTLY[2]}@{cqr_env.PDUS_SMARTLY[1]}"
                PDU_TARGET  = f"https://localhost/restapi/relay/outlets/{cqr_env.PDUS_SMARTLY[4]}/=name,physical_state/"
                PDU_DIGEST  = f"{cqr_env.PDUS_SMARTLY[2]}:{cqr_env.PDUS_SMARTLY[3]}"
                PDU_REMOTE  = f"curl -s -k --digest -u {PDU_DIGEST} -H Accept: application/json --digest {PDU_TARGET}"
                args = [
                    'ssh', '-o', 'StrictHostKeyChecking=accept-new',
                    f"{PDU_PUBLIC}", f"{PDU_REMOTE}"
                ]
            else:
                raise ValueError("Invalid action. Must be 'true' or 'false' or 'get'...")
        else:
            raise ValueError("Invalid protocol. Must be 'HTTP' or 'SSH'...")

        # Execute subprocess.run to invoke system call for SSH.
        try:
            result = subprocess.run(
                args,
                capture_output=True, # Captures stdout and stderr
                text=True,           # Returns output as strings instead of bytes
                check=True           # Raises CalledProcessError if the command fails
            )
            
            # Return the standard output.
            return result.stdout.strip()
            
        except subprocess.CalledProcessError as e:
            print(f"SSH command failed with exit code {e.returncode}")
            print(f"Error output: {e.stderr}")
            return None

# Create a hidden instance of the PDU class.
_pdu_instance = PDUManager()

# Bind each instance method to a module-level variable.
run_curl = _pdu_instance.run_curl
pdu_curl = _pdu_instance.pdu_curl
pdu_url  = _pdu_instance.pdu_url
'''

# ----------------------------------------------------------------------
# Module(s).
# ----------------------------------------------------------------------
import json
import subprocess
import logging

# Configure module-level logger.
logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# Import environment, data, and/or custom methods.
# ----------------------------------------------------------------------
import cqr_env

# Define a PDU class.
class PDUManager:

    # Basic CLI subprocess support.
    def run_curl(self, command: list):
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
            logger.error(f"Command failed with exit code {e.returncode}. Stderr: {e.stderr}")
            return {"error": "Command failed", "stderr": e.stderr}

    # Vendor specific PDU API calls.
    def pdu_curl(self, vendor: str, outlet: str, action: str):
        '''
        Legacy wrapper: Executes an HTTP curl command for PDU based on vendor, outlet, and action.
        '''
        # TODO: Use vendor parameter to support additional smart PDU APIs.
        # TODO: Update cqr_env to support 2nd or additional PDU models.
        
        # Passes execution to the unified URL method
        return self.pdu_url(protocol="http", outlet=outlet, action=action)

    # Vendor specific PDU API calls.
    def pdu_url(self, protocol: str, outlet: str, action: str):
        '''
        Executes a curl command for PDU based on protocol, outlet, and action.
        
        Args:
            protocol (str): HTTP or SSH.
            outlet (str): The specific outlet identifier.
            action (str): 'true', 'false', or 'get'.
        '''
        action = action.lower()
        if action not in ["true", "false", "get"]:
            raise ValueError("Invalid action. Must be 'true', 'false', or 'get'...")

        # Extract common environment variables once
        pdu_ip     = cqr_env.PDUS_SMARTLY[1]
        pdu_user   = cqr_env.PDUS_SMARTLY[2]
        pdu_pass   = cqr_env.PDUS_SMARTLY[3]
        pdu_outlet = cqr_env.PDUS_SMARTLY[4]
        pdu_digest = f"{pdu_user}:{pdu_pass}"

        # 1. Define HTTP Method, Path, and Data Payloads.
        if action in ["true", "false"]:
            http_method = "PUT"
            target_path = f"/restapi/relay/outlets/{pdu_outlet}/state/"
            action_data = f"value={action}"
            headers = ['-H', 'X-CSRF: x']
        else:  # action == "get"
            http_method = "POST"
            target_path = f"/restapi/relay/outlets/{pdu_outlet}/=name,physical_state/"
            action_data = ""
            headers = ['-H', 'Accept: application/json']

        # 2. Build the Subprocess Arguments.
        if protocol.lower() == "http":
            target_url = f"https://{pdu_ip}{target_path}"
            args = [
                'curl', '--silent', '-k',
                '--digest', '--user', pdu_digest,
                '-X', http_method
            ] + headers
            
            if action_data:
                args.extend(['--data', action_data])
            
            args.append(target_url)

        elif protocol.lower() == "ssh":
            # NOTE: Requires Public Key installed on smart PDU.
            target_url = f"https://localhost{target_path}"
            pdu_public = f"{pdu_user}@{pdu_ip}"
            
            # SSH requires formatting the remote curl command as a single string.
            header_str = " ".join([f"{headers[i]} '{headers[i+1]}'" for i in range(0, len(headers), 2)])
            data_str   = f"--data {action_data}" if action_data else ""
            
            remote_curl = f"curl -s -k --digest -u {pdu_digest} -X {http_method} {header_str} {data_str} {target_url}".strip()
            
            args = [
                'ssh', '-o', 'StrictHostKeyChecking=accept-new',
                pdu_public, remote_curl
            ]
        else:
            raise ValueError("Invalid protocol. Must be 'HTTP' or 'SSH'...")

        # 3. Execute via central method.
        return self.run_curl(args)

# Create a hidden instance of the PDU class.
_pdu_instance = PDUManager()

# Bind each instance method to a module-level variable.
run_curl = _pdu_instance.run_curl
pdu_curl = _pdu_instance.pdu_curl
pdu_url  = _pdu_instance.pdu_url
 