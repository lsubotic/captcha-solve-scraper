from multiprocessing.pool import ThreadPool
from bs4 import BeautifulSoup
from colorama import Fore
from pprint import pprint
import pandas as pd
import requests
import random
import pickle
import time
import csv
import sys
import os


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
            if proxy in all_proxies:
                all_proxies.remove(proxy)
            return get_source(url)

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


def find_subcategories_links():
    """
    Extract subcategories links
    """
    url = 'https://www.amazon.co.uk/Best-Sellers-Computers-Accessories-Components-Replacement-Parts/zgbs/computers/428655031/ref=zg_bs_unv_computers_2_430500031_1'
    soup = get_source(url)

    try:
        links = soup.select_one('#zg_browseRoot span.zg_selected').find_parent('li').find_next_sibling('ul').find_all('a')
        links = {link.get('href') for link in links}
    except:
        print(Fore.RED + 'Unable to find subcategories links' + Fore.RESET)
        links = set()

    return links


def extract_asins(link):
    """
    Listing the pages and extracting asins
    """
    soup = get_source(link)
    print(link)
    while True:
        try:
            asins = {asin.get('href').split('/dp/')[-1].split('/')[0] for asin in soup.select('#zg-ordered-list > li a[href*="/dp/"]')}
            for asin in asins:
                csv_writer.writerow([asin])  # save asins
        except:
            print(Fore.RED + 'Product has no asin ' + Fore.RESET)

        next_page = soup.select_one('ul.a-pagination li.a-last > a')
        if next_page:
            next_page = next_page.get('href')
            soup = get_source(next_page)
        else:
            break


def thread_worker():
    """
    Using threadpool to extract product asins
    """
    links = find_subcategories_links()
    if links:
        ThreadPool(processes=len(links)).map(extract_asins, links)


def save_asins():
    """
    Saving the asins to an .csv file
    """
    print('Scraping subcategories')

    global all_proxies, proxies_cookies
    all_proxies = list(pd.read_csv('http_proxies.txt', header=None, names=['Proxy'])['Proxy'].unique())

    proxies_cookies = {}

    # Cookies file
    if os.path.exists('cookies.pkl'):
        proxies_cookies = pickle.load(open('cookies.pkl', 'rb'))  # Load the dictionary back from the pickle file.

    file_name = 'asins.csv'
    with open(file_name, 'w', newline='', errors='ignore', encoding='utf-8') as f:
        global csv_writer
        csv_writer = csv.writer(f)
        csv_writer.writerow(['asin'])

        thread_worker()

        # Saving the cookies
        pickle.dump(proxies_cookies, open('cookies.pkl', 'wb'))
