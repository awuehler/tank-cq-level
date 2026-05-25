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
  - Approximate cost: $20 US (varies)

- CQRobot Contact Water/Liquid Level Sensor (or equivalent)
  - Microcontroller board plus sensor probe
    - Wiki: [SKU: CQRSENYW002](http://www.cqrobot.wiki/index.php/Contact_Water/Liquid_Level_Sensor_SKU:_CQRSENYW002)
      - Refer to the GPIO pin diagram for Raspberry Pi
    - Use of active WiringPi project is now required (the Wiki "Prepare for Raspberry Pi" section is obsolete)
      - See: https://github.com/WiringPi/WiringPi
  - Approximate cost: $15 US (varies)

- ECO-WORTHY RV Fresh Water Pump 12V DC 3.5GPM 45PSI Self Priming (or equivalent)
  - 12V 5A 60W LED Power Supply, AC 100-240V to DC 12 Volt Transformer, Power Adapter
    - available through amazon, ebay, or related online retailers
  - Approximate cost: $60 US (varies)

- Digital Web Loggers Smart PDU (or equivalent)
  - Must support remote outlet ON/OFF cycling via Telnet, SSH, or HTTP/S
    - See: https://www.digital-loggers.com/restapi.pdf
  - Approximate cost: $300 US (varies)

- Additional items include: tubing, one-way inline check valve, water proofing materials, ...
  - Approximate cost: $50 US (varies)

## Version: 0.0

Republish the sample C code and convert it for use in Python running on the RPi platform.

Initial check using GPT-5 to assist with the conversion of the sample C program to Python; used the following prompt:

`Analyze the following program. This code is written in the C programming language. It runs on the Raspberry Pi zero W using the Debian Bookworm OS. The GitHub WiringPi project for GPIO is installed to support the CQRobot Contact Water/Liquid Level Sensor. Please convert this code to Python:`

 - See: [cqrobot.c](https://github.com/awuehler/tank-cq-level/blob/main/0.0/cqrobot.c)

The resulting output in Python was mostly correct, except for using the wrong GPIO pin (for Raspberry Pi it is pin 18). The corrected working version is available for reference:

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

## Version: 0.5

Under development...

## Base OS Configuration

### Step 0

  Install git package; download and install WiringPi package (v3.18 pre-compiled release currently):

    - e.g. sudo apt install git
    - e.g. wget https://github.com/WiringPi/WiringPi/releases/download/3.18/wiringpi_3.18_armhf.deb
    - e.g. chmod +x ./wiringpi_3.18_armhf.deb
    - e.g. sudo apt install ./wiringpi_3.18_armhf.deb

  Test GPIO communication:

    -e.g. gpio readall

```
  pi@rpi-pump-01:~ $ gpio readall
  +-----+-----+---------+------+---+-Pi ZeroW-+---+------+---------+-----+-----+
  | BCM | wPi |   Name  | Mode | V | Physical | V | Mode | Name    | wPi | BCM |
  +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
  |     |     |    3.3v |      |   |  1 || 2  |   |      | 5v      |     |     |
  |   2 |   8 |   SDA.1 | ALT0 | 1 |  3 || 4  |   |      | 5v      |     |     |
  |   3 |   9 |   SCL.1 | ALT0 | 1 |  5 || 6  |   |      | 0v      |     |     |
  |   4 |   7 | GPIO. 7 |   IN | 0 |  7 || 8  | 1 | ALT5 | TxD     | 15  | 14  |
  |     |     |      0v |      |   |  9 || 10 | 1 | ALT5 | RxD     | 16  | 15  |
  |  17 |   0 | GPIO. 0 |   IN | 0 | 11 || 12 | 0 | IN   | GPIO. 1 | 1   | 18  |
  |  27 |   2 | GPIO. 2 |   IN | 0 | 13 || 14 |   |      | 0v      |     |     |
  |  22 |   3 | GPIO. 3 |   IN | 0 | 15 || 16 | 0 | IN   | GPIO. 4 | 4   | 23  |
  |     |     |    3.3v |      |   | 17 || 18 | 0 | IN   | GPIO. 5 | 5   | 24  |
  |  10 |  12 |    MOSI | ALT0 | 0 | 19 || 20 |   |      | 0v      |     |     |
  |   9 |  13 |    MISO | ALT0 | 0 | 21 || 22 | 0 | IN   | GPIO. 6 | 6   | 25  |
  |  11 |  14 |    SCLK | ALT0 | 0 | 23 || 24 | 1 | OUT  | CE0     | 10  | 8   |
  |     |     |      0v |      |   | 25 || 26 | 1 | OUT  | CE1     | 11  | 7   |
  |   0 |  30 |   SDA.0 |   IN | 1 | 27 || 28 | 1 | IN   | SCL.0   | 31  | 1   |
  |   5 |  21 | GPIO.21 |   IN | 1 | 29 || 30 |   |      | 0v      |     |     |
  |   6 |  22 | GPIO.22 |   IN | 1 | 31 || 32 | 0 | IN   | GPIO.26 | 26  | 12  |
  |  13 |  23 | GPIO.23 |   IN | 0 | 33 || 34 |   |      | 0v      |     |     |
  |  19 |  24 | GPIO.24 |   IN | 0 | 35 || 36 | 0 | IN   | GPIO.27 | 27  | 16  |
  |  26 |  25 | GPIO.25 |   IN | 0 | 37 || 38 | 0 | IN   | GPIO.28 | 28  | 20  |
  |     |     |      0v |      |   | 39 || 40 | 0 | IN   | GPIO.29 | 29  | 21  |
  +-----+-----+---------+------+---+----++----+---+------+---------+-----+-----+
  | BCM | wPi |   Name  | Mode | V | Physical | V | Mode | Name    | wPi | BCM |
  +-----+-----+---------+------+---+-Pi ZeroW-+---+------+---------+-----+-----+
  pi@rpi-pump-01:~ $
```

## Step 1

  Download (clone) a copy of this Git repository:

    - e.g. git clone https://github.com/awuehler/tank-cq-level.git

### Step 2

  Place a copy of the current version of source code under /usr/local/src/cqr-pdu:

    - e.g. sudo cp -rfp /home/pi/github/tank-cq-level/0.4 /usr/local/src/cqr-pdu

### Step 3

  Create a service file located under /etc/systemd/system:
  
    - e.g. sudo vim /etc/systemd/system/pdu-manager.service

```
  [Unit]
  Description=PDU Manager Python Service
  # Ensures the network is up before starting this script (for script curl commands).
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

  # Capture standard output/error to the systemd journal (from print() statements).
  StandardOutput=journal
  StandardError=journal
  SyslogIdentifier=pdu-manager

  [Install]
  # Specifies that the service should be started in standard multi-user boot mode.
  WantedBy=multi-user.target
```

### Step 4

  Enable the new PDU Manager service:

    - e.g. sudo systemctl daemon-reload ; sudo systemctl enable pdu-manager.service ; sudo systemctl start pdu-manager.service

### Step 5

  Confirm the service status for PDU Manager and monitor the journal for sensor reports:

    - e.g. sudo systemctl status pdu-manager.service
    - e.g. sudo journalctl -f -u pdu-manager.service

## Addendum

Additional information inserted as needed.

The option to use the SSH protocol for remote command access (vs. curl) requires the creation of a public key (i.e. ssh-keygen) to be placed on the remote PDU. Please note, that the SSH_ASKPASS environment variable is not an easy nor reliable alternative to enable password-less ssh access to the remote PDU commandline shell.

  - For the Digital Web Logger PDU, login -> admin -> Setup -> General Network Settings -> Allowed SSH public keys
  - Follow-up detail for Digital Web Logger PDU: remote API control is only available through its admin account

...
