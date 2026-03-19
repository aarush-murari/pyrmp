"""
Custom exceptions for RateMy GraphQL API wrapper
"""

from typing import Optional, Any


class RateMyProfessorError(Exception):
    """Base exception for RateMyProfessor API errors"""

    pass


class NotFoundError(RateMyProfessorError):
    """Raised when a resource is not found"""

    pass


class APIError(RateMyProfessorError):
    """Raised when the API returns an error response"""

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
    """Raised when pagination fails"""

    pass


class InvalidQueryError(RateMyProfessorError):
    """Raised when a query is invalid"""

    pass
