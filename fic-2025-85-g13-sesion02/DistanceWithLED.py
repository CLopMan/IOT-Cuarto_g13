import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
trig = 24
echo = 25
print ("distance measurement in progress")

GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)

GPIO.output(trig, False)
print("waiting for sensor to settle")
time.sleep(2)
while True:
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)
    while GPIO.input(echo)==0:
        #print("escuchando")
        pulse_start = time.time()
    while GPIO.input(echo)==1:
        #print("recibido")
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150 # velocidad del sonido /2
    distance = round(distance, 2)
    print("Distance:",distance,"cm")
    time.sleep(1)