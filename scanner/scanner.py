from configuration import image_width, image_height, color_scale, color_model_path, value_model_path
import numpy as np
import cv2
import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator


color_dictionary = {0:'c', 1:'d', 2:'h', 3:'s'}
value_dictionary = {0:'10', 1:'9', 2:'a', 3:'err',4:'j', 5:'k',6:'q'}

def guess(path_to_file, model):
    img = cv2.imread(path_to_file, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (image_width, image_height))
    imgs = img.reshape((1, img.shape[0], img.shape[1], 1))
    data_generator = ImageDataGenerator(rotation_range=20, brightness_range=(1, 1.5), shear_range=1.0, zoom_range=[1, 1])
    data_generator.fit(imgs)
    image_iterator = data_generator.flow(imgs)
    img_transformed = image_iterator.next()[0].astype('int') / color_scale
    prediction = model.predict(np.array([img_transformed])).tolist()

    return prediction[0].index(max(prediction[0]))


with tf.device('/CPU:0'):
    color_model = tf.keras.models.load_model(color_model_path)
    value_model = tf.keras.models.load_model(value_model_path)
    print(color_dictionary[guess(r'P:\card cv\talia B\9C0.bmp', color_model)])
    print(value_dictionary[guess(r'P:\card cv\talia B\9C0.bmp', value_model)])


"""
# webcam feature

with tf.device('/CPU:0'):
    color_model = tf.keras.models.load_model(color_model_path)
    value_model = tf.keras.models.load_model(value_model_path)

vid = cv2.VideoCapture(0)
while (True):
    ret, frame = vid.read()
    cv2.imshow('webcam', frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    color = color_dictionary[guess(frame, color_model)]
    value = value_dictionary[guess(frame, value_model)]
    print(color, value)
    time.sleep(1)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


vid.release()
cv2.destroyAllWindows()
"""