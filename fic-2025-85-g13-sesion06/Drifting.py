import time
import json
from mpu6050 import mpu6050

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

if __name__ == '__main__':
    acelerometro = mpu6050(0x68, bus=1)
    time.sleep(1)  # Estabilización del sensor

    offsets = get_accel_offset(acelerometro)
    print(offsets)

