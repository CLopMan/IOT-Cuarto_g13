import RPi.GPIO as GPIO

from cryptography.fernet import Fernet
from pn532.spi import PN532_SPI
import pn532 as nfc
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

N_SECTORS = 16

KEY_FILE = "./soy_una_clave"

def nonUsableBlocks(num_sectors=N_SECTORS) -> list:
    return [(i) * 4 + 3 for i in range(num_sectors)]

def readData(pn532, uid, block):
    key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
    pn532.mifare_classic_authenticate_block(uid, block_number=block, key_number=nfc.pn532.MIFARE_CMD_AUTH_A, key=key_a)
    data = pn532.mifare_classic_read_block(block)
    return data


def readLongData(pn532, uid, initial_block, n_bytes):
    not_usable = nonUsableBlocks()
    usable = []
    curr_block = initial_block
    while len(usable)*16 < n_bytes:
        if curr_block > 63:
            print("Warning! asked for more space than you have {}".format(usable))
            input()
        if curr_block not in not_usable:
            usable.append(curr_block)
        curr_block += 1

    print(usable)
    txt = b''
    for i in usable:
        txt += readData(pn532, uid, i)
    print(txt)
    return txt
        
def decryptmsg(key, data):
    fernet = Fernet(key)
    message_encrypted = data.decode().split("=")[0] + "="*(len(data.decode().split("="))-1)
    decrypted = fernet.decrypt(message_encrypted.encode('utf-8'))
    return decrypted

if __name__ == "__main__":

    global uid
    global pn532
    print("Starting PN532")
    try:
        pn532 = PN532_SPI(debug=False, reset=20, cs=4)
    except Exception as e:
        print("Error!,", e)
        GPIO.cleanup()
        exit()
    
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

    with open(KEY_FILE, 'rb') as fd:
        key = fd.read()

    
    print(key)
    print(" >>> ", decryptmsg(key, readLongData(pn532, uid, 8, 120)))
    print(" >>> ", (readData(pn532, uid, 4)))
    print(" >>> ", decryptmsg(key, readLongData(pn532, uid, 20, 100)))
    print(" >>> ", (readData(pn532, uid, 6)))

