"""
RateMyProfessor GraphQL API Wrapper (READ-ONLY)

A comprehensive Python wrapper for the RateMyProfessor GraphQL API.
This package provides READ-ONLY access to teacher and school ratings.

⚠️ NOTE: This package is read-only to avoid RateMyProfessor blocking the API.
For write operations (rating, bookmarking, etc.), use the separate pyrmp-write package.

Example usage:
    from pyrmp import RateMyProfessorClient

    client = RateMyProfessorClient()

    # Search for teachers
    teachers = client.search_teachers("Smith", count=10)
    for teacher in teachers.items:
        print(f"{teacher.full_name} - {teacher.avg_rating}/5")

    # Get teacher details
    details = client.get_teacher_details(teacher.id)
    print(f"Department: {details.department}")

    client.close()
"""

from .client import RateMyProfessorClient, search_teachers, search_schools
from .models import Teacher, School, Rating, SchoolRating, PaginatedResult
from .exceptions import (
    RateMyProfessorError,
    NotFoundError,
    APIError,
    PaginationError,
    InvalidQueryError,
)

__version__ = "0.1.0"
__all__ = [
    # Client
    "RateMyProfessorClient",
    "search_teachers",
    "search_schools",
    # Models
    "Teacher",
    "School",
    "Rating",
    "SchoolRating",
    "PaginatedResult",
    # Exceptions
    "RateMyProfessorError",
    "NotFoundError",
    "APIError",
    "PaginationError",
    "InvalidQueryError",
]
