from rest_framework.exceptions import ParseError


class Http400(ParseError):
    pass
