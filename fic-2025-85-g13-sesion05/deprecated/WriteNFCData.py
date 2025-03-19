import RPi.GPIO as GPIO
import nfc.pn532
from pn532.spi import PN532_SPI
from cryptography.fernet import fernet
import base64
import random

def generate_key():
    key = Fernet.generate_key()
    print("La clave de cifrado es {}".format(base64.urlsafe_b64decode(key)))
    return key


text = 'CardType: Driver'
encoded = text.encode('utf-8')

""" def storeData(data, block): 
    key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
    pn532.mifare_classic_authenticate_block(uid, block_number=block, key_number=nfc.pn532.MIFARE_CMD_AUTH_A, key=key_a)
    pn532.mifare_classic_write_block(block, encoded)
    if pn532.mifare_classic_write_block(block) == encoded:
        print('write block %d successfully' % block) """

def storeData(data:bytes, block): 
    key_a = b'\xFF\xFF\xFF\xFF\xFF\xFF'
    pn532.mifare_classic_authenticate_block(uid, block_number=block, key_number=nfc.pn532.MIFARE_CMD_AUTH_A, key=key_a)
    pn532.mifare_classic_write_block(block, data)
    if pn532.mifare_classic_write_block(block) == data:
        print('write block %d successfully' % block)

def cypher_message(message, fileKeyName):
    with open(fileKeyName, "rb") as filekey:
        key = filekey.read()
    print("La clave de cifrado es: {}".format(base64.urlsafe_b64decode(key)))

    fernet = Fernet(key)
    crypted = fernet.encrypt(message.encode('utf-8'))
    print("Mensaje cifrado {}".format(crypted))

def generate_cardtype():
    r1 = random.randint(1,3)
    if r1 == 1:
        new_text = "CardType: Driver"
    if r1 == 2:
        new_text = "CardType: Control"
    else:
        new_text = "CardType: Wshop"
    return r1

def generate_cardholder_id():
    myText = "UserID:"
    for i in range(0,8):
        aNumber = random.randint(48,57)
        myText = myText + chr(aNumber)
    aLetter = random.randint(65,90)
    myText = myText + chr(aLetter)
    return myText




if __name__ == "__main__":
    try: 
        pn532 = PN532_SPI(debug=False, reset=20, cs=4)
        ic, ver, rev, support = pn532.get_firmware_version()
        print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
        pn532.SAM_configuration()
        print("waiting for RFID/NFC card...")
        while True:
            uid = pn532.read_passive_target(timeout=0.5)
            print('.', end='')
            if uid is None:
                continue
        print("Found card with UID", [hex(i) for i in uid])

        #Generar un tipo de tarjeta
        card_type_text = generate_cardtype()
        card_type_bytes = cypher_message(card_type_text, 'file_key.key')

        #TODO: Faltan cosas

        text = generate_cardholder_id()
        # Cifrarlo y almacenarlo
        id_bytes = cypher_message(text, 'file_key.key')
        print("El texto en claro es: {}".format(text.encode('utf-8'),id_bytes))
        print("La longitud de los datos a almacenar es {} bytes".format(len(id_bytes)))
        block6_text = "TP:B-" + str(current_block) + ";Size-" + str(len(id_bytes))
        block6_text_bytes = block6_text.encode('utf-8')
        print("La información a almacenar en bloque 6: {}".format(block6_text_bytes))
        #Write block 6
        storeData(block6_text_bytes,6)

        # Deciditr qué bloques se van a utilizar para almacenar la información
        if len(id_bytes) % 16 == 0:
            number_blocks_to_write = len(id_bytes) // 16
        else:
            number_blocks_to_write = (len(id_bytes) // 16) + 1
        print("Necesitamos {} bloques".format(number_blocks_to_write))

        blocks_to_write = []
        for i in range(number_blocks_to_write):
            if(i+1) * 16 > len(id_bytes):
                dollars_number + ((i+1) * 16) - len(id_bytes)
                dollars_text = ''
                for j in range(dollars_number):
                    dollars_text += "$"
                last_block = id_bytes[i * 16:len(id_bytes)]
                last_block = last_block + dollars_text.encode('utf-8')
                blocks_to_write.append(last_block)
            else:
                blocks_to_write.append(id_bytes[i * 16:(i+1)*16])
            print("La información a almacenar en Bloque {}:{}".format(current_block,blocks_to_write))
            storeData(blocks_to_write,current_block)
            current_block += 1
            if current_block == (current_sector - 1) * 4 + i #No sé si lo ultimo es una i
                current_block += 1
                current_sector += 1
    except Exception as e:
        print(e)
    
    finally:
        GPIO.cleanup()
        
        
        


