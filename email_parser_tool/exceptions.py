class EmailParserException(Exception):
    """
    Base exception class for the email parser.
    """
    pass

class InvalidEmailFormatException(EmailParserException):
    """
    Exception raised for invalid email formats.
    """
    pass
