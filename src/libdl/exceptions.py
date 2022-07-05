class Error(Exception):
    """Base class for all exceptions."""


class ClientError(Error):
    """Raised when responses has 4xx status."""


class ServerError(Error):
    """Raised when responses has 5xx status."""


class InvalidURL(Error):
    """Raised when there is an invalid URL."""
