import mpu6050
import time
import signal
acelerometro = None
def signal_handler(sig, frame):
    if acelerometro:
        acelerometro.bus.close()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    acelerometro = mpu6050.mpu6050(0x68)
    while 1:
        accelerometer_data = acelerometro.get_accel_data()
        time.sleep(0.1)
        a_x = accelerometer_data['x']
        a_y = accelerometer_data['y']
        a_z = accelerometer_data['z']
        velocidad_x = 0.1*a_x
        velocidad_y = 0.1*a_y
        velocidad_z = 0.1*a_z

        print("velocidad: [{% 0.2f}, {% 0.2f}, {% 0.2f}]" % (velocidad_x, velocidad_y, velocidad_z))
        time.sleep(1)
