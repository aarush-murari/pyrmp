"""
Custom exceptions for pyrmp.

This module defines exceptions specific to the RateMyProfessor API wrapper.
"""

from typing import Optional, Any


class RateMyProfessorError(Exception):
    """
    Base exception for all pyrmp errors.

    All other exceptions in this module inherit from this class.
    """

    pass


class NotFoundError(RateMyProfessorError):
    """
    Raised when a requested resource cannot be found.

    This may occur when searching for a teacher or school that doesn't exist,
    or when fetching details for an invalid ID.
    """

    pass


class APIError(RateMyProfessorError):
    """
    Raised when the RateMyProfessor API returns an error.

    This includes HTTP errors (4xx, 5xx responses) and GraphQL-level errors.

    Attributes:
        status_code: The HTTP status code if available.
        response_data: Raw response data if available.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Any] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

    def __str__(self):
        if self.status_code:
            return f"{self.args[0]} (Status: {self.status_code})"
        return str(self.args[0])


class PaginationError(RateMyProfessorError):
    """
    Raised when pagination operations fail.

    This may occur when an invalid cursor is provided or when
    attempting to fetch pages beyond the available results.
    """

    pass


class InvalidQueryError(RateMyProfessorError):
    """
    Raised when query parameters are invalid.

    This includes cases like:
    - count parameter out of valid range (1-100)
    - Empty search queries when required
    - Invalid filter values
    """

    pass
