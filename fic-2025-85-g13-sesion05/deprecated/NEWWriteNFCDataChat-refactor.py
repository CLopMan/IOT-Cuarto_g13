import RPi.GPIO as GPIO
from pn532.spi import PN532_SPI
import pn532 as nfc
from cryptography.fernet import Fernet
import random
import time


# Clave de fábrica de MIFARE Classic
DEFAULT_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

# Bloques a resetear (salta el bloque 0 que contiene el UID)
BLOCKS_TO_RESET = list(range(1, 64))  # Para MIFARE Classic 1K
BLOCKS_TO_READ = list(range(0, 64))  # Bloques a leer

def readData(block_number):
    key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
    pn532.mifare_classic_authenticate_block(
        uid, block_number=block_number,
        key_number=nfc.pn532.MIFARE_CMD_AUTH_A, key=key_a)
    data = pn532.mifare_classic_read_block(block_number)
    return data

def setup_pn532():
    """ Configura el lector PN532 """
    pn532 = PN532_SPI(debug=False, reset=20, cs=4)
    ic, ver, rev, support = pn532.get_firmware_version()
    print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
    pn532.SAM_configuration()
    return pn532

def reset_nfc_card(pn532):
    """ Resetea la tarjeta NFC """
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

            # Escribir 16 bytes de ceros en el bloque
            if not pn532.mifare_classic_write_block(block, [0x00] * 16):
                print(f"Fallo al escribir en el bloque {block}.")
                continue
            print(f"Bloque {block} restaurado con éxito.")
        except Exception as e:
            print(f"Error al intentar reseteo del bloque {block}: {e}")
            continue

    print("Restauración completa.")
    return True

def read_nfc_blocks(pn532):
    """ Lee los bloques de la tarjeta NFC """
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

            # Mostrar el contenido del bloque
            print(f"Bloque {block}: {block_data.hex()}")
        except:
            print(f"exception in block {block}")

    print("Lectura completa.")

def write_encrypted_data(pn532, uid, start_block, data):
    """ Escribe datos cifrados en los bloques de la tarjeta NFC """
    chunks = [data[i:i + 16] for i in range(0, len(data), 16)]
    for i, chunk in enumerate(chunks):
        padded_chunk = chunk.ljust(16, b' ')[:16]
        block = start_block + i
        if not pn532.mifare_classic_authenticate_block(uid, block, nfc.pn532.MIFARE_CMD_AUTH_A, DEFAULT_KEY):
            print(f"Error al autenticar el bloque {block}")
            return False
        if not pn532.mifare_classic_write_block(block, list(padded_chunk)):
            print(f"Error al escribir en el bloque {block}")
            return False
    return True

def main():
    global pn532
    global uid
    """ Función principal que orquesta la lógica """
    pn532 = setup_pn532()

    # Generar clave Fernet
    key = Fernet.generate_key()
    cipher = Fernet(key)
    print("Clave de cifrado:", key.decode())

    # Generar tipo de tarjeta aleatorio
    card_types = ["Driver", "Control", "Wshop"]
    card_type = random.choice(card_types)
    card_type_str = f"CardType:{card_type}"

    # Cifrar la información del tipo de tarjeta
    encrypted_card_type = cipher.encrypt(card_type_str.encode())

    # Leemos la tarjeta NFC
    print("Esperando tarjeta NFC...")
    while True:
        uid = pn532.read_passive_target(timeout=1)
        if uid:
            break

            
    print(readData(12))

    exit()

    # Escribir tipo de tarjeta cifrado en bloques
    block_tp = 4  # Información sobre el tipo de tarjeta
    if write_encrypted_data(pn532, pn532.read_passive_target(timeout=1), block_tp + 1, encrypted_card_type):
        print("Tipo de tarjeta cifrado escrito correctamente")

    # Simular un ID de usuario (16 bytes aleatorios)
    user_id = b"1234567890ABCDEF"  # Ejemplo de 16 bytes
    block_id = 6  # Información sobre el ID
    if write_encrypted_data(pn532, pn532.read_passive_target(timeout=1), block_id + 1, user_id):
        print("ID escrito correctamente")

    print("Escritura en la tarjeta completada.")
    print("Clave de cifrado (guárdala para leer los datos):", key.decode())

if __name__ == "__main__":
    main()

