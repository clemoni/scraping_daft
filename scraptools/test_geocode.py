# module test geocode format

def is_float(num):
    """
    Test if given value can be convertible to float

    Parameters
    ----------
    num (str)
        A given 'string' number

    Raises
    ------
    ValueError
        If given number can't be convertible to float
        Print : "Value error: Not convertible to float:"

    Returns
    -------
    res (float)
        The converted number to float
    """
    try:
        res = float(num)
    except ValueError:
        print(f"Value error: Not convertible to float: '{num}'")
    else:
        return res


def is_geo_format(func):
    def wrapper(lat, geo_type):
        try:
            res = func(lat, geo_type)
        except Exception:
            print(f"Not in the expected format for {geo_type}: '{lat}'")
        else:
            return res

    return wrapper

# test latitude float fron -90 to 90


@is_geo_format
def is_latitude_format(lat, geo_type='latitute'):
    """
    Test if given float value matches the paramter of a latitude format. 
    A latitute format is expected to be between a float number between -90 to 90

    Parameters
    ----------
    lat (float)
        The given float number to be tested

    geo_type (str), default='latitute'
        The type of format tested. 
        It is used as an informative value when printing error message

    Raises
    ------
    Exception
        If failed the test
        Print : "Not in the expected format for latitude: '{lat}'"

    Returns
    -------
    res (str)
        The lat value tested
    """
    return str(lat) if lat > -90 and lat < 90 else False


# test longtitude float from -180 to 180
@is_geo_format
def is_longitude_format(long, geo_type='longitude'):
    """
    Test if given float value matches the paramter of a longitude format. 
    A latitute format is expected to be between a float number between -180 to 180

    Parameters
    ----------
    long (float)
        The given float number to be tested

    geo_type (str), default='longitude'
        The type of format tested. 
        It is used as an informative value when printing error message

    Raises
    ------
    Exception
        If failed the test
        Print : "Not in the expected format for longitude: '{long}'"

    Returns
    -------
    res (str)
        The longitude value tested
    """
    return str(long) if long > -180 and long < 180 else False


def geo_test(is_format, is_float):
    """
    Curry function applies successive test functions to a given value.
    To be applied for testing latitude and longitude with first if the value
    is convertible to float and if the value is in format longitude or latitude. 

    Parameters
    ----------
    is_format (function)
        Test function, check if value is in format longitude or latitude.

    is_float (function)'
        Test function, check if value can be convertible to float.

    Returns
    -------
    geo (float)
        The geo value tested
    """
    def init_geo_type(geo_type):

        def init_geo(geo):

            return is_format(is_float(geo), geo_type)

        return init_geo

    return init_geo_type


is_latitude = geo_test(is_latitude_format, is_float)(geo_type='latitute')
is_longitude = geo_test(is_longitude_format, is_float)(geo_type='longitude')


if __name__ == "__main__":
    print('main : to be build')
