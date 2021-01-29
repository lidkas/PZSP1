from device_connection import ArduinoConnection
from configuration import color_model_path, value_model_path
import tensorflow as tf
from scanner import receive_and_guess

from time import sleep

color_model = None
value_model = None


def tensorflow_load_models():
    with tf.device('/CPU:0'):
        color_model = tf.keras.models.load_model(color_model_path)
        value_model = tf.keras.models.load_model(value_model_path)

    return color_model, value_model


def play(reps):
    color_model, value_model = tensorflow_load_models()
    ard_conn = ArduinoConnection()

    # ard_conn.give_card()
    # sleep(0.5)
    # print('First card')
    # ard_conn.get_and_save_image('curr_card.bmp', True)
    # ard_conn.give_card()

    for i in range(reps):
        # print('Enter card')
        # input()
        # ard_conn.give_card()
        # sleep(0.5)
        # sleep(0.5)
        # ard_conn.get_and_save_image('curr_card.bmp', True)
        # sleep(3)

        print(ard_conn.get_card(color_model, value_model))
        print('Decide:\n1 - Give to me\n2 - Give to not me\n0 - Retake photo')
        choice = int(input('Nr of choice: '))
        if choice == 1:
            ard_conn.give_card(True)
        elif choice == 2:
            ard_conn.give_card(False)
        else:
            ard_conn.give_card()

        ard_conn.get_image()

    ard_conn.ser.close()


play(20)
