import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
LED = 5
trig = 24
echo = 25
GPIO.setup(LED, GPIO.OUT)
led_pwm = GPIO.PWM(LED, 100)
led_pwm.start(0)
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
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    print("Distance:",distance,"cm")

    if distance < 25:
        if distance < 12:
            intensidad = 100
        else:
            intensidad = int((25 - distance) / (25-12) * 100)
    else:
        intensidad = 0
    led_pwm.ChangeDutyCycle(intensidad)

    time.sleep(0.5)