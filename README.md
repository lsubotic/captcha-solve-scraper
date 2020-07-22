# captcha-solve-scraper
## Whats it about?
Creating a Deep Learning model, to be implemented with a large scale Web Scraper, that will be able to consistently break CAPTCHA robot checks that shows up while scraping.

## Overview
### The Model:
The process of getting the model ready to come up with CAPTCHA solutions comes in different parts... <br/>
* Firstly, an image data set is needed to train the model on. The images in *captcha_images* folder are some of the images that I obtained and saved through my experience of scraping Amazon. <br/>
* After getting the images, some processing an cutting needs to be done so the model can learn each letter separately. This was done using [OpenCV2](https://pypi.org/project/opencv-python/) in the *'split_and_save.py'* module, which after executing will create a folder for each letter separately that contains all of the instances of that letter in different CAPTCHAS. (*Note that OpenCV may not split the letters right, so that image will be excluded*)
* Creating the model using Deep Convolutional Neural Networks with [Keras](https://keras.io/), is next, where previously created letter images are now used for training.
* After the model has been compiled, it will be saved as **model.hdf5** and it's labels as **labels.dat**(names can be changed in *'constants.py'*) and now can be loaded into the Web Scraper using the *'load_model'* module

