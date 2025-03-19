import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

def setup_devices():
    global rgb_red
    global rgb_green
    global rgb_blue
    global pwm_rgb_red
    global pwm_rgb_green
    global pwm_rgb_blue

    rgb_red = 5
    GPIO.setup(rgb_red, GPIO.OUT)
    GPIO.output(rgb_red, True)
    pwm_rgb_red = GPIO.PWM(rgb_red, 100)
    pwm_rgb_red.start(0)
    pwm_rgb_red.ChangeDutyCycle(0)

    rgb_green = 6
    GPIO.setup(rgb_green, GPIO.OUT)
    GPIO.output(rgb_green, True)
    pwm_rgb_green = GPIO.PWM(rgb_green, 100)
    pwm_rgb_green.start(0)
    pwm_rgb_green.ChangeDutyCycle(0)

    rgb_blue = 13
    GPIO.setup(rgb_blue, GPIO.OUT)
    GPIO.output(rgb_blue, True)
    pwm_rgb_blue = GPIO.PWM(rgb_blue, 100)
    pwm_rgb_blue.start(0)
    pwm_rgb_blue.ChangeDutyCycle(0)


def pinOn(pwm_object, freq=100):
    pwm_object.ChangeDutyCycle(freq)

def pinOff(pwm_object):
    pwm_object.ChangeDutyCycle(0)

def red(redPin, greenPin, bluePin):
    pinOn(redPin)
    pinOff(greenPin)
    pinOff(bluePin)
def yellow(redPin, greenPin, bluePin):
    pinOn(redPin)
    pinOn(greenPin)
    pinOff(bluePin)

def white(redPin,greenPin, bluePin):
    pinOn(redPin)
    pinOn(greenPin)
    pinOn(bluePin)


def turnOff(redPin, greenPin, bluePin):
    pinOff(redPin)
    pinOff(greenPin)
    pinOff(bluePin)

if __name__ == '__main__':
    global pwm_rgb_red
    global pwm_rgb_green
    global pwm_rgb_blue
    setup_devices()
    yellow(pwm_rgb_red, pwm_rgb_green, pwm_rgb_blue)
    time.sleep(3)
    red(pwm_rgb_red, pwm_rgb_green, pwm_rgb_blue)
    time.sleep(3)
    white(pwm_rgb_red, pwm_rgb_green, pwm_rgb_blue)
    time.sleep(3)
    turnOff(pwm_rgb_red, pwm_rgb_green, pwm_rgb_blue)
