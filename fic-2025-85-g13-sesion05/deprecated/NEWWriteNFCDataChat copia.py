import RPi.GPIO as GPIO
from Adafruit_PN532 import PN532_SPI
from cryptography.fernet import Fernet
import random

# Configuración del PN532
RESET_PIN = 20
CS_PIN = 4
pn532 = PN532_SPI(debug=False, reset=RESET_PIN, cs=CS_PIN)
pn532.SAM_configuration()

# Generamos una clave de cifrado Fernet (esta clave debe ser almacenada para poder descifrar los datos)
key = Fernet.generate_key()
cipher = Fernet(key)

# Generar un tipo de tarjeta aleatorio
card_types = ["Driver", "Control", "Wshop"]
card_type = random.choice(card_types)
card_type_str = f"CardType:{card_type}"

# Cifrar la información del tipo de tarjeta
encrypted_card_type = cipher.encrypt(card_type_str.encode())

# UID de la tarjeta
print("Acerca la tarjeta NFC...")
uid = pn532.read_passive_target(timeout=5)
if uid is None:
    print("No se detectó tarjeta.")
    exit()

print("Tarjeta detectada, UID:", [hex(i) for i in uid])

# **Aquí sí seguimos la estructura pedida:**
block_tp = 4   # Información sobre el tipo de tarjeta
block_id = 6   # Información sobre el ID

# Crear las etiquetas de metadatos
metadata_tp = f"TP:B-{block_tp+1:02d};Size-{len(encrypted_card_type):03d}"
metadata_id = f"ID:B-{block_id+1:02d};Size-016"  # ID fijo de 16 bytes por ejemplo

# Asegurar que las etiquetas ocupan exactamente 16 bytes
metadata_tp_bytes = metadata_tp.ljust(16, ' ').encode()[:16]
metadata_id_bytes = metadata_id.ljust(16, ' ').encode()[:16]

# Autenticación (clave por defecto 0xFFFFFFFFFFFF)
key_a = [0xFF] * 6

# Autenticamos y escribimos en el bloque 4 (TP)
if not pn532.mifare_classic_authenticate_block(uid, block_tp, PN532_SPI.MIFARE_CMD_AUTH_A, key_a):
    print("Error al autenticar el bloque 4")
    exit()
if not pn532.mifare_classic_write_block(block_tp, list(metadata_tp_bytes)):
    print("Error al escribir en el bloque 4")

# Autenticamos y escribimos en el bloque 6 (ID)
if not pn532.mifare_classic_authenticate_block(uid, block_id, PN532_SPI.MIFARE_CMD_AUTH_A, key_a):
    print("Error al autenticar el bloque 6")
    exit()
if not pn532.mifare_classic_write_block(block_id, list(metadata_id_bytes)):
    print("Error al escribir en el bloque 6")

# Escribir los datos en los bloques correspondientes
def write_encrypted_data(start_block, data):
    chunks = [data[i:i+16] for i in range(0, len(data), 16)]
    for i, chunk in enumerate(chunks):
        padded_chunk = chunk.ljust(16, b' ')[:16]
        block = start_block + i
        if not pn532.mifare_classic_authenticate_block(uid, block, PN532_SPI.MIFARE_CMD_AUTH_A, key_a):
            print(f"Error al autenticar el bloque {block}")
            return False
        if not pn532.mifare_classic_write_block(block, list(padded_chunk)):
            print(f"Error al escribir en el bloque {block}")
            return False
    return True

# Escribir tipo de tarjeta cifrado (desde el bloque 5)
if write_encrypted_data(block_tp + 1, encrypted_card_type):
    print("Tipo de tarjeta cifrado escrito correctamente")

# Simular un ID de usuario (16 bytes aleatorios)
user_id = b"1234567890ABCDEF"  # Ejemplo de 16 bytes

# Escribir ID cifrado (desde el bloque 7)
if write_encrypted_data(block_id + 1, user_id):
    print("ID escrito correctamente")

print("Escritura en la tarjeta completada.")
print("Clave de cifrado (guárdala para leer los datos):", key.decode())
