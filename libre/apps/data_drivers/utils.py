import csv, codecs


# http://stackoverflow.com/questions/4248399/page-range-for-printing-algorithm
def parse_range(astr):
    result = set()
    for part in astr.split(u','):
        x = part.split(u'-')
        result.update(range(int(x[0]), int(x[-1]) + 1))
    return sorted(result)


def convert_to_number(data):
    #int(re.sub(r'[^\d-]+', '', data))
    if '.' in data:
        return float(data.replace(',', '').replace('$', ''))
    else:
        return int(data.replace(',', '').replace('$', ''))


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        try:
            return self.reader.next().encode('utf-8')
        except UnicodeDecodeError:
            # Ignore unknown encoded rows
            return ''
            #try:
            #    return unicode(self.reader.next(), 'iso-8859-1')
            #except:
            #    return ''


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding='utf-8', **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        if row:
            return [unicode(s, 'utf-8') for s in row]
        else:
            return []

    def __iter__(self):
        return self
