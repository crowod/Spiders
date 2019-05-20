import json
import base64
import zlib
import random
import re
import time
import logging
from urllib.parse import urlencode, unquote

import requests
from requests import RequestException

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(lineno)d')


class Token:
    def __init__(self, query):
        self.args = dict()
        self.query = query
        if '_token' in self.query:
            del self.query['_token']

    def make_sign(self):
        sign = str(
            base64.b64encode(
                zlib.compress(
                    bytes(
                        json.dumps(unquote(urlencode({key: value for key, value in sorted(self.query.items())})), ensure_ascii=False),
                        encoding='utf8'))),
            encoding='utf8')
        return sign

    @property
    def make_token(self):
        self.args.update({
            'rId':
            100900,
            'ver':
            '1.0.6',
            'ts':
            int(time.time() * 1000),
            'cts':
            int(time.time() * 1000) + random.randint(61, 100),
            'brVD': [520, 800],
            'brR': [[1706, 960], [1707, 960], 24, 24],
            'bI': [self.query.get('originUrl'), self.query.get('originUrl')],
            'mT': [],
            'kT': [],
            'aT': [],
            'tT': [],
            'aM':
            ""
        })
        self.args['sign'] = self.make_sign()
        token = str(
            base64.b64encode(
                zlib.compress(
                    bytes(
                        json.dumps(self.args, ensure_ascii=False, separators=(',', ':')),
                        encoding='utf8'))),
            encoding='utf8')
        return token


class MeituanFood:
    def __init__(self, cityName='', page=None, originUrl=''):
        self.logger = logging.getLogger(__name__)
        self.query = dict()
        self.query.update({
            'cityName': cityName,
            'cateId': 0,
            'areaId': 0,
            'sort': '',
            'dinnerCountAttrId': '',
            'page': page,
            'userId': '',
            'uuid': '7dc561715eb14f9ebcb6.1558077843.1.0.0',
            'platform': 1,
            'partner': 126,
            'originUrl': originUrl,
            'riskLevel': 1,
            'optimusCode': 1,
        })
        self.session = requests.Session()
        self.session.headers = {
            'Accept':
            'application/json',
            'Host':
            'www.meituan.com',
            'Referer':
            'http://www.meituan.com',
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
        }

    def get_page(self, url):
        try:
            token = Token(self.query)
            self.query['_token'] = token.make_token
            url = url + '?' + urlencode(self.query)
            response = self.session.get(url)
            if response.status_code == 200:
                return response.text
            else:
                self.logger.info('Canot get page')
                return self.get_page()
        except RequestException:
            self.logger.warning('Cannot get page')
            time.sleep(1)
            return self.get_page()

    def parse_page(self, html):
        content = json.loads(html)
        data = content.get('data')
        for poinInfo in data.get('poiInfos'):
            print(poinInfo.get('title'))

def main():
    meituan = MeituanFood('北京', 1, 'http://bj.meituan.com/meishi/')
    html = meituan.get_page('http://bj.meituan.com/meishi/api/poi/getPoiList')
    meituan.parse_page(html)


if __name__ == '__main__':
    main()