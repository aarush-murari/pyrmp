"""
Data models for pyrmp.

These are the objects you'll be working with when searching for teachers,
schools, or ratings. Each model wraps the data returned by the RateMyProfessor
API in a Python dataclass.

Typical usage::

    from pyrmp import RateMyProfessorClient

    client = RateMyProfessorClient()
    teachers = client.search_teachers("John Smith", count=10)

    for teacher in teachers.items:  # Teacher objects
        print(teacher.full_name, teacher.avg_rating)
        if teacher.school:
            print(teacher.school.name)  # School object

    ratings = client.get_teacher_ratings(teacher.id, count=5)
    for rating in ratings.items:  # Rating objects
        print(rating.comment, rating.clarity_rating)

    client.close()
"""

from typing import Optional, List, Dict, Any, Union, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime

if TYPE_CHECKING:
    from .client import RateMyProfessorClient


@dataclass
class School:
    """
    A school or university on RateMyProfessor.

    You'll get School objects when searching for schools or when a teacher
    is associated with a school.

    Usage::

        school = client.get_school_details("Teacher-123")
        print(school.name)      # "Stanford University"
        print(school.num_ratings)  # 5000
        print(school.avg_rating)   # 4.2

        # When searching
        results = client.search_schools("MIT")
        for school in results.items:
            print(school.name, school.city, school.state)

        # Get ratings (ORM method)
        ratings = school.get_ratings(count=10)
        for rating in ratings.items:
            print(rating.facilities_rating, rating.comment)

        # Get details (ORM method)
        details = school.get_details()

    Attributes:
        id: Unique identifier for this school (used in API calls).
        legacy_id: Original numeric ID from older RMP system.
        name: Full school name (e.g., "Stanford University").
        city: City where the school is located.
        state: State abbreviation (e.g., "CA").
        country: Country of the school.
        num_ratings: Total number of ratings this school has received.
        avg_rating: Average overall school rating (0.0-5.0).
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
    _client: Optional[Any] = field(default=None, repr=False, compare=False)

    def get_ratings(self, count: int = 20):
        """
        Get ratings for this school.

        Args:
            count: How many ratings (1-100). Defaults to 20.

        Returns:
            PaginatedResult with SchoolRating objects.

        Example::

            results = client.search_schools("MIT")
            school = results.items[0]
            ratings = school.get_ratings(count=10)
            for rating in ratings.items:
                print(rating.facilities_rating, rating.comment)
        """
        if self._client is None:
            raise ValueError(
                "No client associated. Use client.search_schools() or client.get_school_details() first."
            )
        return self._client.get_school_ratings(self.id, count=count)

    def get_details(self):
        """
        Get full details for this school.

        Returns:
            School object with all fields populated.

        Example::

            results = client.search_schools("MIT")
            school = results.items[0]
            details = school.get_details()
            print(details.num_ratings)
        """
        if self._client is None:
            raise ValueError(
                "No client associated. Use client.search_schools() or client.get_school_details() first."
            )
        return self._client.get_school_details(self.id)

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

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, School):
            return self.id == other.id
        return False


@dataclass
class Teacher:
    """
    A teacher/professor on RateMyProfessor.

    This is the main object you'll work with when searching for or
    getting details about professors.

    Usage::

        # Search for teachers
        results = client.search_teachers("John Smith")
        teacher = results.items[0]

        print(teacher.full_name)     # "John Smith"
        print(teacher.avg_rating)    # 4.5
        print(teacher.num_ratings)   # 100
        print(teacher.department)    # "Computer Science"

        # Teacher's school info
        if teacher.school:
            print(teacher.school.name)  # "Stanford University"

        # Get more details (ORM method)
        details = teacher.get_details()
        print(details.would_take_again_percent)  # 80.0
        print(details.avg_difficulty)            # 3.0

        # Get ratings (ORM method)
        ratings = teacher.get_ratings(count=10)
        for rating in ratings.items:
            print(rating.clarity_rating, rating.comment)

    Attributes:
        id: Unique identifier for this teacher (used in API calls).
        legacy_id: Original numeric ID from older RMP system.
        first_name: Teacher's first name.
        last_name: Teacher's last name.
        department: Department the teacher belongs to (e.g., "Computer Science").
        department_id: Numeric department identifier.
        school: The school this teacher is associated with.
        avg_rating: Average rating from students (0.0-5.0).
        avg_difficulty: Average difficulty rating (0.0-5.0).
        num_ratings: Total number of ratings received.
        would_take_again_percent: Percentage of students who would take again.
        ratings_distribution: Breakdown of rating distribution (dict with r1-r5).
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
    _client: Optional[Any] = field(default=None, repr=False, compare=False)

    def get_ratings(self, count: int = 20, course_filter: Optional[str] = None):
        """
        Get ratings for this teacher.

        Args:
            count: How many ratings (1-100). Defaults to 20.
            course_filter: Only get ratings for a specific course (e.g., "CS101").

        Returns:
            PaginatedResult with Rating objects.

        Raises:
            RateMyProfessorError: If no client is associated with this teacher.

        Example::

            results = client.search_teachers("John Smith")
            teacher = results.items[0]
            ratings = teacher.get_ratings(count=10)
            for rating in ratings.items:
                print(rating.clarity_rating, rating.comment)
        """
        if self._client is None:
            raise ValueError(
                "No client associated. Use client.search_teachers() or client.get_teacher_details() first."
            )
        return self._client.get_teacher_ratings(
            self.id, count=count, course_filter=course_filter
        )

    def get_details(self):
        """
        Get full details for this teacher.

        Returns:
            Teacher object with all fields populated.

        Raises:
            RateMyProfessorError: If no client is associated with this teacher.

        Example::

            results = client.search_teachers("John Smith")
            teacher = results.items[0]
            details = teacher.get_details()
            print(details.would_take_again_percent)
        """
        if self._client is None:
            raise ValueError(
                "No client associated. Use client.search_teachers() or client.get_teacher_details() first."
            )
        return self._client.get_teacher_details(self.id)

    @property
    def full_name(self) -> Optional[str]:
        """
        Get the teacher's full name.

        Returns the first and last name combined, or None if either is missing.
        Useful for display purposes.

        Returns:
            "John Smith" if both names exist, None otherwise.

        Example::

            teacher = Teacher(id="1", first_name="John", last_name="Smith")
            print(teacher.full_name)  # "John Smith"

            teacher2 = Teacher(id="2", first_name="John")
            print(teacher2.full_name)  # None
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return None

    def __str__(self):
        return self.full_name or "Teacher"

    def __repr__(self):
        return f"<Teacher {self.full_name or self.id}>"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Teacher):
            return self.id == other.id
        return False


@dataclass
class Rating:
    """
    An individual teacher rating/review from a student.

    Ratings come from `client.get_teacher_ratings()` or
    `client.get_rating_details()`.

    Usage::

        ratings = client.get_teacher_ratings(teacher_id, count=10)

        for rating in ratings.items:
            print(f"Rating: {rating.clarity_rating}/5")
            print(f"Difficulty: {rating.difficulty_rating}/5")
            print(f"Grade: {rating.grade}")
            print(f"Class: {rating.class_name}")
            print(f"Comment: {rating.comment}")
            print(f"Would take again: {rating.would_take_again}")
            print(f"Helpful votes: {rating.thumbs_up_total}")
            print("---")

    Attributes:
        id: Unique identifier for this rating.
        legacy_id: Original numeric ID from older RMP system.
        teacher: The teacher this rating is for (if available).
        comment: The written review text from the student.
        helpful_rating: Helpfulness rating (1-5, where 5 is most helpful).
        clarity_rating: Clarity rating (1-5, where 5 is most clear).
        difficulty_rating: Difficulty rating (1-5, where 5 is most difficult).
        grade: Grade received in the class (e.g., "A", "B+", "Pass").
        class_name: Name of the class rated (e.g., "CS101").
        would_take_again: Whether the student would take the teacher again.
        is_for_credit: Whether the class was taken for credit.
        textbook_used: Whether a textbook was used in the class.
        attendance_mandatory: Whether attendance was mandatory.
        is_for_online_class: Whether this was for an online class.
        rating_tags: List of tags describing the rating (e.g., ["amazing lectures"]).
        thumbs_up_total: Number of "helpful" votes this rating received.
        thumbs_down_total: Number of "unhelpful" votes this rating received.
        date: Date the rating was posted (string or datetime).
        flag_status: Whether the rating has been flagged for review.
        created_by_user: Whether this rating was created by the current user.
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

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, Rating):
            return self.id == other.id
        return False


@dataclass
class SchoolRating:
    """
    A rating/review for an entire school (not a teacher).

    School ratings come from `client.get_school_ratings()` or
    `client.get_rating_details()`.

    Usage::

        ratings = client.get_school_ratings(school_id, count=10)

        for rating in ratings.items:
            print(f"Facilities: {rating.facilities_rating}/5")
            print(f"Food: {rating.food_rating}/5")
            print(f"Social: {rating.social_rating}/5")
            print(f"Comment: {rating.comment}")
            print("---")

    Attributes:
        id: Unique identifier for this school rating.
        legacy_id: Original numeric ID from older RMP system.
        school: The school this rating is for (if available).
        comment: The written review text from the student.
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

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if isinstance(other, SchoolRating):
            return self.id == other.id
        return False


@dataclass
class PaginatedResult:
    """
    A page of results from a search or listing operation.

    All search and listing methods return this wrapper. Use `items` to access
    the actual Teacher/School/Rating objects, and `has_next_page`/`end_cursor`
    for pagination.

    Usage::

        # Get first page
        results = client.search_teachers("Smith", count=10)

        print(len(results))           # Number of items in this page
        print(bool(results))          # True if any items

        for teacher in results.items:
            print(teacher.full_name)

        # Get next page
        if results.has_next_page:
            next_page = client.search_teachers("Smith", count=10)
            # ... handle next_page

    Attributes:
        items: List of items in the current page (Teacher, School, or Rating objects).
        has_next_page: Whether there are more pages available after this one.
        end_cursor: Cursor string to use for fetching the next page.
        total_count: Total number of items across all pages (if available).
    """

    items: List[Any]
    has_next_page: bool
    end_cursor: Optional[str] = None
    total_count: Optional[int] = None

    def __len__(self):
        """Number of items in the current page.

        Usage::

            results = client.search_teachers("Smith")
            print(len(results))  # e.g., 10
        """
        return len(self.items)

    def __bool__(self):
        """True if there are any items in the current page.

        Usage::

            results = client.search_teachers("nonexistent teacher")
            if not results:
                print("No teachers found")
        """
        return len(self.items) > 0
