import RPi.GPIO as GPIO
import pn532 as nfc
from pn532 import *
from pn532.spi import PN532_SPI
import sys


from cryptography.fernet import Fernet
import random
BLOCKS_TO_READ = list(range(0, 64))

# Clave de fábrica de MIFARE Classic
DEFAULT_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

# Bloques a resetear (salta el bloque 0 que contiene el UID)
BLOCKS_TO_RESET = list(range(1, 64))  # Para MIFARE Classic 1K

def reset_nfc_card():
    uid = pn532.read_passive_target(timeout=1)
    if uid is None:
        print("No se detectó ninguna tarjeta NFC.")
        return False

    print(f"Reseteando tarjeta con UID: {uid}")

    for block in BLOCKS_TO_RESET:
        try:
            if not pn532.mifare_classic_authenticate_block(uid, block, nfc.pn532.MIFARE_CMD_AUTH_A, DEFAULT_KEY):
                print(f"Error autenticando el bloque {block}. Puede estar bloqueado.")
                continue

# Escrib    ir 16 bytes de ceros en el bloque
            if not pn532.mifare_classic_write_block(block, [0x00] * 16):
                print(f"Fallo al escribir en el bloque {block}.")
                continue
            print(f"Bloque {block} restaurado con éxito.")
        except:
            print(f"except {block}")
            continue


    print("Restauración completa.")
    return True

def read_nfc_blocks():
    # Intentar leer la tarjeta NFC
    uid = pn532.read_passive_target(timeout=1)
    if uid is None:
        print("No se detectó ninguna tarjeta NFC.")
        return False

    print(f"UID detectado: {uid}")

    # Leer cada bloque de la tarjeta
    for block in BLOCKS_TO_READ:
        try:
            # Autenticar el bloque con la clave predeterminada (key A)
            if not pn532.mifare_classic_authenticate_block(uid, block, nfc.pn532.MIFARE_CMD_AUTH_A, DEFAULT_KEY):
                print(f"❌ Error autenticando el bloque {block}. Puede que la clave sea incorrecta.")
                continue

            # Leer el bloque de la tarjeta
            block_data = pn532.mifare_classic_read_block(block)
            if block_data is None:
                print(f"❌ No se pudo leer el bloque {block}.")
                continue
        except:
            print(f"exception in block {block}")


        # Mostrar el contenido del bloque
        print(f"Bloque {block}: {block_data.hex()}")

    print("Lectura completa.")



# Generamos una clave de cifrado Fernet (esta clave debe ser almacenada para poder descifrar los datos)
key = Fernet.generate_key()
cipher = Fernet(key)
print(key)

# Generar un tipo de tarjeta aleatorio
card_types = ["Driver", "Control", "Wshop"]
card_type = random.choice(card_types)
card_type_str = f"CardType:{card_type}"

# Cifrar la información del tipo de tarjeta
encrypted_card_type = cipher.encrypt(card_type_str.encode())

print("Starting PN532")
pn532 = PN532_SPI(debug=False, reset=20, cs=4)


ic, ver, rev, support = pn532.get_firmware_version()
print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
pn532.SAM_configuration()
print("waiting for RFID/NFC card...")
read_nfc_blocks()
exit()
while True:
    uid = pn532.read_passive_target(timeout=0.5)
    print('.', end='')
    if uid is None:
        continue
    else:
        break
print("Found card with UID", [hex(i) for i in uid])


# UID de la tarjeta
print("Acerca la tarjeta NFC...")
uid = pn532.read_passive_target(timeout=5)
if uid is None:
    print("No se detectó tarjeta.")
    exit()

print("Tarjeta detectada, UID:", [hex(i) for i in uid])


try: 
    leido = pn532.mifare_classic_read_block(6)
    print(leido)
    exit()
except Exception as e:
    print("excepcion", e)
    exit()





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
if not pn532.mifare_classic_authenticate_block(uid, block_number=block_tp, key_number = nfc.pn532.MIFARE_CMD_AUTH_A, key=key_a):
    print("Error al autenticar el bloque 4")
    exit()
if not pn532.mifare_classic_write_block(block_tp, list(metadata_tp_bytes)):
    print("Error al escribir en el bloque 4")

# Autenticamos y escribimos en el bloque 6 (ID)
if not pn532.mifare_classic_authenticate_block(uid, block_number=block_id, key_number = nfc.pn532.MIFARE_CMD_AUTH_A, key=key_a):
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
        if not pn532.mifare_classic_authenticate_block(uid, block, nfc.pn532.MIFARE_CMD_AUTH_A, key_a):
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
