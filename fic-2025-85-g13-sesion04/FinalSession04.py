import signal
import sys
import RPi.GPIO as GPIO
import time
import threading
import mpu6050
from Drifting import get_accel_offset

GPIO.setmode(GPIO.BCM)

should_run = False
execute_command = True
tacograph_thread = None
speed_thread = None

LED = 5

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
    while execute_command:
        GPIO.output(trig, True)
        time.sleep(0.00001)
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
        print("Distance:", distance, "cm")

        if distance < 25:
            if distance < 12:
                intensidad = 100
            else:
                intensidad = int((25 - distance) / (25 - 12) * 100)
        else:
            intensidad = 0
        led_pwm.ChangeDutyCycle(intensidad)
        time.sleep(0.01)
    return 0

def speed_stimator():
    while execute_command:
        accelerometer_data = acelerometro.get_accel_data()
        time.sleep(0.1)
        a_x = accelerometer_data['x'] - offsets[0]
        a_y = accelerometer_data['y'] - offsets[1]
        a_z = accelerometer_data['z'] - offsets[2]
        velocidad_x = 0.1 * a_x
        velocidad_y = 0.1 * a_y
        velocidad_z = 0.1 * a_z

        print("velocidad: [{% 0.2f}, {% 0.2f}, {% 0.2f}]" % (velocidad_x, velocidad_y, velocidad_z))
        time.sleep(0.01)
    return 0



def shutdown():
    while tacograph_thread.is_alive() or speed_thread.is_alive():
        print("[SYSTEM]: JOIN")
        tacograph_thread.join()
        speed_thread.join()
    #print(f"[SYSTEM]: STATE tacograph {tacograph_thread.is_alive()} speed {speed_thread.is_alive()}")


def run_tacograph():
    global tacograph_thread
    tacograph_thread = threading.Thread(target=tacograph_handler)
    tacograph_thread.start()
    global speed_thread
    speed_thread = threading.Thread(target=speed_stimator)
    speed_thread.start()

if __name__ == '__main__':
    GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BUTTON_GPIO, GPIO.FALLING, callback=button_callback, bouncetime=200)
    GPIO.setup(LED, GPIO.OUT)
    led_pwm = GPIO.PWM(LED, 100)
    led_pwm.start(0)
    GPIO.setup(trig, GPIO.OUT)
    GPIO.setup(echo, GPIO.IN)
    signal.signal(signal.SIGINT, signal_handler)
    acelerometro = mpu6050.mpu6050(0x68)
    print("[SYSTEM]: Calibrating sensor...")
    offsets = get_accel_offset(acelerometro)
    print(f"[SYSTEM]: sensor calibrated with offsets = {offsets}...")

    while True:
        if should_run and (not execute_command):
            execute_command = True
            run_tacograph()
        else:
            if (not should_run) and (not execute_command):
                execute_command = False
                shutdown()

