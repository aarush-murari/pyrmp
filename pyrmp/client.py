"""
RateMyProfessor API Client.

This module provides a READ-ONLY Python wrapper around the RateMyProfessor
GraphQL API. You can search for teachers and schools, get details, and
read ratings - but you cannot write or submit anything.

Typical usage::

    from pyrmp import RateMyProfessorClient

    # Search for teachers
    with RateMyProfessorClient() as client:
        teachers = client.search_teachers("John Smith", count=10)
        for teacher in teachers.items:
            print(f"{teacher.full_name} - {teacher.avg_rating}/5 ({teacher.num_ratings} ratings)")

        # Get teacher details
        details = client.get_teacher_details(teachers.items[0].id)
        print(f"Department: {details.department}")
        print(f"Would take again: {details.would_take_again_percent}%")

        # Get ratings
        ratings = client.get_teacher_ratings(details.id, count=5)
        for rating in ratings.items:
            print(f"  {rating.clarity_rating}/5 - {rating.comment[:50]}")

For quick one-off searches (auto-creates/closes a client)::

    from pyrmp import search_teachers, search_schools

    results = search_teachers("John Smith")
    for teacher in results.items:
        print(teacher.full_name)

NOTE: This library is intentionally READ-ONLY. For write operations
(submitting ratings, etc.), use a separate authenticated client.
"""

from typing import Optional, List, Dict, Any, Union
import time
import base64

from gql import Client, gql
from gql.graphql_request import GraphQLRequest
from gql.transport.requests import RequestsHTTPTransport

from .models import School, Teacher, Rating, SchoolRating, PaginatedResult
from .queries import (
    NEWSEARCHTEACHERS_QUERY,
    NEWSEARCHSCHOOLS_QUERY,
    TEACHERRATINGSPAGE_QUERY,
    SCHOOLRATINGSPAGE_QUERY,
    RATINGSLIST_QUERY,
    SCHOOLRATINGSLIST_QUERY,
    RATINGPAGE_QUERY,
)
from .exceptions import RateMyProfessorError, InvalidQueryError


def _decode_id(b64_id: str) -> str:
    """
    Decode a base64-encoded ID to human-readable format.

    Converts "VGVhY2hlci05NDExNzQ=" to "Teacher-941174".
    Returns the original string if decoding fails.
    """
    try:
        return base64.b64decode(b64_id).decode("utf-8")
    except Exception:
        return b64_id


def _encode_id(readable_id: str) -> str:
    """
    Encode a human-readable ID to base64 format.

    Converts "Teacher-941174" to "VGVhY2hlci05NDExNzQ=".
    Returns the original string if it's already base64.
    """
    try:
        # Check if already base64 by decoding - if it works and produces readable format, re-encode
        decoded = base64.b64decode(readable_id).decode("utf-8")
        if decoded.startswith(("Teacher-", "School-", "Rating-")):
            return readable_id  # Already base64
    except Exception:
        pass
    # Encode the readable ID
    return base64.b64encode(readable_id.encode("utf-8")).decode("utf-8")


class RateMyProfessorClient:
    """
    Client for searching teachers, schools, and reading ratings from RateMyProfessor.

    This client connects to the RateMyProfessor API and lets you search for
    teachers/schools, get their details, and read ratings/reviews.

    Usage::

        # As context manager (recommended - auto-closes)
        with RateMyProfessorClient() as client:
            teachers = client.search_teachers("John Smith")

        # Or manually
        client = RateMyProfessorClient()
        teachers = client.search_teachers("John Smith")
        client.close()

    Args:
        base_url: API endpoint URL. Defaults to the official RateMyProfessor GraphQL endpoint.
        timeout: How long to wait for API responses (in seconds). Defaults to 30.

    Attributes:
        base_url: The API endpoint being used.
        timeout: Request timeout in seconds.

    Raises:
        RateMyProfessorError: If the API is unreachable or returns an error.
        InvalidQueryError: If search parameters are invalid (e.g., count > 100).
    """

    _last_request_time = 0
    _min_request_interval = 0.5
    _is_closed = False

    def __init__(
        self,
        base_url: str = "https://www.ratemyprofessors.com/graphql",
        timeout: int = 30,
    ):
        """
        Create a new RateMyProfessor client.

        Args:
            base_url: The API endpoint URL. You probably don't need to change this.
            timeout: How long to wait for API responses (in seconds). Increase for slow connections.

        Example::

            # Default settings
            client = RateMyProfessorClient()

            # Custom timeout
            client = RateMyProfessorClient(timeout=60)

            # Custom endpoint (for testing)
            client = RateMyProfessorClient(base_url="http://localhost:4000/graphql")
        """
        self.base_url = base_url
        self.timeout = timeout

        self.transport = RequestsHTTPTransport(
            url=base_url,
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Origin": "https://www.ratemyprofessors.com",
                "Referer": "https://www.ratemyprofessors.com/",
            },
        )
        self.client = Client(
            transport=self.transport, fetch_schema_from_transport=False
        )

    def _execute_query(
        self, query: str, variable_values: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a GraphQL query with rate limiting and error handling.

        Args:
            query: The GraphQL query string.
            variable_values: Optional variables for the query.

        Returns:
            The data portion of the GraphQL response.

        Raises:
            RateMyProfessorError: If the client is closed or query fails.
        """
        if self._is_closed:
            raise RateMyProfessorError("Client is closed. Create a new client.")

        current_time = time.time()
        time_since_last = current_time - RateMyProfessorClient._last_request_time
        if time_since_last < RateMyProfessorClient._min_request_interval:
            time.sleep(RateMyProfessorClient._min_request_interval - time_since_last)

        RateMyProfessorClient._last_request_time = time.time()

        try:
            request = GraphQLRequest(
                request=gql(query), variable_values=variable_values or {}
            )
            result = self.client.execute(request)
            return result
        except Exception as e:
            error_msg = str(e)
            if "invalid base64" in error_msg:
                raise RateMyProfessorError(f"Invalid ID format: {error_msg}")
            elif "403" in error_msg or "Forbidden" in error_msg:
                raise RateMyProfessorError(f"Access forbidden (403)")
            elif "429" in error_msg or "rate" in error_msg.lower():
                raise RateMyProfessorError(f"Rate limited: {error_msg}")
            else:
                raise RateMyProfessorError(f"GraphQL query failed: {error_msg}")

    def _parse_teacher_node(self, teacher_node: Dict[str, Any]) -> Teacher:
        """
        Parse a teacher node from the GraphQL response into a Teacher object.

        Args:
            teacher_node: Raw teacher data from the API.

        Returns:
            A Teacher dataclass instance.
        """
        if not teacher_node:
            return Teacher(id="")

        school = None
        if teacher_node.get("school"):
            school_data = teacher_node["school"]
            school = School(
                id=_decode_id(school_data.get("id", "")),
                legacy_id=school_data.get("legacyId"),
                name=school_data.get("name"),
                city=school_data.get("city"),
                state=school_data.get("state"),
                country=school_data.get("country"),
                num_ratings=school_data.get("numRatings"),
                avg_rating=school_data.get("avgRating"),
                avg_rating_rounded=school_data.get("avgRatingRounded"),
            )

        return Teacher(
            id=_decode_id(teacher_node.get("id", "")),
            legacy_id=teacher_node.get("legacyId"),
            first_name=teacher_node.get("firstName"),
            last_name=teacher_node.get("lastName"),
            department=teacher_node.get("department"),
            department_id=teacher_node.get("departmentId"),
            school=school,
            avg_rating=teacher_node.get("avgRating"),
            avg_difficulty=teacher_node.get("avgDifficulty"),
            num_ratings=teacher_node.get("numRatings"),
            would_take_again_percent=teacher_node.get("wouldTakeAgainPercentRounded"),
            ratings_distribution=teacher_node.get("ratingsDistribution"),
            course_codes=[
                code.get("courseName") for code in teacher_node.get("courseCodes", [])
            ],
            lock_status=teacher_node.get("lockStatus"),
            is_saved=teacher_node.get("isSaved"),
        )

    def _parse_school_node(self, school_node: Dict[str, Any]) -> School:
        """
        Parse a school node from the GraphQL response into a School object.

        Args:
            school_node: Raw school data from the API.

        Returns:
            A School dataclass instance.
        """
        if not school_node:
            return School(id="")

        return School(
            id=_decode_id(school_node.get("id", "")),
            legacy_id=school_node.get("legacyId"),
            name=school_node.get("name"),
            city=school_node.get("city"),
            state=school_node.get("state"),
            country=school_node.get("country"),
            num_ratings=school_node.get("numRatings"),
            avg_rating=school_node.get("avgRating"),
            avg_rating_rounded=school_node.get("avgRatingRounded"),
            departments=school_node.get("departments"),
            summary=school_node.get("summary"),
        )

    def _parse_rating_node(
        self, rating_node: Dict[str, Any], teacher: Optional[Teacher] = None
    ) -> Rating:
        """
        Parse a rating node from the GraphQL response into a Rating object.

        Args:
            rating_node: Raw rating data from the API.
            teacher: Optional associated Teacher object.

        Returns:
            A Rating dataclass instance.
        """
        if not rating_node:
            return Rating(id="")

        return Rating(
            id=_decode_id(rating_node.get("id", "")),
            legacy_id=rating_node.get("legacyId"),
            teacher=teacher,
            comment=rating_node.get("comment"),
            helpful_rating=rating_node.get("helpfulRating"),
            clarity_rating=rating_node.get("clarityRating"),
            difficulty_rating=rating_node.get("difficultyRating"),
            grade=rating_node.get("grade"),
            class_name=rating_node.get("class"),
            would_take_again=rating_node.get("iWouldTakeAgain"),
            is_for_credit=rating_node.get("isForCredit"),
            textbook_used=rating_node.get("textbookIsUsed"),
            attendance_mandatory=rating_node.get("attendanceMandatory"),
            is_for_online_class=rating_node.get("isForOnlineClass"),
            rating_tags=rating_node.get("ratingTags"),
            thumbs_up_total=rating_node.get("thumbsUpTotal"),
            thumbs_down_total=rating_node.get("thumbsDownTotal"),
            date=rating_node.get("date"),
            flag_status=rating_node.get("flagStatus"),
            created_by_user=rating_node.get("createdByUser"),
        )

    def _parse_school_rating_node(
        self, rating_node: Dict[str, Any], school: Optional[School] = None
    ) -> SchoolRating:
        """
        Parse a school rating node from the GraphQL response into a SchoolRating object.

        Args:
            rating_node: Raw school rating data from the API.
            school: Optional associated School object.

        Returns:
            A SchoolRating dataclass instance.
        """
        if not rating_node:
            return SchoolRating(id="")

        return SchoolRating(
            id=_decode_id(rating_node.get("id", "")),
            legacy_id=rating_node.get("legacyId"),
            school=school,
            comment=rating_node.get("comment"),
            clubs_rating=rating_node.get("clubsRating"),
            facilities_rating=rating_node.get("facilitiesRating"),
            food_rating=rating_node.get("foodRating"),
            happiness_rating=rating_node.get("happinessRating"),
            internet_rating=rating_node.get("internetRating"),
            location_rating=rating_node.get("locationRating"),
            opportunities_rating=rating_node.get("opportunitiesRating"),
            reputation_rating=rating_node.get("reputationRating"),
            safety_rating=rating_node.get("safetyRating"),
            social_rating=rating_node.get("socialRating"),
            date=rating_node.get("date"),
            thumbs_up_total=rating_node.get("thumbsUpTotal"),
            thumbs_down_total=rating_node.get("thumbsDownTotal"),
            flag_status=rating_node.get("flagStatus"),
            created_by_user=rating_node.get("createdByUser"),
        )

    def search_teachers(
        self, query: str, count: int = 10, include_compare: bool = False
    ) -> PaginatedResult:
        """
        Search for teachers by name.

        This is the main way to find professors. The search is fuzzy - you don't
        need to spell the name exactly.

        Args:
            query: Teacher name to search for (e.g., "John Smith", "Smith", "J. Smith").
            count: How many results to return (1-100). Defaults to 10.
            include_compare: Include comparison data. You probably want False.

        Returns:
            PaginatedResult with Teacher objects in `.items`.

        Raises:
            InvalidQueryError: If count is not between 1 and 100.

        Example::

            # Simple search
            results = client.search_teachers("John Smith")
            for teacher in results.items:
                print(teacher.full_name, teacher.avg_rating)

            # Get more results
            results = client.search_teachers("Smith", count=50)

            # Paginate
            if results.has_next_page:
                # next_page = client.search_teachers("Smith", count=50)
                pass
        """
        if count < 1 or count > 100:
            raise InvalidQueryError(f"count must be between 1 and 100, got {count}")

        search_query = {"text": query if query else ""}

        variables = {
            "query": search_query,
            "count": count,
            "includeCompare": include_compare,
        }

        response = self._execute_query(NEWSEARCHTEACHERS_QUERY, variables)

        teachers_data = response.get("newSearch", {}).get("teachers", {})
        edges = teachers_data.get("edges", [])

        teachers = []
        for edge in edges:
            teacher_node = edge.get("node")
            if teacher_node:
                teachers.append(self._parse_teacher_node(teacher_node))

        return PaginatedResult(
            items=teachers,
            has_next_page=teachers_data.get("pageInfo", {}).get("hasNextPage", False),
            end_cursor=teachers_data.get("pageInfo", {}).get("endCursor"),
        )

    def search_schools(
        self,
        query: Optional[str] = None,
        count: int = 10,
        include_compare: bool = False,
    ) -> PaginatedResult:
        """
        Search for schools by name.

        Args:
            query: School name to search for (e.g., "MIT", "Stanford", "Arizona State"). Optional.
            count: How many results to return (1-100). Defaults to 10.
            include_compare: Include comparison data. You probably want False.

        Returns:
            PaginatedResult with School objects in `.items`.

        Raises:
            InvalidQueryError: If count is not between 1 and 100.

        Example::

            results = client.search_schools("MIT")
            for school in results.items:
                print(school.name, school.city, school.state)
                print(f"  {school.num_ratings} ratings, avg {school.avg_rating}")
        """
        if count < 1 or count > 100:
            raise InvalidQueryError(f"count must be between 1 and 100, got {count}")

        search_query = None if not query else {"text": query}

        variables = {"query": search_query, "includeCompare": include_compare}

        response = self._execute_query(NEWSEARCHSCHOOLS_QUERY, variables)

        schools_data = response.get("newSearch", {}).get("schools", {})
        edges = schools_data.get("edges", [])

        schools = []
        for edge in edges:
            school_node = edge.get("node")
            if school_node:
                schools.append(self._parse_school_node(school_node))

        return PaginatedResult(
            items=schools,
            has_next_page=schools_data.get("pageInfo", {}).get("hasNextPage", False),
            end_cursor=schools_data.get("pageInfo", {}).get("endCursor"),
        )

    def get_teacher_details(self, teacher_id: str) -> Optional[Teacher]:
        """
        Get detailed info about a specific teacher.

        Use this after searching to get full details about a teacher, including
        their school, department, and ratings breakdown.

        Args:
            teacher_id: The teacher's ID from a previous search result
                       (e.g., "VGVhY2hlci0xMjM=").

        Returns:
            Teacher object with full details, or None if not found.

        Example::

            # Search first, then get details
            results = client.search_teachers("John Smith")
            if results.items:
                teacher_id = results.items[0].id
                details = client.get_teacher_details(teacher_id)

                print(f"Department: {details.department}")
                print(f"Avg rating: {details.avg_rating}")
                print(f"Would take again: {details.would_take_again_percent}%")
                print(f"School: {details.school.name if details.school else 'N/A'}")
        """
        variables = {"id": _encode_id(teacher_id)}
        response = self._execute_query(TEACHERRATINGSPAGE_QUERY, variables)

        teacher_node = response.get("node")
        if teacher_node and teacher_node.get("__typename") == "Teacher":
            return self._parse_teacher_node(teacher_node)
        return None

    def get_school_details(self, school_id: str) -> Optional[School]:
        """
        Get detailed info about a specific school.

        Args:
            school_id: The school's ID from a previous search result.

        Returns:
            School object with full details, or None if not found.

        Example::

            results = client.search_schools("Stanford")
            if results.items:
                school = client.get_school_details(results.items[0].id)
                print(f"{school.name} - {school.num_ratings} ratings")
        """
        variables = {"id": _encode_id(school_id)}
        response = self._execute_query(SCHOOLRATINGSPAGE_QUERY, variables)

        school_node = response.get("school")
        if school_node and school_node.get("__typename") == "School":
            return self._parse_school_node(school_node)
        return None

    def get_teacher_ratings(
        self,
        teacher_id: str,
        count: int = 20,
        course_filter: Optional[str] = None,
        cursor: Optional[str] = None,
    ) -> PaginatedResult:
        """
        Get ratings/reviews for a specific teacher.

        This is how you read what students actually wrote about a professor.

        Args:
            teacher_id: The teacher's ID (from search or details).
            count: How many ratings to fetch (1-100). Defaults to 20.
            course_filter: Only get ratings for a specific course (e.g., "CS101").
            cursor: Pagination cursor for fetching the next page.

        Returns:
            PaginatedResult with Rating objects in `.items`.

        Example::

            # Get ratings for a teacher
            ratings = client.get_teacher_ratings(teacher_id, count=10)

            for rating in ratings.items:
                print(f"Clarity: {rating.clarity_rating}/5")
                print(f"Difficulty: {rating.difficulty_rating}/5")
                print(f"Grade: {rating.grade}")
                print(f"Comment: {rating.comment}")
                print("---")

            # Filter by course
            cs_ratings = client.get_teacher_ratings(teacher_id, course_filter="CS101")
        """
        variables = {
            "count": count,
            "id": _encode_id(teacher_id),
            "courseFilter": course_filter,
            "cursor": cursor,
        }

        response = self._execute_query(RATINGSLIST_QUERY, variables)

        teacher_node = response.get("node")
        if not teacher_node or teacher_node.get("__typename") != "Teacher":
            return PaginatedResult(items=[], has_next_page=False)

        teacher = self._parse_teacher_node(teacher_node)

        ratings = []
        ratings_data = teacher_node.get("ratings", {})
        if ratings_data.get("edges"):
            for edge in ratings_data["edges"]:
                rating_node = edge.get("node")
                if rating_node:
                    ratings.append(self._parse_rating_node(rating_node, teacher))

        return PaginatedResult(
            items=ratings,
            has_next_page=ratings_data.get("pageInfo", {}).get("hasNextPage", False),
            end_cursor=ratings_data.get("pageInfo", {}).get("endCursor"),
        )

    def get_school_ratings(
        self, school_id: str, count: int = 20, cursor: Optional[str] = None
    ) -> PaginatedResult:
        """
        Get ratings/reviews for a specific school.

        School ratings cover things like facilities, food, social life, etc.

        Args:
            school_id: The school's ID (from search or details).
            count: How many ratings to fetch (1-100). Defaults to 20.
            cursor: Pagination cursor for fetching the next page.

        Returns:
            PaginatedResult with SchoolRating objects in `.items`.

        Example::

            ratings = client.get_school_ratings(school_id, count=10)

            for rating in ratings.items:
                print(f"Facilities: {rating.facilities_rating}/5")
                print(f"Food: {rating.food_rating}/5")
                print(f"Social: {rating.social_rating}/5")
                print(f"Comment: {rating.comment}")
                print("---")
        """
        variables = {"count": count, "id": _encode_id(school_id), "cursor": cursor}

        response = self._execute_query(SCHOOLRATINGSLIST_QUERY, variables)

        school_node = response.get("node")
        if not school_node or school_node.get("__typename") != "School":
            return PaginatedResult(items=[], has_next_page=False)

        school = self._parse_school_node(school_node)

        school_ratings = []
        ratings_data = school_node.get("ratings", {})
        if ratings_data.get("edges"):
            for edge in ratings_data["edges"]:
                rating_node = edge.get("node")
                if rating_node:
                    school_ratings.append(
                        self._parse_school_rating_node(rating_node, school)
                    )

        return PaginatedResult(
            items=school_ratings,
            has_next_page=ratings_data.get("pageInfo", {}).get("hasNextPage", False),
            end_cursor=ratings_data.get("pageInfo", {}).get("endCursor"),
        )

    def get_rating_details(
        self, rating_id: str
    ) -> Optional[Union[Rating, SchoolRating]]:
        """
        Get full details for a specific rating.

        Useful when you have a rating ID and want to see the full review.

        Args:
            rating_id: The rating's ID.

        Returns:
            Rating or SchoolRating object with full details, or None if not found.

        Example::

            # Get a specific rating
            rating = client.get_rating_details(rating_id)
            if rating:
                print(f"Comment: {rating.comment}")
                print(f"Helpful: {rating.clarity_rating}/5")
        """
        variables = {"rid": _encode_id(rating_id)}
        response = self._execute_query(RATINGPAGE_QUERY, variables)

        rating_node = response.get("rating")
        if not rating_node:
            return None

        if rating_node.get("__typename") == "Rating":
            teacher_data = rating_node.get("teacher")
            teacher = self._parse_teacher_node(teacher_data) if teacher_data else None
            return self._parse_rating_node(rating_node, teacher)
        elif rating_node.get("__typename") == "SchoolRating":
            school_data = rating_node.get("school")
            school = self._parse_school_node(school_data) if school_data else None
            return self._parse_school_rating_node(rating_node, school)

        return None

    def close(self):
        """
        Close the client and release resources.

        Safe to call multiple times. Prefer using context manager instead.

        Example::

            client = RateMyProfessorClient()
            try:
                teachers = client.search_teachers("Smith")
            finally:
                client.close()  # Always close

            # Or better:
            with RateMyProfessorClient() as client:
                teachers = client.search_teachers("Smith")
            # Auto-closed here
        """
        if not self._is_closed:
            self._is_closed = True
            if hasattr(self.transport, "close"):
                try:
                    self.transport.close()
                except Exception:
                    pass

    def __enter__(self):
        """Support context manager protocol."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support context manager protocol."""
        self.close()


def search_teachers(query: str, count: int = 10) -> PaginatedResult:
    """
    Quick search for teachers by name.

    Creates a temporary client, does the search, and closes it automatically.
    Perfect for one-off searches.

    Args:
        query: Teacher name to search for.
        count: How many results (1-100). Defaults to 10.

    Returns:
        PaginatedResult with Teacher objects.

    Example::

        from pyrmp import search_teachers

        results = search_teachers("John Smith")
        for teacher in results.items:
            print(teacher.full_name, teacher.avg_rating)
    """
    with RateMyProfessorClient() as client:
        return client.search_teachers(query, count)


def search_schools(query: Optional[str] = None, count: int = 10) -> PaginatedResult:
    """
    Quick search for schools by name.

    Creates a temporary client, does the search, and closes it automatically.
    Perfect for one-off searches.

    Args:
        query: School name to search for. Optional.
        count: How many results (1-100). Defaults to 10.

    Returns:
        PaginatedResult with School objects.

    Example::

        from pyrmp import search_schools

        results = search_schools("MIT")
        for school in results.items:
            print(school.name, school.city, school.state)
    """
    with RateMyProfessorClient() as client:
        return client.search_schools(query, count)
