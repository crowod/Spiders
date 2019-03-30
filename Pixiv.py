import re
import os
import requests
import time
import pymongo
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup

MONGO_URL = 'localhost'
MONGO_DB = 'Pixiv'
COLLECTION_NAME = ''

KEYWORD = ''
USERNAME = ''
PASSWORD = ''

client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]
collection = db[COLLECTION_NAME]

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--disable-gpu')
# chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)

page_pattern = re.compile(u'href=\"(.*?)\" rel', re.S)
image_pattern = re.compile(u'background-image: url\(\"(.*?)\"\);')
file_pattern = re.compile(u'/(\d{2}/){5}(.*?_p.*?)\.')


def is_element_exist(css):
    flag = True
    try:
        driver.find_element_by_css_selector(css)
        return flag
    except:
        flag = False
        return flag


def search_and_login(keyword):
    url = 'https://www.pixiv.net/search.php?word=' + \
          keyword + '&order=date_d'
    try:
        driver.get(url)
        login = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR,
                 'body > div.newindex.newindex-gdpr > div > section > div.newindex-signup > div > a.ui-button._login')))
        login.click()
        input_username = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 '#LoginComponent > form > div.input-field-group > div:nth-child(1) > input[type="text"]')
            )
        )
        input_password = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 '#LoginComponent > form > div.input-field-group > div:nth-child(2) > input[type="password"]')
            )
        )
        submit = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '#LoginComponent > form > button')
            )
        )
        input_username.send_keys(USERNAME)
        input_password.send_keys(PASSWORD)
        submit.click()
    except TimeoutException:
        return search_and_login(keyword)


def next_page():
    while True:
        results = []
        for i in range(1, 20):
            js = "var q=document.documentElement.scrollTop=" + str(i * 200)
            driver.execute_script(js)
            time.sleep(1)
        if is_last_page() is False:
            next = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '#wrapper > div.layout-body > div > nav > div > span.next > a')))
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        items = soup.select('#js-react-search-mid > div > div')
        for item in items:
            if item.decode().find('_premium-lead-popular-d-body') > 0:
                continue
            if item.select('div > span'):
                results_ = manga_page_result(item)
                for result in results_:
                    save_to_mongodb(result)
                    download_image(result)
                    results.append(result)
            else:
                result = normal_page_result(item)
                save_to_mongodb(result)
                download_image(result)
                results.append(result)
        if is_last_page() is False:
            next.click()
        else:
            break


def manga_page_result(item):
    results_ = []
    target = item.select('a')[0].decode()
    page_url = re.findall(page_pattern, target)
    page_url = page_url[0].replace('amp;', '')
    page_url = page_url.replace('mode=medium', 'mode=manga')
    page_url = 'https://www.pixiv.net' + page_url
    data_user_name = item.select('a')[3]['data-user_name']
    data_user_id = item.select('a')[3]['data-user_id']
    title = item.select('a')[2]['title']
    bookmarks = item.select('a')[4]['data-tooltip']
    response = requests.get(page_url)
    if response.status_code is 200:
        soup = BeautifulSoup(response.text, 'lxml')
        imgs = soup.select('.item-container img')
        for img in imgs:
            img_url = transform_to_original(img['data-src'])
            x = re.search(file_pattern, img_url)
            img_id = x.group(2)
            result = {
                'title': title,
                'data_user_name': data_user_name,
                'data_user_id': data_user_id,
                'img_id': img_id,
                'img_url': img_url,
                'page_url': page_url,
                'bookmarks': bookmarks,
            }
            results_.append(result)
        return results_
    else:
        return None


def normal_page_result(item):
    target = item.select('a')[0].decode()
    page_url = re.findall(page_pattern, target)
    page_url = page_url[0].replace('amp;', '')
    page_url = 'https://www.pixiv.net' + page_url
    img_src = re.findall(image_pattern, target)
    img_orig_src = transform_to_original(img_src[0])
    data_user_name = item.select('a')[3]['data-user_name']
    data_user_id = item.select('a')[3]['data-user_id']
    title = item.select('a')[2]['title']
    img_id = re.search(file_pattern, img_orig_src).group(2)
    bookmarks = item.select('a')[4]['data-tooltip']
    result = {
        'title': title,
        'data_user_name': data_user_name,
        'data_user_id': data_user_id,
        'img_id': img_id,
        'img_url': img_orig_src,
        'page_url': page_url,
        'bookmarks': bookmarks,
    }
    return result


def is_last_page():
    if (is_element_exist('#wrapper > div.layout-body > div > nav > div > span.next > a') is False and is_element_exist(
            '#wrapper > div.layout-body > div > nav > div > span.prev > a')) or \
            (is_element_exist(
                '#wrapper > div.layout-body > div > nav > div > span.next > a') is False and is_element_exist(
                '#wrapper > div.layout-body > div > nav > div > span.prev > a') is False):
        return True
    else:
        return False


def save_to_mongodb(item):
    try:
        if collection.update({'img_id': item['img_id']}, {'$set': dict(item)}, True):
            print('Save mongodb successful')
            return True
        else:
            return False
    except DeprecationWarning:
        return


def download_image(item):
    try:
        headers = {
            'dnt': '1',
            'upgrade-insecure-requests': '1',
            'referer': item['page_url'],
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/69.0.3497.102 Safari/537.36 Vivaldi/2.0.1309.29 '
        }
        url = item['img_url']
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            save_image(response.content, item, url[-3:], url)
        else:
            dot = url.rfind('.')
            if url[dot + 1:] == 'jpg':
                url = url.replace('jpg', 'png')
            elif url[dot + 1:] == 'png':
                url = url.replace('png', 'jpg')
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                save_image(response.content, item, url[-3:], url)
            else:
                return
    except ConnectionError as e:
        print(e.strerror)
    except requests.exceptions.ProxyError:
        time.sleep(2)
        download_image(item)


def save_image(content, item, suffix, url):
    symbols = ['\\', '/', ':', '*', '?', '\"', '<', '>', '|']
    if not os.path.exists('Pixiv'):
        os.makedirs('Pixiv')
    search_file_name = 'Pixiv/' + KEYWORD
    if not os.path.exists(search_file_name):
        os.makedirs(search_file_name)
    data_user_name = item['data_user_name']
    for symbol in symbols:
        if symbol in data_user_name:
            data_user_name = data_user_name.replace(symbol, '')
    dir_path = search_file_name + '/' + data_user_name + '-' + item['data_user_id']

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_path = '{0}/{1}_{2}.{3}'.format(dir_path, item['img_id'], item['bookmarks'], suffix)
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            print('{1}: {2}', item['title'], url)
            f.write(content)
            f.close()


def transform_to_original(img_src):
    start = img_src.find('img/')
    end = img_src.find('_master1200')
    dot = img_src[:].rfind('.')
    img_orig_src = 'https://i.pximg.net/img-original/' + img_src[start:end] + img_src[dot:]
    return img_orig_src


def main():
    search_and_login(KEYWORD)
    next_page()


if __name__ == '__main__':
    main()
