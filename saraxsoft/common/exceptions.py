"""Custom exception class for errors."""

from __future__ import annotations


class BaseError(Exception):
    """
    Base class for all exceptions.

    Attributes
    ----------
    message : str
        The error message.
    """

    message: str

    def __init__(self, message: str) -> None:
        """
        Initialize the BaseError.

        Parameters
        ----------
        message : str
            The error message.
        """
        self.message = message
