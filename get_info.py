import sys
import urllib.request

import bs4
import urllib.request as request
import collections as col


def get_tag(start_tag, path):
    tag = start_tag
    for args, kwargs, pos in path:
        if pos == -1:
            tag = tag.find(*args, **kwargs)
        else:
            tag = tag.find_all(*args, **kwargs)[pos]
    return tag


def get_name(soup):
    path = [
        (('div',), {'class_': 'main-content'}, -1),
        (('div',), {'id': 'page'}, -1),
        (('div',), {'class_': 'breadcrumbs-widget pjax-inner-replace'}, -1),
        (('div',), {'class_': 'container'}, -1),
        (('ul',), {'class_': 'breadcrumbs-list'}, -1),
        (('li',), {}, 3),
        (('span',), {}, -1)
    ]
    dest = get_tag(soup.html.body, path)
    return dest.get_text()


def get_image(soup):
    path = [
        (('div',), {'class_': 'main-content'}, -1),
        (('div',), {'id': 'page'}, -1),
        (('div',), {'class_': 'game-card'}, -1),
        (('div',), {'class_': 'game-info-image'}, -1),
        (('img',), {}, -1),
    ]
    tag = get_tag(soup.html.body, path)
    return tag['src']


def get_market_url(soup):
    path = [
        (('div',), {'class_': 'main-content'}, -1),
        (('div',), {'id': 'page'}, -1),
        (('div',), {'class_': 'game-card'}, -1),
        (('div',), {'class_': 'game-info-image'}, -1),
        (('a',), {'class_': 'game-link-widget'}, -1)
    ]
    tag = get_tag(soup.html.body, path)
    url = tag['href']
    req = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    res = urllib.request.urlopen(req)
    return res.geturl()


def collect_stat(url):
    stat = col.OrderedDict()

    # download html file
    with open('index.html', 'r') as file:
        soup = bs4.BeautifulSoup(file, 'html.parser')

    stat['url'] = url
    stat['name'] = get_name(soup)
    stat['image'] = get_image(soup)
    stat['market_url'] = get_market_url(soup)

    return stat


smth = collect_stat('https://gg.deals/game/tricky-towers/')
print(smth)
