def compose(g, f):
    """
    Curry function of 3 paramters in the form:
    g(f(x))
    or 
    compose(g -> f) (x)

    Parameters:
    -----------
    g, f (function)
        The first function, f, applied to x
        The second function, g, applied to f(x)

    Returns:
    --------
        h (function) 
            The function that parses x

            Parameters:
            -----------
                x (*)
                    A given value

            Returns:
            --------
                x (*)
                    Under form g(f(x))

    Application:
    ------------
    compose(g, f)(x)

    """
    def h(x):
        return g(f(x))
    return h


def compose_3(h, g, f):
    """
    Curry function of 4 paramters in the form:
    h(g(f(x)))
    or 
    compose(h-> g -> f) (x)

    Parameters:
    -----------
    h, g, f(function)
        The first function, f, applied to x
        The second function, g, applied to f(x)
        The third function, h, applied to g(f(x))

    Returns:
    --------
        i (function) 
            The function that parses x

            Parameters:
            -----------
                x (*)
                    A given value

            Returns:
            --------
                x (*)
                    Under form h(g(f(x)))
    Application:
    ------------
    compose(h, g, f)(x)
    """
    def i(x):
        return h(g(f(x)))
    return i


def compose_4(i, h, g, f):
    """
    Curry function of 5 paramters in the form:
    i(h(g(f(x))))
    or 
    compose(i->h-> g -> f) (x)

    Parameters:
    -----------
    i, h, g, f(function)
        f: The first function, f, applied to x, 
        so that's f(x)

        g: The second function, g, applied to f(x),
        so that's g(f(x))

        h: The thrid function, h, applied to g(f(x)),
        so that's h(g(f(x)))

        i: The fouth function, i, applied to g(f(x)),
        so that i(g(f(x)))

    Returns:
    --------
        j (function) 
            The function that parses x

            Parameters:
            -----------
                x (*)
                    A given value

            Returns:
            --------
                x (*)
                    Under form h(g(f(x)))
    Application:
    ------------
    compose(i, h, g, f)(x)
    """
    def j(x):
        return i(h(g(f(x))))
    return j


def compose_args(*funcs):
    """
    Curry function of *funcs paramters in the form:
    compose_args(*funcs)(x)

    Parameters:
    -----------
    *funcs (tuple)
        Tuple of functions successively applies to a given value. 

    Returns:
    --------
        init (function) 
            The function that parses x

            Parameters:
            -----------
                x (*)
                    A given value

            Returns:
            --------
                x (*)
                    Under form g(f(x))

    Application:
    ------------
    compose_args(g, f)(x)
    or 
    compose_args(h, g, f)(x)

    """
    def init(x):
        if len(funcs) == 0:
            return x
        else:
            func = funcs[-1]
            back_funcs = funcs[:-1]
            y = func(x)
            return compose_args(*back_funcs)(y)
    return init


def filter_map_2(filter_g, map_f):
    def h(x):
        return filter(filter_g, map(map_f, x))
    return h


def filter_map_3(filter_h, map_g, f):
    def i(x):
        return filter(filter_h, map(map_g, f(x)))
    return i


def filter_map_4(i, filter_h, map_g, f):
    def j(x):
        return i(filter(filter_h, map(map_g, f(x))))
    return j


def init_format_compose(*funcs, **keys):
    def format_compose(x):
        vals = [f(x) for f in funcs]
        return {key: vals[i] for i, key in enumerate(keys.values())}
    return format_compose


if __name__ == "__main__":
    print('main : to be build')
