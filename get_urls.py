import sys
import bs4
import urllib.request as request


def namer(func, name):
    def wrapper(name_):
        return func(name_, name)
    return wrapper


def cmp_with_name(name_, name):
    return name_ == name


def naming(name):
    return namer(cmp_with_name, name)


def has_my_attr(tag, name):
    return tag.has_attr(name)


def get_names(html):
    soup = bs4.BeautifulSoup(html, 'html.parser')
    games_tag = soup.find_all(class_=naming('grid-list games-hover-boxes'))[0]
    games_tags = games_tag.find_all(namer(has_my_attr, 'data-game-name'))
    return [tag['data-game-name'] for tag in games_tags]


def fetch_url(url, max_attempts=50):
    attempts = 0
    while attempts < max_attempts:
        try:
            req = request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            return request.urlopen(req).read().decode(encoding='utf-8')
        except ...:
            pass
        attempts += 1
    raise TimeoutError


def fetch_urls():
    num = 1
    names = []
    aim = 300
    url = 'https://gg.deals/games/?sort=metascore&type=1&page='
    while len(names) < aim:
        try:
            text = fetch_url(url + str(num))
            names += get_names(text)
        except TimeoutError:
            return num
        num += 1
    return names


games = fetch_urls()
if isinstance(games, int):
    print(games, file=sys.stderr)
else:
    with open('urls.txt', 'w') as file:
        for game in games[:300]:
            print('https://gg.deals/game/' + game, file=file)
