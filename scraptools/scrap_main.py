import fptools.fptools as fp

from urllib.request import urlopen
from bs4 import BeautifulSoup, BeautifulStoneSoup


##############################
#          INIT URL          #
##############################


def init_url(county, page=0):
    return {
        'base': 'https://www.daft.ie',
        'general_search': '/property-for-rent/',
        'county': county,
        'pages': f'?from={page}&pageSize=20'
    }


# Get HTML APP

def init_get_app(parser):

    def get_app(*urls):
        url = ''.join(urls)
        html = urlopen(url)
        return BeautifulSoup(html.read(), parser)

    return get_app


def try_action(func):

    def init_action(*args):

        try:
            res = func(*args)

        except Exception as e:
            print(e)
        else:
            return res

    return init_action


def extract_ads(daft):
    children = daft.find('ul', {'data-testid': 'results'}).children
    return list(filter(lambda el: el.name == 'li', children))


def get_sub(ad):
    return ad.find('div', {'data-testid': 'sub-units-container'})


def if_sub_get_lis(sub):
    return sub.find('ul', {'data-testid': 'sub-units'}).find_all('li')
