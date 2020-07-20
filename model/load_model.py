from keras.models import load_model
import pickle
import cv2
import numpy as np
# Files
from constants import *
from split_and_save import process_image, extract_letters


def captcha_predict(image_file):
    """
    Loads the pre-compiled deep learing model and attempts to break the CAPTCHA
    :param image_file: CAPTCHA image
    :return: recognized CAPTCHA letters in a string format
    """
    # Load labels and model
    with open(LABELS_FILE, "rb") as f:
        lb = pickle.load(f)
    model = load_model('model.hdf5')

    print("[*] Processing image")
    contours, image = process_image(image_file)
    letters_list = extract_letters(contours)
    solution = ""

    for num, letter in enumerate(letters_list):
        x, y, w, h = letter.values()
        # Each separate letter as an image
        letter_image = image[y: y + h, x: x + w]
        letter_image = cv2.resize(letter_image, IMAGE_SHAPE)
        letter_image = np.expand_dims(letter_image, axis=2)
        letter_image = np.expand_dims(letter_image, axis=0)

        prediction = model.predict(letter_image)
        predicted = lb.inverse_transform(prediction)[0]
        solution += predicted

    return solution
