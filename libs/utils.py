import re


def camel2snake(s, delimiter="_"):
    return re.sub(r'([a-z0-9])([A-Z])', r'\1{}\2'.format(delimiter), s).lower()


def tuple2dict(tpl, keys, many=False):
    convert = lambda t: dict(zip(keys, t))
    if many:
        yield from map(convert, tpl)
    else:
        return convert(tpl)
