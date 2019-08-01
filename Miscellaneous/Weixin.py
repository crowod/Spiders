from urllib.parse import urlencode
import requests
from pyquery import PyQuery as pq
from requests.exceptions import ConnectionError

base_url = 'http://weixin.sogou.com/weixin?'
headers = {
    'Cookie': 'sw_uuid=4757679932; ssuid=7231426420; dt_ssuid=1207387350; start_time=1524729084956; pex=C864C03270DED3DD8A06887A372DA219231FFAC25A9D64AE09E82AED12E416AC; IPLOC=CN1100; SUID=3C6CC17C6119940A000000005AE71C05; SUV=1525095426317996; ABTEST=0|1525095445|v1; weixinIndexVisited=1; ppinf=5|1525095656|1526305256|dHJ1c3Q6MToxfGNsaWVudGlkOjQ6MjAxN3x1bmlxbmFtZTo1OlhpYW5nfGNydDoxMDoxNTI1MDk1NjU2fHJlZm5pY2s6NTpYaWFuZ3x1c2VyaWQ6NDQ6bzl0Mmx1RGdZQWJkNXF1NWhlcW5oTFVoSDJmZ0B3ZWl4aW4uc29odS5jb218; pprdig=kXfATfyoY3voZ4pIKUrHBb995k1GOhiys9T4DMEGdmtxAInX1qq_aPZ9RNMGuXjF5pZCPXN1cP6EvMPXAvKml1HYf5aI7pazRz7i84IQ7jc5rHh5aIW-D9GjMLad5cAz4KJrYDPWipc4I6ozRmXwCxrB464P-PkgbyIwHk7Triw; sgid=02-32711651-AVrnHOjicfICssibOoogOPUh4; SNUID=2072DE621E1B756B563138951F1821F0; ppmdig=15255220560000006890c136b9f2d6f3640562ad19918aed; JSESSIONID=aaaeTxnAxS6W6fGsyZKmw; sct=6',
    'Host': 'weixin.sogou.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.189 Safari/537.36 Vivaldi/1.95.1077.55'
}
proxy_pool_url = 'http://localhost:5555/get'
proxy = None
max_count = 5


def get_proxy():
    try:
        response = requests.get(proxy_pool_url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None


def get_html(url, count=1):
    print('Crawling', url)
    print('Trying Count', count)
    global proxy
    if count >= max_count:
        print('Tried Too Many Counts')
        return None
    try:
        if proxy:
            proxies = {
                'http': 'http://' + proxy
            }
            response = requests.get(
                url, allow_redirects=False, headers=headers, proxies=proxies)
        else:
            response = requests.get(
                url, allow_redirects=False, headers=headers)
        if response.status_code == 200:
            return response.text
        if response.status_code == 302:
            print('302')
            proxy = get_proxy()
            if proxy:
                print('Using Proxy', proxy)
                return get_html(url)
            else:
                print('Get Proxy Failed')
                return None
    except ConnectionError as e:
        print('Erro Occurred', e.args)
        proxy = get_proxy()
        count += 1
        return get_html(url, count)


def get_index(keyword, page):
    data = {
        'query': keyword,
        'type': '2',
        'page': page
    }
    queries = urlencode(data)
    url = base_url + queries
    html = get_html(url)
    return html


def parse_index(html):
    doc = pq(html)
    items = doc('.news-box .news-list li .txt-box h3 a').items()
    for item in items:
        yield item.attr('href')


def get_detail(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except ConnectionError:
        return None


def parse_detail(html):
    doc = pq(html)
    title = doc('.rich_media_title').text()
    content = doc('.rich_media_content').text()
    data = doc('#post-date').text()
    nickname = doc('#js_profile_qrcode > div > strong').text()
    wechat = doc('#js_profile_qrcode > div > p:nth-child(3) > span').text()
    return {
        'title': title,
        'data': data,
        'nickname': nickname,
        'wechat': wechat,
        'content': content
    }


def main(keyword):
    for page in range(1, 101):
        html = get_index(keyword, page)
        if html:
            article_urls = parse_index(html)
            for article_url in article_urls:
                article_html = get_detail(article_url)
                if article_html:
                    article_data = parse_detail(article_html)
                    print(article_data)


if __name__ == '__main__':
    keyword = 'yurisa'
    main(keyword)
