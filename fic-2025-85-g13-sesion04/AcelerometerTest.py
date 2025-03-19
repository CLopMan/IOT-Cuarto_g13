import mpu6050
import time

if __name__ == '__main__':
    acelerometro = mpu6050.mpu6050(0x68)
    while 1:
        accelerometer_data = acelerometro.get_accel_data()

        gyroscope_data = acelerometro.get_gyro_data()
        temperature = acelerometro.get_temp()

        print(f"Accelerometer data\n\t- x: {accelerometer_data['x']} y: {accelerometer_data['y']} z: {accelerometer_data['z']}")
        print(f"gyroscope data\n\t {gyroscope_data}")
        print(f"temperature data\n\t {temperature}")

        #acelerometro.bus.close()
        time.sleep(1) 
