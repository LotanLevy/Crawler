from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotInteractableException
from bs4 import BeautifulSoup
import sys
import os
import time
import requests

import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)


chromedriver = 'C://Users//lotan//OneDrive//Documents//\studies//affordances\dataset_crawler//executable_files//chromedriver.exe'
keywords = ["Precision Knife", "Utility Knife", "Chef's Knife", "Trimming Knife", "Boning Knife", "Oyster Knife", "Linoleum Knife"]
search_url = lambda keyword: 'https://www.google.com/search?q=' + keyword.replace(" ", "+") + '&source=lnms&tbm=isch'
OUTPUT = 'pictures'


def get_div_child(soup, child_id):
    for child in soup.recursiveChildGenerator():
        # if child.name and child.attrs and child.attrs.get("id"):
        #     print(child.attrs.get("id"))
        if child.name == "div" and child.attrs and child.attrs.get("id") == child_id:
            return child

def build_browser(searchurl):
    """
    Build a browser object a and pointer to the page body, of the search results.
    :param searchurl: The search url
    :return: the pointer to the body and browser object
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    try:
        browser = webdriver.Chrome(chromedriver, options=options)
    except Exception as e:
        print(f'No found chromedriver in this environment.')
        print(f'Install on your machine. exception: {e}')
        sys.exit()

    browser.set_window_size(1280, 1024)
    browser.get(searchurl)
    time.sleep(1)

    print(f'Getting you a lot of images. This may take a few moments...')
    body = browser.find_element_by_tag_name('body')
    return body, browser


def download_urls(urls, path):
    """
    Download the images according to the given URL list
    :param urls: A list of the images urls
    :param path: The output path
    """
    count = 0
    if urls:
        for url in urls:
            try:
                res = requests.get(url, verify=False, stream=True)
                rawdata = res.raw.read()
                with open(os.path.join(path, 'img_' + str(count) + '.jpg'), 'wb') as f:
                    f.write(rawdata)
                    count += 1
            except Exception as e:
                print('Failed to write rawdata.')
                print(e)


def get_images(outputdir, searchurl, maximum):
    """
    The main program, execute the search by the given keyword and download all the search images,
    until the counter cross the maximum.
    :param outputdir: The path where the output should be stored
    :param searchurl: The url of the searching
    :param maximum: maximum number to be downloaded
    """
    body, browser = build_browser(searchurl)

    urls = []

    while len(urls) < maximum:
        try:
            page_source = browser.page_source
            soup = BeautifulSoup(page_source, 'lxml')

            search_result_soup = get_div_child(soup.body, "islrg")
            images = search_result_soup.find_all('img')
            urls = get_url_from_images(images)

            for i in range(50):
                scroll_down(body)
            browser.find_element_by_xpath('//*[@id="islmp"]/div/div/div/div/div[5]/input').click()
        except ElementNotInteractableException: # There is no next page
            break



    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    download_urls(urls, outputdir)
    browser.close()

def scroll_down(body):
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(0.3)

def get_url_from_images(html_images):
    """
    Collect all the images url by an html images objects
    :param html_images: a list of the html objects represents the images
    :return: The images urls
    """
    urls = []
    for image in html_images:
        try:
            url = image['data-src']
            if not url.find('https://'):
                urls.append(url)
        except:
            try:
                url = image['src']
                if not url.find('https://'):
                    urls.append(image['src'])
            except Exception as e:
                print(f'No found image sources.')
                print(e)
    return urls

get_images(os.path.join(OUTPUT, keywords[0]), search_url(keywords[0]), 500)
get_images(os.path.join(OUTPUT, keywords[1]), search_url(keywords[1]), 500)