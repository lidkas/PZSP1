import serial
from PIL import Image

from serial.tools import list_ports
from time import sleep

from scanner import receive_and_guess


class NoByteReceivedError(Exception):
    def __init__(self):
        super().__init__('No byte was transmitted, timed out')


class NotEnoughBytesReceivedError(Exception):
    def __init__(self, bytes_received, bytes_expected):
        msg = f'{bytes_received} out of {bytes_expected} excpected bytes'
        msg += ' were transmitted before timeout'
        super().__init__(msg)


class ArduinoConnection:
    def __init__(self):
        self.port = list_ports.comports()[0].name
        self.img_width = 320  # change requires arduino code modification
        self.img_height = 240  # change requires arduino code modification
        self.rdy = '*RDY*'  # change requires arduino code modification
        self.ser = self.open_ser(10)
        self.serial_conf()  # Commented out because waits for byte

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

    def get_image(self, wait_button=False):
        self.wait_for_button(wait_button)
        nr_of_bytes = self.img_width*self.img_height
        img_bytes = self.get_bytes_of_image(nr_of_bytes)
        return self.get_image_from_bytes(img_bytes)

    def save_image(self, img, img_name):
        img.save(img_name)

    def get_and_save_image(self, img_name, wait_button=False):
        img = self.get_image(wait_button)
        self.save_image(img, img_name)
        return img

    def open_ser(self, timeout_time):
        return serial.Serial(self.port, 1000000, timeout=timeout_time)
        # 1000000 - constant in arduino code
        # REMEMBER TO CLOSE SER

    def serial_conf(self):
        '''Used to omit images before automatic light regulation'''

        sleep(3)
        self.get_image(False)
        self.give_card()
        self.get_image(False)
        # self.give_card()

    def give_card(self, to_me=None):
        if to_me is None:
            self.ser.write(b'x')
            return
        if to_me:
            self.ser.write(b'm')
        else:
            self.ser.write(b'o')

    def wait_for_button(self, wait=False):
        # if wait:
        #     self.ser.write(b'y')
        # else:
        #     self.ser.write(b'n')
        pass

    def get_card(self, models):
        print('Włóż kartę i wciśnij enter')
        input()
        self.give_card()

        color, value = receive_and_guess(self, models)
        while value == 'err':
            self.give_card()
            color, value = receive_and_guess(self, models)

        return color, value

    def scan_card(self, my_cards, models):
        color, value = self.get_card(models)
        card = str(self.card_id(color, value))
        if card not in my_cards:
            print(f'Rozpoznano {card}. Nie powinieneś mieć takiej karty.')
            self.give_card(True)
            self.get_image()
            return
        self.give_card(False)
        self.get_image()
        return card

    def deal_one_card(self, my_cards, models):
        color, value = self.get_card(models)
        card = str(self.card_id(color, value))
        if card not in my_cards:
            self.give_card(False)
            self.get_image()
            return False
        self.give_card(True)
        self.get_image()
        return True

    def deal_cards(self, cards_to_give, models):
        given_cards = 0
        while given_cards < len(cards_to_give):
            if self.deal_one_card(cards_to_give, models):
                given_cards += 1

    def card_id(self, color, value):
        value_ids = {
            'a': 0,
            'k': 1,
            'q': 2,
            'j': 3,
            '10': 4,
            '9': 5,
        }
        color_ids = {
            's': 0,
            'h': 1,
            'd': 2,
            'c': 3,
        }

        return 4*value_ids[value] + color_ids[color] + 1
