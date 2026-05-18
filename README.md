## Statement Of Work [![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/awuehler/tank-cq-level)
The primary goal for this project is to build a low cost solution to monitor a stand-alone AC chiller with an isolated condensation tank (i.e. no drain access). The tank requires manual dumping every 24 to 48 hours depending on seasonal temperature or humidity.

Automating the water purge from the AC catch basin is based on an optical sensor used to identify water level. When a full tank is detected, that event is used to send a signal to a smart PDU. The PDU outlet used for the water pump is turned ON/OFF triggered by the optical sensor event.

This feedback loop depends on several factors:

  - WiFi access from the RPi Zero W to the smart PDU
  - Smart PDU network access to enable remote API call
  - Custom script (Bash, Python, ...) to monitor GPIO pin signal

The end to end summary is about purging the water from a catch basin (AC condensation tank) as it fills up using a small controller (Raspberry Pi) and sensor (CQRobot optical) to turn ON and turn OFF a pump without the need for daily or weekly human assistance.

## Hardware Inventory Required

- Raspberry Pi Zero W with GPIO header (or equivalent)
  - Pi Zero Case Kit Compatible Pin Header
  - Micro USB Cable Power Supply 5.25 Volts 3 Amps for Raspberry Pi Zero Board
  - Additional attachments (as needed) for USB, and/or HDMI devices
  - Aproximate cost: $20 US (varies)

- CQRobot Contact Water/Liquid Level Sensor (or equivalent)
  - Microcontroller board plus sensor probe
    - Wiki: [SKU: CQRSENYW002](http://www.cqrobot.wiki/index.php/Contact_Water/Liquid_Level_Sensor_SKU:_CQRSENYW002)
  - Aproximate cost: $15 US (varies)

- ECO-WORTHY RV Fresh Water Pump 12V DC 3.5GPM 45PSI Self Priming (or equivalent)
  - 12V 5A 60W LED Power Supply, AC 100-240V to DC 12 Volt Transformer, Power Adapter
    - available through amazon, ebay, or related online retailers
  - Aproximate cost: $60 US (varies)

- Digital Web Loggers Smart PDU (or equivalent)
  - Must support remote outlet ON/OFF cycling via Telnet, SSH, or HTTP/S
    - See: https://www.digital-loggers.com/restapi.pdf
  - Aproximate cost: $300 US (varies)

- Additional items include: tubing, one-way inline check valve, water proofing materials, ...
  - Aproximate cost: $50 US (varies)

## Version: 0.0

Republish the sample C code and convert it for use in Python running on the RPi platform.

Initial check using GPT-5 to assist with the conversion of the sample C program to Python; used the following prompt:

`Analyze the following program. This code is written in the C programming language. It runs on the Raspberry Pi zero W using the Debian Bookworm OS. The GitHub WiringPi project for GPIO is installed to support the CQRobot Contact Water/Liquid Level Sensor. Please convert this code to Python:`

 - See: [cqrobot.c](https://github.com/awuehler/tank-cq-level/blob/main/0.0/cqrobot.c)

The resulting output in Python was mostly correct, except for using the wrong GPIO pin (for Raspberry Pi it is pin 17). The corrected working version is available for reference:

 - See: [cqrobot.py](https://github.com/awuehler/tank-cq-level/blob/main/0.0/cqrobot.py)

## Version: 0.1

Proof of concept to report each state change whenever the optical sensor detected water. Confirmed angle of operation limitation due to drip of water clinging to it whenever the sensor is placed off angle to water surface (results in false positive reading until the droplet is removed). Operational work-around is the need to apply a protective hydrophobic coating to remedy i.e. prevent.

## Version: 0.2

Re-align functional areas into sparate files for environment, timer, pdu, and main.

## Version: 0.3

Define a PDU Manager class for future improvements in support of +1 additional smart PDU vendors. Refine logging for clear reporting of water level e.g.

```
2026-05-17 16:39:59.139908  CQRobot: 0 (H2O level below sensor)  DWL: ['AC Chill #3', False] (outlet power state)
2026-05-17 16:40:18.002513  CQRobot: 1 (H2O level is at sensor)  DWL: ['AC Chill #3', True] (outlet power state)
2026-05-17 16:40:19.720775  Start non-blocking timer for 43 seconds...
         40 seconds left...
         35 seconds left...
         30 seconds left...
2026-05-17 16:40:36.349391  CQRobot: 0 (H2O level below sensor)  DWL: ['AC Chill #3', True] (outlet power state)
         25 seconds left...
         20 seconds left...
         15 seconds left...
         10 seconds left...
2026-05-17 16:40:54.110099  CQRobot: 0 (H2O level below sensor)  DWL: ['AC Chill #3', True] (outlet power state)
         5 seconds left...
2026-05-17 16:41:11.864647  CQRobot: 0 (H2O level below sensor)  DWL: ['AC Chill #3', False] (outlet power state)
2026-05-17 16:41:29.607391  CQRobot: 0 (H2O level below sensor)  DWL: ['AC Chill #3', False] (outlet power state)
```

## Version: 0.4

Clean up, add comments, and make ready for initial deployment of end-2-end solution with pump hardware attached to AC chiller.

## Base OS Configuration

### Step 1

  Place a copy of the source code located under /usr/local/src/cqr-pdu

    - e.g. sudo cp -rfp /home/pi/github/tank-cq-level/0.4 /usr/local/src/cqr-pdu

### Step 2

  Create a service file located under /etc/systemd/system/pdu-manager.service
  
    - e.g. sudo vim /etc/systemd/system/pdu-manager.service

```
  [Unit]
  Description=PDU Manager Python Service
  # Ensures the network is up before starting this script (required by embedded curl commands).
  After=network.target

  [Service]
  # The user and group that the service will run as (e.g., your RPi username).
  # Output from script must be sent to journal immediately.
  Environment="PYTHONUNBUFFERED=1"
  User=pi
  Group=pi

  # The directory where your script is located.
  WorkingDirectory=/usr/local/src/cqr-pdu/

  # The exact command to start the script (must use absolute paths).
  ExecStart=/usr/bin/python3 /usr/local/src/cqr-pdu/cqr_get.py

  # Automatically restart the service if it crashes.
  Restart=always
  # Wait 11 seconds before restarting
  RestartSec=11

  # Capture standard output/error to the systemd journal (captures your print() statements).
  StandardOutput=journal
  StandardError=journal
  SyslogIdentifier=pdu-manager

  [Install]
  # Specifies that the service should be started in standard multi-user boot mode.
  WantedBy=multi-user.target
```

### Step 3

  Enable the new PDU Manager service

    - e.g. sudo systemctl daemon-reload ; sudo systemctl enable pdu-manager.service ; sudo systemctl start pdu-manager.service

### Step 4

  Confirm the service status for PDU Manager and monitor the journal for sensor reports

    - e.g. sudo systemctl status pdu-manager.service
    - e.g. sudo journalctl -f

## Addendum

Additional information inserted as needed.
...
