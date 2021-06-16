from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementNotInteractableException
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import sys
import os
import time
import requests
import ast

import json
from pprint import pprint

import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)


chromedriver = 'C:\\Users\\lotan\\Documents\\studies\\phoenix\\affordances\\Crawler\\executable_files\\chromedriver.exe'
keywords = {"lamp":["lamp"]}
search_url = lambda keyword: 'https://www.google.com/search?q=' + keyword.replace(" ", "+") + '&source=lnms&tbm=isch'
OUTPUT = 'C:\\Users\\lotan\\Documents\\studies\\phoenix\\ballpark_datasets\\ballpark_datasets\\new\\flowerpot\\test'
MAX_EXAMPLES_FOR_CLASS = 500
JSON_FILE = "urls.json"


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
        browser = webdriver.Chrome(ChromeDriverManager().install())
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


def get_images(outputdir, parent_key, key, searchurl, maximum, json_path):
    """
    The main program, execute the search by the given keyword and download all the search images,
    until the counter cross the maximum.
    :param parent_key:
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
            print(urls)

            for i in range(50):
                scroll_down(body)
            # browser.find_element_by_xpath('//*[@id="islmp"]/div/div/div/div')
            browser.find_element_by_class_name("mye4qd").click()
            print(len(urls) < maximum)
        except ElementNotInteractableException as e: # There is no next page
            print(e)
            break



    if not os.path.exists(outputdir):
        os.makedirs(outputdir)

    write_urls(json_path, parent_key, key, urls)

    # download_urls(urls, outputdir)
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
            if not url.find("https://"):
                urls.append(url)
        except:
            try:
                url = image['src']
                if not url.find("https://"):
                    urls.append(image['src'])
            except Exception as e:
                print(f'No found image sources.')
                print(e)
    return urls

def write_urls(path, parent_type, type, urls):
    string_list = (",".join(urls))
    data = dict()
    if os.path.isfile(path):
        with open(path, 'r') as fp:
            data = json.load(fp)
            data = ast.literal_eval(data)
    if parent_type not in data:
        data[parent_type] = dict()
    data[parent_type][type] = string_list
    with open(path, 'w') as fp:
        json.dump(str(data), fp)


def download_from_file(file_path, outputdir):
    if os.path.isfile(file_path):
        with open(file_path, 'r') as fp:
            data = json.load(fp)
            data = ast.literal_eval(data)

    for key in keywords:
        for sub_key in keywords[key]:
            path = os.path.join(os.path.join(outputdir, key), sub_key)
            if not os.path.exists(path):
                os.makedirs(path)
            urls = data[key][sub_key]

            urls = urls.split(",")
            download_urls(urls, path)

for key in keywords:
    for sub_key in keywords[key]:
        path = os.path.join(os.path.join(OUTPUT, key),sub_key)
        get_images(path, key, sub_key, search_url(sub_key), MAX_EXAMPLES_FOR_CLASS, JSON_FILE)

download_from_file(JSON_FILE, OUTPUT)
