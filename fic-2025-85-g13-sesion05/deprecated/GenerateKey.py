from cryptography.fernet import Fernet
import base64


def genereate_key():
    key = Fernet.generate_key()
    print("La clave de cifrado es: {}".format(base64.urlsafe_b64decode(key)))
    return key


def store_key(key, filename):
    with open(filename, 'wb') as filekey:
        filekey.write(key)
        filekey.close()


if __name__ == '__main__':
    try:
        key_to_store = genereate_key()
        store_key(key_to_store, 'file_key.key')
    except Exception as e:
        print(e)
