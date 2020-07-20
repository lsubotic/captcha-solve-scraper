from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.layers import Dense
import tensorflow as tf
import keras
import numpy as np
import pickle
import cv2
import os

# constants
from constants import *


data = []
labels = []
nr_labels = len(os.listdir(LETTERS_FOLDER))

for label in os.listdir(LETTERS_FOLDER):
    for image_file in glob(os.path.join(LETTERS_FOLDER, label, '*.jpg')):
        image = cv2.imread(image_file)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Resize the image so all images have the same input shape
        image = cv2.resize(image, IMAGE_SHAPE)
        # Expand dimensions for Keras
        image = np.expand_dims(image, axis=2)
        data.append(image)
        labels.append(label)

# Normalize the data so every value lies between zero and one
data = np.array(data, dtype='float') / 255
labels = np.array(labels)

# Create a training-test split
(X_train, X_test, Y_train, Y_test) = train_test_split(data, labels, test_size=0.25, random_state=0)
# Binarize the labels
lb = LabelBinarizer().fit(Y_train)
Y_train = lb.transform(Y_train)
Y_test = lb.transform(Y_test)

# Save the binarization
with open(LABELS_FILE, 'wb') as f:
    pickle.dump(lb, f)

# Constructing the model
model = keras.Sequential()
model.add(Conv2D(20, (5, 5), padding="same", input_shape=(IMAGE_SHAPE[0], IMAGE_SHAPE[1], 1), activation="relu"))
model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

model.add(Conv2D(50, (5, 5), padding="same", activation="relu"))
model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

model.add(keras.layers.Flatten())
model.add(Dense(256, activation="relu"))
model.add(Dense(32, activation='relu'))
model.add(Dense(nr_labels, activation="softmax"))

model.compile(loss=keras.losses.BinaryCrossentropy(), optimizer='adam', metrics=['accuracy'])

model.fit(X_train, Y_train, validation_data=(X_test, Y_test), batch_size=16, epochs=7, verbose=1)

model.save(MODEL_FILE)




