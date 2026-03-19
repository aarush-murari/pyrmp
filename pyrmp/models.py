"""
Data models for RateMyProfessor API responses
"""

from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass
from datetime import datetime


@dataclass
class School:
    """Represents a school/ university"""

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
        return (
            f"{self.name} ({self.city}, {self.state})"
            if self.name and self.city and self.state
            else "School"
        )

    def __repr__(self):
        return f"<School {self.name}>"


@dataclass
class Teacher:
    """Represents a teacher/professor"""

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
        """Get the teacher's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return None

    def __str__(self):
        return self.full_name or "Teacher"

    def __repr__(self):
        return f"<Teacher {self.full_name or self.id}>"


@dataclass
class Rating:
    """Represents a teacher rating"""

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
        return f"Rating for {self.teacher}" if self.teacher else "Rating"

    def __repr__(self):
        return f"<Rating {self.id}>"


@dataclass
class SchoolRating:
    """Represents a school rating"""

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
        return f"School Rating for {self.school}" if self.school else "School Rating"

    def __repr__(self):
        return f"<SchoolRating {self.id}>"


@dataclass
class PaginatedResult:
    """Represents a paginated result"""

    items: List[Any]
    has_next_page: bool
    end_cursor: Optional[str] = None
    total_count: Optional[int] = None

    def __len__(self):
        return len(self.items)

    def __bool__(self):
        return len(self.items) > 0
