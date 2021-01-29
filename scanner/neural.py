from configuration import color_dataset_path, color_model_path, image_width, image_height, color_scale

import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf


physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

data = np.load(color_dataset_path, allow_pickle=True)
middle = 48000
train = data[:middle]
test = data[middle:]
train_X = []
train_y = []
for x in train:
    train_X.append(x[0])
    train_y.append(x[1])
test_X = []
test_y = []
for x in test:
    test_X.append(x[0])
    test_y.append(x[1])
train_X = np.array(train_X)
train_Y = np.array(train_y)
test_X = np.array(test_X)
test_Y = np.array(test_y)


tf.keras.backend.clear_session()
np.random.seed(7)
tf.random.set_seed(7)

epochs=40
batch_size=32

model = tf.keras.models.Sequential([
        tf.keras.layers.Conv2D(filters=8,kernel_size=(2, 2), activation='relu', input_shape=(train_X.shape[1], train_X.shape[2], train_X.shape[3])),
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2), strides=1),
        tf.keras.layers.Conv2D(filters=16, kernel_size=(3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2), strides=1),
        tf.keras.layers.Conv2D(filters=8, kernel_size=(3, 3), activation='relu'),
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2), strides=1),
        tf.keras.layers.Conv2D(filters=8, kernel_size=(4, 4), activation='softmax'),
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2), strides=1),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(8),
        tf.keras.layers.Dense(8),
        tf.keras.layers.Dense(4, activation='softmax')
])

model.summary()
cp = tf.keras.callbacks.ModelCheckpoint(filepath="models/checkpoint.h5", save_best_only=True, verbose=0)
model.compile(loss = 'sparse_categorical_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

with tf.device('/GPU:0'):
    history = model.fit(train_X, train_Y, epochs=epochs, batch_size=batch_size, validation_data=(test_X, test_Y),callbacks=[cp]).history

model.save(color_model_path)





acc = history['accuracy']
val_acc = history['val_accuracy']
loss = history['loss']
val_loss = history['val_loss']
epochs = range(len(acc))
plt.plot(epochs, acc, 'r', label='Training accuracy')
plt.plot(epochs, val_acc, 'b', label='Validation accuracy')
plt.title('ACCURANCY')
plt.legend(loc=0)
plt.show()