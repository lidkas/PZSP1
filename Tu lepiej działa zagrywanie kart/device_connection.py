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


class ArduinoConnection:
    def __init__(self, port='COM2'):
        self.port = port
        self.img_width = 320  # change requires arduino code modification
        self.img_height = 240  # change requires arduino code modification
        self.rdy = '*RDY*'  # change requires arduino code modification
        self.ser = self.open_ser(10)
        self.serial_conf()

    def read_byte_as_str(self):
        received_byte = self.ser.read(1)
        if len(received_byte) == 0:
            raise NoByteReceivedError()
        return str(received_byte)[2:3]

    def read_byte_for_rdy(self, curr):
        curr += self.read_byte_as_str()
        curr = curr[1:]
        return curr

    def wait_for_rdy(self):
        curr = self.read_byte_for_rdy(self.rdy)
        while curr != self.rdy:
            curr = self.read_byte_for_rdy(curr)

    def get_bytes_of_image(self, nr_of_bytes):
        self.wait_for_rdy()
        received_bytes = self.ser.read(nr_of_bytes)
        if len(received_bytes) < nr_of_bytes:
            raise NotEnoughBytesReceivedError(len(received_bytes), nr_of_bytes)
        return received_bytes

    def get_image_from_bytes(self, img_bytes):
        img_size = (self.img_width, self.img_height)
        return Image.frombytes('L', img_size, img_bytes, 'raw')

    def get_image(self):
        nr_of_bytes = self.img_width*self.img_height
        img_bytes = self.get_bytes_of_image(nr_of_bytes)
        return self.get_image_from_bytes(img_bytes)

    @staticmethod
    def save_image(img, img_name):
        img.save(img_name)

    def get_and_save_image(self, img_name):
        img = self.get_image()
        self.save_image(img, img_name)
        return img

    def open_ser(self, timeout_time):
        return serial.Serial(self.port, 1000000, timeout=timeout_time)
        # 1000000 - constant in arduino code
        # REMEMBER TO CLOSE SER

    def serial_conf(self):
        """Used to omit images before automatic light regulation"""

        self.get_image()
        self.get_image()
