from django.utils.translation import ugettext_lazy as _

# Row based
DEFAULT_LIMIT = 100

# Excel
DEFAULT_SHEET = '0'

DATA_TYPE_STRING = 1
DATA_TYPE_NUMBER = 2
# TODO: DATA_TYPE_AUTO = 3
# TODO: Boolean

DATA_TYPE_CHOICES = (
    (DATA_TYPE_STRING, _('String')),
    (DATA_TYPE_NUMBER, _('Number')),
)


def convert_to_number(data):
    #int(re.sub(r'[^\d-]+', '', data))
    try:
        if '.' in data:
            return float(data.replace(',', '').replace('$', ''))
        else:
            return int(data.replace(',', '').replace('$', ''))
    except Exception:
        return str(data)


DATA_TYPE_FUNCTIONS = {
    DATA_TYPE_STRING: lambda x: str(x).strip(),
    DATA_TYPE_NUMBER: lambda x: convert_to_number(x),
}
