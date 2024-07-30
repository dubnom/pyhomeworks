"""Homeworks exceptions."""


class HomeworksException(Exception):
    """Base class for exceptions."""


class HomeworksConnectionFailed(HomeworksException):
    """Connection failed."""


class HomeworksConnectionLost(HomeworksException):
    """Connection lost."""


class HomeworksAuthenticationException(HomeworksException):
    """Base class for authentication exceptions."""


class HomeworksNoCredentialsProvided(HomeworksAuthenticationException):
    """Credentials needed."""


class HomeworksInvalidCredentialsProvided(HomeworksAuthenticationException):
    """Invalid credentials."""
