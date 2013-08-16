from rest_framework.exceptions import ParseError


class Http400(ParseError):
    pass


class LIBREError(ParseError):
    pass


class LIBREValueError(LIBREError):
    pass


class LIBREFieldError(LIBREError):
    pass
