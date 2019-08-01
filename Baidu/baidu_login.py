import time
import math
import random
import base64
import json
import email
import imaplib

import requests
import re
import traceback
from http import cookiejar
from urllib.parse import urlencode, urlsplit, parse_qsl
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5

from function import *


class BaiduLogin:
    def __init__(self):
        self.session = requests.Session()
        self.session.cookies = cookiejar.LWPCookieJar(filename='cookies')
        self.gid = self.cal_gid()
        self.fuid = fuid = "FOCoIC3q5fKa8fgJnwzbE+YhNskVRU4HW930FeLFkOByMFn76lfGbpe1mvnbXASpprBSgAj8TeGH+O6o2VUDCfLdJ4BbXu0qA2r9fH5GA51vxNYIV7rYxWsNNjqUx/Yat+ovxzzsosXaoURHehskadkCHCKxv8NbdR+rC6LdcuDYJqYod0SQONg0Otv5eOFVd5+V0SfDj7up9XM1ftftm6qcCgPiAMYZ/gyM2VtRdKMYmcDtlrvyg/ZbHG1RvfYUwwWPsktD+ISAuCZeADsfKTGDdd24O7UtAZwjxBqHhz0qzn4GbnsMc4bhfAu2fXO1by1GopSSoOGA/kVHD00teZOTADkZD+HIh2Z2obx77xbMECC9YTPkH0SYH5a7gCFBZKO/CJPteFWdA84Wg95Fa8iUEACPczYjRW9BOPO2ptPZ0zUv6SzFnHrrNHu+e/1DZIBwny85kiMgxqbEor+pVsheeciRI7bZS61mzwLJvT54XIWkktu4TY6WXC6fyKroTvlLX57BOu2kovr8ICKLEv+CYTlfjalFajCI7T84a0X7+B4iuZO+f7FUDWABtt/WWQqHKVfXMaw5WUmKnfSR5wwQa+N01amx6X+p+x97kkGmoNOSwxWgGvuezNFuiJQdt51yrWaL9Re9fZveXFsIu7gqiVcHEmV2uSfaIOmRVA6IsRNIWWghWQd3Lf4jYlSvRq7kgutHojUUBEP2UiHZKmymWEvBvsXSXSAkuBVFUna9A5mNm34ZPuoRV+zY3FkhDaw5QtNtFShnskfkCxyuTXURkpbqjOBbgIBwr3Z6nxpto/iUyx0WqwWHOWtTFkieGEQw3OLo5dsSUeQDd6vDni1evF/M7yvmL+FUAwPmWZFbvNq69O2z3wBW+ogxJUDyHQyXRw7Tp8GptlIfbw9+IYXySaj1El9Nb4g/exl38O5H/kemrNyTwBF7HTnQ7FhAICZ/mTFaxCyO6V8/CZKPV797kgx6Pwt5JhS62rrxGKVINxW6hKjOiZkR6pMEYUiUNkRx+L3BtOrUtFm2YoJs780bM3mLxclwj0rieaMqDoKAjylxPH1+91jmdJgJRdZn"
        self.email_user = ''
        self.email_pass = ''

    def cal_password(self, pwd, pub_key):
        rsakey = RSA.importKey(pub_key)
        cipher = Cipher_pkcs1_v1_5.new(rsakey)
        cipher_text = base64.b64encode(
            cipher.encrypt(pwd.encode(encoding="utf-8"))).decode('utf8')
        return cipher_text

    def cal_gid(self):
        strs = "xxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"

        gid = ''
        for s in strs:
            t = int(16 * random.random()) | 0
            if s == 'x':
                gid += hex(t)[2:].upper()
            elif s == 'y':
                gid += hex(3 & t | 8)[2:].upper()
            else:
                gid += s
        return gid

    def create_traceid(self):
        t = str(int(time.time()) * 1000) + str(int(90 * random.random() + 10))
        n = hex(int(t))[2:]
        r = len(n)
        i = n[r - 6:r].upper()
        return i + '01'

    def login(self, username, password):
        if self.__step1() and self.__step2() and self.__step3():
            headers = {
                'Connection': 'keep-alive',
                'Cache-Control': 'max-age=0',
                'Origin': 'https://pan.baidu.com',
                'Upgrade-Insecure-Requests': '1',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent':
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
                'Accept':
                'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                'Referer': 'https://pan.baidu.com/',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            }

            tk = "tk" + str(random.random()) + str(int(time.time() * 1000))
            data = {
                'staticpage':
                'https://pan.baidu.com/res/static/thirdparty/pass_v3_jump.html',
                'charset': 'UTF-8',
                'token': self.token,
                'tpl': 'netdisk',
                'subpro': 'netdisk_web',
                'apiver': 'v3',
                'tt': str(int(time.time() * 1000)),
                'codestring': '',
                'safeflg': '0',
                'u': 'https://pan.baidu.com/disk/home',
                'isPhone': 'false',
                'detect': '1',
                'gid': self.gid,
                'quick_user': '0',
                'logintype': 'basicLogin',
                'logLoginType': 'pc_loginBasic',
                'idc': '',
                'loginmerge': 'true',
                'mkey': '',
                'username': username,
                'password': self.cal_password(password, self.pub_key),
                'mem_pass': 'on',
                'rsakey': self.key,
                'crypttype': '12',
                'ppui_logintime': '8587',
                'countrycode': '',
                'fp_uid': '',
                'fp_info': '',
                'loginversion': 'v4',
                'ds': self.ds,
                'tk': self.tk,
                'dv': tk + '@' + cal_dv(tk),
                'fuid': self.fuid,
                'traceid': self.create_traceid(),
                'callback': 'parent.bself.verify_result_pcbs__9hkk2b'
            }

            try:
                response = self.session.post(
                    'https://passport.baidu.com/v2/api/?login',
                    headers=headers,
                    data=data)
                result = re.search(r'href \+= "(.*?)"\+accounts',
                                   response.content.decode('utf8')).group(1)
                url = 'https://pan.baidu.com/res/static/thirdparty/pass_v3_jump.html?' + result + '&accounts='
                result = dict(
                    parse_qsl(urlsplit(url).query))
                if 'err_no' in result and result['err_no'] == '120021':
                    headers = {
                        'Host': 'pan.baidu.com',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent':
                        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
                        'Accept':
                        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                        'Referer': 'https://passport.baidu.com/v2/api/?login',
                        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    }
                    self.session.get(url, headers=headers)
                    self.verify_result = result
                    self.verify_by_email()
                self.session.cookies.save()
                return self.session.cookies
            except Exception as e:
                traceback.print_exc()
                return None

    def __step1(self):
        headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            'Accept':
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        response = self.session.get('https://pan.baidu.com/', headers=headers)

        params = (
            ('tpl', 'netdisk'),
            ('subpro', 'netdisk_web'),
            ('apiver', 'v3'),
            ('tt', str(int(time.time() * 1000))),
            ('class', 'login'),
            ('gid', self.gid),
            ('loginversion', 'v4'),
            ('logintype', 'basicLogin'),
            ('traceid', ''),
            ('callback', 'bself.verify_result_cbs__5noasf'),
        )
        self.session.headers = headers
        url = 'https://passport.baidu.com/v2/api/?getapi&' + urlencode(params)
        response = self.session.get(url, headers=headers)
        try:
            token = re.search(r'token" : "(.*?)",.*?cookie',
                              response.text).group(1)
            self.token = token
            return True
        except Exception as e:
            traceback.print_exc()
            return False

    def __step2(self):
        headers = {
            'Referer':
            'https://pan.baidu.com/',
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        }

        params = (
            ('token', self.token),
            ('tpl', 'netdisk'),
            ('subpro', 'netdisk_web'),
            ('apiver', 'v3'),
            ('tt', str(int(time.time() * 1000))),
            ('gid', self.gid),
            ('loginversion', 'v4'),
            ('traceid', ''),
            ('callback', 'bself.verify_result_cbs__veg4wp'),
        )
        self.session.headers = headers
        response = self.session.get(
            'https://passport.baidu.com/v2/getpublickey',
            headers=headers,
            params=params,
        )
        try:
            result = json.loads(
                re.search(r'\(({.*?})\)',
                          response.content.decode('utf8')).group(1).replace(
                              '\'', '\"'))
            self.pub_key = result['pubkey']
            self.key = result['key']
            return True
        except Exception as e:
            traceback.print_exc()
            return False

    def __step3(self):
        headers = {
            'Referer':
            'https://pan.baidu.com/',
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        }

        params = (('ak', '1e3f2dd1c81f2075171a547893391274'),
                  ('callback', 'jsonpCallbacka' +
                   str(math.floor(1e4 * random.random() + 500))),
                  ('v', str(math.floor(1e4 * random.random() + 500))))

        self.session.headers = headers

        response = self.session.get(
            'https://passport.baidu.com/viewlog',
            headers=headers,
            params=params,
        )

        try:
            result = json.loads(
                re.search(r'\(({.*?})\)',
                          response.content.decode('utf8')).group(1))['data']
            self.ds = result['ds']
            self.tk = result['tk']
            return True
        except Exception as e:
            traceback.print_exc()
            return False

    def verify_by_email(self):
        self.__verify_step1()
        self.__verify_step2()
        time.sleep(3)
        M = imaplib.IMAP4_SSL('imap.qq.com', 993)
        M.login(self.email_user, self.email_pass)
        M.select()
        typ, message_numbers = M.search(
            None, '(FROM "passport@baidu.com")'
        )  # change variable name, and use new name in for loop
        typ, data = M.fetch(message_numbers[0].split()[-1], '(RFC822)')
        message = email.message_from_string(data[0][1].decode('utf8'))
        text = {message.get_payload(decode=True)}
        text = text.pop()
        code = re.search(r'\d{6}', text.decode('utf8')).group()
        M.close()
        M.logout()
        if self.__verify_step3(code):
            self.__verify_step4()

    def __verify_step1(self):
        headers = {
            'Referer':
            'https://pan.baidu.com/',
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        }

        params = (
            ('authtoken', self.verify_result['authtoken']),
            ('type', ''),
            ('jsonp', '1'),
            ('apiver', 'v3'),
            ('verifychannel', ''),
            ('action', 'getapi'),
            ('vcode', ''),
            ('questionAndAnswer', ''),
            ('needsid', ''),
            ('rsakey', ''),
            ('countrycode', ''),
            ('subpro', 'netdisk_web'),
            ('u', 'https://pan.baidu.com/disk/home'),
            ('lstr', self.verify_result['lstr']),
            ('ltoken', self.verify_result['ltoken']),
            ('tpl', 'netdisk'),
            ('winsdk', ''),
            ('authAction', ''),
            ('traceid', self.gid),
            ('callback', 'bself.verify_result_cbs__m9kqgm'),
        )

        response = self.session.get(
            'https://passport.baidu.com/v2/sapi/authwidgetverify',
            headers=headers,
            params=params)

    def __verify_step2(self):
        headers = {
            'Referer':
            'https://pan.baidu.com/',
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        }

        params = (
            ('authtoken', self.verify_result['authtoken']),
            ('type', 'email'),
            ('jsonp', '1'),
            ('apiver', 'v3'),
            ('verifychannel', ''),
            ('action', 'send'),
            ('vcode', ''),
            ('questionAndAnswer', ''),
            ('needsid', ''),
            ('rsakey', ''),
            ('countrycode', ''),
            ('subpro', 'netdisk_web'),
            ('u', 'https://pan.baidu.com/disk/home'),
            ('lstr', self.verify_result['lstr']),
            ('ltoken', self.verify_result['ltoken']),
            ('tpl', 'netdisk'),
            ('winsdk', ''),
            ('authAction', ''),
            ('traceid', self.gid),
            ('callback', 'bself.verify_result_cbs__wkoq0k'),
        )

        response = self.session.get(
            'https://passport.baidu.com/v2/sapi/authwidgetverify',
            headers=headers,
            params=params)

    def __verify_step3(self, code):
        headers = {
            'Referer':
            'https://pan.baidu.com/',
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        }

        params = (
            ('authtoken', self.verify_result['authtoken']),
            ('type', 'email'),
            ('jsonp', '1'),
            ('apiver', 'v3'),
            ('verifychannel', ''),
            ('action', 'check'),
            ('vcode', code),
            ('questionAndAnswer', ''),
            ('needsid', ''),
            ('rsakey', ''),
            ('countrycode', ''),
            ('subpro', 'netdisk_web'),
            ('u', 'https://pan.baidu.com/disk/home'),
            ('lstr', self.verify_result['lstr']),
            ('ltoken', self.verify_result['ltoken']),
            ('tpl', 'netdisk'),
            ('secret', ''),
            ('winsdk', ''),
            ('authAction', ''),
            ('traceid', self.gid),
            ('callback', 'bself.verify_result_cbs__vsjg0e'),
        )
        try:
            response = self.session.get(
                'https://passport.baidu.com/v2/sapi/authwidgetverify',
                headers=headers,
                params=params)
            result = json.loads(
                re.search(r'\(({.*?})\)',
                          response.content.decode('utf8')).group(1).replace(
                              "\'", '\"'))
            if result['errno'] == '110000':
                return True
            return False
        except Exception as e:
            traceback.print_exc()
            return False

    def __verify_step4(self):
        headers = {
            'Referer':
            'https://pan.baidu.com/',
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        }

        params = (
            ('u', 'https://pan.baidu.com/disk/home'),
            ('tpl', 'netdisk'),
            ('ltoken', self.verify_result['ltoken']),
            ('lstr', self.verify_result['lstr']),
            ('client', ''),
            ('traceid', [self.gid, self.gid, self.gid]),
            ('actiontype', '3'),
            ('apiver', 'v3'),
            ('tt', str(int(time.time() * 1000))),
            ('callback', 'bself.verify_result_cbs__pzpamg'),
        )
        url = 'https://passport.baidu.com/v2/?loginproxy&' + urlencode(params)

        response = self.session.get(url, headers=headers, params=params)


if __name__ == "__main__":
    baidu = BaiduLogin()
    username = ''
    password = ''
    cookies = baidu.login(username, password)

    headers = {
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Referer': 'https://pan.baidu.com/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }

    params = (
        ('errno', '0'),
        ('errmsg', 'Auth Login Sucess'),
        ('', ''),
        ('bduss', ''),
        ('ssnerror', '0'),
        ('traceid', ''),
    )

    response = requests.get('https://pan.baidu.com/disk/home',
                            headers=headers,
                            params=params,
                            cookies=cookies)

