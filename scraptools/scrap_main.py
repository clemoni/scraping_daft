import fptools.fptools as fp

from urllib.request import HTTPPasswordMgrWithDefaultRealm, urlopen
from bs4 import BeautifulSoup, BeautifulStoneSoup

from tqdm import tqdm
from time import sleep
from datetime import date

from . import scrap_info as si
# import scrap_info as si


##############################
#          INIT URL          #
##############################

# Application
# url = sc.init_url('cork')  > init dictionary for county and page
# get_app = sc.init_get_app('lxml') > specified parser type
# get_daft = sc.try_action(get_app) > init the capture of html

# > run capture of hmtl
# daft = get_daft(url['base'], url['general_search'], url['county'], url['pages'])

# if issue print error
# Not my create error log file


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


# The main page, list the property
# under structure ul > li
# After grabing ul.children
# need to filter to keep only li
def extract_ads(daft):
    children = daft.find('ul', {'data-testid': 'results'}).children
    return list(filter(lambda el: el.name == 'li', children))

# Some advert in property list
# advert a main buidling (ie: the Altus complex)
# and then list available type of property
# available within this complex
# required to test if advert is unique advert of
# "wrapper" of differnet subs advert
# happend to Dublin ++


def get_sub(ad):
    return ad.find('div', {'data-testid': 'sub-units-container'})

# After if statement
# if there is subs adv under a wrapper ad
# get the list of these property


def if_sub_get_lis(sub):
    return sub.find('ul', {'data-testid': 'sub-units'}).find_all('li')


##############################
#       PARSE ADVERT         #
##############################

# create dictionary for each advert listed in main Daft rent page

# Since get_daft cn only be accessible
# though main script, it requires to do
# a bit of fitting between args and functions
# To have schema of all the functions
# togeter see compose_ace and extract_and_get_data_ads

# In addition the the info collection with function
# from scrap_info, the following info are
# also added:
#     - advert href
#     - created_at (first moment the app has been collected)
#     - closed_at (when app is gone)
#     - Close if advert is close

def init_parse_advert(get_ad_data):
    def insert_get_daft(get_daft, url):
        def parse_advert(li):
            ad_href = li.a['href']

            ad = get_daft(url['base'], ad_href)
            ad_data = get_ad_data(ad)
            ad_data['url'] = ad_href
            ad_data['Created_at'] = date.today()
            ad_data['Closed_at'] = None
            ad_data['Close'] = False
            geo = si.get_tested_geo(ad)
            ov = si.get_overview(ad)

            return ad_data | ov | geo

        return parse_advert
    return insert_get_daft


def test_main_ad_has_price(ad):
    price = ad.find('div', {'data-testid': 'price'}).get_text()
    return price.split()[0].lstrip('€').replace(',', '').isdigit()


#########################################
#      extract_and_get_data_ads         #
#########################################

# Heart of the collect of info for each adverts.

# first for/loop, iterates through the advert list
# if one advert is wrapper (incluse sub-ads ie: Elysian Cork)
#     collect the subs adverts and call parse_advert()
# When regular ads, parse_advert is call upon each advert.

# return res

def init_get_data_ads(get_sub, if_sub_get_lis, parse_advert):

    def insert_get_daft(get_daft, url):

        def get_data_ads(ads):
            res = []
            parse_advert_from_daft = parse_advert(get_daft, url)

            for ad in tqdm(ads):  # iterate for each advert on the current page
                sleep(0.25)

                if sub := get_sub(ad):  # if there is sub adverts

                    # get the list of sub-adverts
                    sub_ads = if_sub_get_lis(sub)

                    for sub_ad in sub_ads:  # and iterates thouth those sub-adverts

                        # for each: go to the web page of the advert
                        res.append(parse_advert_from_daft(sub_ad))
                        # and get the info
                else:
                    # test created to filter real ad
                    # issue with some "advert"
                    if test_main_ad_has_price(ad):
                        res.append(parse_advert_from_daft(ad))
                    # else:
                    #     res.append(parse_advert_from_daft(ad))

            return res
        return get_data_ads
    return insert_get_daft


def compose_ace(g, f):
    def init(*args):
        def h(x):
            return g(*args)(f(x))
        return h
    return init


parse_advert = init_parse_advert(si.get_ad_data)

get_data_ads = init_get_data_ads(get_sub, if_sub_get_lis, parse_advert)

extract_and_get_data_ads = compose_ace(get_data_ads, extract_ads)


##############################
#       CALCUL LIMIT         #
##############################

# Get the total adverts
# knowing there are 20 adverts per page
# calculate the number of page that would need
# to go though


def extract_ads_count(daft): return daft.main.find(
    'h1', {'data-testid': 'search-h1'}).get_text()


def format_ads_counts(extracted_counts):
    return [int(str) for str in extracted_counts.split() if str.isdigit()][0]


get_ads_counts = fp.compose(format_ads_counts, extract_ads_count)


def calc_lim(num_ads):
    if num_ads % 20 != 0:
        return num_ads + 20
    else:
        return num_ads


get_calculated_limit = fp.compose_3(
    calc_lim, format_ads_counts, extract_ads_count)

##################################
#        GET_ADDS_BY_PAGE        #
##################################


def init_get_adds_by_page(get_daft):
    def get_adds_by_page(limit, county, page=0, res=[]):
        if page > (limit):
            return res
        else:
            url = init_url(county, page)
            daft = get_daft(url['base'], url['general_search'],
                            url['county'], url['pages'])
            res.append(extract_and_get_data_ads(get_daft, url)(daft))
            next_page = page+20
            return get_adds_by_page(limit, county=county, page=next_page, res=res)
    return get_adds_by_page


####################################
#        FLATTEN THE RESULT        #
####################################

# Because of the limit with
# adds to make sure that
# all the ads ares collected
# the final list result has empty array.

# Therefore filter_empty_ads removes those
# empty list.

# Finaly, we flatten the nested list to have only one array.


def filter_empty_ads(res): return [ads for ads in res if len(ads) != 0]


def unpack_res(res):
    out = []
    for ads in res:
        out = [*out, *ads]
    return out


flatten_data_ads = fp.compose(unpack_res, filter_empty_ads)
