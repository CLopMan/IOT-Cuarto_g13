import signal
import sys
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

detect = False


LED = 5
GPIO.setup(LED, GPIO.OUT)
led_pwm = GPIO.PWM(LED, 100)
led_pwm.start(0)

BUTTON_GPIO = 23
trig = 24
echo = 25


GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN)

def button_callback(channel):
    global detect
    detect = not detect
    if detect:
        print("Start measuring")
        time.sleep(2)


def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

if __name__ == '__main__':
    GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BUTTON_GPIO, GPIO.FALLING, callback=button_callback, bouncetime=200)
    signal.signal(signal.SIGINT, signal_handler)
    while True:

        if detect:
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
