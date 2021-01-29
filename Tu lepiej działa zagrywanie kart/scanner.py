from configuration import image_width, image_height, color_scale
import numpy as np
import cv2
from tensorflow.keras.preprocessing.image import ImageDataGenerator


color_dictionary = {0: 'c', 1: 'd', 2: 'h', 3: 's'}
value_dictionary = {0: '10', 1: '9', 2: 'a', 3: 'err', 4: 'j', 5: 'k', 6: 'q'}


def guess(path_to_file, model):
    img = cv2.imread(path_to_file, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (image_width, image_height))
    imgs = img.reshape((1, img.shape[0], img.shape[1], 1))
    data_generator = ImageDataGenerator(rotation_range=20, brightness_range=(1, 1.5),
                                        shear_range=1.0, zoom_range=[1, 1])
    data_generator.fit(imgs)
    image_iterator = data_generator.flow(imgs)
    img_transformed = image_iterator.next()[0].astype('int') / color_scale
    prediction = model.predict(np.array([img_transformed])).tolist()
    return prediction[0].index(max(prediction[0]))


def receive_and_guess(ard_conn, color_model, value_model):
    file_name = 'curr_card.bmp'
    ard_conn.get_and_save_image(file_name)
    guessed_color = color_dictionary[guess(file_name, color_model)]
    guessed_value = value_dictionary[guess(file_name, value_model)]
    return guessed_color, guessed_value
