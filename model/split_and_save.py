import cv2
from constants import *


def process_image(image_path):
    """
    Basic image processing
    :return: returns all of the contours found by OpenCV, and the processed image
    """
    image = cv2.imread(image_path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV, cv2.THRESH_OTSU)
    contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    return contours, gray


def extract_letters(contours):
    """
    Creates a list containing the coordinates of each letter in the image
    """
    letter_image_regions = []

    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        new_contour = {'x': x, 'y': y, 'w': w, 'h': h}

        # If the contour is too wide, split it in two
        if w / h > 1.20:
            half_width = int(w / 2)
            letter_image_regions.append({'x': x, 'y': y, 'w': half_width, 'h': h})
            letter_image_regions.append({'x': x + half_width, 'y': y, 'w': half_width, 'h': h})
        else:
            letter_image_regions.append(new_contour)

        # Sort by size, keep only the first CAPTCHA_LEN letters
        letter_image_regions = sorted(letter_image_regions, key=lambda x: x['w'] * x['h'], reverse=True)[:CAPTCHA_LEN]
        # Sort the detected letter images based on x coordinate to make sure each letter is matched with the right image
        letter_image_regions = sorted(letter_image_regions, key=lambda x: x['x'])

    return letter_image_regions


def save_letters(image, letters_list, captcha_text):
    """
    Saves each letter as an separate image
    """
    for n, letter_text in enumerate(captcha_text):
        x, y, w, h = letters_list[n].values()
        letter_image = image[y: y + h, x: x + w]

        # Folder path that the letter image will be saved in (A), (B), etc...
        save_path = os.path.join(OUTPUT_FOLDER, letter_text)
        # Different output folders for storing different letters, if it doesn't exist, create it
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        # Write the letter image to a file
        print('\tSaving letter: ', letter_text)
        p = os.path.join(save_path, f"{captcha_text}_{n}.jpg")
        cv2.imwrite(p, letter_image)


def main():
    # Counts how many times an image has been skipped because the amount of contours found did not match CAPTCHA_LEN
    skip_count = 0

    for image_file in ALL_CAPTCHAS:
        file_name = os.path.basename(image_file)
        print('[!]Current image file: ', file_name)

        # Captcha solution(name of that image file)
        captcha_text = file_name.split('.')[0]

        # Getting contours and the processed image
        contours, image = process_image(image_file)
        # List that holds the coordinates of the letters
        letters_list = extract_letters(contours)
        if len(letters_list) != CAPTCHA_LEN:
            skip_count += 1
            print(f'>>{skip_count}<<Found an incorrect number of letters, skipping...')
            continue

        # Saving separate letters as separate images
        save_letters(image, letters_list, captcha_text)


if __name__ == '__main__':
    main()


