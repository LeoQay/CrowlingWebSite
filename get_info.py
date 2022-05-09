import sys
import urllib.request

import bs4
import urllib.request as request
import collections as col


def namer(func, name):
    def wrapper(thing):
        return func(thing, name)
    return wrapper


def has_attr(tag, name):
    return tag.has_attr(name)


def consist(name_, name):
    return name_.find(name) != -1


def get_tag(start_tag, path):
    tag = start_tag
    for args, kwargs, pos in path:
        if pos == -1:
            tag = tag.find(*args, **kwargs)
        else:
            tag = tag.find_all(*args, **kwargs)[pos]
    return tag


def get_name(stat, soup):
    path = [
        (('div',), {'class_': 'breadcrumbs-widget pjax-inner-replace'}, -1),
        (('div',), {'class_': 'container'}, -1),
        (('ul',), {'class_': 'breadcrumbs-list'}, -1),
        (('li',), {}, 3),
        (('span',), {}, -1)
    ]
    dest = get_tag(soup, path)
    stat['name'] = dest.get_text()


def get_image(stat, soup):
    path = [
        (('img',), {}, -1),
    ]
    tag = get_tag(soup, path)
    stat['image'] = tag['src']


def get_market_url(stat, soup):
    path = [
        (('a',), {'class_': 'game-link-widget'}, -1)
    ]
    tag = get_tag(soup, path)
    url = tag['href']
    req = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    res = urllib.request.urlopen(req)
    stat['market_url'] = res.geturl()


def get_from_game_info_image(stat, soup):
    path = [
        (('div',), {'class_': 'game-info-image'}, -1),
    ]
    soup = get_tag(soup, path)
    get_image(stat, soup)
    get_market_url(stat, soup)


def get_wishlist_counter(stat, soup):
    path = [
        ((), {'class_': namer(consist, 'wishlisted-game')}, -1),
        (('span',), {'class_': 'user-count'}, -1),
        (('span',), {'class_': 'count'}, -1)
    ]
    soup = get_tag(soup, path)
    stat['wishlist_count'] = soup.get_text()


def get_alert_counter(stat, soup):
    path = [
        ((), {'class_': namer(consist, 'alerted-game')}, -1),
        (('span',), {'class_': 'user-count'}, -1),
        (('span',), {'class_': 'count'}, -1)
    ]
    soup = get_tag(soup, path)
    stat['alert_count'] = soup.get_text()


def get_own_counter(stat, soup):
    path = [
        ((), {'class_': namer(consist, 'owned-game')}, -1),
        (('span',), {'class_': 'user-count'}, -1),
        (('span',), {'class_': 'count'}, -1)
    ]
    soup = get_tag(soup, path)
    stat['owners_count'] = soup.get_text()


def get_from_game_collection_actions(stat, soup):
    path = [
        (('div',), {'class_': 'game-header game-header-container container'}, -1),
        ((namer(has_attr, 'data-counters-url'),), {}, -1),
    ]
    soup = get_tag(soup, path)
    get_wishlist_counter(stat, soup)
    get_alert_counter(stat, soup)
    get_own_counter(stat, soup)


def get_from_game_card(stat, soup):
    path = [
        (('div',), {'class_': 'game-card'}, -1),
    ]
    soup = get_tag(soup, path)
    get_from_game_info_image(stat, soup)
    get_from_game_collection_actions(stat, soup)


def get_from_main_content_page(stat, soup):
    path = [
        (('div',), {'class_': 'main-content'}, -1),
        (('div',), {'id': 'page'}, -1),
    ]
    soup = get_tag(soup, path)
    get_name(stat, soup)
    get_from_game_card(stat, soup)


def collect_stat(url):
    stat = col.OrderedDict()

    # download html file
    with open('index.html', 'r') as file:
        soup = bs4.BeautifulSoup(file, 'html.parser')

    soup = soup.html.body

    stat['url'] = url
    get_from_main_content_page(stat, soup)

    return stat


smth = collect_stat('https://gg.deals/game/tricky-towers/')
print(smth)
