import RPi.GPIO as GPIO
import signal
import time
import sys

GPIO.setmode(GPIO.BCM)

LED = 5

GPIO.setup(LED, GPIO.OUT)

BUTTON_GPIO = 23

def button_callback(channel):
    if GPIO.input(BUTTON_GPIO):
        GPIO.output(LED, GPIO.LOW)
    else:
        GPIO.output(LED, GPIO.HIGH)

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BUTTON_GPIO, GPIO.BOTH, callback=button_callback, bouncetime=50)
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()
