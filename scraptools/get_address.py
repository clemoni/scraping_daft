# module - use geocoder to get information
# get_address_fom_geo for latitute to longitude
# get returm simplied address

from geopy.geocoders import Nominatim
from random import randrange


def compose(g, f):
    def h(*x):
        return g(f(*x))
    return h


def init_rgeolocation():
    user_agent = 'Clemoni'+str(randrange(1000))+str(randrange(1000))

    def get_rgeolocation(*coord):

        return Nominatim(user_agent=user_agent).reverse(coord)

    return get_rgeolocation


def extract_address(geo):
    address = geo.raw['address']
    number, road, city_district, city, country, *rest = address.values()
    return f'{number} {road} {city_district}, {city}, {country}'


get_geo = init_rgeolocation()

get_address_from_geo = compose(extract_address, get_geo)
