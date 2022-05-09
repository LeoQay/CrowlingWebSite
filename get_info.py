import sys
import urllib.request

import bs4
import urllib.request as request


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
    stat['wishlist_count'] = int(soup.get_text())


def get_alert_counter(stat, soup):
    path = [
        ((), {'class_': namer(consist, 'alerted-game')}, -1),
        (('span',), {'class_': 'user-count'}, -1),
        (('span',), {'class_': 'count'}, -1)
    ]
    soup = get_tag(soup, path)
    stat['alert_count'] = int(soup.get_text())


def get_own_counter(stat, soup):
    path = [
        ((), {'class_': namer(consist, 'owned-game')}, -1),
        (('span',), {'class_': 'user-count'}, -1),
        (('span',), {'class_': 'count'}, -1)
    ]
    soup = get_tag(soup, path)
    stat['owners_count'] = int(soup.get_text())


def get_from_game_collection_actions(stat, soup):
    path = [
        (('div',), {'class_': 'game-header game-header-container container'}, -1),
        ((namer(has_attr, 'data-counters-url'),), {}, -1),
    ]
    soup = get_tag(soup, path)
    get_wishlist_counter(stat, soup)
    get_alert_counter(stat, soup)
    get_own_counter(stat, soup)


def get_release_date(stat, soup):
    path = [
        (('div',), {'class_': 'game-info-details-section game-info-details-section-release'}, -1),
        (('p',), {'class_': 'game-info-details-content'}, -1)
    ]
    soup = get_tag(soup, path)
    stat['release_date'] = soup.get_text()


def get_developer(stat, soup):
    path = [
        (('div',), {'class_': 'game-info-details-section game-info-details-section-developer'}, -1),
        (('p',), {'class_': 'game-info-details-content'}, -1)
    ]
    soup = get_tag(soup, path)
    stat['developer'] = soup.get_text()


def get_metacritic_score(stat, soup):
    path = [
        (('span',), {'class_': 'overlay'}, -1)
    ]
    soup = get_tag(soup, path)
    stat['metacritic_score'] = int(soup.get_text())


def get_user_score(stat, soup):
    path = [
        (('span',), {'class_': 'overlay'}, -1)
    ]
    soup = get_tag(soup, path)
    stat['user_score'] = float(soup.get_text())


def get_from_first_score(stat, soup):
    soups = soup.find_all('div', class_='score-col')
    get_metacritic_score(stat, soups[0])
    get_user_score(stat, soups[1])


def get_from_second_score(stat, soup):
    path = [
        (('a',), {'class_': 'score-grade'}, -1),
        (('span',), {}, -1)
    ]
    soup = get_tag(soup, path)
    text = soup.get_text().split()
    stat['review_label'] = ' '.join(text[:-1])
    stat['review_positive_pctg'] = int(soup['title'].split()[0][:-1])
    count = ''.join(text[-1].strip()[1:-1].split(','))
    stat['review_count'] = int(count)


def get_from_reviews(stat, soup):
    path = [
        (('div',), {'class_': 'game-info-details-section game-info-details-section-reviews'}, -1),
        (('div',), {'class_': 'game-info-details-content'}, -1)
    ]
    soup = get_tag(soup, path)
    soups = soup.find_all('div', class_='score')
    get_from_first_score(stat, soups[0])
    get_from_second_score(stat, soups[1])


def get_platforms(stat, soup):
    path = [
        (('div',), {'class_': 'game-info-details-section game-info-details-section-platforms'}, -1),
        (('div',), {'class_': 'platform-link-icons-wrapper'}, -1)
    ]
    soup = get_tag(soup, path)
    soups = soup.find_all('svg')
    stat['platforms'] = [svg['title'] for svg in soups]


def get_from_game_info_details(stat, soup):
    path = [
        (('div',), {'class_': 'game-info-details'}, -1)
    ]
    soup = get_tag(soup, path)
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
    soups = soup.find_all('a')
    stat['genres'] = [a.get_text() for a in soups]


def get_tags(stat, soup):
    path = [
        (('div',), {'id': 'game-info-tags'}, -1),
        (('div',), {}, -1)
    ]
    soup = get_tag(soup, path)
    soups = soup.find_all('a')
    stat['tags'] = [a.get_text() for a in soups]


def get_features(stat, soup):
    path = [
        (('div',), {'id': 'game-info-features'}, -1),
        (('div',), {}, -1)
    ]
    soup = get_tag(soup, path)
    soups = soup.find_all('a')
    stat['features'] = [a.get_text() for a in soups]


def get_from_game_offers_col_right(stat, soup):
    path = [
        (('div',), {'class_': 'col-right'}, -1),
        (('div',), {'class_': 'game-info-content shadow-box-big-light'}, -1)
    ]
    soup = get_tag(soup, path)
    get_from_game_info_details(stat, soup)
    get_genres(stat, soup)
    get_tags(stat, soup)
    get_features(stat, soup)


def get_href(hover):
    soup = hover.find('a')
    return 'https://gg.deals' + soup['href']


def get_dlcs(stat, soup):
    path = [
        (('section',), {'id': 'game-dlcs'}, -1),
    ]
    soup = get_tag(soup, path)
    soups = soup.find_all('div', class_=namer(consist, 'hoverable-box'))
    stat['dlcs'] = [get_href(hover) for hover in soups]


def get_packs(stat, soup):
    path = [
        (('section',), {'id': 'game-packs'}, -1),
    ]
    soup = get_tag(soup, path)
    soups = soup.find_all('div', class_=namer(consist, 'hoverable-box'))
    stat['packs'] = [get_href(hover) for hover in soups]


def get_from_game_offers_col_left(stat, soup):
    path = [
        (('div',), {'class_': 'game-section section-row'}, -1)
    ]
    soup = get_tag(soup, path)
    get_dlcs(stat, soup)
    get_packs(stat, soup)


def get_from_game_offers(stat, soup):
    path = [
        (('div',), {'class_': 'game-section game-offers'}, -1),
        (('div',), {'class_': 'container'}, -1),
    ]
    soup = get_tag(soup, path)
    get_from_game_offers_col_right(stat, soup)
    get_from_game_offers_col_left(stat, soup)


def get_from_game_card(stat, soup):
    path = [
        (('div',), {'class_': 'game-card'}, -1),
    ]
    soup = get_tag(soup, path)
    get_from_game_info_image(stat, soup)
    get_from_game_collection_actions(stat, soup)
    get_from_game_offers(stat, soup)


def get_from_main_content_page(stat, soup):
    path = [
        (('div',), {'class_': 'main-content'}, -1),
        (('div',), {'id': 'page'}, -1),
    ]
    soup = get_tag(soup, path)
    get_name(stat, soup)
    get_from_game_card(stat, soup)


def collect_stat(url):
    stat = {}

    # download html file
    with open('index.html', 'r') as file:
        soup = bs4.BeautifulSoup(file, 'html.parser')

    soup = soup.html.body

    stat['url'] = url
    get_from_main_content_page(stat, soup)

    return stat


smth = collect_stat('https://gg.deals/game/tricky-towers/')
print(*smth.items(), sep='\n')
