import RPi.GPIO as GPIO
import pn532 as nfc
from pn532.spi import PN532_SPI
from cryptography.fernet import Fernet
import base64
from datetime import datetime, timedelta


def readData(pn532_device, uid, block):
    key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
    pn532_device.mifare_classic_authenticate_block(
        uid, block_number=block, key_number=nfc.pn532.MIFARE_CMD_AUTH_A, key=key_a)
    data = pn532_device.mifare_classic_read_block(block)
    return data


def decypher_message_from_card(message, fileKeyName):
    print(1)
    print("Datos cifrados de la tarjeta: {}".format(message.decode('utf-8')))
    with open(fileKeyName, 'rb') as filekey:
        key = filekey.read()
    print(2)
    print("La clave de cifrado es: {}".format(base64.urlsafe_b64decode(key)))
    fernet = Fernet(key)
    print(3)
    decrypted = fernet.decrypt(message.decode('utf-8'))
    print("Mensaje en limpio de la tarjeta: {}".format(decrypted))
    return decrypted


def getInfoIndex (pn532_device, uid, block_to_read):
    print('Vamos a leer el bloque {}'.format(block_to_read))
    block12_text_bytes = readData(pn532_device, uid, block_to_read)
    print(4)
    print(block12_text_bytes)
    print(type(block12_text_bytes))

    block12_text = block12_text_bytes.decode('utf-8')
    print("La información leida del Bloque {}: {}".format(block_to_read, block12_text))
    cardTypeIndexParts = block12_text.split(";")
    block_rough_info = cardTypeIndexParts[0].split("-")
    print(block_rough_info)
    block_with_info = int(block_rough_info[1])
    bytes_rough_info = cardTypeIndexParts[1].split("-")
    bytes_to_read = int(bytes_rough_info[1])
    print("AAA")
    return block_with_info, bytes_to_read


def getInfoFromCard (pn532_device, uid, block, blocks_number, bytes_to_read):
    read_bytes = bytearray()
    current_sector = (block // 4) + 1
    current_block = block
    for i in range(blocks_number):
        blocks_bytes = readData(pn532_device, uid, current_block)
        for j in range(len(blocks_bytes)):
            read_bytes.append(blocks_bytes[j])
        current_block += 1
        if current_block == (current_sector - 1) * 4 + 3:
            current_block += 1
            current_sector += 1
    return read_bytes[0:bytes_to_read]


def calculate_blocks_to_read (bytesNumber):
    if bytesNumber % 16 == 0:
        number_blocks_to_read = bytesNumber // 16
    else:
        number_blocks_to_read = (bytesNumber // 16) + 1
    return number_blocks_to_read


def get_reader_uid():
    pn532 = PN532_SPI(debug=False, reset=20, cs=4)

    ic, ver, rev, support = pn532.get_firmware_version()
    print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
    # Configure PN532 to communicate with MiFare cards
    pn532.SAM_configuration()
    return pn532


def read_tachograph_info_from_card (pn532_device):
    print('Waiting for RFID/NFC card to write to!')
    my_card_type = 'Error'
    my_id = 'Error'
    target_time = datetime.now() + timedelta(seconds=3)
    check_card = True
    while check_card:
        # Check if a card is available to read
        uid = pn532_device.read_passive_target(timeout=0.5)
        print('.', end="")
        # Try again if no card is available.
        if uid is not None:
            print('Found card with UID:', [hex(i) for i in uid])
            my_card_type, my_id = read_info_from_card(pn532_device, uid)
            check_card = False
        else:
            current_time = datetime.now()
            if current_time > target_time:
                check_card = False

    return my_card_type, my_id


def read_info_from_card(pn532_device, uid):
    try:
        block_number = 12
        card_type_block, card_type_bytes_number = getInfoIndex(pn532_device, uid, block_number)
        print("El bloque con la info de tipo de tarjeta es {} y el número de bytes a leer es: {}".format( card_type_block, card_type_bytes_number))
        card_type_blocks_number = calculate_blocks_to_read(card_type_bytes_number)
        print("El número de bloques a leer para el tipo de tarjeta es: {}".format(card_type_blocks_number))
        card_type_bytes = getInfoFromCard(pn532_device, uid, card_type_block, card_type_blocks_number, card_type_bytes_number)
        print(5)
        print("Los bytes del tipo tarjeta es: {}".format(card_type_bytes.decode('utf-8')))
        card_type = decypher_message_from_card(card_type_bytes, 'file_key.key')
        print(6)
        print("El tipo de tarjeta es: {}".format(card_type.decode('utf-8')))
        block_number = 14
        card_id_block, card_id_bytes_number = getInfoIndex(pn532_device, uid, block_number)
        print("El bloque con la info del id de tarjeta es {} y el número de bytes a leer es: {}".format( card_id_block, card_id_bytes_number))
        card_id_blocks_number = calculate_blocks_to_read(card_id_bytes_number)
        print("El número de bloques a leer para el id de tarjeta es: {}".format(card_id_blocks_number))
        card_id_bytes = getInfoFromCard(pn532_device, uid, card_id_block, card_id_blocks_number, card_id_bytes_number)
        print(7)
        print("Los bytes del id tarjeta es: {}".format(card_id_bytes.decode('utf-8')))
        id = decypher_message_from_card(card_id_bytes, 'file_key.key')
        print(8)
        print("El id de la tarjeta es: {}".format(id.decode('utf-8')))
    except:
        print("Excepcion")
        card_type = 'Error'
        id = 'Error'
    print(9)
    return card_type.decode('utf-8'), id.decode('utf-8')


if __name__ == '__main__':
    try:
        pn532 = get_reader_uid()
        my_card_type, my_id = read_tachograph_info_from_card(pn532)
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()