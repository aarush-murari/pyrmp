"""
Data models for pyrmp.

This module provides Python dataclasses that represent the data structures
returned by the RateMyProfessor API.
"""

from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass
from datetime import datetime


@dataclass
class School:
    """
    Represents a school or university on RateMyProfessor.

    Attributes:
        id: The GraphQL node ID (base64 encoded).
        legacy_id: The original numeric RMP ID.
        name: Full school name.
        city: City where the school is located.
        state: State or region where the school is located.
        country: Country of the school.
        num_ratings: Total number of school ratings.
        avg_rating: Average overall rating (0.0-5.0).
        avg_rating_rounded: Average rating rounded to nearest 0.5.
        departments: List of departments at the school.
        summary: Detailed ratings for various school aspects.
    """

    id: str
    legacy_id: Optional[int] = None
    name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    num_ratings: Optional[int] = None
    avg_rating: Optional[float] = None
    avg_rating_rounded: Optional[float] = None
    departments: Optional[List[Dict[str, Any]]] = None
    summary: Optional[Dict[str, Any]] = None

    def __str__(self):
        parts = []
        if self.name:
            parts.append(self.name)
        location_parts = []
        if self.city:
            location_parts.append(self.city)
        if self.state:
            location_parts.append(self.state)
        if location_parts:
            parts.append(f"({', '.join(location_parts)})")
        return " ".join(parts) if parts else "School"

    def __repr__(self):
        return f"<School {self.name}>"


@dataclass
class Teacher:
    """
    Represents a teacher/professor on RateMyProfessor.

    Attributes:
        id: The GraphQL node ID (base64 encoded).
        legacy_id: The original numeric RMP ID.
        first_name: Teacher's first name.
        last_name: Teacher's last name.
        department: Department the teacher belongs to.
        department_id: Numeric department identifier.
        school: The school this teacher is associated with.
        avg_rating: Average rating from students (0.0-5.0).
        avg_difficulty: Average difficulty rating (0.0-5.0).
        num_ratings: Total number of ratings received.
        would_take_again_percent: Percentage of students who would take again.
        ratings_distribution: Breakdown of rating distribution.
        course_codes: List of course codes taught by this teacher.
        lock_status: Whether the professor's page is locked.
        is_saved: Whether the professor is saved by the current user.
    """

    id: str
    legacy_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    department: Optional[str] = None
    department_id: Optional[int] = None
    school: Optional[School] = None
    avg_rating: Optional[float] = None
    avg_difficulty: Optional[float] = None
    num_ratings: Optional[int] = None
    would_take_again_percent: Optional[float] = None
    ratings_distribution: Optional[Dict[str, Any]] = None
    course_codes: Optional[List[str]] = None
    lock_status: Optional[str] = None
    is_saved: Optional[bool] = None

    @property
    def full_name(self) -> Optional[str]:
        """
        Get the teacher's full name.

        Returns:
            The teacher's first and last name combined, or None if either is missing.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return None

    def __str__(self):
        return self.full_name or "Teacher"

    def __repr__(self):
        return f"<Teacher {self.full_name or self.id}>"


@dataclass
class Rating:
    """
    Represents an individual teacher rating.

    Attributes:
        id: The GraphQL node ID for this rating.
        legacy_id: The original numeric RMP ID.
        teacher: The teacher this rating is for.
        comment: The written review text.
        helpful_rating: Helpfulness rating (1-5).
        clarity_rating: Clarity rating (1-5).
        difficulty_rating: Difficulty rating (1-5).
        grade: Grade received in the class.
        class_name: Name of the class rated.
        would_take_again: Whether the student would take the teacher again.
        is_for_credit: Whether the class was taken for credit.
        textbook_used: Whether a textbook was used.
        attendance_mandatory: Whether attendance was mandatory.
        is_for_online_class: Whether this was for an online class.
        rating_tags: List of tags describing the rating.
        thumbs_up_total: Number of helpful votes.
        thumbs_down_total: Number of unhelpful votes.
        date: Date the rating was posted.
        flag_status: Whether the rating has been flagged.
        created_by_user: Whether this was created by the current user.
    """

    id: str
    legacy_id: Optional[int] = None
    teacher: Optional[Teacher] = None
    comment: Optional[str] = None
    helpful_rating: Optional[float] = None
    clarity_rating: Optional[float] = None
    difficulty_rating: Optional[float] = None
    grade: Optional[str] = None
    class_name: Optional[str] = None
    would_take_again: Optional[bool] = None
    is_for_credit: Optional[bool] = None
    textbook_used: Optional[bool] = None
    attendance_mandatory: Optional[bool] = None
    is_for_online_class: Optional[bool] = None
    rating_tags: Optional[List[str]] = None
    thumbs_up_total: Optional[int] = None
    thumbs_down_total: Optional[int] = None
    date: Optional[Union[str, datetime]] = None
    flag_status: Optional[str] = None
    created_by_user: Optional[bool] = None

    def __str__(self):
        if self.teacher:
            return f"Rating for {self.teacher}"
        return "Rating"

    def __repr__(self):
        return f"<Rating {self.id}>"


@dataclass
class SchoolRating:
    """
    Represents a rating for an entire school.

    Attributes:
        id: The GraphQL node ID for this rating.
        legacy_id: The original numeric RMP ID.
        school: The school this rating is for.
        comment: The written review text.
        clubs_rating: Rating for clubs and activities (1-5).
        facilities_rating: Rating for facilities (1-5).
        food_rating: Rating for food quality (1-5).
        happiness_rating: Overall happiness rating (1-5).
        internet_rating: Rating for internet speed (1-5).
        location_rating: Rating for campus location (1-5).
        opportunities_rating: Rating for opportunities (1-5).
        reputation_rating: Rating for school reputation (1-5).
        safety_rating: Rating for campus safety (1-5).
        social_rating: Rating for social activities (1-5).
        date: Date the rating was posted.
        thumbs_up_total: Number of helpful votes.
        thumbs_down_total: Number of unhelpful votes.
        flag_status: Whether the rating has been flagged.
        created_by_user: Whether this was created by the current user.
    """

    id: str
    legacy_id: Optional[int] = None
    school: Optional[School] = None
    comment: Optional[str] = None
    clubs_rating: Optional[float] = None
    facilities_rating: Optional[float] = None
    food_rating: Optional[float] = None
    happiness_rating: Optional[float] = None
    internet_rating: Optional[float] = None
    location_rating: Optional[float] = None
    opportunities_rating: Optional[float] = None
    reputation_rating: Optional[float] = None
    safety_rating: Optional[float] = None
    social_rating: Optional[float] = None
    date: Optional[Union[str, datetime]] = None
    thumbs_up_total: Optional[int] = None
    thumbs_down_total: Optional[int] = None
    flag_status: Optional[str] = None
    created_by_user: Optional[bool] = None

    def __str__(self):
        if self.school:
            return f"School Rating for {self.school}"
        return "School Rating"

    def __repr__(self):
        return f"<SchoolRating {self.id}>"


@dataclass
class PaginatedResult:
    """
    Represents a paginated result set.

    This wrapper provides a consistent interface for handling paginated API responses.

    Attributes:
        items: List of items in the current page.
        has_next_page: Whether there are more pages available.
        end_cursor: Cursor to use for fetching the next page.
        total_count: Total number of items (if available).
    """

    items: List[Any]
    has_next_page: bool
    end_cursor: Optional[str] = None
    total_count: Optional[int] = None

    def __len__(self):
        """Return the number of items in the current page."""
        return len(self.items)

    def __bool__(self):
        """Return True if there are any items in the current page."""
        return len(self.items) > 0
