import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN)

try:
    while True:
        val = GPIO.input(18)
        print(f"Raw GPIO value: {val}")
        time.sleep(1)
except KeyboardInterrupt:
    print("Program stopped")
finally:
    GPIO.cleanup()
