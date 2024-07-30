"""Homeworks exceptions."""


class HomeworksException(Exception):
    """Base class for exceptions."""


class HomeworksConnectionFailed(HomeworksException):
    """Connection failed."""


class HomeworksConnectionLost(HomeworksException):
    """Connection lost."""
