from pandas.errors import ParserError


class CSVParseError(ParserError):
    def __init__(self, message, cause):
        super(CSVParseError, self).__init__(message + ', caused by ' + repr(cause))
        self.cause = cause


class JavaNotFoundError(Exception):
    pass
