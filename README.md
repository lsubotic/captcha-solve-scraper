# captcha-solve-scraper
## Whats it about?
Creating a Deep Learning model, to be implemented with a large scale Web Scraper, that will be able to consistently break CAPTCHA robot checks that shows up while scraping.

## How to use?
First, to make sure you have all of the required modules installed, get them from the supplied *requirements.txt* using the following command:
```bash
$ pip install -r requirements.txt
```
After that, you should be all set up to run the scripts - for detailed information, see below.
#### - Getting the model ready
First, use ``` $ python split_and_save.py``` to split the images into letters that the model will use as input data. Then ``` $ python create_model.py``` to train and save the model. From then on, the model will be loaded in to the Scraper to solve the CAPTCHA with the **load_model.py** module.


## Overview
### The Model:
The process of getting the model ready to come up with CAPTCHA solutions comes in few parts... <br/>
* Firstly, an image data set is needed to train the model on. The images in *captcha_images* folder are some of the images that I obtained and saved through my experience of scraping Amazon. <br/>
* After getting the images, some processing an cutting needs to be done so the model can learn each letter separately. This was done using [OpenCV2](https://pypi.org/project/opencv-python/) in the *'split_and_save.py'* module, which after executing will create a folder for each letter separately that contains all of the instances of that letter in different CAPTCHAS. (*Note that OpenCV may not split the letters right, so that image will be excluded*)
* Creating the model using Deep Convolutional Neural Networks with [Keras](https://keras.io/), is next, where previously created letter images are now used for training.
* After the model has been compiled, it will be saved as **model.hdf5** and it's labels as **labels.dat**(names can be changed in *'constants.py'*) and now can be loaded into the Web Scraper using the *'load_model.py'* module

