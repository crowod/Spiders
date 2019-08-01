import hashlib
import time

import re
import requests

headers = {
    'cookie':
    'tt_webid=6697808077570016781; WEATHER_CITY=%E5%8C%97%E4%BA%AC; tt_webid=6697808077570016781; UM_distinctid=16b16c6861d23a-057aa75b8f27a4-3f72045a-18fd80-16b16c6861e1a5; csrftoken=dbb9e08e249c90e8a747d88f5fb35f4a; CNZZDATA1259612802=307279115-1559454282-https%253A%252F%252Fwww.google.com%252F%7C1559961887; __tasessionId=uf296s86q1559962468439',
    'referer':
    'https://www.toutiao.com/',
    'user-agent':
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
}

session = requests.Session()
session.headers = headers


def s():
    t = int(time.time())
    e = hex(t).lstrip('0x').upper()
    md5 = hashlib.md5()
    md5.update(str.encode(str(t), encoding='utf8'))
    i = md5.hexdigest()
    n = i[0:5]
    s = i[-5:]
    a = ''
    for r in range(5):
        a += n[r] + e[r]
    l = ''
    for u in range(5):
        l += e[u + 3] + s[u]
    return ({'as': 'A1' + a + e[-3:], 'cp': e[0:3] + l + 'E1'})


def get_signature():
    response = session.get('https://www.toutiao.com')
    tac = re.search(r'tac=\'(.*?)\'</script',
                    response.text).group(1).replace('\\\\', '\\')
    pattern = re.findall(r'(\\x\w{2})', tac)
    for _ in range(len(pattern)):
        tac = re.sub(r'(\\x\w{2})', chr(ord('\1')), tac, 1)
    with open('toutiao.js', 'r', encoding='utf8') as f:
        line = f.readline()
        jstr = ''
        while line:
            jstr = jstr + line
            line = f.readline()
    context = execjs.compile(jstr)
    signature = context.call('x')
    return signature


if __name__ == "__main__":
    data = []
    e = s()
    signature = get_signature()
    min_data = {
        'min_behot_time': '0',
        'category': '__all__',
        'utm_source': 'toutiao',
        'widen': '1',
        'tadrequire': 'true' if tadrequire else 'false',
        'as': e.get('as'),
        'cp': e.get('cp'),
        '_signature': signature
    }
    url = 'https://www.toutiao.com/api/pc/feed/?' + urlencode(min_data)
    response = session.get(url)
    data.append(json.loads(response.text))
    for _ in range(300):
        time.sleep(1)
        e = s()
        max_data = {
            'max_behot_time': str(data[-1].get('next').get('max_behot_time')),
            'category': '__all__',
            'tadrequire': 'true' if tadrequire else 'false',
            'as': e.get('as'),
            'cp': e.get('cp'),
            '_signature': signature
        }
        url = 'https://www.toutiao.com/api/pc/feed/?' + urlencode(max_data)
        response = session.get(url)
        data.append(json.loads(response.text))