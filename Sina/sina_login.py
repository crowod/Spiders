import time
import math
import random
import base64

import requests
import rsa


class SinaLogin:
    def __init__(self):
        self.modulus = "EB2A38568661887FA180BDDB5CABD5F21C7BFD59C090CB2D245A87AC253062882729293E5506350508E7F9AA3BB77F4333231490F915F6D63C55FE2F08A49B353F444AD3993CACC02DB784ABBB8E42A9B1BBFFFB38BE18D78E87A0E41B9B8F73A928EE0CCEE1F6739884B9777E4FE9E88A1BBE495927AC4A799B3181D6442443"
        self.pub_key = '10001'

    def make_nonce(self, a):
        b = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        c = ""
        for d in range(a):
            c += b[(math.ceil(random.random() * 1e6) % len(b))]
        return c

    def rsa_encrypt(self, text, pubKey, modulus):
        PublicKey = rsa.PublicKey(int(modulus, 16), int(pubKey,16))  # rsa库公钥形式
        rs = rsa.encrypt(text, PublicKey)
        return rs.hex()

    def login(self, username, password):
        headers = {
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://www.weibo.com',
            'Upgrade-Insecure-Requests': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'Accept':
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Referer': 'https://www.weibo.com/login.php',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }

        params = (('client', 'ssologin.js(v1.4.19)'), )
        servertime = int(time.time())
        nonce = self.make_nonce(6)
        data = {
            'entry':
            'weibo',
            'gateway':
            '1',
            'from':
            '',
            'savestate':
            '7',
            'qrcode_flag':
            'false',
            'useticket':
            '1',
            'pagerefer':
            'https://www.google.com/',
            'vsnf':
            '1',
            'su':
            base64.b64encode(bytes(username, 'utf8')).decode('utf8'),
            'service':
            'miniblog',
            'servertime':
            servertime,
            'nonce':
            nonce,
            'pwencode':
            'rsa2',
            'rsakv':
            '1330428213',
            'sp':
            self.rsa_encrypt(
                bytes('\t'.join([str(servertime), nonce]) + '\n' + password,
                      'utf8'), self.pub_key, self.modulus),
            'sr':
            '1706*960',
            'encoding':
            'UTF-8',
            'prelt':
            '26',
            'url':
            'https://www.weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype':
            'META'
        }

        response = requests.post('https://login.sina.com.cn/sso/login.php',
                                 headers=headers,
                                 params=params,
                                 data=data)
        print(response.text)


if __name__ == "__main__":
    pass
    # sina = SinaLogin()
    # usernmae = ''
    # password = '' 
    # sina.login(username, password)