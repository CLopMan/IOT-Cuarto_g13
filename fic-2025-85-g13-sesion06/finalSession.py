import RPi.GPIO as GPIO
import time
import threading
import mpu6050
import sys
import signal

should_run = False
execute_command = True

# Pin Definitions
RED_LED_PIN = 5
GREEN_LED_PIN = 6
BLUE_LED_PIN = 12
BUTTON_PIN = 23
TRIG = 24
ECHO = 25

keep_on = False

driver_registered = None

MAX_VELOCITY = 10
override_velocity = False

OBSTACLE_DISTANCE_DETECTED = 5
obstacle_detected = False

acelerometro = mpu6050.mpu6050(0x68)

def signal_handler(sig, frame):
    global execute_command
    execute_command = False
    shutdown_tachograph()
    GPIO.cleanup()
    sys.exit(0)


def setup_devices():
    GPIO.setmode(GPIO.BCM)
    
    global RED_LED_PIN
    global GREEN_LED_PIN
    global BLUE_LED_PIN

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

    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(TRIG,GPIO.OUT)
    GPIO.setup(ECHO,GPIO.IN)


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

def get_accel_offset(acelerometro: mpu6050, samples=100):

    # Valores esperados en reposo
    ax_expected, ay_expected, az_expected = 0, 0, 9.8

    # Almacenar datos para descartar valores extremos
    ax_list, ay_list, az_list = [], [], []

    for _ in range(samples):
        try:
            data = acelerometro.get_accel_data()
            ax_list.append(data['x'])
            ay_list.append(data['y'])
            az_list.append(data['z'])
        except Exception as e:
            print(f"Error al leer acelerómetro: {e}")
            return None

        time.sleep(0.01)

    # Ordenar y eliminar valores extremos (media recortada del 10%)
    # Filtro paso alto y bajo
    def trimmed_mean(data, trim=0.1):
        n = int(len(data) * trim)
        return sum(sorted(data)[n:-n]) / (len(data) - 2 * n)

    ax_offset = ax_expected - trimmed_mean(ax_list)
    ay_offset = ay_expected - trimmed_mean(ay_list)
    az_offset = az_expected - trimmed_mean(az_list)

    offsets = {'ax_offset': ax_offset, 'ay_offset': ay_offset, 'az_offset': az_offset}

    return ax_offset, ay_offset, az_offset

def detect_obstacle():
    global obstacle_detected
    obstacle_distance = 0

    while execute_command:
        print(execute_command)

        
        # TODO: Falta medir la distancia del obstaculo, se usará obstacle_distance
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
        while GPIO.input(ECHO) == 0:
            print("escuchando")
            pulse_start = time.time()
        while GPIO.input(ECHO) == 1:
            print("recibido")
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        obstacle_distance = round(distance, 2)
        print("Distance:", obstacle_distance, "cm")                

        if obstacle_distance < OBSTACLE_DISTANCE_DETECTED and obstacle_detected == True:

            obstacle_detected = True

        elif obstacle_distance > OBSTACLE_DISTANCE_DETECTED and obstacle_detected == False:
            obstacle_detected = False
        time.sleep(0.1)

def override_velocity():
    velocity = 0
    global override_velocity
    global velocity_lock
    
    print(execute_command)
    offsets = get_accel_offset(acelerometro)
    while execute_command:
        #TODO: Falta medir la velocidad


        accelerometer_data = acelerometro.get_accel_data()
        time.sleep(0.1)
        a_x = accelerometer_data['x'] - offsets[0]
        a_y = accelerometer_data['y'] - offsets[1]
        a_z = accelerometer_data['z'] - offsets[2]
        velocidad_x = 0.1 * a_x
        velocidad_y = 0.1 * a_y
        velocidadW_z = 0.1 * a_z

        print("velocidad: [{% 0.2f}, {% 0.2f}, {% 0.2f}]" % (velocidad_x, velocidad_y, velocidad_z))

        if any(v > MAX_VELOCITY for v in velocity.values()) and override_velocity == False:

            override_velocity = True

        if any(v > MAX_VELOCITY for v in velocity.values()) and override_velocity == True:
            override_velocity = False
        time.sleep(0.1)

def register_driver():
    global driver_registered

    while execute_command:
        # TODO: Falta leer el nfc para saber si el conductor está registrado
        pass



def led_control():

    global pwm_rgb_red
    global pwm_rgb_green
    global pwm_rgb_blue


    while execute_command:

        if override_velocity == True:
            red(pwm_rgb_red, pwm_rgb_green, pwm_rgb_blue)

        elif obstacle_detected == True:
            yellow(pwm_rgb_red, pwm_rgb_green, pwm_rgb_blue)

        elif driver_registered == False:
            blue(pwm_rgb_red, pwm_rgb_green, pwm_rgb_blue)

        elif driver_registered == True:
            green(pwm_rgb_red, pwm_rgb_green, pwm_rgb_blue)
        
        time.sleep(0.1)

threads = [
    threading.Thread(target=detect_obstacle),
    threading.Thread(target=override_velocity),
    threading.Thread(target=register_driver),
    threading.Thread(target=led_control)
]

def run_tachograph():

    for thread in threads:
        thread.start()

def shutdown_tachograph():
    
    for thread in threads:
        thread.join()
    print("[SYSTEM]: JOIN")

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

if __name__ == "__main__":
    setup_devices()

    GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=300)
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        if should_run and (not execute_command):
            execute_command = True
            print("Encender")
            run_tachograph()
        else:
            if (not should_run) and (not execute_command):
                execute_command = False
                print("Apagar")
                shutdown_tachograph()