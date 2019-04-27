import json
import re
import time
import pprint
import logging
from multiprocessing import Pool

import requests
import pymongo
from retrying import retry
from bs4 import BeautifulSoup

MONGO_URL = 'mongodb://localhost:27017/'
MONGO_DB = 'tmp'
COLLECTION = 'DianPing'

client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

pp = pprint.PrettyPrinter(indent=4)


class Dianping:
    def __init__(self):
        with open('./Dianping_Font.json', 'r') as f:
            self.memo = json.load(f)
        self.offsets = dict()
        self.backgrounds = dict()
        self.html = ''
        self.logger = logging.getLogger(__name__)

    @retry(
        stop_max_attempt_number=10,
        stop_max_delay=10000,
        wait_random_min=500,
        wait_random_max=5000,
    )
    def get_css(self, html):
        headers_css = {
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 '
            'Safari/537.36',
            'Host':
            's3plus.meituan.net'
        }
        try:
            css_url = 'http:' + re.search(r'href="(.*?svgtextcss.*?.css)"',
                                          html).group(1)
            response = requests.get(css_url, headers=headers_css)
            if response.status_code == 200:
                return response.text
            else:
                self.logger.warning('Can not find css')
        except Exception as e:
            self.logger.warning(e)

    @retry(
        stop_max_attempt_number=10,
        stop_max_delay=10000,
        wait_random_min=500,
        wait_random_max=5000,
    )
    def get_page(self, url):
        headers = {
            'Host':
            'www.dianping.com',
            'Origin':
            'http://www.dianping.com',
            'Referer':
            url,
            'Cookie':
            '_lxsdk_cuid=169d4528a3ac8-091e9e745e44b8-1a201708-18fd80-169d4528a3ac8; '
            '_lxsdk=169d4528a3ac8-091e9e745e44b8-1a201708-18fd80-169d4528a3ac8; '
            '_hc.v=2380f528-f846-62d8-495f-dd741194d554.1554045376; '
            'Hm_lvt_e6f449471d3527d58c46e24efb4c343e=1554045373,1554045567; cy=2; cye=beijing; '
            '_lx_utm=utm_source%3Dgoogle%26utm_medium%3Dorganic; s_ViewType=10; '
            '_lxsdk_s=16a103e6a97-6ca-ba9-88%7C%7C131',
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/73.0.3683.103 Safari/537.36',
            'X-Request':
            'JSON',
            'X-Requested-With':
            'XMLHttpRequest'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            if '验证码' in response.text:
                logger.info('Verify')
                time.sleep(5)
                self.get_page(url)
            else:
                self.html = response.text
                self.parse_page(response.text)
        else:
            self.logger.warning('Can not get page')
            return None

    def parse_css(self, html):
        try:
            svgmtsi = re.findall(
                r'svgmtsi\[class\^="(.*?)"\].*?background-image: url\((.*?)\);',
                html, re.S)
            if svgmtsi:
                for prefix, url in svgmtsi:
                    response = requests.get('http:' + url)
                    if response.status_code == 200:
                        result = re.findall(
                            r'text.*?y="(.*?)">(.*?)</text>|xlink:href="#(.*?)".*?>(.*?)<',
                            response.text, re.S)
                        cheat = re.findall(
                            r'path id="\d+" d="M0 (.*?) H600"/>',
                            response.text, re.S)
                        if result:
                            if cheat:
                                result = [list(val) for val in result]
                                for i in range(len(result)):
                                    result[i][2] = cheat[i]
                            self.offsets[prefix] = result
                html_ = re.sub(r'\.0px', 'px', html)
                backgrounds_ = re.findall(
                    r'\.(.*?)\{background:-(\d+)px -(\d+)px;\}', html_)
                if backgrounds_:
                    self.backgrounds = {
                        prefix: [x, y]
                        for prefix, x, y in backgrounds_
                    }
        except Exception as e:
            self.logger.warning(e)

    def parse_page(self, html):
        css_html = self.get_css(html)
        if css_html:
            self.parse_css(css_html)
        soup = BeautifulSoup(html, 'lxml')
        items = soup.select('#shop-all-list ul li')
        for item in items:
            title = item.find('h4').string
            if item.find('a', class_='shop-branch') is not None:
                title += ' ' + item.find(
                    'a', class_='shop-branch').string.strip()
            rank_starts = item.find(
                'span', class_='sml-rank-stars').attrs.get('title')
            review_num = self.get_review_num(item)
            avg_price = self.get_avgprice(item)
            tag = self.get_tag(item)
            addr = self.get_addr(item)
            comment_list = self.get_comment_list(item)
            self.save_to_mongo({
                'title': title,
                'rank_starts': rank_starts,
                'review_num': review_num,
                'avg_price': avg_price,
                'tag': tag,
                'addr': addr,
                'comment-list': comment_list
            })

    def get_review_num(self, item):
        if not item.select('.review-num b'):
            return ''
        text = item.select('.review-num b')[0].decode()
        result = self.get_words(text, 0)
        return result

    def get_avgprice(self, item):
        if not item.select('.mean-price b'):
            return ''
        text = item.select('.mean-price b')[0].decode()
        result = self.get_words(text, 0)
        return ''.join(result)

    def get_tag(self, item):
        tags = item.select('.tag')
        result = [self.get_words(tag.decode(), 1) for tag in tags]
        return result

    def get_addr(self, item):
        text = item.select('.addr')[0].decode()
        result = self.get_words(text, 1)
        return result

    def get_comment_list(self, item):
        spans = item.select('.comment-list span')
        result = {
            span.contents[0]: self.get_words(span.contents[1].decode(), 1)
            for span in spans
        }
        return result

    def compute_offsets(self, val):
        texts = []
        try:
            x, y = self.backgrounds[val]
            offset = self.offsets[val[:len(list(self.offsets.keys())[0])]]
            if not offset[0][0]:
                for val in offset:
                    if int(y) <= int(val[2]):
                        texts = val[3]
                        break
                return texts[int(x) // 12]
            else:
                for val in offset:
                    if int(y) <= int(val[0]):
                        texts = val[1]
                        break
                return texts[int(x) // 12]
        except KeyError as e:
            logger.warning(e)
            css_html = self.get_css(self.html)
            if css_html:
                self.parse_css(css_html)
            return self.compute_offsets(val)

    def get_words(self, text, mod):
        try:
            result = []
            class_name = 'address' if mod else 'shopNum'
            if rf'class="{class_name}"' in text:
                match = re.findall(r'>(\S+?)<', text)
                match = [repr(val).strip('\'') for val in match]
                result = [
                    self.memo.get(val[-4:]) if val.startswith('\\u') else val
                    for val in match
                ]
            else:
                match = re.findall(r'>(\S+?)<|svgmtsi class="(.*?)">', text)
                result = [
                    self.compute_offsets(val[1]) if not val[0] else val[0]
                    for val in match
                ]

            return ''.join(result)
        except TypeError as e:
            self.logger.warning(e, result)

    def save_to_mongo(self, result):
        try:
            if db[COLLECTION].insert_one(result):
                pp.pprint(f'{result}')
                return True
        except Exception as e:
            self.logger.warning(e)
            return Flase


if __name__ == '__main__':
    dianping = Dianping()
    url = 'http://www.dianping.com/nanjing/ch10/g110p'
    urls = [url + str(i) for i in range(1, 51)]
    pool = Pool(4)
    pool.map(dianping.get_page, urls)
    pool.close()
    pool.join()
