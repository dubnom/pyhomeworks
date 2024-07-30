"""Homeworks exceptions."""

class HomeworksException(Exception):
    """Base class for exceptions."""


class HomeworksConnectionLost(HomeworksException):
    """Connection lost."""
