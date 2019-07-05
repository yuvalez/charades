import io
import os

import serial
import sys
from Crypto.Cipher import AES
from PIL import Image
import re

fh = 'white.bmp'


MESSAGE_FORMAT = "EB90{opcode}{checksum}{message}"

def pad(data):
    return data + b"\x00"*(16-len(data)%16)

def tohex(val, nbits):
  return hex((val + (1 << nbits)) % (1 << nbits))[2:]

def encrypt(message, key):
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(pad(message))

def calc_checksum(message):
    array = re.findall('..', message)
    checksum = 0
    for byte in array:
        checksum += int(byte, 16)

    return tohex(0-checksum, 8).zfill(2)

def send_image_ready(on_off, plain_dec):
    data = 0
    if on_off:
        data += 1
    if plain_dec:
        data += 2
    # new image.
    data += 4

    status = "0000000000000000000000000000000{data}".format(data=data)
    checksum = 0 - (0xeb + 0x90 + 0x01 + int(status, 16))
    checksum = tohex(checksum, 8)
    message = MESSAGE_FORMAT.format(opcode="01",
                             checksum=checksum.upper(),
                             message = status)
    print(message)
    return bytes.fromhex(message)


def send_screen_off():
    data = 0

    status = "0000000000000000000000000000000{data}".format(data=data)
    checksum = 0 - (0xeb + 0x90 + 0x01 + int(status, 16))
    checksum = tohex(checksum, 8)
    message = MESSAGE_FORMAT.format(opcode="01",
                             checksum=checksum.upper(),
                             message = status)
    print(message)
    return bytes.fromhex(message)

def send_key(key):
    message = MESSAGE_FORMAT.format(opcode="02",
                             checksum="00",
                             message=key)
    checksum = calc_checksum(message)
    message = MESSAGE_FORMAT.format(opcode="02",
                             checksum=checksum,
                             message=key)
    print(message)
    return bytes.fromhex(message)

def send_picture(ser, data, encrypted):
    if encrypted:
        opcode = "0A"
    else:
        opcode = "0B"
    for idx, block in enumerate(data):

        my_block = block.hex().zfill(256)
        word_list = [my_block[i:i + 4] for i in range(0, len(my_block), 4)]

        word_list = list(map(lambda x: "{}{}".format(x[2:], x[:2]), word_list))

        my_block = ''.join(word_list)
        if idx == 0:
            print(my_block)
        message = MESSAGE_FORMAT.format(opcode=opcode,
                                        checksum="00",
                                        message=my_block)
        checksum = calc_checksum(message)
        message = MESSAGE_FORMAT.format(opcode=opcode,
                                        checksum=checksum,
                                        message=my_block)
        ser.write(bytes.fromhex(message))

if __name__ == "__main__":

    # send_screen_off()
    #
    # sys.exit(1)

    with open(fh, 'rb') as f:
        x = bytearray(f.read())

    header = x[:122]
    data = x[122:]


    # key = bytes.fromhex("00" * 16)
    # enc = encrypt(data, key)
    enc = data
    with open('hara_enc.bmp', 'wb') as f:
        f.write(header)
        f.write(enc)

    ser = serial.Serial(port="COM7",
                        baudrate=115200,
                        timeout=10)

    if ser.is_open:
        ser.close()

    ser.open()

    ser.write(send_image_ready(True, False))
    # ser.write(send_key("00" * 16))

    ser.read_until(size=20)

    info = [enc[i:i + 128] for i in range(0, len(enc), 128)]
    send_picture(ser, info, False)

    ser.close()