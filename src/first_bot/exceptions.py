class BotException(Exception):
    """Base exception for the bot."""


class FileReadError(BotException):
    """Raised when a file cannot be read."""


class ValidationFailedError(BotException):
    """Raised when validation of a row fails."""


class SubmissionError(BotException):
    """Raised when submitting a request to the web form fails."""
