#import os
#import sys
#import RPi.GPIO as GPIO
#
#button_pin = 16
#
#if __name__ == "__main__":
#    try:
#        GPIO.setmode(GPIO.BCM)
#        GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#        while True:
#            GPIO.wait_for_edge(button_pin, GPIO.BOTH)
#            if not GPIO.input(button_pin):
#                    print("Button pressed!")
#            else:
#                print("Button released!")
#
#    except Exception as e:
#        print(e)
#        GPIO.cleanup()
#        sys.exit(0)


import signal
import sys
import RPi.GPIO as GPIO
BUTTON_GPIO = 23

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

def button_pressed_callback(channel):
    print("Button pressed")

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BUTTON_GPIO, GPIO.FALLING, callback=button_pressed_callback, bouncetime=200)
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()