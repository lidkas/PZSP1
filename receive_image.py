import serial
from PIL import Image


class NoByteReceivedError(Exception):
    def __init__(self):
        super().__init__('No byte was transmitted, timed out')


class NotEnoughBytesReceivedError(Exception):
    def __init__(self, bytes_received, bytes_expected):
        msg = f'{bytes_received} out of {bytes_expected} excpected bytes'
        msg += ' were transmitted before timeout'
        super().__init__(msg)


def read_byte_as_str(ser):
    received_byte = ser.read(1)
    if len(received_byte) == 0:
        raise NoByteReceivedError()
    return str(received_byte)[2:3]


def read_byte_for_rdy(ser, curr):
    curr += read_byte_as_str(ser)
    curr = curr[1:]
    return curr


def wait_for_rdy(ser, rdy):
    curr = read_byte_for_rdy(ser, rdy)
    while curr != rdy:
        curr = read_byte_for_rdy(ser, curr)


def get_bytes_of_image(ser, nr_of_bytes, rdy):
    wait_for_rdy(ser, rdy)
    received_bytes = ser.read(nr_of_bytes)
    if len(received_bytes) < nr_of_bytes:
        raise NotEnoughBytesReceivedError(len(received_bytes), nr_of_bytes)
    return received_bytes


def get_image_from_bytes(img_bytes, img_width, img_height):
    return Image.frombytes('L', (img_width, img_height), img_bytes, 'raw')


def get_image(ser, img_width, img_height, rdy):
    nr_of_bytes = img_width*img_height
    img_bytes = get_bytes_of_image(ser, nr_of_bytes, rdy)
    return get_image_from_bytes(img_bytes, img_width, img_height)


def save_image(img, img_name):
    img.save(img_name)


def get_and_save_image(ser, img_name, img_width, img_height, rdy):
    img = get_image(ser, img_width, img_height, rdy)
    save_image(img, img_name)
    return img


def open_ser(port_name, timeout_time):
    return serial.Serial(port_name, 1000000, timeout=timeout_time)
    # 1000000 - constant in arduino code
    # REMEMBER TO CLOSE SER


def serial_conf(port):
    # REMEMBER TO CLOSE SER

    wd = 320    # change requires arduino code modification
    hg = 240    # change requires arduino code modification
    rdy = '*RDY*'   # change requires arduino code modification
    # port = 'COM2'

    ser = open_ser(port, 10)
    get_image(ser, wd, hg, rdy)
    get_image(ser, wd, hg, rdy)

    return ser
