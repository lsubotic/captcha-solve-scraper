from threading import Thread
from pprint import pprint
import pandas as pd
import threading
import random
import pickle
import time
import sys
import csv
import re
import os

from bs4 import BeautifulSoup
import requests

from save_data import *
from model.load_model import captcha_predict


def get_source(url, proxy=None, cookies=None):
    headers = {
        'authority': 'www.amazon.co.uk',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-US,en;q=0.9,sr;q=0.8,hy;q=0.7,bs;q=0.6',
    }

    if not proxy:
        proxy = random.choice(all_proxies)

    proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}

    if not cookies:
        cookies = proxies_cookies[proxy] if proxy in proxies_cookies else {}

    try:
        r = requests.get(url, headers=headers, proxies=proxies, cookies=cookies, timeout=10)

        cookies = r.cookies.get_dict()
        proxies_cookies.setdefault(proxy, {}).update(cookies)

        status_code = r.status_code

        if status_code == 404:
            return None

        if status_code == 503:
            if proxy in all_proxies:
                all_proxies.remove(proxy)
            return get_source(url)

        soup = BeautifulSoup(r.text, 'lxml')
        title = soup.title.text.strip()
        if 'Robot Check' in title:
            print('Solving Captcha...', soup.select_one('img[src*="/captcha/"]').get('src'))

            get_image_source(soup=soup, cookies=cookies, proxies=proxies, headers=headers, url=url)
            return None

        if status_code == 200 and 'Robot Check' not in title:
            return soup
        else:
            print('Problem ----', status_code)
            print('Title: ', title)
            return None
    except Exception as e:
        if proxy in all_proxies:
            all_proxies.remove(proxy)
        return get_source(url)


def get_image_source(soup, cookies, headers, proxies, url):
    # - Solving captcha
    try:
        captcha_image = soup.select_one('img[src*="/captcha/"]').get('src')
        amzn = soup.select_one('[name="amzn"]').get('value')
        amzn_r = soup.select_one('[name="amzn-r"]').get('value')
    except:
        return None

    # Does 3 attempts to get the CAPTCHA image
    for _ in range(3):
        try:
            img_content = requests.get(captcha_image, headers=headers, cookies=cookies, proxies=proxies, timeout=10, stream=True).content
            # Import the function to solve the CAPTCHA
            captcha_keywords = captcha_predict(img_content)
            print('IMG url: ', captcha_image)
            print('Predicted value: ', captcha_keywords)
            break
        except:
            pass
    else:
        return None

    for _ in range(3):
        # Sending an request to solve the CAPTCHA, max 3 attempts.
        data = validate_captcha(cookies=cookies, referer=url, captcha_keywords=captcha_keywords, proxies=proxies, amzn=amzn, amzn_r=amzn_r, img_content=img_content)
        if not data:
            continue

        if data == 1:
            break

        if str(type(data)) == "<class 'bs4.BeautifulSoup'>":
            try:
                captcha_image = data.select_one('img[src*="/captcha/"]').get('src')
                amzn = data.select_one('[name="amzn"]').get('value')
                amzn_r = data.select_one('[name="amzn-r"]').get('value')
            except:
                continue

            # Passing throgh the CAPTCHA image again in case the model fails to solve it
            # Attempts 3 times
            for _ in range(3):
                try:
                    img_content = requests.get(captcha_image, headers=headers, cookies=cookies, proxies=proxies, timeout=10, stream=True).content
                    # Import the function to solve the CAPTCHA
                    captcha_keywords = captcha_predict(img_content)
                    print('Predicted value: ', captcha_keywords)
                    break
                except:
                    pass
            else:
                return None


def validate_captcha(cookies, referer, captcha_keywords, proxies, amzn, amzn_r, img_content):
    headers = {
        'authority': 'www.amazon.co.uk',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': referer,
        'accept-language': 'en-US,en;q=0.9',
    }

    params = (
        ('amzn', amzn),
        ('amzn-r', amzn_r),
        ('field-keywords', captcha_keywords),
    )

    url = 'https://www.amazon.co.uk/errors/validateCaptcha'

    try:
        r = requests.get(url, headers=headers, params=params, cookies=cookies, proxies=proxies, timeout=13)

        cookies = r.cookies.get_dict()
        proxies_cookies.setdefault(proxies["http"].split("//")[-1], {}).update(cookies)

        soup = BeautifulSoup(r.text, 'lxml')
        title = soup.title.text.strip()
        status_code = r.status_code

        if status_code == 503:
            return None
        if status_code == 404:
            return None

        if 'Robot Check' not in title and status_code == 200:
            extract_products_info(asin=referer.split('/dp/')[-1], soup=BeautifulSoup(r.text, 'lxml'))
            # Saving the image
            with open(f'predict_correct/{captcha_keywords}.jpg', 'wb') as f:
                f.write(img_content)
            return 1
        elif 'Robot Check' in title:
            print('CAPTCHA solve failed: ', soup.select_one('img[src*="/captcha/"]').get('src'))
            # Saving the image
            with open(f'predict_wrong/{captcha_keywords}.jpg', 'wb') as f:
                f.write(img_content)
            return soup
        else:
            print('STATUS CODE: ', status_code)
            return None
    except Exception as e:
        return None


def extract_products_info(asin, soup=None):
    if not soup:
        url = f'https://www.amazon.co.uk/dp/{asin}'
        soup = get_source(url)
        if not soup:
            return None

    # Product title
    try:
        title = soup.select_one('#productTitle').get_text(strip=True)
    except:
        print('[!] Product title not found')
        return None

    # Price
    price = ''
    css_price = ['#price_inside_buybox', '#priceblock_ourprice', '#unqualified-buybox-olp span.a-color-price',
                 '#olp-upd-new span.a-color-price']
    for css_p in css_price:
        price = soup.select_one(css_p)
        if price:
            if 'data-asin-price' in str(price):
                price = price.get('data-asin-price')
                break
            else:
                price = price.get_text(strip=True)
                break

    # Availability
    availability = soup.select_one('#availability')
    availability = availability.get_text(strip=True) if availability else ''

    # Product Summary
    product_summary = ''
    product_summaries = soup.select('#feature-bullets ul > li')
    if product_summaries:
        for summary in product_summaries:
            product_summary += f'{summary.get_text(strip=True)}\n'

    # Item Weight
    item_weight = soup.find('td', text=re.compile(r'Item Weight'))
    item_weight = item_weight.find_next_sibling('td').get_text(strip=True) if item_weight else ''

    # Product Dimensions
    product_dimensions = soup.find('td', text=re.compile(r'Product Dimensions'))
    product_dimensions = product_dimensions.find_next_sibling('td').get_text(strip=True) if product_dimensions else ''

    # Shipping Weight
    shipping_weight = soup.find('td', text=re.compile(r'Shipping Weight'))
    shipping_weight = shipping_weight.find_next_sibling('td').get_text(strip=True) if shipping_weight else ''

    # Customer Reviews
    customer_reviews = soup.select_one('#acrPopover')
    customer_reviews = customer_reviews.get_text(strip=True) if customer_reviews else ''

    # Customer Ratings
    customer_ratings = soup.select_one('div[data-hook="total-review-count"]')
    customer_ratings = customer_ratings.get_text(strip=True) if customer_ratings else ''

    # Pictures
    pictures = re.findall(r'"large":"(.+?)",', str(soup))
    pictures = ', '.join(pictures) if pictures else ''

    # Brand
    brand = soup.select_one('#bylineInfo')
    brand = brand.get_text(strip=True) if brand else ''

    # Technical Details
    technical_details = str(soup.select_one('#productDetails_techSpec_section_1'))
    if not technical_details:
        technical_details = ''

    # Product specifications
    product_specifications = str(soup.select_one('#technicalSpecifications_section_1'))
    if not product_specifications:
        product_specifications = ''

    # Save to SQL database
    product = Products(asin=asin, product_title=title, product_summary=product_summary, technical_details=technical_details,
                       product_specifications=product_specifications, brand=brand, item_weight=item_weight,
                       product_dimensions=product_dimensions, shipping_weight=shipping_weight, customer_reviews=customer_reviews,
                       customer_ratings=customer_ratings, pictures=pictures, price=price, availability=availability)

    session.add(product) 
    session.commit()

    global products_counter
    products_counter += 1
    print(f'{products_counter}. {asin}')
    print(80*'=')


def save_products_info():
    global proxies_cookies, products_counter, all_proxies
    products_counter = 0
    proxies_cookies = {}

    # File sa kolacicima
    if os.path.exists('cookies.pkl'):
        proxies_cookies = pickle.load(open('cookies.pkl', 'rb'))  # Load the dictionary from the pickle file.

    all_proxies = list(pd.read_csv('http_proxies.txt', header=None, names=['Proxy'])['Proxy'].unique())
    print('Total proxies: ', len(all_proxies))

    if not os.path.exists('predict_correct'):
        os.makedirs('predict_correct')

    if not os.path.exists('predict_wrong'):
        os.makedirs('predict_wrong')

    # Gruva MultiThreading
    threads = []
    asins = set(pd.read_csv('asins.csv')['asin'])
    for asin in asins:
        t = Thread(target=extract_products_info, args=[asin])
        t.start()
        threads.append(t)

        if threading.active_count() > 25:
            while True:
                if threading.active_count() < 20:
                    break
                time.sleep(1)

    for thread in threads:
        thread.join()

    # Saving proxies' cookies
    pickle.dump(proxies_cookies, open('cookies.pkl', 'wb'))



