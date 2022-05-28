from pandas.errors import ParserError  # type: ignore


class CSVParseError(ParserError):
    """Error represents CSV parse error, which mainly caused by pandas."""

    def __init__(self, message, cause) -> None:
        super(CSVParseError, self).__init__(message + ", caused by " + repr(cause))
        self.cause = cause


class JavaNotFoundError(Exception):
    """Error represents Java doesn't exist."""

    pass
