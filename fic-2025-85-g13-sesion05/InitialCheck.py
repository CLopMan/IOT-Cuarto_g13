import RPi.GPIO as GPIO
from pn532.spi import PN532_SPI
import time

if __name__ == "__main__":
        print("Starting PN532")
        try:
            pn532 = PN532_SPI(debug=False, reset=20, cs=4)
        except Exception as e:
            print("Error!,", e)
            GPIO.cleanup()
        

        ic, ver, rev, support = pn532.get_firmware_version()
        print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))
        pn532.SAM_configuration()
        print("waiting for RFID/NFC card...")
        while True:
            uid = pn532.read_passive_target(timeout=0.5)
            if uid is None:
                continue
            break
        print("Found card with UID", [hex(i) for i in uid])



