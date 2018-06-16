from requests.exceptions import MissingSchema
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, Timeout
from hashlib import md5
from urllib.parse import urlencode
from json import JSONDecodeError
from aiohttp.web import HTTPException
from asyncio import TimeoutError, CancelledError
import json
import asyncio
import aiohttp
import io
import requests
import time
import os
import re

requests.adapters.DEFAULT_RETRIES = 10
keyword = '命运石之门'
headers = {
    'User-Agent': 'User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.183 Safari/537.36 Vivaldi/1.96.1147.42',
    'Cookie': 'PHPSESSID=vsegtf80gno7fnuqiqc9kumlv4; z_theme=1; cookienotice=1; __gads=ID=208931876480f94f:T=1528418469:S=ALNI_Mai-0DIRDEM-vEZdUF9CjteXa2YUw; __utmc=7894585; OX_plg=pm; __qca=P0-1979948242-1528420466283; __utmz=7894585.1528461592.5.4.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmt=1; __utma=7894585.252750239.1528418459.1528508180.1528519112.9; z_id=1360179; z_hash=a42fb5a95a454bb6e968af0352a6228a; __utmb=7894585.8.10.1528519115'
}


def get_page_index(offset):
    url = 'https://www.zerochan.net/Steins%3BGate?d=0&t=0&s=fav' + \
        '&p=' + str(offset)
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return response.text
        else:
            print('状态码异常', offset)
            return get_page_index(offset)
    except RecursionError or Timeout:
        print('出现异常', offset)
        return get_page_index(offset)

# thumbs2 > li:nth-child(10) > p > a:nth-child(2) > img


def parse_page_index(html):
    soup = BeautifulSoup(html, 'lxml')
    items = soup.select('#thumbs2 li > a > img')
    for item in items:
        url = item.get('src')
        url = url.replace('//s3.', '//static.')
        url = url.replace('.240.', '.full.')
        download_image(url)


def download_image(url):
    if not os.path.exists(keyword):
        os.makedirs(keyword)
    print('正在下载', url)
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            save_image(response.content)
        else:
            print('状态码异常', url)
            if '.png' in url:
                return None
            else:
                url = url.replace('.jpg', '.png')
                download_image(url)
        # async with aiohttp.ClientSession() as session:
        #     async with session.get(url, timeout=10) as response:
        #         if response.status == 200:
        #             content = response.read()
        #              save_image(content)
        #         else:
        #              download_image(url)
    except RequestException or Timeout:
        print('出现异常', url)
        download_image(url)


def save_image(content):
    file_path = '{0}/{1}.{2}'.format(keyword,
                                     md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()


def main():
    for offset in range(86, 88):
        print(offset)
        html = get_page_index(offset)
        parse_page_index(html)


if __name__ == '__main__':
    # groups = [x for x in range(1, 91)]
    # pool = Pool()
    # pool.map(main, groups)
    # pool.close()
    # pool.join()
    main()
