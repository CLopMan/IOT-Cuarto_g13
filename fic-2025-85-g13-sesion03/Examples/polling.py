import RPi.GPIO as GPIO
import time
import sys

button_pin = 23
if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        pressed = False
        while True:
            if not GPIO.input(button_pin):
                if not pressed:
                    print("Button pressed")
                    pressed = True
            else:
                pressed = False
            time.sleep(0.1)
    except Exception as e:
        print(e)
        GPIO.cleanup()
        sys.exit(0)

