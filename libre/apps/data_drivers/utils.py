# http://stackoverflow.com/questions/4248399/page-range-for-printing-algorithm
def parse_range(astr):
    result = set()
    for part in astr.split(u','):
        x = part.split(u'-')
        result.update(range(int(x[0]), int(x[-1]) + 1))
    return sorted(result)
