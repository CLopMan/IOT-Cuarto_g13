import RPi.GPIO as GPIO

from cryptography.fernet import Fernet
from pn532.spi import PN532_SPI
import pn532 as nfc
import time
import random
import base64

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

N_SECTORS = 16
KEY_FILE = "./soy_una_clave"

def nonUsableBlocks(num_sectors=N_SECTORS) -> list:
    return [(i) * 4 + 3 for i in range(num_sectors)]

def storeData(data, block):
    global pn532
    global uid
    key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
    print("args: ", data, block)
    try:
        print("start authentication")
        pn532.mifare_classic_authenticate_block(
            uid,
            block_number=block,
            key_number=nfc.pn532.MIFARE_CMD_AUTH_A,
            key=key_a
        )
        print("auth")
        pn532.mifare_classic_write_block(block, data)
        # check
        if pn532.mifare_classic_read_block(block) == data:
            print('write block %d successfully' % block)
    except Exception as e:
        print("Failed Authentication", e)

def storeLongData(data, initial_block):
    """función para almacenar datos de más de 16 bytes en varios bloques"""
    
    # calc num blocks
    blocks = [data[_:_ + 16] for _ in range(0, len(encoded), 16)]
    # padding
    while (len (blocks[-1]) < 16):
        blocks[-1] += b'0'

    # calc bloques donde se tiene que almacenar
    not_usable = nonUsableBlocks()
    usable = []
    curr_block = initial_block
    while len(usable) < len(blocks):
        if curr_block > 63:
            print(f"Warning, data will not fit, wanna continue? size: {len(blocks)}")
            input()
        if curr_block not in not_usable:
            usable.append(curr_block)
        curr_block += 1
    
    # everything ok
    for i, b in enumerate(blocks):
        storeData(b, usable[i])
    print(f"stored {data} in blocks {usable}")

    return len(blocks)


def encrypt(key, data):
    print(f"encrypting using key {base64.urlsafe_b64decode(key)}")
    encrypted = Fernet(key).encrypt(data.encode('utf-8'))
    return encrypted


if __name__ == "__main__":
    global uid
    global pn532
    print("Starting PN532")
    try:
        pn532 = PN532_SPI(debug=False, reset=20, cs=4)
    except Exception as e:
        print("Error!,", e)
        GPIO.cleanup()
    
    print(pn532)

    ic, ver, rev, support = pn532.get_firmware_version()
    print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
    pn532.SAM_configuration()
    print("waiting for RFID/NFC pn532...")
    while True:
        uid = pn532.read_passive_target(timeout=0.5)
        if uid is None:
            continue
        break

    # test
    print("Found pn532 with UID", [hex(i) for i in uid])

    key = None
    with open(KEY_FILE, 'rb') as keyFile:
        key = keyFile.read()

    print("key: ", key)
    
    # card type
    CardType = random.choice(["Driver", "Control", "Wshop"])
    text = f"CardType: {CardType}"
    encoded = encrypt(key, text)
    storeLongData(encoded, 8) 
    print("writed: ", text)

    # info of card type
    text = "TP:B-08;Size-{:03}".format(len(encoded))
    storeData(text.encode('utf-8'), 4)
    print("Writed", text)

    # id
    text = "ID:1492"
    encoded = encrypt(key, text)
    storeLongData(encoded, 20)
    print("Writed", text)

    # info of ID
    text = "ID:B-20;Size-{:03}".format(len(encoded))
    storeData(text.encode('utf-8'), 6)
    print("Writed", text)

    print("Finish")
    GPIO.cleanup()

