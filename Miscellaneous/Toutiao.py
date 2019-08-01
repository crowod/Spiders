import requests
import re
import json
import os
import pymongo
from bs4 import BeautifulSoup
from hashlib import md5
from urllib.parse import urlencode
from json.decoder import JSONDecodeError
from requests.exceptions import RequestException
from config import *
from multiprocessing import Pool

client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]


def get_page_index(offset, keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': 20,
        'cur_tab': 3,
        'from': 'gallery'
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except RequestException:
        print('请求索引页出错')
        return None


def parse_page_index(html):
    try:
        data = json.loads(html)
        if data and 'data' in data.keys():
            for item in data.get('data'):
                yield item.get('article_url')
    except JSONDecodeError:
        pass


def get_page_detail(url):
    try:
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
    except RequestException:
        print('请求详情页出错', url)
        return None


def parse_page_detail(html, url):
    soup = BeautifulSoup(html, 'lxml')
    result = soup.select('title')
    title = result[0].get_text() if result else ''
    print(title)
    images_pattern = re.compile('gallery: JSON.parse\("(.*)"\)', re.S)
    result = re.search(images_pattern, html)
    if result:
        data = json.loads(result.group(1).replace('\\', ''))
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url') for item in sub_images]
            for image in images:
                download_image(image)
            return {
                'title': title,
                'url': url,
                'images': images
            }


def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('Save successfully', result)
        return True
    return False


def download_image(url):
    print('正在下载', url)
    try:
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            save_image(response.content)
    except RequestException:
        print('请求图片出错', url)
        return None


def save_image(content):
    file_path = '{0}/{1}.{2}'.format('yurisa',
                                     md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()


def main():
    for offset in range(GROUP_START, GROUP_END):
        html = get_page_index(offset, KEYWORD)
        for url in parse_page_index(html):
            html = get_page_detail(url)
            if html:
                result = parse_page_detail(html, url)
                if result:
                    save_to_mongo(result)


if __name__ == '__main__':
    main()
