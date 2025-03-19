#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import os
import sys

button_pin = 23
if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        #while True:
        #    GPIO.wait_for_edge(button_pin, GPIO.FALLING)
        #    print("Button pressed")
        while True:
           GPIO.wait_for_edge(button_pin, GPIO.BOTH)
           if not GPIO.input(button_pin):
               print("You've presed the Button!")
               time.sleep(1)
           #else:
           #    print("You've released the Button!")
    except Exception as e:
        print("Exception:", e)
        GPIO.cleanup()



