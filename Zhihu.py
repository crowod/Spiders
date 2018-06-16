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
import requests
import time
import os
import re

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)


def get_page():
    try:
        browser.get('https://www.zhihu.com/question/28853910')
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#QuestionAnswers-answers > div > div > div.List-header')))
        for i in range(1, 300):
            js = "var q=document.documentElement.scrollTop=" + str(i * 10000)
            browser.execute_script(js)
        html = browser.page_source
        soup = BeautifulSoup(html, 'lxml')
        items = soup.select('figure img')
        result = soup.select('title')
        title = result[0].get_text().strip()[:-5]
        content = ''
        for item in items:
            download_image(item.get('src'), title)
    except TimeoutError:
        get_page()


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


def main():
    get_page()


if __name__ == '__main__':
    main()
