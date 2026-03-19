"""
RateMyProfessor GraphQL API Client (READ-ONLY)

A robust, defensive wrapper around the RateMyProfessor GraphQL API.
This package provides READ-ONLY access to protect the RMP API.

⚠️ NOTE: This is intentionally read-only. For write operations,
see the separate pyrmp-write package.
"""

from typing import Optional, List, Dict, Any, Union
import time

from gql import Client, gql
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


class RateMyProfessorClient:
    """
    READ-ONLY client for RateMyProfessor GraphQL API.

    This client only supports read operations (search, get details, get ratings).
    Write operations are available in a separate package to protect the RMP API.
    """

    _last_request_time = 0
    _min_request_interval = 0.5
    _is_closed = False

    def __init__(
        self,
        base_url: str = "https://www.ratemyprofessors.com/graphql",
        timeout: int = 30,
    ):
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
        self.client = Client(transport=self.transport, fetch_schema_from_transport=False)

    def _execute_query(
        self, query: str, variable_values: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if self._is_closed:
            raise RateMyProfessorError("Client is closed. Create a new client.")

        current_time = time.time()
        time_since_last = current_time - RateMyProfessorClient._last_request_time
        if time_since_last < RateMyProfessorClient._min_request_interval:
            time.sleep(RateMyProfessorClient._min_request_interval - time_since_last)

        RateMyProfessorClient._last_request_time = time.time()

        try:
            result = self.client.execute(gql(query), variable_values=variable_values or {})
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
        if not teacher_node:
            return Teacher(id="")

        school = None
        if teacher_node.get("school"):
            school_data = teacher_node["school"]
            school = School(
                id=school_data.get("id", ""),
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
            id=teacher_node.get("id", ""),
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
            course_codes=[code.get("courseName") for code in teacher_node.get("courseCodes", [])],
            lock_status=teacher_node.get("lockStatus"),
            is_saved=teacher_node.get("isSaved"),
        )

    def _parse_school_node(self, school_node: Dict[str, Any]) -> School:
        if not school_node:
            return School(id="")

        return School(
            id=school_node.get("id", ""),
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
        if not rating_node:
            return Rating(id="")

        return Rating(
            id=rating_node.get("id", ""),
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
        if not rating_node:
            return SchoolRating(id="")

        return SchoolRating(
            id=rating_node.get("id", ""),
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
        variables = {"id": teacher_id}
        response = self._execute_query(TEACHERRATINGSPAGE_QUERY, variables)

        teacher_node = response.get("node")
        if teacher_node and teacher_node.get("__typename") == "Teacher":
            return self._parse_teacher_node(teacher_node)
        return None

    def get_school_details(self, school_id: str) -> Optional[School]:
        variables = {"id": school_id}
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
        variables = {
            "count": count,
            "id": teacher_id,
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
        variables = {"count": count, "id": school_id, "cursor": cursor}

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
                    school_ratings.append(self._parse_school_rating_node(rating_node, school))

        return PaginatedResult(
            items=school_ratings,
            has_next_page=ratings_data.get("pageInfo", {}).get("hasNextPage", False),
            end_cursor=ratings_data.get("pageInfo", {}).get("endCursor"),
        )

    def get_rating_details(self, rating_id: str) -> Optional[Union[Rating, SchoolRating]]:
        variables = {"rid": rating_id}
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
        if not self._is_closed:
            self._is_closed = True
            if hasattr(self.transport, "close"):
                try:
                    self.transport.close()
                except Exception:
                    pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def search_teachers(query: str, count: int = 10) -> PaginatedResult:
    """Quick search for teachers"""
    with RateMyProfessorClient() as client:
        return client.search_teachers(query, count)


def search_schools(query: Optional[str] = None, count: int = 10) -> PaginatedResult:
    """Quick search for schools"""
    with RateMyProfessorClient() as client:
        return client.search_schools(query, count)
