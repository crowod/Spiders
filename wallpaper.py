from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from requests.exceptions import MissingSchema
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from hashlib import md5
from multiprocessing import pool
import io
import requests
import time
import os
import re

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)


def is_element_exist(css):
    try:
        browser.find_element_by_css_selector(css)
        return True
    except:
        return False


def search(Keyword):
    try:
        browser.get('https://wall.alphacoders.com/?lang=Chinese')
        input = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#search_zone_index > input.search-bar.form-control.input-lg'))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#search_zone_index > span > button')))
        input.send_keys(Keyword)
        submit.click()
        if is_element_exist('#container_page > div:nth-child(8) > div.hidden-xs.hidden-sm > div > div > input'):
            total = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#container_page > div:nth-child(8) > div.hidden-xs.hidden-sm > ul > li:nth-child(13) > a')))
        total = browser.find_elements_by_css_selector('.pagination li')
        return total[-2].text
    except TimeoutException:
        return search(Keyword)


def next_page(title):
    try:
        while is_element_exist('#next_page'):
            next = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, '#next_page')))
            html = browser.page_source
            soup = BeautifulSoup(html, 'lxml')
            items = soup.select('.center .boxgrid img')
            mystrip = re.compile('thumb-\d+?-')
            for item in items:
                src = item.get('src')
                url = re.sub(mystrip, '', src)
                download_image(url, title)
            next.click()
    except TimeoutException:
        next_page(page_number)


def download_image(url, title):
    print('正在下载', url)
    try:
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            save_image(response.content, title)
    except RequestException:
        print('请求图片出错', url)
        return None


def save_image(content, title):
    if not os.path.exists(title):
        os.makedirs(title)
    file_path = '{0}/{1}.{2}'.format(title,
                                     md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()


def task_canceller(t):
    print('in task_canceller')
    t.cancel()
    print('canceled the task')


def main():
    keyword = '命运石之门'
    search(keyword)
    next_page(keyword)


if __name__ == '__main__':
    main()
