from django.utils.translation import ugettext_lazy as _

# Row based
DEFAULT_LIMIT = 100

# Excel
DEFAULT_SHEET = '0'

DATA_TYPE_STRING = 1
DATA_TYPE_NUMBER = 2
# TODO: DATA_TYPE_AUTO = 3

DATA_TYPE_CHOICES = (
    (DATA_TYPE_STRING, _('String')),
    (DATA_TYPE_NUMBER, _('Number')),
)

DATA_TYPE_FUNCTIONS = {
    DATA_TYPE_STRING: lambda x: str(x).strip(),
    DATA_TYPE_NUMBER: lambda x: float(x.replace(',', '').replace('$', '')) if '.' in x else int(x.replace(',', '').replace('$', ''))
}
