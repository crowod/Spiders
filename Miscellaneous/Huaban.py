from requests.exceptions import MissingSchema
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from hashlib import md5
from urllib.parse import urlencode
from multiprocessing import Pool
from json import JSONDecodeError
import json
import io
import requests
import time
import os
import re

keyword = '命运石之门'
headers = {
    'Cookie': r'_f=iVBORw0KGgoAAAANSUhEUgAAADIAAAAUCAYAAADPym6aAAABJElEQVRYR%2B1VOxYCIQwMF7KzsvFGXmW9kY2VnQfxCvgCRmfzCD9lnz53myWQAJOZBEfeeyIi7xz%2FyEXzZRPFhYbPc3hHXO6I6TbFixmfEyByeQQSxu6BcAXSkIGMazMjuBcz8pQcq44o0Iuyyc1p38C62kNsOdeSZDOQlLRQ80uOMalDgWCGMfsW2B5%2FATMUyGh2uhgptV9Ly6l5nNOa1%2F6zmjTqkH2aGEk2jY72%2B5k%2BNd9lBfLMh8GIP11iK95vw8uv7RQr4oNxOfbQ%2F7g5Z4meveyt0uKDEIiMLRC4jrG1%2FjkwKxCRE2e5lF30leyXYvQ628MZKV3q64HUFvnPAMkVuSWlEouLSiuV6dp2WtPBrPZ7uO5I18tbXWvEC27t%2BTcv%2Bx0JuJAoUm2L%2FQAAAABJRU5ErkJggg%3D%3D%2CWin32.1536.864.24; __auc=99d387a0163db150028981fd5bc; sid=NXk0k9zcr3Zo6V9l67sQqUiNyQm.23dDxT5V7NMo4trIgALjuaG%2FV0iPG72iN6Gkctq%2BoTg; _ga=GA1.2.687228621.1528387343; __gads=ID=826d53c5a14b803a:T=1528387353:S=ALNI_Mar_h8nNkzWmTLY83A0fn98Roe5fw; _uab_collina=152838734279151620441343; UM_distinctid=163dafc16d9213-05652d00ba1f97-39614807-144000-163dafc16da3b6; __uid=947a4c16579ba338ee0b393ddd6c64e8; uid=24081098; __asc=3f383bc6163dcb5997031be53ca; _cnzz_CV1256903590=is-logon%7Clogged-in%7C1528417466365%26urlname%7Cctkpvzu83j%7C1528417466365; CNZZDATA1256903590=2071183697-1528384068-%7C1528415106',
    'Host': 'huaban.com',
    'User-Agent': ' Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
}


# def search(keyword):
#     # try:
#     #     browser.get('http://huaban.com')
#         # login = wait.until(
#         #     EC.element_to_be_clickable(
#         #         (By.CSS_SELECTOR, '#header > div > div > div.right-part > div > a.login.btn.wbtn > span'))
#         # )
#         # login.click()
#         # time.sleep(3)
#         # input_username = wait.until(
#         #     EC.presence_of_element_located(
#         #         (By.CSS_SELECTOR, '#login_frame > div.login > div > form > input:nth-child(2)'))
#         # )
#         # intput_password = wait.until(
#         #     EC.presence_of_element_located(
#         #         (By.CSS_SELECTOR, '#login_frame > div.login > div > form > input:nth-child(3)'))
#         # )
#         # input_username.send_keys('18385583924')
#         # intput_password.send_keys('weareyoung')
#         # login_final = wait.until(
#         #     EC.element_to_be_clickable(
#         #         (By.CSS_SELECTOR, '#login_frame > div.login > div > form > a'))
#         # )
#         # login_final.click()
#     #     cookies = pickle.load(open("cookies.pkl", "rb"))
#     #     for cookie in cookies:
#     #         browser.add_cookie(cookie)
#     #     query = wait.until(EC.presence_of_element_located(
#     #         (By.CSS_SELECTOR, '#query')))
#     #     query_button = wait.until(
#     #         EC.element_to_be_clickable(
#     #             (By.CSS_SELECTOR, '#search_form > a'))
#     #     )
#     #     query.send_keys(keyword)
#     #     query_button.click()
#     # except TimeoutException:
#     #     search(keyword)


def get_page_index(offset):
    data = {
        'q': keyword,
        'page': offset,
        'per_page': 20,
        'wfl': 1
    }
    url = 'http://huaban.com/search/?' + urlencode(data)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
    except RequestException:
        print('请求索引页出错')
        return None


def parse_page_index(html):
    soup = BeautifulSoup(html, 'lxml')
    key_pattern = re.compile(r'"file":.*?"key":"(.*?)", "type"', re.S)
    items = re.findall(key_pattern, html)
    for item in items:
        url = 'http://img.hb.aicdn.com/' + item + '_fw658'
        download_image(url)


def download_image(url):
    if not os.path.exists(keyword):
        os.makedirs(keyword)
    print('正在下载', url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            save_image(response.content)
    except RequestException:
        print('请求图片出错', url)
        return None


def save_image(content):
    file_path = '{0}/{1}.{2}'.format(keyword,
                                     md5(content).hexdigest(), 'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()


def main(offset):
    # for offset in range(1, 80):
    print(offset)
    html = get_page_index(offset)
    parse_page_index(html)


if __name__ == '__main__':
    groups = [x for x in range(1, 80)]
    pool = Pool()
    pool.map(main, groups)
    pool.close()
    pool.join()
    # main()
