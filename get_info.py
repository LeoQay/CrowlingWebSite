import sys
from multiprocessing.dummy import Pool, Queue
import urllib.request
import requests
import bs4
import urllib.request as request
import time


def err(stat, what='error'):
    print(f'Error: url: {stat["url"]}: with {what}', file=sys.stderr)


def namer(func, name):
    def wrapper(thing):
        return func(thing, name)
    return wrapper


def has_attr(tag, name):
    return tag is not None and tag.has_attr(name)


def consist(name_, name):
    return name_ is not None and name_.find(name) != -1


def get_tag(start_tag, path):
    tag = start_tag
    for args, kwargs, pos in path:
        if tag is None:
            return None
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
    if dest is not None:
        stat['name'] = dest.get_text()
    else:
        err(stat, 'name')


def get_image(stat, soup):
    path = [
        (('img',), {}, -1),
    ]
    tag = get_tag(soup, path)
    if tag is not None:
        stat['image'] = tag['src']
    else:
        err(stat, 'image')


def get_market_url(stat, soup):
    path = [
        (('a',), {'class_': 'game-link-widget'}, -1)
    ]
    tag = get_tag(soup, path)
    if tag is None:
        err(stat, 'market_url')
        return
    url = tag['href']
    try:
        req = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        res = urllib.request.urlopen(req)
    except ...:
        err(stat, 'market_url')
    else:
        stat['market_url'] = res.geturl()


def get_from_game_info_image(stat, soup):
    path = [
        (('div',), {'class_': 'game-info-image'}, -1),
    ]
    soup = get_tag(soup, path)
    if soup is None:
        err(stat, 'game-info-image')
        return
    get_image(stat, soup)
    get_market_url(stat, soup)


def get_wishlist_counter(stat, soup):
    path = [
        ((), {'class_': namer(consist, 'wishlisted-game')}, -1),
        (('span',), {'class_': 'user-count'}, -1),
        (('span',), {'class_': 'count'}, -1)
    ]
    soup = get_tag(soup, path)
    if soup is not None:
        stat['wishlist_count'] = int(soup.get_text())
    else:
        err(stat, 'wishlist_count')


def get_alert_counter(stat, soup):
    path = [
        ((), {'class_': namer(consist, 'alerted-game')}, -1),
        (('span',), {'class_': 'user-count'}, -1),
        (('span',), {'class_': 'count'}, -1)
    ]
    soup = get_tag(soup, path)
    if soup is not None:
        stat['alert_count'] = int(soup.get_text())
    else:
        err(stat, 'alert_count')


def get_own_counter(stat, soup):
    path = [
        ((), {'class_': namer(consist, 'owned-game')}, -1),
        (('span',), {'class_': 'user-count'}, -1),
        (('span',), {'class_': 'count'}, -1)
    ]
    soup = get_tag(soup, path)
    if soup is not None:
        try:
            stat['owners_count'] = int(soup.get_text())
        except ...:
            err(stat, 'owners_count')
    else:
        err(stat, 'owners_count')


def get_from_game_collection_actions(stat, soup):
    path = [
        (('div',), {'class_': 'game-header game-header-container container'}, -1),
        ((namer(has_attr, 'data-counters-url'),), {}, -1),
    ]
    soup = get_tag(soup, path)
    if soup is None:
        err(stat, 'game-header game-header-container container')
        return
    get_wishlist_counter(stat, soup)
    get_alert_counter(stat, soup)
    get_own_counter(stat, soup)


def get_release_date(stat, soup):
    path = [
        (('div',), {'class_': 'game-info-details-section game-info-details-section-release'}, -1),
        (('p',), {'class_': 'game-info-details-content'}, -1)
    ]
    soup = get_tag(soup, path)
    if soup is not None:
        stat['release_date'] = soup.get_text()
    else:
        err(stat, 'release_date')


def get_developer(stat, soup):
    path = [
        (('div',), {'class_': 'game-info-details-section game-info-details-section-developer'}, -1),
        (('p',), {'class_': 'game-info-details-content'}, -1)
    ]
    soup = get_tag(soup, path)
    if soup is not None:
        stat['developer'] = soup.get_text()
    else:
        err(stat, 'developer')


def get_metacritic_score(stat, soup):
    path = [
        (('span',), {'class_': 'overlay'}, -1)
    ]
    soup = get_tag(soup, path)
    if soup is not None:
        stat['metacritic_score'] = int(soup.get_text())
    else:
        err(stat, 'metacritic_score')


def get_user_score(stat, soup):
    path = [
        (('span',), {'class_': 'overlay'}, -1)
    ]
    soup = get_tag(soup, path)
    if soup is not None:
        stat['user_score'] = float(soup.get_text())
    else:
        err(stat, 'user_score')


def get_from_first_score(stat, soup):
    soups = soup.find_all('div', class_='score-col')
    if len(soups) == 0:
        err(stat, 'metacritic_score')
        return
    get_metacritic_score(stat, soups[0])
    if len(soups) == 1:
        err(stat, 'user_score')
        return
    get_user_score(stat, soups[1])


def get_from_second_score(stat, soup):
    path = [
        (('a',), {'class_': 'score-grade'}, -1),
        (('span',), {}, -1)
    ]
    soup = get_tag(soup, path)
    if soup is None:
        err(stat, 'review block')
        return
    try:
        if soup.has_attr('title'):
            stat['review_positive_pctg'] = int(soup['title'].split()[0][:-1])
        else:
            err(stat, 'review_positive_pctg')
        text = soup.get_text().split()
        stat['review_label'] = ' '.join(text[:-1])
        count = ''.join(text[-1].strip()[1:-1].split(','))
        stat['review_count'] = int(count)
    except ...:
        err(stat, 'review block')


def get_from_reviews(stat, soup):
    path = [
        (('div',), {'class_': 'game-info-details-section game-info-details-section-reviews'}, -1),
        (('div',), {'class_': 'game-info-details-content'}, -1)
    ]
    soup = get_tag(soup, path)
    if soup is None:
        err(stat, 'review, score block')
        return
    soups = soup.find_all('div', class_='score')
    if len(soups) == 0:
        err(stat, 'review, score block')
        return
    get_from_first_score(stat, soups[0])
    if len(soups) == 1:
        err(stat, 'review, score block')
        return
    get_from_second_score(stat, soups[1])


def get_platforms(stat, soup):
    path = [
        (('div',), {'class_': 'game-info-details-section game-info-details-section-platforms'}, -1),
        (('div',), {'class_': 'platform-link-icons-wrapper'}, -1)
    ]
    soup = get_tag(soup, path)
    if soup is None:
        err(stat, 'platforms')
        return
    soups = soup.find_all('svg')
    result = []
    for svg in soups:
        if svg.has_attr('title'):
            result.append(svg['title'])
        else:
            err(stat, 'platform title')
    stat['platforms'] = result


def get_from_game_info_details(stat, soup):
    path = [
        (('div',), {'class_': 'game-info-details'}, -1)
    ]
    soup = get_tag(soup, path)
    if soup is None:
        err(stat, 'game-info-details')
        return
    get_release_date(stat, soup)
    get_developer(stat, soup)
    get_from_reviews(stat, soup)
    get_platforms(stat, soup)


def get_genres(stat, soup):
    path = [
        (('div',), {'id': 'game-info-genres'}, -1),
        (('div',), {'class_': 'tags-list badges-container'}, -1)
    ]
    soup = get_tag(soup, path)
    if soup is None:
        err(stat, 'genres')
        return
    soups = soup.find_all('a')
    stat['genres'] = [a.get_text() for a in soups]


def get_tags(stat, soup):
    path = [
        (('div',), {'id': 'game-info-tags'}, -1),
        (('div',), {}, -1)
    ]
    soup = get_tag(soup, path)
    if soup is None:
        err(stat, 'tags')
        return
    soups = soup.find_all('a')
    stat['tags'] = [a.get_text() for a in soups]


def get_features(stat, soup):
    path = [
        (('div',), {'id': 'game-info-features'}, -1),
        (('div',), {}, -1)
    ]
    soup = get_tag(soup, path)
    if soup is None:
        err(stat, 'features')
        return
    soups = soup.find_all('a')
    stat['features'] = [a.get_text() for a in soups]


def get_from_game_offers_col_right(stat, soup):
    path = [
        (('div',), {'class_': 'col-right'}, -1),
        (('div',), {'class_': 'game-info-content shadow-box-big-light'}, -1)
    ]
    soup = get_tag(soup, path)
    if soup is None:
        err(stat, 'game-offers-col-right')
        return
    get_from_game_info_details(stat, soup)
    get_genres(stat, soup)
    get_tags(stat, soup)
    get_features(stat, soup)


def get_href(hover):
    soup = hover.find('a')
    if soup is None or not soup.has_attr('href'):
        pass
    else:
        return 'https://gg.deals' + soup['href']


def get_dlcs(stat, soup):
    path = [
        (('section',), {'id': 'game-dlcs'}, -1),
    ]
    soup = get_tag(soup, path)
    if soup is None:
        err(stat, 'dlcs')
        return
    soups = soup.find_all('div', class_=namer(consist, 'hoverable-box'))
    result = []
    for hover in soups:
        href = get_href(hover)
        if href is not None:
            result.append(href)
        else:
            err(stat, 'dlcs href')
    stat['dlcs'] = result


def get_packs(stat, soup):
    path = [
        (('section',), {'id': 'game-packs'}, -1),
    ]
    soup = get_tag(soup, path)
    if soup is None:
        err(stat, 'packs')
        return
    soups = soup.find_all('div', class_=namer(consist, 'hoverable-box'))
    result = []
    for hover in soups:
        href = get_href(hover)
        if href is not None:
            result.append(href)
        else:
            err(stat, 'packs href')
    stat['packs'] = result


def get_from_game_offers_col_left(stat, soup):
    path = [
        (('div',), {'class_': 'game-section section-row'}, -1)
    ]
    soup = get_tag(soup, path)
    if soup is None:
        err(stat, 'game-offers-col-left')
        return
    get_dlcs(stat, soup)
    get_packs(stat, soup)


def get_from_game_offers(stat, soup):
    path = [
        (('div',), {'class_': 'game-section game-offers'}, -1),
        (('div',), {'class_': 'container'}, -1)
    ]
    soup = get_tag(soup, path)
    if soup is None:
        err(stat, 'game-offers')
        return
    get_from_game_offers_col_right(stat, soup)
    get_from_game_offers_col_left(stat, soup)


def get_price_history(stat, soup):
    path = [
        (('div',), {'class_': 'game-section game-about game-price-history'}, -1),
        (('div',), {'class_': 'container'}, -1),
        (('div',), {'class_': 'col-left'}, -1),
        (('div',), {'class_': 'chart-container'}, -1)
    ]
    soup = get_tag(soup, path)
    if soup is None or not soup.has_attr('data-with-keyshops-url'):
        err(stat, 'price_history')
        return
    url = soup['data-with-keyshops-url']
    n = 0
    max_n = 5
    while n < max_n:
        try:
            response = requests.get(
                'https://gg.deals' + url,
                headers={
                    'accept': 'application/json',
                    'path': url,
                    'scheme': 'https',
                    'method': 'GET',
                    'accept-encoding': 'gzip, deflate, br',
                    'authority': 'gg.deals',
                    'x-requested-with': 'XMLHttpRequest',
                    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
                }
            )
        except ...:
            n += 1
        else:
            break
    if n == max_n:
        err(stat, 'price_history fetch')
        return
    response = response.json()['chartData']['deals']
    for it in response:
        it['ts'] = it['x']
        it['price'] = it['y']
        del it['name']
        del it['x']
        del it['y']
    stat['price_history'] = response


def get_from_game_card(stat, soup):
    path = [
        (('div',), {'class_': 'game-card'}, -1),
    ]
    soup = get_tag(soup, path)
    if soup is None:
        err(stat, 'game-card')
        return
    get_from_game_info_image(stat, soup)
    get_from_game_collection_actions(stat, soup)
    get_from_game_offers(stat, soup)


def get_from_main_content_page(stat, soup):
    path = [
        (('div',), {'class_': 'main-content'}, -1),
        (('div',), {'id': 'page'}, -1),
    ]
    soup = get_tag(soup, path)
    if soup is None:
        err(stat, 'main-content-page')
        return
    get_name(stat, soup)
    get_from_game_card(stat, soup)


def get_page(url, n_attempts=5, t_sleep=0.1):
    n = 0
    while n < n_attempts:
        try:
            req = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            return urllib.request.urlopen(req)
        except ...:
            n += 1
            time.sleep(t_sleep)


def collect_stat(url):
    res = get_page(url)
    if res is None:
        err({'url': url}, 'fetch')
        return None
    data = res.read().decode(encoding='utf-8')
    soup = bs4.BeautifulSoup(data, 'html.parser')
    stat = {}
    soup = soup.html.body
    stat['url'] = url
    get_from_main_content_page(stat, soup)
    get_price_history(stat, soup)
    return stat


smth = collect_stat('https://gg.deals/game/descent-2')
print(*smth.items(), sep='\n')
