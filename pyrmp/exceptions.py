"""
Exception classes for pyrmp.

All exceptions in this module inherit from RateMyProfessorError, so you
can catch just that one base class if you don't care about specific errors.

Usage::

    from pyrmp import RateMyProfessorClient
    from pyrmp.exceptions import RateMyProfessorError, InvalidQueryError

    try:
        with RateMyProfessorClient() as client:
            teachers = client.search_teachers("Smith", count=10)
    except InvalidQueryError:
        print("Bad search parameters!")
    except RateMyProfessorError as e:
        print(f"Something went wrong: {e}")
"""

from typing import Optional, Any


class RateMyProfessorError(Exception):
    """
    Base exception for all pyrmp errors.

    Catch this to handle any error from this library.

    Usage::

        try:
            client.search_teachers("Smith")
        except RateMyProfessorError as e:
            print(f"Error: {e}")
    """

    pass


class NotFoundError(RateMyProfessorError):
    """
    Raised when a teacher, school, or rating doesn't exist.

    This happens when you try to get details for an ID that doesn't exist
    or has been removed from RateMyProfessor.

    Usage::

        try:
            teacher = client.get_teacher_details("some_id")
        except NotFoundError:
            print("Teacher not found")
    """

    pass


class APIError(RateMyProfessorError):
    """
    Raised when the RateMyProfessor API returns an error.

    This covers HTTP errors (like 500 server errors) and GraphQL-level errors.

    Attributes:
        status_code: HTTP status code (e.g., 500, 503). None for GraphQL errors.
        response_data: Raw response data if available (for debugging).

    Usage::

        try:
            client.search_teachers("Smith")
        except APIError as e:
            print(f"API error: {e}")
            if e.status_code:
                print(f"HTTP status: {e.status_code}")
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
    Raised when pagination fails.

    This might happen if you pass an invalid cursor string.

    Usage::

        try:
            next_page = client.search_teachers("Smith", cursor="bad_cursor")
        except PaginationError:
            print("Invalid pagination cursor")
    """

    pass


class InvalidQueryError(RateMyProfessorError):
    """
    Raised when search parameters are invalid.

    This happens when you pass bad values to methods like `search_teachers()`.
    Common causes:
    - `count` less than 1 or greater than 100
    - Empty search query (for methods that require one)

    Usage::

        try:
            client.search_teachers("Smith", count=200)  # Too many!
        except InvalidQueryError as e:
            print(f"Bad parameter: {e}")
    """

    pass
