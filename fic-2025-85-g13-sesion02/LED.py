import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(5,GPIO.OUT)
i = 0
while i < 10:
    print("Led on")
    GPIO.output(5,GPIO.HIGH)
    time.sleep(1)
    print("Led off")
    GPIO.output(5,GPIO.LOW)
    time.sleep(1)
    i += 1