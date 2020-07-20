from glob import glob
import os


"""
Constants
"""
CAPTCHA_LEN = 6  # number of letters in CAPTCHA
OUTPUT_FOLDER = 'letter_images'
LETTERS_FOLDER = 'letter_images'

ALL_CAPTCHAS = glob(os.path.join('captcha_images', "*"))

IMAGE_SHAPE = (50, 50)  # Image shape that the model uses

MODEL_FILE = 'model.hdf5'
LABELS_FILE = 'labels.dat'



