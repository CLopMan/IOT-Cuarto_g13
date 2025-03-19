import signal
import sys
import RPi.GPIO as GPIO
import time
import threading
import mpu6050
from Drifting import get_accel_offset
from ReadNFCData import *

GPIO.setmode(GPIO.BCM)

should_run = False
execute_command = True
tacograph_thread = None
speed_thread = None
nfc_thread = None
led_thread = None

RED_LED_PIN = 5
GREEN_LED_PIN = 6
BLUE_LED_PIN = 13

driver_registered = None

MAX_VELOCITY = 1.5
override_velocity = False

OBSTACLE_DISTANCE_DETECTED = 10
obstacle_detected = False


BUTTON_GPIO = 23
trig = 24
echo = 25

offsets = [0, 0, 0]

def button_callback(channel):
    global should_run
    global execute_command
    should_run = not should_run
    execute_command = False
    if should_run:
        print("[SYSTEM]: START")
        time.sleep(2)
    else:
        print("[SYSTEM]: STOP")


def signal_handler(sig, frame):
    global execute_command
    execute_command = False
    shutdown()
    GPIO.cleanup()
    sys.exit(0)

def tacograph_handler():

    global obstacle_detected
    obstacle_distance = 0

    while execute_command:
        GPIO.output(trig, True)
        time.sleep(0.5)
        GPIO.output(trig, False)
        while GPIO.input(echo) == 0:
            # print("escuchando")
            pulse_start = time.time()
        while GPIO.input(echo) == 1:
            # print("recibido")
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        obstacle_distance = distance
        print("Distance:", obstacle_distance, "cm")

        if obstacle_distance < OBSTACLE_DISTANCE_DETECTED:

            obstacle_detected = True

        elif obstacle_distance > OBSTACLE_DISTANCE_DETECTED:
            
            obstacle_detected = False
    return 0

def speed_stimator():

    global override_velocity

    while execute_command:
        accelerometer_data = acelerometro.get_accel_data()
        time.sleep(0.1)
        a_x = accelerometer_data['x'] - offsets[0]
        a_y = accelerometer_data['y'] - offsets[1]
        a_z = accelerometer_data['z'] - offsets[2]
        velocidad_x = 0.1 * a_x
        velocidad_y = 0.1 * a_y
        velocidad_z = 0.1 * a_z

        velocity = {"x": velocidad_x, "y":velocidad_y, "z":velocidad_z}

        print("velocidad: [{% 0.2f}, {% 0.2f}, {% 0.2f}]" % (velocidad_x, velocidad_y, velocidad_z))

        if any(abs(v) > MAX_VELOCITY for v in velocity.values()) and override_velocity == False:

            override_velocity = True
            print("rojo")
        elif any(abs(v) < MAX_VELOCITY for v in velocity.values()) and override_velocity == True:
            override_velocity = False

        time.sleep(0.5)
    return 0



def shutdown():
    while tacograph_thread.is_alive() or speed_thread.is_alive() or nfc_thread.is_alive():
        print("[SYSTEM]: JOIN")
        tacograph_thread.join()
        speed_thread.join()
        nfc_thread.join()
        turnOff(pwm_rgb_red, pwm_rgb_green, pwm_rgb_blue)

    #print(f"[SYSTEM]: STATE tacograph {tacograph_thread.is_alive()} speed {speed_thread.is_alive()}")


def run_tacograph():
    global tacograph_thread
    tacograph_thread = threading.Thread(target=tacograph_handler)
    tacograph_thread.start()
    global speed_thread
    speed_thread = threading.Thread(target=speed_stimator)
    speed_thread.start()
    global nfc_thread
    nfc_thread = threading.Thread(target=card_info)
    nfc_thread.start()
    global led_thread
    led_thread = threading.Thread(target=led_control)
    led_thread.start()

def card_info():
    while execute_command:
        card_type = decryptmsg(key, readLongData(pn532, uid, 8, 120))
        card_id   = decryptmsg(key, readLongData(pn532, uid, 20, 100))
        print(f"El tipo de tarjeta es: {card_type}\nEl ID de tarjeta es {card_id}")

        time.sleep(10)

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

def green(redPin, greenPin, bluePin):
    pinOff(redPin)
    pinOn(greenPin)
    pinOff(bluePin)

def blue(redPin, greenPin, bluePin):
    pinOff(redPin)
    pinOff(greenPin)
    pinOn(bluePin)

def turnOff(redPin, greenPin, bluePin):
    pinOff(redPin)
    pinOff(greenPin)
    pinOff(bluePin)

def led_control():

    global pwm_rgb_red
    global pwm_rgb_green
    global pwm_rgb_blue


    while execute_command:
        print(driver_registered)
        time.sleep(0.1)
        if override_velocity == True:
            print("Rojo")
            red(pwm_rgb_red, pwm_rgb_green, pwm_rgb_blue)

        elif obstacle_detected == True:
            yellow(pwm_rgb_red, pwm_rgb_green, pwm_rgb_blue)

        elif driver_registered == False:
            blue(pwm_rgb_red, pwm_rgb_green, pwm_rgb_blue)

        elif driver_registered == True:
            green(pwm_rgb_red, pwm_rgb_green, pwm_rgb_blue)

        else:
            turnOff(pwm_rgb_red, pwm_rgb_green, pwm_rgb_blue)
        
        time.sleep(0.5)

if __name__ == '__main__':
    global pn532
    global uid

    GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BUTTON_GPIO, GPIO.FALLING, callback=button_callback, bouncetime=200)

    GPIO.setup(trig, GPIO.OUT)
    GPIO.setup(echo, GPIO.IN)
    
    GPIO.setmode(GPIO.BCM)

    global pwm_rgb_red
    global pwm_rgb_green
    global pwm_rgb_blue

    GPIO.setup(RED_LED_PIN, GPIO.OUT)
    GPIO.output(RED_LED_PIN, True)
    pwm_rgb_red = GPIO.PWM(RED_LED_PIN, 100)
    pwm_rgb_red.start(0)
    pwm_rgb_red.ChangeDutyCycle(0)

    GPIO.setup(GREEN_LED_PIN, GPIO.OUT)
    GPIO.output(GREEN_LED_PIN, True)
    pwm_rgb_green = GPIO.PWM(GREEN_LED_PIN, 100)
    pwm_rgb_green.start(0)
    pwm_rgb_green.ChangeDutyCycle(0)

    GPIO.setup(BLUE_LED_PIN, GPIO.OUT)
    GPIO.output(BLUE_LED_PIN, True)
    pwm_rgb_blue = GPIO.PWM(BLUE_LED_PIN, 100)
    pwm_rgb_blue.start(0)
    pwm_rgb_blue.ChangeDutyCycle(0)


    signal.signal(signal.SIGINT, signal_handler)
    acelerometro = mpu6050.mpu6050(0x68)
    print("[SYSTEM]: Calibrating sensor...")
    offsets = get_accel_offset(acelerometro)
    print(f"[SYSTEM]: sensor calibrated with offsets = {offsets}...")

    print("[SYSTEM]: Starting PN532")
    try:
        pn532 = PN532_SPI(debug=False, reset=20, cs=4)
    except Exception as e:
        print("Error!,", e)
        GPIO.cleanup()
        exit()
    
    print(pn532)

    ic, ver, rev, support = pn532.get_firmware_version()
    print('[SYSTEM]: Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
    pn532.SAM_configuration()
    print("[SYSTEM]: waiting for RFID/NFC pn532...")
    while True:
        uid = pn532.read_passive_target(timeout=0.5)
        if uid is None:
            continue
        break

    # test
    print("[SYSTEM]: Found pn532 with UID", [hex(i) for i in uid])

    with open(KEY_FILE, 'rb') as fd:
        key = fd.read()

    while True:
        if should_run and (not execute_command):
            execute_command = True
            run_tacograph()
        else:
            if (not should_run) and (not execute_command):
                execute_command = False
                shutdown()

