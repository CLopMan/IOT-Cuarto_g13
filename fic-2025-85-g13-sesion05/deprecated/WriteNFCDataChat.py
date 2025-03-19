import RPi.GPIO as GPIO
import pn532 as nfc
from pn532.spi import PN532_SPI
from cryptography.fernet import Fernet
import base64
import random


def storeData(data: bytes, block):
    key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'

    print("uid;",uid)
    print("numero bloque:",block)

    print("numero key:", nfc.pn532.MIFARE_CMD_AUTH_A)
    print("key:", key_a)
    
    pn532.mifare_classic_authenticate_block(
        uid, block_number=block, key_number=nfc.pn532.MIFARE_CMD_AUTH_A, key=key_a)
    print("AAAAAA")
    pn532.mifare_classic_write_block(block, data)
    print("BBBBBBB")
    if pn532.mifare_classic_read_block(block) == data:
        print('write block %d successfully' % block)
    else:
        print(pn532.mifare_classic_read_block(block))

def cypher_message(message, fileKeyName):
    with open(fileKeyName, 'rb') as filekey:
        key = filekey.read()
    print("La clave de cifrado es: {}".format(base64.urlsafe_b64decode(key)))

    # using the generated key
    fernet = Fernet(key)
    crypted = fernet.encrypt(message.encode('utf-8'))
    print("Mensaje cifrado: {}".format(crypted))
    return crypted


def generate_cardtype():
    r1 = random.randint(1, 3)
    if r1 == 1:
        new_text = "CardType: Driver"
    elif r1 == 2:
        new_text = "CardType: Control"
    else:
        new_text = "CardType: Wshop"
    return new_text


def generate_cardholder_id():
    myText = "UserID:"
    for i in range(0, 8):
        aNumber = random.randint(48, 57) #Son los códigos ascii correspondientes a los dígitos del 0 al 9
        myText = myText + chr(aNumber)
    aLetter = random.randint(65, 90)
    myText = myText + chr(aLetter)
    return myText


if __name__ == '__main__':
    try:
        pn532 = PN532_SPI(debug=False, reset=20, cs=4)

        ic, ver, rev, support = pn532.get_firmware_version()
        print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()

        print('Waiting for RFID/NFC card to write to!')

        while True:
            # Check if a card is available to read
            uid = pn532.read_passive_target(timeout=0.5)
            print('.', end="")
            # Try again if no card is available.
            if uid is not None:
                break
        print('Found card with UID:', [hex(i) for i in uid])

        # Generar un tipo de tarjeta
        card_type_text = generate_cardtype()
        card_type_bytes = cypher_message(card_type_text, 'file_key.key')
        current_block = 12
        current_sector = 4
        block12_text = 'TP:B-12;Size-' + str(len(card_type_bytes)).zfill(3)
        block12_text_bytes = block12_text.encode('utf-8')
        print("La información a almacenar en Bloque 4: {}".format(block12_text_bytes))
        storeData(block12_text_bytes, 12)

        if len(card_type_bytes) % 16 == 0:
            number_blocks_to_write = len(card_type_bytes) // 16
        else:
            number_blocks_to_write = (len(card_type_bytes) // 16) + 1

        for i in range(number_blocks_to_write):
            if (i + 1) * 16 > len(card_type_bytes):
                dollars_number = ((i + 1) * 16) - len(card_type_bytes)
                dollars_text = ''
                for j in range(dollars_number):
                    dollars_text += '$'
                block_to_write = card_type_bytes[i * 16:len(card_type_bytes)]
                block_to_write = block_to_write + dollars_text.encode('utf-8')
            else:
                block_to_write = card_type_bytes[i * 16:(i + 1) * 16]
            print("La información a almacenar en Bloque {}: {}".format(current_block, block_to_write))
            storeData(block_to_write, current_block)
            current_block += 1
            if current_block == (current_sector - 1) * 4 + 3:
                current_block += 1
                current_sector += 1

        # A partir de este momento, generar aleatoriamente un DNI (número a numero - 8 números - y una letra del alfabeto)
        text = generate_cardholder_id()
        # Cifrarlo y almacenarlo
        id_bytes = cypher_message(text, 'file_key.key')
        print("El texto en claro es: {}, y su cifrado es: {}".format(text.encode("utf-8"), id_bytes))
        print("La longitud de los datos a almacenar es {} bytes".format(len(id_bytes)))

        block14_text = 'TP:B-' + str(current_block) + ';Size-' + str(len(id_bytes))
        block14_text_bytes = block14_text.encode('utf-8')
        print("La información a almacenar en Bloque 6: {}".format(block14_text_bytes))
        # Write block #6
        storeData(block14_text_bytes, 14)

        # Decidir qué bloques se van a utilizar para almacenar la informción.
        if len(id_bytes) % 16 == 0:
            number_blocks_to_write = len(id_bytes) // 16
        else:
            number_blocks_to_write = (len(id_bytes) // 16) + 1
        print("Necesitamos {} bloques".format(number_blocks_to_write))

        blocks_to_write = []
        for i in range(number_blocks_to_write):
            if (i + 1) * 16 > len(id_bytes):
                dollars_number = ((i + 1) * 16) - len(id_bytes)
                dollars_text = ''
                for j in range(dollars_number):
                    dollars_text += '$'
                last_block = id_bytes[i * 16:len(id_bytes)]
                last_block = last_block + dollars_text.encode('utf-8')
                blocks_to_write.append(last_block)
            else:
                blocks_to_write.append(id_bytes[i * 16:(i + 1) * 16])
            print("La información a almacenar en Bloque {}: {}".format(current_block, blocks_to_write))
            storeData(block_to_write, current_block)
            current_block += 1
            if current_block == (current_sector - 1) * 4 + 3:
                current_block += 1
                current_sector += 1
        # Se les da puntos adicionales si implementan un mecanismo de seguridad más robusto
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
