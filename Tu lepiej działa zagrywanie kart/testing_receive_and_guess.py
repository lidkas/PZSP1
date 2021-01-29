from device_connection import ArduinoConnection
from configuration import color_model_path, value_model_path
import tensorflow as tf
from scanner import receive_and_guess

color_model = None
value_model = None


def tensorflow_load_models():
    with tf.device('/CPU:0'):
        _color_model = tf.keras.models.load_model(color_model_path)
        _value_model = tf.keras.models.load_model(value_model_path)

    return _color_model, _value_model


def play(reps):
    ard_conn = ArduinoConnection()
    _color_model, _value_model = tensorflow_load_models()

    for i in range(reps):
        print(receive_and_guess(ard_conn, _color_model, _value_model))

    ard_conn.ser.close()


play(20)
