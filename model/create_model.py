from sklearn.preprocessing import LabelBinarizer
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.layers import Dense, Dropout
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

# Normalize the data so every value lies between zero and one and convert to numpy array
data = np.array(data, dtype='float') / 255
labels = np.array(labels)

# Binarize the labels
lb = LabelBinarizer().fit(labels)
# Save the binarization
with open(LABELS_FILE, 'wb') as f:
    pickle.dump(lb, f)

# Convert labels to float an shuffle data and labels in the same way
# No train_test_split - validating with k-fold cross validation
labels = lb.transform(labels).astype('float32')
labels = shuffle(labels, random_state=0)
data = shuffle(data, random_state=0)

# Creating the model
def build_model():
    model = keras.Sequential()
    model.add(Conv2D(20, (5, 5), padding="same", input_shape=(IMAGE_SHAPE[0], IMAGE_SHAPE[1], 1), activation="relu"))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

    model.add(Conv2D(40, (5, 5), padding="same", activation="tanh"))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))
    
    model.add(Conv2D(64, (5, 5), padding="same", activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

    model.add(keras.layers.Flatten())
    
    model.add(Dense(128, activation="tanh"))
    model.add(Dropout(0.5))

    model.add(Dense(128, activation="tanh"))
    model.add(Dropout(0.3))

    model.add(Dense(nr_labels, activation="softmax"))

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


model = build_model()
model.fit(data, labels, batch_size=8, epochs=6, verbose=1)

model.save(MODEL_FILE)
