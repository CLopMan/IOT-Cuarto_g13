from cryptography.fernet import Fernet
import base64

KEY_FILE = "./soy_una_clave"

def generate_key():
    key = Fernet.generate_key()
    print("clave de cifrado:", base64.urlsafe_b64decode(key))
    return key

if __name__ == "__main__":
    key = generate_key()
    with open(KEY_FILE, 'wb') as fd:
        fd.write(key)


