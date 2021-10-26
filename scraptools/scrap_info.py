from urllib.request import urlopen
from bs4 import BeautifulSoup, BeautifulStoneSoup
import re

import fptools.fptools as fp
from .test_geocode import is_latitude, is_longitude
from .get_address import get_address_from_geo


#########################################
#         SCRAPRING THE ADVERT          #
#########################################

# On a single Advert page, the following information are retrieve:
#     - id
#     - rent (price and frequence. ie. 2000 / month)
#     - type ('house', 'flat', ...)
#     - overview
#     - facilities (opt.)
#     - BER (opt.)
#     - description
#     - author
#     - geolocation ( lat/long and addresses)

##############################
#         ADVERT ID          #
##############################


# first extract:
# <p class="DaftIDText__StyledDaftIDParagraph-vbn7aa-0 iWkymm">
# Daft ID: <!-- -->26455566
# </p>
# then text
# Alternative : ad.find('p', {'class':'iWkymm'}).get_text()
def extract_id(ad):
    return ad.find('p', {'class': re.compile('DaftIDText.')}).get_text()


# format from Daft ID: 26369624 to 26369624
def format_id(ad_id):
    return ad_id.lstrip('Daft ID: ')


get_ad_id = fp.compose(format_id, extract_id)


##############################
#       ADVERT RENT          #
##############################


# ie retrieve "€3,100 per month"
def extract_price(ad):
    price = ad.find('div', {'data-testid': 'price'})
    return price.p.span.get_text() if price else 'NaN'


# ie retrieve "month" from "€3,100 per month"
def format_payment_frq(price):
    return 'month' if 'per month' in price else 'week'


# ie format 3,100 from from "€3,100 per month"
def format_price(price):
    return price.split()[0].lstrip('€').replace(',', '')


# compose type functions
get_payment_frq = fp.compose(format_payment_frq, extract_price)

# compose price functions
get_price = fp.compose(format_price, extract_price)


# When one information
# is split in two.
# ie RENT is two information Price and the Frequency
# init_format_compose from fp is used.
# init_format_compose performes as follow:
# vals = [f(x) for f in funcs]
# {key: vals[i] for i, key in enumerate(keys.values())}
#
# Format to data:  {'Price': '3,100', 'Type': 'month'}
get_rent = fp.init_format_compose(
    get_price, get_payment_frq, k_1='Price', k_2='Type')


##############################
#        ADVERT TYPE         #
##############################


# Retrieve 'House' fom <p data-testid='property-type'>
def get_property_type(ad):
    property_type = ad.find('p', {'data-testid': 'property-type'})
    return property_type.get_text() if property_type else 'NaN'


##############################
#      ADVERT OVERVIEW       #
##############################


# ie Retrieve list of following:
# <li>
# <span
# class="PropertyPage__ListLabel-sc-14jmnho-10 ssSHo">
# Double Bedroom
# </span>
# : <!-- -->4
# </li>
def extract_overview(ad):
    overview = ad.find('div', {'data-testid': 'overview'})
    return overview.ul.children if overview else 'NaN'


# Iterate thought map() when curry with filter_map_4
# ie retrive [['Double Bedroom', ' 4'], ['Available From', ' Immediately'], ...]
def format_overview(overview_li): return overview_li.get_text().split(':')


# Filter with fitler() when curry in filter_map_4.
# Remove some "overview" from oveview list.
# ie: remove 'Available From'
# and produces: [['Available From', ' Immediately'], ...]
def init_useful_overview(*useful_overview):
    def is_useful_overview(overview):
        if overview[0] in useful_overview:
            return overview

    return is_useful_overview


# Only keep the following:
# 'Double Bedroom', 'Single Bedroom',
# 'Bathroom', 'Furnished', 'Lease'
is_useful_overview = init_useful_overview(
    'Double Bedroom', 'Single Bedroom', 'Bathroom', 'Furnished', 'Lease')


# Format nested list to dictionary
# ie {'Double Bedroom': '4',
#  'Bathroom': '3', ...}
def format_filtered_overview(filtered_overview):
    return {overview[0]: overview[1].strip(' ') for overview in filtered_overview}


def format_filtered_overview(filtered_overview):
    overview_dic = {'Double Bedroom': None,
                    'Single Bedroom': None,
                    'Bathroom': None,
                    'Furnished': None,
                    'Lease': None}

    for overview in filtered_overview:
        overview_dic[overview[0]] = overview[1].strip(' ')

    return overview_dic


# Function filter_map_4 schema is as follow:
# format_filtered_overview
# (filter(is_useful_overview,
# map(format_overview, extract_overview(ad))))
#
# ie From
# list of <li> <span ... Double Bedroom ... 4</li>
# to  {'Double Bedroom': '4', 'Bathroom': '3',...}
get_overview = fp.filter_map_4(
    format_filtered_overview, is_useful_overview, format_overview, extract_overview)


##############################
#     ADVERT FACILITIES      #
##############################

# Optional information
# not all adverts have
# facilities list
# hence the if statement
# and return 'NaN' is no facilities
def get_facilities(ad):
    div = ad.find('div', {'data-testid': 'facilities'})
    if div:
        return [li.get_text() for li in div.ul.children]
    else:
        return 'NaN'


##############################
#          ADVERT BER        #
##############################


# BER is an optional information
# Some advert don't have BER.

# When availalbe, when looks as followed
# in html: <div ...> <img alt='A3' /></div>

# The 'alt' is the value to access.

# BER is an optional information
# Some advert don't have BER.

# Hence when retrieving the BER with
# div = ad.find('div', {'data-testid': 'ber'})

# If statement made on to test
# if empty return NaN
# if not retrieve alt value
# with a convertion if alt is 'SI_666' => BER EXEMPT

# If BER is 'BER EXEMPT' in the advert
# the alt value is 'SI_666'
# Therefor convert to str 'BER EXEMPT'
def convert_ber_exempt(ber):
    return 'BER EXEMPT' if ber == 'SI_666' else ber


def init_get_ber_id(fun):
    def get_ber_id(ad):
        ber = ad.find('div', {'data-testid': 'ber'})
        return fun(ber.img['alt']) if ber else 'NaN'
    return get_ber_id


get_ber_id = init_get_ber_id(convert_ber_exempt)


# BER can also have an optional number
# With the EIRE CODE can provide
# additional information
# (never manages to access those information)
# can't test validity of number
# since optional if statement is required
def get_ber_number(ad):
    ber_number = ad.find('p', {'data-testid': 'ber-code'})
    return ber_number.get_text().lstrip('BER No: ') if ber_number else 'NaN'

# format both BER and BER number
# to a Dictionary as follow
# def init_get_ber(func_1, func_2):
#     def get_ber(ad):
#         return {'BER': func_1(ad), 'BER n': func_2(ad)}
#     return get_ber


# When one information
# is split in two.
# ie BER is two information BER and the BER number
# init_format_compose from fp is used.
# init_format_compose performes as follow:
# vals = [f(x) for f in funcs]
# {key: vals[i] for i, key in enumerate(keys.values())}
# ie: {'BER': 'BER EXEMPT', 'BER n': 'NaN'}
get_ber = fp.init_format_compose(
    get_ber_id, get_ber_number, k_1='BER', k_2='BER n')

##############################
#       ADVERT AUTHOR        #
##############################


def get_ad_author(ad): return ad.find(
    'p', {'class': re.compile('ContactPanel__ImageLabel.')}).get_text()


##############################
#     ADVERT DESCRIPTION     #
##############################

# Description is large text with
# some escape sequence, Asterisk.
# We tried to clean the text as best as possible


def extract_description(ad): return ad.find(
    'div', {'data-testid': 'description'}).get_text()


def format_description(description): return description.lstrip(
    'Description**').replace('\r', '').replace('\n', ' ')


# compose follow the classic form of
# 1- extract information
# 2- format information
get_description = fp.compose(format_description, extract_description)


##############################
#     ADVERT GEOLOCATION     #
##############################

# 3 information are related to GEOLOCATION:
#     - geocoloation (lat/long)
#     - the address from the advert
#     - the address from geocoder


#     ADVERT GEOLOCATION LAT/LONG     #

def extract_geo(ad): return ad.find(
    'a', {'data-testid': 'streetview-button'})['href']


def format_geo(geo): return geo.lstrip(
    'https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=').split(',')


def init_test_geo(func_1, func_2):
    def test_geo(lat_long):
        lat, long = lat_long
        tested_lat = func_1(lat)
        tested_long = func_2(long)
        return tested_lat, tested_long

    return test_geo


test_geo = init_test_geo(is_latitude, is_longitude)


def format_tested_geo(tested_geo):
    tested_lat, tested_long = tested_geo
    return {'Latitude': tested_lat, 'Longitude': tested_long}


get_tested_geo = fp.compose_4(
    format_tested_geo, test_geo, format_geo, extract_geo)


#     ADVERT ADDRESS FRON DAFT     #
def get_address(ad):
    address = ad.find('h1', {'data-testid': 'address'})
    return address.get_text() if address else 'NaN'


#     CURRY ALL    #
# last function retrieve address from geocoder
# with teh given geolocation lat/long
# to increade performance could be remove
# fetched_address = fp.compose_4(
#     get_address_from_geo, test_geo, format_geo, extract_geo)

# get_addresses = fp.init_format_compose(
#     get_address, fetched_address, k_1='Advert', k_2='Fetched')


get_ad_data = fp.init_format_compose(get_ad_id, get_price, get_payment_frq,
                                     get_address, get_property_type,
                                     get_facilities, get_ber_id, get_ber_number, get_ad_author,
                                     get_description, k_1='id', k_2='Rent', k_3='Frequence',
                                     k_4='Address', k_5='Type',
                                     k_6='Facilities', k_7='Ber', k_8='Ber n', k_9='Author',
                                     k_10='Description')
if __name__ == "__main__":
    print('main : to be build')
