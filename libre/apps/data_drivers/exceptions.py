from rest_framework.exceptions import APIException, ParseError


class LIBREError(Exception):
    pass


class SourceFileError(LIBREError):
    pass


class LIBREAPIError(ParseError):
    pass


class LQLParseError(LIBREError, LIBREAPIError):
    pass


class LQLFilterError(LIBREError, LIBREAPIError):
    pass


class LIBREFieldError(LIBREError, LIBREAPIError):
    pass


class LIBREValueError(LIBREError, LIBREAPIError):
    pass
