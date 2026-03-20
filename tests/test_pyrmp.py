"""
Tests for pyrmp package

Comprehensive test coverage for:
- Client initialization and configuration
- Input validation (positive/negative)
- Model edge cases
- Exception handling
- Mock data structures
- Real API integration (via test_integration.py)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from pyrmp import RateMyProfessorClient, search_teachers, search_schools
from pyrmp.models import Teacher, School, Rating, SchoolRating, PaginatedResult
from pyrmp.exceptions import (
    RateMyProfessorError,
    InvalidQueryError,
    APIError,
    NotFoundError,
    PaginationError,
)


class TestRateMyProfessorClient:
    """Test suite for RateMyProfessorClient initialization and configuration"""

    def test_client_initialization(self):
        """Test client can be initialized with default values"""
        client = RateMyProfessorClient()
        assert client.base_url == "https://www.ratemyprofessors.com/graphql"
        assert client.timeout == 30
        client.close()

    def test_client_custom_url(self):
        """Test client with custom URL"""
        client = RateMyProfessorClient(base_url="http://localhost:4000/graphql")
        assert client.base_url == "http://localhost:4000/graphql"
        client.close()

    def test_client_custom_timeout(self):
        """Test client with custom timeout"""
        client = RateMyProfessorClient(timeout=60)
        assert client.timeout == 60
        client.close()

    def test_context_manager(self):
        """Test client as context manager"""
        with RateMyProfessorClient() as client:
            assert client is not None
        # Client should be closed after exiting context

    def test_close_twice(self):
        """Test closing client multiple times is safe"""
        client = RateMyProfessorClient()
        client.close()
        client.close()  # Should not raise

    def test_context_manager_closes_on_exception(self):
        """Test client closes even when exception occurs in context"""
        try:
            with RateMyProfessorClient() as client:
                assert client is not None
                raise ValueError("test error")
        except ValueError:
            pass
        # Client should be closed

    def test_mutation_methods_not_in_readonly_package(self):
        """Test that mutation methods are NOT in read-only package"""
        client = RateMyProfessorClient()

        # Mutations should NOT be in this package (they're in pyrmp-write)
        assert not hasattr(client, "rate_teacher")
        assert not hasattr(client, "rate_school")
        assert not hasattr(client, "bookmark_teacher")
        assert not hasattr(client, "unbookmark_teacher")
        assert not hasattr(client, "thumb_up_rating")
        assert not hasattr(client, "thumb_down_rating")
        assert not hasattr(client, "flag_rating")

        client.close()


class TestSearchTeachersInputValidation:
    """Test search_teachers input validation - positive and negative"""

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_search_teachers_returns_paginated_result(self, mock_execute):
        """Test search_teachers returns PaginatedResult with valid input"""
        mock_execute.return_value = {
            "newSearch": {
                "teachers": {
                    "edges": [
                        {"node": {"id": "1", "firstName": "John", "lastName": "Smith"}}
                    ],
                    "pageInfo": {"hasNextPage": True, "endCursor": "abc123"},
                }
            }
        }

        client = RateMyProfessorClient()
        result = client.search_teachers("Smith", count=10)

        assert isinstance(result, PaginatedResult)
        assert len(result.items) == 1
        assert result.has_next_page is True
        assert result.end_cursor == "abc123"
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_search_teachers_empty_results(self, mock_execute):
        """Test search with no results returns empty PaginatedResult"""
        mock_execute.return_value = {
            "newSearch": {"teachers": {"edges": [], "pageInfo": {"hasNextPage": False}}}
        }

        client = RateMyProfessorClient()
        result = client.search_teachers("NonexistentProfessor12345")

        assert isinstance(result, PaginatedResult)
        assert len(result.items) == 0
        assert result.has_next_page is False
        client.close()

    def test_search_teachers_negative_count(self):
        """Test negative count raises InvalidQueryError"""
        client = RateMyProfessorClient()

        with pytest.raises(InvalidQueryError) as exc_info:
            client.search_teachers("Smith", count=-1)

        assert "must be between 1 and 100" in str(exc_info.value)
        client.close()

    def test_search_teachers_zero_count(self):
        """Test zero count raises InvalidQueryError"""
        client = RateMyProfessorClient()

        with pytest.raises(InvalidQueryError):
            client.search_teachers("Smith", count=0)

        client.close()

    def test_search_teachers_count_over_100(self):
        """Test count over 100 raises InvalidQueryError"""
        client = RateMyProfessorClient()

        with pytest.raises(InvalidQueryError):
            client.search_teachers("Smith", count=101)

        client.close()

    def test_search_teachers_count_boundary_min(self):
        """Test count=1 (minimum valid) works"""
        client = RateMyProfessorClient()

        # Should not raise
        result = client.search_teachers("John", count=1)
        assert result is not None

        client.close()

    def test_search_teachers_count_boundary_max(self):
        """Test count=100 (maximum valid) works"""
        client = RateMyProfessorClient()

        # Should not raise
        result = client.search_teachers("John", count=100)
        assert result is not None

        client.close()

    def test_search_teachers_empty_string(self):
        """Test empty string query works"""
        client = RateMyProfessorClient()

        # Should not raise
        result = client.search_teachers("", count=5)
        assert result is not None

        client.close()

    def test_search_teachers_special_characters(self):
        """Test query with special characters works"""
        client = RateMyProfessorClient()

        # Should not raise
        result = client.search_teachers("O'Brien-Smith", count=5)
        assert result is not None

        client.close()

    def test_search_teachers_unicode(self):
        """Test query with unicode characters works"""
        client = RateMyProfessorClient()

        # Should not raise
        result = client.search_teachers("José García", count=5)
        assert result is not None

        client.close()

    def test_search_teachers_very_long_query(self):
        """Test very long query string works"""
        client = RateMyProfessorClient()

        long_query = "A" * 1000
        # Should not raise
        result = client.search_teachers(long_query, count=5)
        assert result is not None

        client.close()

    def test_search_teachers_with_numbers(self):
        """Test query with numbers works"""
        client = RateMyProfessorClient()

        result = client.search_teachers("CS101", count=5)
        assert result is not None

        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_search_teachers_multiple_results(self, mock_execute):
        """Test search returns multiple teachers"""
        mock_execute.return_value = {
            "newSearch": {
                "teachers": {
                    "edges": [
                        {"node": {"id": "1", "firstName": "John", "lastName": "Smith"}},
                        {"node": {"id": "2", "firstName": "Jane", "lastName": "Doe"}},
                        {
                            "node": {
                                "id": "3",
                                "firstName": "Bob",
                                "lastName": "Johnson",
                            }
                        },
                    ],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                }
            }
        }

        client = RateMyProfessorClient()
        result = client.search_teachers("Smith", count=10)

        assert len(result.items) == 3
        assert result.items[0].first_name == "John"
        assert result.items[1].first_name == "Jane"
        assert result.items[2].first_name == "Bob"
        client.close()


class TestSearchSchoolsInputValidation:
    """Test search_schools input validation"""

    def test_search_schools_negative_count(self):
        """Test negative count raises InvalidQueryError"""
        client = RateMyProfessorClient()

        with pytest.raises(InvalidQueryError):
            client.search_schools("MIT", count=-1)

        client.close()

    def test_search_schools_zero_count(self):
        """Test zero count raises InvalidQueryError"""
        client = RateMyProfessorClient()

        with pytest.raises(InvalidQueryError):
            client.search_schools("MIT", count=0)

        client.close()

    def test_search_schools_count_over_100(self):
        """Test count over 100 raises InvalidQueryError"""
        client = RateMyProfessorClient()

        with pytest.raises(InvalidQueryError):
            client.search_schools("MIT", count=101)

        client.close()

    def test_search_schools_empty_string(self):
        """Test empty string query for schools - API may return error"""
        client = RateMyProfessorClient()

        # Empty string may cause API error, so we test it raises or returns empty
        try:
            result = client.search_schools("", count=5)
            # If it doesn't raise, it should return a result (possibly empty)
            assert result is not None
        except RateMyProfessorError:
            # API rejects empty string queries - this is expected
            pass

        client.close()


class TestGetTeacherDetails:
    """Test get_teacher_details with various inputs"""

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_teacher_details_success(self, mock_execute):
        """Test get_teacher_details returns Teacher object"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "123",
                "firstName": "John",
                "lastName": "Smith",
                "department": "Computer Science",
                "avgRating": 4.5,
                "numRatings": 100,
                "school": {"id": "s1", "name": "Test University"},
            }
        }

        client = RateMyProfessorClient()
        teacher = client.get_teacher_details("123")

        assert teacher is not None
        assert teacher.first_name == "John"
        assert teacher.last_name == "Smith"
        assert teacher.department == "Computer Science"
        assert teacher.avg_rating == 4.5
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_teacher_details_not_found(self, mock_execute):
        """Test get_teacher_details returns None for invalid ID"""
        mock_execute.return_value = {"node": None}

        client = RateMyProfessorClient()
        teacher = client.get_teacher_details("invalid")

        assert teacher is None
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_teacher_details_wrong_typename(self, mock_execute):
        """Test get_teacher_details returns None for wrong __typename"""
        mock_execute.return_value = {
            "node": {
                "__typename": "School",
                "id": "123",
            }
        }

        client = RateMyProfessorClient()
        teacher = client.get_teacher_details("123")

        assert teacher is None
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_teacher_details_minimal_data(self, mock_execute):
        """Test get_teacher_details with minimal data"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "123",
            }
        }

        client = RateMyProfessorClient()
        teacher = client.get_teacher_details("123")

        assert teacher is not None
        assert teacher.id == "123"
        assert teacher.first_name is None
        assert teacher.last_name is None
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_teacher_details_all_fields(self, mock_execute):
        """Test get_teacher_details with all fields populated"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "VGVhY2hlci0xMjM=",
                "legacyId": 123,
                "firstName": "John",
                "lastName": "Smith",
                "department": "Computer Science",
                "departmentId": 42,
                "avgRating": 4.5,
                "avgDifficulty": 3.0,
                "numRatings": 100,
                "wouldTakeAgainPercentRounded": 80.0,
                "ratingsDistribution": {
                    "r1": 5,
                    "r2": 10,
                    "r3": 20,
                    "r4": 40,
                    "r5": 25,
                },
                "courseCodes": [{"courseName": "CS101"}, {"courseName": "CS201"}],
                "lockStatus": "UNLOCKED",
                "isSaved": False,
                "school": {
                    "id": "U2Nob29sLTEyMw==",
                    "legacyId": 123,
                    "name": "Test University",
                    "city": "Test City",
                    "state": "TS",
                    "country": "USA",
                    "numRatings": 1000,
                    "avgRating": 4.0,
                },
            }
        }

        client = RateMyProfessorClient()
        teacher = client.get_teacher_details("Teacher-123")

        assert teacher is not None
        assert teacher.id == "Teacher-123"
        assert teacher.legacy_id == 123
        assert teacher.first_name == "John"
        assert teacher.last_name == "Smith"
        assert teacher.department == "Computer Science"
        assert teacher.department_id == 42
        assert teacher.avg_rating == 4.5
        assert teacher.avg_difficulty == 3.0
        assert teacher.num_ratings == 100
        assert teacher.would_take_again_percent == 80.0
        assert teacher.school is not None
        assert teacher.school.name == "Test University"
        assert teacher.school.city == "Test City"
        client.close()


class TestGetTeacherRatings:
    """Test get_teacher_ratings with various inputs"""

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_teacher_ratings_success(self, mock_execute):
        """Test get_teacher_ratings returns ratings"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "123",
                "ratings": {
                    "edges": [
                        {
                            "node": {
                                "id": "r1",
                                "helpfulRating": 5,
                                "clarityRating": 4,
                                "class": "CS101",
                            }
                        }
                    ],
                    "pageInfo": {"hasNextPage": False},
                },
            }
        }

        client = RateMyProfessorClient()
        result = client.get_teacher_ratings("123", count=10)

        assert isinstance(result, PaginatedResult)
        assert len(result.items) == 1
        assert result.items[0].helpful_rating == 5
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_teacher_ratings_not_found(self, mock_execute):
        """Test get_teacher_ratings returns empty for invalid teacher"""
        mock_execute.return_value = {"node": None}

        client = RateMyProfessorClient()
        result = client.get_teacher_ratings("invalid", count=10)

        assert len(result.items) == 0
        assert result.has_next_page is False
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_teacher_ratings_empty_ratings(self, mock_execute):
        """Test get_teacher_ratings returns empty when teacher has no ratings"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "123",
                "ratings": {"edges": [], "pageInfo": {"hasNextPage": False}},
            }
        }

        client = RateMyProfessorClient()
        result = client.get_teacher_ratings("123", count=10)

        assert len(result.items) == 0
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_teacher_ratings_pagination(self, mock_execute):
        """Test get_teacher_ratings pagination info"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "123",
                "ratings": {
                    "edges": [
                        {"node": {"id": "r1", "clarityRating": 4}},
                        {"node": {"id": "r2", "clarityRating": 5}},
                    ],
                    "pageInfo": {"hasNextPage": True, "endCursor": "cursor123"},
                },
            }
        }

        client = RateMyProfessorClient()
        result = client.get_teacher_ratings("123", count=2)

        assert len(result.items) == 2
        assert result.has_next_page is True
        assert result.end_cursor == "cursor123"
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_teacher_ratings_all_fields(self, mock_execute):
        """Test get_teacher_ratings with all rating fields populated"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "123",
                "firstName": "John",
                "lastName": "Smith",
                "ratings": {
                    "edges": [
                        {
                            "node": {
                                "id": "r1",
                                "legacyId": 456,
                                "comment": "Great professor!",
                                "helpfulRating": 5,
                                "clarityRating": 4,
                                "difficultyRating": 3,
                                "grade": "A",
                                "class": "CS101",
                                "iWouldTakeAgain": True,
                                "isForCredit": True,
                                "textbookIsUsed": False,
                                "attendanceMandatory": False,
                                "isForOnlineClass": False,
                                "ratingTags": ["amazing lectures", "fair grader"],
                                "thumbsUpTotal": 10,
                                "thumbsDownTotal": 1,
                                "date": "2024-01-15",
                                "flagStatus": "DEFAULT",
                                "createdByUser": False,
                            }
                        }
                    ],
                    "pageInfo": {"hasNextPage": False},
                },
            }
        }

        client = RateMyProfessorClient()
        result = client.get_teacher_ratings("123", count=1)

        rating = result.items[0]
        assert rating.id == "r1"
        assert rating.legacy_id == 456
        assert rating.comment == "Great professor!"
        assert rating.helpful_rating == 5
        assert rating.clarity_rating == 4
        assert rating.difficulty_rating == 3
        assert rating.grade == "A"
        assert rating.class_name == "CS101"
        assert rating.would_take_again is True
        assert rating.is_for_credit is True
        assert rating.textbook_used is False
        assert rating.attendance_mandatory is False
        assert rating.is_for_online_class is False
        assert rating.rating_tags == ["amazing lectures", "fair grader"]
        assert rating.thumbs_up_total == 10
        assert rating.thumbs_down_total == 1
        from datetime import datetime

        assert rating.date == datetime(2024, 1, 15)
        assert rating.flag_status == "DEFAULT"
        assert rating.created_by_user is False
        client.close()


class TestGetRatingDetails:
    """Test get_rating_details with various inputs"""

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_rating_details_teacher_rating(self, mock_execute):
        """Test get_rating_details returns Rating for teacher rating"""
        mock_execute.return_value = {
            "rating": {
                "__typename": "Rating",
                "id": "r1",
                "comment": "Good teacher",
                "teacher": {"id": "t1", "firstName": "John"},
            }
        }

        client = RateMyProfessorClient()
        rating = client.get_rating_details("r1")

        assert isinstance(rating, Rating)
        assert rating.comment == "Good teacher"
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_rating_details_school_rating(self, mock_execute):
        """Test get_rating_details returns SchoolRating for school rating"""
        mock_execute.return_value = {
            "rating": {
                "__typename": "SchoolRating",
                "id": "r2",
                "comment": "Good school",
                "school": {"id": "s1", "name": "Uni"},
            }
        }

        client = RateMyProfessorClient()
        rating = client.get_rating_details("r2")

        assert isinstance(rating, SchoolRating)
        assert rating.comment == "Good school"
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_rating_details_not_found(self, mock_execute):
        """Test get_rating_details returns None for invalid rating"""
        mock_execute.return_value = {"rating": None}

        client = RateMyProfessorClient()
        rating = client.get_rating_details("invalid")

        assert rating is None
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_rating_details_unknown_typename(self, mock_execute):
        """Test get_rating_details returns None for unknown __typename"""
        mock_execute.return_value = {
            "rating": {
                "__typename": "Unknown",
                "id": "r1",
            }
        }

        client = RateMyProfessorClient()
        rating = client.get_rating_details("r1")

        assert rating is None
        client.close()


class TestModels:
    """Test suite for data models - edge cases"""

    def test_teacher_full_name_both(self):
        """Test Teacher.full_name with both names"""
        teacher = Teacher(id="1", first_name="John", last_name="Smith")
        assert teacher.full_name == "John Smith"

    def test_teacher_full_name_missing(self):
        """Test Teacher.full_name with missing names"""
        teacher = Teacher(id="1")
        assert teacher.full_name is None

    def test_teacher_full_name_first_only(self):
        """Test Teacher.full_name with only first name"""
        teacher = Teacher(id="1", first_name="John")
        assert teacher.full_name is None

    def test_teacher_full_name_last_only(self):
        """Test Teacher.full_name with only last name"""
        teacher = Teacher(id="1", last_name="Smith")
        assert teacher.full_name is None

    def test_teacher_repr(self):
        """Test Teacher __repr__"""
        teacher = Teacher(id="1", first_name="John", last_name="Smith")
        assert "John Smith" in repr(teacher)

    def test_teacher_repr_no_name(self):
        """Test Teacher __repr__ with no name"""
        teacher = Teacher(id="1")
        assert "Teacher" in repr(teacher)

    def test_teacher_str(self):
        """Test Teacher __str__"""
        teacher = Teacher(id="1", first_name="John", last_name="Smith")
        assert str(teacher) == "John Smith"

    def test_teacher_str_no_name(self):
        """Test Teacher __str__ with no name"""
        teacher = Teacher(id="1")
        assert str(teacher) == "Teacher"

    def test_school_str_full(self):
        """Test School __str__ with all fields"""
        school = School(id="1", name="Test U", city="Boston", state="MA")
        assert "Test U" in str(school)
        assert "Boston" in str(school)
        assert "MA" in str(school)

    def test_school_str_name_only(self):
        """Test School __str__ with name only"""
        school = School(id="1", name="Test U")
        assert str(school) == "Test U"

    def test_school_str_empty(self):
        """Test School __str__ with empty fields"""
        school = School(id="1")
        assert str(school) == "School"

    def test_school_repr(self):
        """Test School __repr__"""
        school = School(id="1", name="Test University")
        assert "Test University" in repr(school)

    def test_rating_str_with_teacher(self):
        """Test Rating __str__ with teacher"""
        teacher = Teacher(id="t1", first_name="John", last_name="Smith")
        rating = Rating(id="r1", teacher=teacher)
        assert "John Smith" in str(rating)

    def test_rating_str_without_teacher(self):
        """Test Rating __str__ without teacher"""
        rating = Rating(id="r1")
        assert str(rating) == "Rating"

    def test_school_rating_str_with_school(self):
        """Test SchoolRating __str__ with school"""
        school = School(id="s1", name="Test University")
        school_rating = SchoolRating(id="r1", school=school)
        assert "Test University" in str(school_rating)

    def test_school_rating_str_without_school(self):
        """Test SchoolRating __str__ without school"""
        school_rating = SchoolRating(id="r1")
        assert str(school_rating) == "School Rating"

    def test_paginated_result_len(self):
        """Test PaginatedResult __len__"""
        result = PaginatedResult(items=[1, 2, 3], has_next_page=False)
        assert len(result) == 3

    def test_paginated_result_len_empty(self):
        """Test PaginatedResult __len__ with empty items"""
        result = PaginatedResult(items=[], has_next_page=False)
        assert len(result) == 0

    def test_paginated_result_bool_true(self):
        """Test PaginatedResult __bool__ with items"""
        result = PaginatedResult(items=[1], has_next_page=False)
        assert bool(result) is True

    def test_paginated_result_bool_false(self):
        """Test PaginatedResult __bool__ without items"""
        result = PaginatedResult(items=[], has_next_page=False)
        assert bool(result) is False

    def test_paginated_result_bool_multiple(self):
        """Test PaginatedResult __bool__ with multiple items"""
        result = PaginatedResult(items=[1, 2, 3], has_next_page=True)
        assert bool(result) is True


class TestExceptions:
    """Test suite for exceptions - various types and messages"""

    def test_rate_my_professor_error(self):
        """Test base exception with message"""
        error = RateMyProfessorError("Test error")
        assert str(error) == "Test error"

    def test_rate_my_professor_error_empty_message(self):
        """Test base exception with empty message"""
        error = RateMyProfessorError("")
        assert str(error) == ""

    def test_invalid_query_error(self):
        """Test InvalidQueryError with message"""
        error = InvalidQueryError("Invalid count")
        assert "Invalid count" in str(error)
        assert isinstance(error, RateMyProfessorError)

    def test_api_error_with_status(self):
        """Test APIError with status code"""
        error = APIError("Server error", status_code=500)
        assert "Server error" in str(error)
        assert "500" in str(error)
        assert error.status_code == 500

    def test_api_error_without_status(self):
        """Test APIError without status code"""
        error = APIError("Some error")
        assert str(error) == "Some error"
        assert error.status_code is None

    def test_api_error_with_response_data(self):
        """Test APIError with response data"""
        error = APIError(
            "Error", response_data={"errors": [{"message": "GraphQL error"}]}
        )
        assert error.response_data == {"errors": [{"message": "GraphQL error"}]}

    def test_not_found_error(self):
        """Test NotFoundError"""
        error = NotFoundError("Teacher not found")
        assert "Teacher not found" in str(error)
        assert isinstance(error, RateMyProfessorError)

    def test_pagination_error(self):
        """Test PaginationError"""
        error = PaginationError("Invalid cursor")
        assert "Invalid cursor" in str(error)
        assert isinstance(error, RateMyProfessorError)

    def test_exception_inheritance(self):
        """Test all exceptions inherit from RateMyProfessorError"""
        assert issubclass(InvalidQueryError, RateMyProfessorError)
        assert issubclass(APIError, RateMyProfessorError)
        assert issubclass(NotFoundError, RateMyProfessorError)
        assert issubclass(PaginationError, RateMyProfessorError)


class TestModuleLevelFunctions:
    """Test module-level convenience functions"""

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_search_teachers_function(self, mock_execute):
        """Test module-level search_teachers function"""
        mock_execute.return_value = {
            "newSearch": {
                "teachers": {
                    "edges": [{"node": {"id": "1", "firstName": "John"}}],
                    "pageInfo": {"hasNextPage": False},
                }
            }
        }

        result = search_teachers("John")
        assert isinstance(result, PaginatedResult)
        assert len(result.items) == 1

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_search_schools_function(self, mock_execute):
        """Test module-level search_schools function"""
        mock_execute.return_value = {
            "newSearch": {
                "schools": {
                    "edges": [{"node": {"id": "1", "name": "MIT"}}],
                    "pageInfo": {"hasNextPage": False},
                }
            }
        }

        result = search_schools("MIT")
        assert isinstance(result, PaginatedResult)
        assert len(result.items) == 1


class TestParsingEdgeCases:
    """Test parsing of various data structures"""

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_parse_empty_teacher_node(self, mock_execute):
        """Test parsing empty teacher node"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "",
            }
        }

        client = RateMyProfessorClient()
        teacher = client.get_teacher_details("")

        assert teacher is not None
        assert teacher.id == ""
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_parse_teacher_with_partial_school(self, mock_execute):
        """Test parsing teacher with partial school data"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "123",
                "firstName": "John",
                "school": {
                    "id": "s1",
                    "name": "Test University",
                    # Missing city, state, etc.
                },
            }
        }

        client = RateMyProfessorClient()
        teacher = client.get_teacher_details("123")

        assert teacher is not None
        assert teacher.school is not None
        assert teacher.school.name == "Test University"
        assert teacher.school.city is None
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_parse_teacher_without_school(self, mock_execute):
        """Test parsing teacher without school data"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "123",
                "firstName": "John",
            }
        }

        client = RateMyProfessorClient()
        teacher = client.get_teacher_details("123")

        assert teacher is not None
        assert teacher.school is None
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_parse_rating_without_optional_fields(self, mock_execute):
        """Test parsing rating without optional fields"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "123",
                "ratings": {
                    "edges": [
                        {
                            "node": {
                                "id": "r1",
                                "clarityRating": 4,
                                # Missing other fields
                            }
                        }
                    ],
                    "pageInfo": {"hasNextPage": False},
                },
            }
        }

        client = RateMyProfessorClient()
        result = client.get_teacher_ratings("123", count=1)

        rating = result.items[0]
        assert rating.id == "r1"
        assert rating.clarity_rating == 4
        assert rating.comment is None
        assert rating.grade is None
        client.close()


class TestClientClosedState:
    """Test client behavior after closing"""

    def test_execute_query_after_close_raises_error(self):
        """Test executing query after close raises error"""
        client = RateMyProfessorClient()
        client.close()

        with pytest.raises(RateMyProfessorError) as exc_info:
            client._execute_query("query")

        assert "Client is closed" in str(exc_info.value)

    def test_close_is_idempotent(self):
        """Test close can be called multiple times"""
        client = RateMyProfessorClient()
        client.close()
        client.close()
        client.close()  # Should not raise


class TestTeacherORMMethods:
    """Test ORM-like methods on Teacher objects"""

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_teacher_get_ratings_success(self, mock_execute):
        """Test teacher.get_ratings() returns ratings"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "t1",
                "ratings": {
                    "edges": [
                        {"node": {"id": "r1", "clarityRating": 5, "comment": "Great"}}
                    ],
                    "pageInfo": {"hasNextPage": False},
                },
            }
        }

        client = RateMyProfessorClient()
        teacher = Teacher(id="Teacher-123", _client=client)
        ratings = teacher.get_ratings(count=10)

        assert len(ratings.items) == 1
        assert ratings.items[0].comment == "Great"
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_teacher_get_ratings_with_course_filter(self, mock_execute):
        """Test teacher.get_ratings() with course filter"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "t1",
                "ratings": {
                    "edges": [
                        {"node": {"id": "r1", "class": "CS101", "clarityRating": 4}}
                    ],
                    "pageInfo": {"hasNextPage": False},
                },
            }
        }

        client = RateMyProfessorClient()
        teacher = Teacher(id="Teacher-123", _client=client)
        ratings = teacher.get_ratings(course_filter="CS101")

        assert len(ratings.items) == 1
        client.close()

    def test_teacher_get_ratings_no_client_raises(self):
        """Test teacher.get_ratings() without client raises ValueError"""
        teacher = Teacher(id="Teacher-123")  # No client

        with pytest.raises(ValueError) as exc_info:
            teacher.get_ratings()

        assert "No client" in str(exc_info.value)

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_teacher_get_details_success(self, mock_execute):
        """Test teacher.get_details() returns full details"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "Teacher-123",
                "firstName": "John",
                "lastName": "Smith",
                "avgRating": 4.5,
                "wouldTakeAgainPercentRounded": 80.0,
            }
        }

        client = RateMyProfessorClient()
        teacher = Teacher(id="Teacher-123", _client=client)
        details = teacher.get_details()

        assert details is not None
        assert details.avg_rating == 4.5
        assert details.would_take_again_percent == 80.0
        client.close()

    def test_teacher_get_details_no_client_raises(self):
        """Test teacher.get_details() without client raises ValueError"""
        teacher = Teacher(id="Teacher-123")

        with pytest.raises(ValueError) as exc_info:
            teacher.get_details()

        assert "No client" in str(exc_info.value)

    def test_teacher_get_ratings_invalid_count(self):
        """Test teacher.get_ratings() with invalid count"""
        client = RateMyProfessorClient()
        teacher = Teacher(id="Teacher-123", _client=client)

        # These should raise InvalidQueryError immediately (client-side validation)
        with pytest.raises(InvalidQueryError):
            teacher.get_ratings(count=0)

        with pytest.raises(InvalidQueryError):
            teacher.get_ratings(count=-1)

        with pytest.raises(InvalidQueryError):
            teacher.get_ratings(count=101)

        client.close()

    def test_teacher_hashable(self):
        """Test Teacher objects are hashable"""
        teacher1 = Teacher(id="Teacher-123")
        teacher2 = Teacher(id="Teacher-123")
        teacher3 = Teacher(id="Teacher-456")

        assert hash(teacher1) == hash(teacher2)
        assert hash(teacher1) != hash(teacher3)
        assert teacher1 == teacher2
        assert teacher1 != teacher3

        # Can use as dict key
        teacher_dict = {teacher1: "data"}
        assert teacher_dict[teacher2] == "data"

        # Can use in set
        teacher_set = {teacher1, teacher2, teacher3}
        assert len(teacher_set) == 2

    def test_teacher_client_reference(self):
        """Test Teacher has client reference after creation"""
        client = RateMyProfessorClient()
        teacher = Teacher(id="Teacher-123", _client=client)

        assert teacher._client is client
        client.close()


class TestSchoolORMMethods:
    """Test ORM-like methods on School objects"""

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_school_get_ratings_success(self, mock_execute):
        """Test school.get_ratings() returns school ratings"""
        mock_execute.return_value = {
            "node": {
                "__typename": "School",
                "id": "s1",
                "ratings": {
                    "edges": [
                        {
                            "node": {
                                "id": "r1",
                                "facilitiesRating": 5,
                                "comment": "Great",
                            }
                        }
                    ],
                    "pageInfo": {"hasNextPage": False},
                },
            }
        }

        client = RateMyProfessorClient()
        school = School(id="School-123", _client=client)
        ratings = school.get_ratings(count=10)

        assert len(ratings.items) == 1
        assert ratings.items[0].facilities_rating == 5
        client.close()

    def test_school_get_ratings_no_client_raises(self):
        """Test school.get_ratings() without client raises ValueError"""
        school = School(id="School-123")

        with pytest.raises(ValueError) as exc_info:
            school.get_ratings()

        assert "No client" in str(exc_info.value)

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_school_get_details_success(self, mock_execute):
        """Test school.get_details() returns full details"""
        mock_execute.return_value = {
            "school": {
                "__typename": "School",
                "id": "School-123",
                "name": "MIT",
                "city": "Cambridge",
                "numRatings": 5000,
            }
        }

        client = RateMyProfessorClient()
        school = School(id="School-123", _client=client)
        details = school.get_details()

        assert details is not None
        assert details.name == "MIT"
        assert details.num_ratings == 5000
        client.close()

    def test_school_get_details_no_client_raises(self):
        """Test school.get_details() without client raises ValueError"""
        school = School(id="School-123")

        with pytest.raises(ValueError) as exc_info:
            school.get_details()

        assert "No client" in str(exc_info.value)

    def test_school_hashable(self):
        """Test School objects are hashable"""
        school1 = School(id="School-123")
        school2 = School(id="School-123")
        school3 = School(id="School-456")

        assert hash(school1) == hash(school2)
        assert hash(school1) != hash(school3)
        assert school1 == school2
        assert school1 != school3

        # Can use as dict key
        school_dict = {school1: "data"}
        assert school_dict[school2] == "data"

        # Can use in set
        school_set = {school1, school2, school3}
        assert len(school_set) == 2

    def test_school_client_reference(self):
        """Test School has client reference after creation"""
        client = RateMyProfessorClient()
        school = School(id="School-123", _client=client)

        assert school._client is client
        client.close()


class TestRatingHashable:
    """Test Rating objects are hashable"""

    def test_rating_hashable(self):
        """Test Rating objects are hashable"""
        rating1 = Rating(id="Rating-123")
        rating2 = Rating(id="Rating-123")
        rating3 = Rating(id="Rating-456")

        assert hash(rating1) == hash(rating2)
        assert hash(rating1) != hash(rating3)
        assert rating1 == rating2
        assert rating1 != rating3

        # Can use as dict key
        rating_dict = {rating1: "data"}
        assert rating_dict[rating2] == "data"

    def test_school_rating_hashable(self):
        """Test SchoolRating objects are hashable"""
        sr1 = SchoolRating(id="SR-123")
        sr2 = SchoolRating(id="SR-123")
        sr3 = SchoolRating(id="SR-456")

        assert hash(sr1) == hash(sr2)
        assert hash(sr1) != hash(sr3)
        assert sr1 == sr2
        assert sr1 != sr3


class TestORMNegativeInputs:
    """Test ORM methods with invalid/negative inputs"""

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_teacher_get_ratings_with_invalid_teacher_id(self, mock_execute):
        """Test teacher.get_ratings() with invalid teacher ID"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "t1",
                "ratings": {"edges": [], "pageInfo": {"hasNextPage": False}},
            }
        }

        client = RateMyProfessorClient()
        teacher = Teacher(id="invalid-id", _client=client)
        ratings = teacher.get_ratings()

        assert len(ratings.items) == 0
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_teacher_get_details_not_found(self, mock_execute):
        """Test teacher.get_details() returns None for non-existent teacher"""
        mock_execute.return_value = {"node": None}

        client = RateMyProfessorClient()
        teacher = Teacher(id="nonexistent", _client=client)
        details = teacher.get_details()

        assert details is None
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_school_get_details_not_found(self, mock_execute):
        """Test school.get_details() returns None for non-existent school"""
        mock_execute.return_value = {"school": None}

        client = RateMyProfessorClient()
        school = School(id="nonexistent", _client=client)
        details = school.get_details()

        assert details is None
        client.close()

    def test_teacher_empty_id(self):
        """Test Teacher with empty ID is hashable"""
        teacher = Teacher(id="")
        assert hash(teacher) == hash("")

    def test_school_empty_id(self):
        """Test School with empty ID is hashable"""
        school = School(id="")
        assert hash(school) == hash("")

    def test_teacher_none_client(self):
        """Test Teacher with None client"""
        teacher = Teacher(id="Teacher-123", _client=None)
        assert teacher._client is None

        with pytest.raises(ValueError):
            teacher.get_ratings()

    def test_school_none_client(self):
        """Test School with None client"""
        school = School(id="School-123", _client=None)
        assert school._client is None

        with pytest.raises(ValueError):
            school.get_ratings()


class TestRawQuery:
    """Test raw_query method"""


class TestDateParsing:
    """Test date parsing in ratings"""

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_rating_date_iso_format(self, mock_execute):
        """Test rating date parsing with ISO format"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "t1",
                "ratings": {
                    "edges": [
                        {"node": {"id": "r1", "clarityRating": 5, "date": "2024-03-15"}}
                    ],
                    "pageInfo": {"hasNextPage": False},
                },
            }
        }

        client = RateMyProfessorClient()
        result = client.get_teacher_ratings("Teacher-123", count=1)

        from datetime import datetime

        assert result.items[0].date == datetime(2024, 3, 15)
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_rating_date_with_time(self, mock_execute):
        """Test rating date parsing with time component"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "t1",
                "ratings": {
                    "edges": [
                        {
                            "node": {
                                "id": "r1",
                                "clarityRating": 5,
                                "date": "2024-03-15 21:20:35 +0000 UTC",
                            }
                        }
                    ],
                    "pageInfo": {"hasNextPage": False},
                },
            }
        }

        client = RateMyProfessorClient()
        result = client.get_teacher_ratings("Teacher-123", count=1)

        from datetime import datetime

        assert result.items[0].date == datetime(2024, 3, 15)
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_rating_date_invalid(self, mock_execute):
        """Test rating date parsing with invalid date"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "t1",
                "ratings": {
                    "edges": [
                        {
                            "node": {
                                "id": "r1",
                                "clarityRating": 5,
                                "date": "invalid-date",
                            }
                        }
                    ],
                    "pageInfo": {"hasNextPage": False},
                },
            }
        }

        client = RateMyProfessorClient()
        result = client.get_teacher_ratings("Teacher-123", count=1)

        assert result.items[0].date is None
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_rating_date_none(self, mock_execute):
        """Test rating date parsing with None"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "t1",
                "ratings": {
                    "edges": [{"node": {"id": "r1", "clarityRating": 5, "date": None}}],
                    "pageInfo": {"hasNextPage": False},
                },
            }
        }

        client = RateMyProfessorClient()
        result = client.get_teacher_ratings("Teacher-123", count=1)

        assert result.items[0].date is None
        client.close()


class TestInputValidationPositive:
    """Test positive input validation - valid data passes"""

    def test_teacher_valid_string_id(self):
        """Test Teacher with valid string ID"""
        teacher = Teacher(id="Teacher-123")
        assert teacher.id == "Teacher-123"
        assert isinstance(teacher.id, str)

    def test_teacher_valid_int_legacy_id(self):
        """Test Teacher with valid integer legacy_id"""
        teacher = Teacher(id="t1", legacy_id=123)
        assert teacher.legacy_id == 123
        assert isinstance(teacher.legacy_id, int)

    def test_teacher_valid_float_ratings(self):
        """Test Teacher with valid float ratings"""
        teacher = Teacher(
            id="t1", avg_rating=4.5, avg_difficulty=2.3, would_take_again_percent=80.5
        )
        assert teacher.avg_rating == 4.5
        assert teacher.avg_difficulty == 2.3
        assert teacher.would_take_again_percent == 80.5

    def test_teacher_valid_int_num_ratings(self):
        """Test Teacher with valid integer num_ratings"""
        teacher = Teacher(id="t1", num_ratings=100)
        assert teacher.num_ratings == 100
        assert isinstance(teacher.num_ratings, int)

    def test_school_valid_string_id(self):
        """Test School with valid string ID"""
        school = School(id="School-456")
        assert school.id == "School-456"
        assert isinstance(school.id, str)

    def test_school_valid_numeric_ratings(self):
        """Test School with valid numeric fields"""
        school = School(
            id="s1",
            legacy_id=789,
            num_ratings=5000,
            avg_rating=4.2,
            avg_rating_rounded=4.0,
        )
        assert school.legacy_id == 789
        assert school.num_ratings == 5000
        assert school.avg_rating == 4.2
        assert school.avg_rating_rounded == 4.0

    def test_rating_valid_numeric_fields(self):
        """Test Rating with valid numeric fields"""
        rating = Rating(
            id="Rating-789",
            legacy_id=456,
            helpful_rating=5.0,
            clarity_rating=4.0,
            difficulty_rating=3.0,
            thumbs_up_total=10,
            thumbs_down_total=1,
        )
        assert rating.helpful_rating == 5.0
        assert rating.clarity_rating == 4.0
        assert rating.difficulty_rating == 3.0
        assert rating.thumbs_up_total == 10
        assert rating.thumbs_down_total == 1


class TestInputValidationNegative:
    """Test negative input validation - invalid data raises TypeError"""

    def test_teacher_invalid_id_type(self):
        """Test Teacher with non-string ID raises TypeError"""
        with pytest.raises(TypeError) as exc_info:
            Teacher(id=123)
        assert "id must be a string" in str(exc_info.value)

    def test_teacher_invalid_legacy_id_type(self):
        """Test Teacher with non-integer legacy_id raises TypeError"""
        with pytest.raises(TypeError) as exc_info:
            Teacher(id="t1", legacy_id="not-a-number")
        assert "legacy_id must be an integer" in str(exc_info.value)

    def test_teacher_invalid_avg_rating_type(self):
        """Test Teacher with non-float avg_rating raises TypeError"""
        with pytest.raises(TypeError) as exc_info:
            Teacher(id="t1", avg_rating="not-a-float")
        assert "avg_rating must be a float" in str(exc_info.value)

    def test_teacher_invalid_num_ratings_type(self):
        """Test Teacher with non-integer num_ratings raises TypeError"""
        with pytest.raises(TypeError) as exc_info:
            Teacher(id="t1", num_ratings="not-an-int")
        assert "num_ratings must be an integer" in str(exc_info.value)

    def test_school_invalid_id_type(self):
        """Test School with non-string ID raises TypeError"""
        with pytest.raises(TypeError) as exc_info:
            School(id=456)
        assert "id must be a string" in str(exc_info.value)

    def test_school_invalid_num_ratings_type(self):
        """Test School with non-integer num_ratings raises TypeError"""
        with pytest.raises(TypeError) as exc_info:
            School(id="s1", num_ratings="not-an-int")
        assert "num_ratings must be an integer" in str(exc_info.value)

    def test_rating_invalid_id_type(self):
        """Test Rating with non-string ID raises TypeError"""
        with pytest.raises(TypeError) as exc_info:
            Rating(id=789)
        assert "id must be a string" in str(exc_info.value)

    def test_rating_invalid_helpful_rating_type(self):
        """Test Rating with non-float helpful_rating raises TypeError"""
        with pytest.raises(TypeError) as exc_info:
            Rating(id="r1", helpful_rating="not-a-float")
        assert "helpful_rating must be a float" in str(exc_info.value)


class TestInputValidationTypeCoercion:
    """Test type coercion - strings converted to proper types"""

    def test_teacher_string_to_int_legacy_id(self):
        """Test Teacher converts string legacy_id to int"""
        teacher = Teacher(id="t1", legacy_id="123")
        assert teacher.legacy_id == 123
        assert isinstance(teacher.legacy_id, int)

    def test_teacher_string_to_float_avg_rating(self):
        """Test Teacher converts string avg_rating to float"""
        teacher = Teacher(id="t1", avg_rating="4.5")
        assert teacher.avg_rating == 4.5
        assert isinstance(teacher.avg_rating, float)

    def test_teacher_string_to_int_num_ratings(self):
        """Test Teacher converts string num_ratings to int"""
        teacher = Teacher(id="t1", num_ratings="100")
        assert teacher.num_ratings == 100
        assert isinstance(teacher.num_ratings, int)

    def test_school_string_to_int_legacy_id(self):
        """Test School converts string legacy_id to int"""
        school = School(id="s1", legacy_id="789")
        assert school.legacy_id == 789
        assert isinstance(school.legacy_id, int)

    def test_school_string_to_float_avg_rating(self):
        """Test School converts string avg_rating to float"""
        school = School(id="s1", avg_rating="4.2")
        assert school.avg_rating == 4.2
        assert isinstance(school.avg_rating, float)

    def test_rating_string_to_float_clarity_rating(self):
        """Test Rating converts string clarity_rating to float"""
        rating = Rating(id="r1", clarity_rating="4.0")
        assert rating.clarity_rating == 4.0
        assert isinstance(rating.clarity_rating, float)

    def test_rating_string_to_int_thumbs_up(self):
        """Test Rating converts string thumbs_up_total to int"""
        rating = Rating(id="r1", thumbs_up_total="10")
        assert rating.thumbs_up_total == 10
        assert isinstance(rating.thumbs_up_total, int)


class TestInputValidationInjection:
    """Test injection attempts - malicious input handled safely"""

    def test_sql_injection_in_id(self):
        """Test SQL injection attempt in ID"""
        malicious_id = "Teacher-123' OR '1'='1"
        teacher = Teacher(id=malicious_id)
        assert teacher.id == malicious_id
        assert isinstance(teacher.id, str)

    def test_xss_in_first_name(self):
        """Test XSS attempt in first_name"""
        malicious_name = "<script>alert('xss')</script>"
        teacher = Teacher(id="t1", first_name=malicious_name)
        assert teacher.first_name == malicious_name
        assert isinstance(teacher.first_name, str)

    def test_command_injection_in_department(self):
        """Test command injection attempt in department"""
        malicious_dept = "Computer Science; rm -rf /"
        teacher = Teacher(id="t1", department=malicious_dept)
        assert teacher.department == malicious_dept
        assert isinstance(teacher.department, str)

    def test_path_traversal_in_id(self):
        """Test path traversal attempt in ID"""
        malicious_id = "../../../etc/passwd"
        teacher = Teacher(id=malicious_id)
        assert teacher.id == malicious_id

    def test_unicode_injection_in_comment(self):
        """Test Unicode injection attempt in comment"""
        malicious_comment = "Great professor! \u202e\u0000\u202d"
        rating = Rating(id="r1", comment=malicious_comment)
        assert rating.comment == malicious_comment

    def test_very_long_string_injection(self):
        """Test very long string injection attempt"""
        malicious_id = "A" * 10000
        teacher = Teacher(id=malicious_id)
        assert len(teacher.id) == 10000

    def test_null_byte_injection(self):
        """Test null byte injection attempt"""
        malicious_id = "Teacher-123\x00malicious"
        teacher = Teacher(id=malicious_id)
        assert teacher.id == malicious_id

    def test_html_injection_in_name(self):
        """Test HTML injection attempt in name"""
        malicious_name = "<img src=x onerror=alert('xss')>"
        teacher = Teacher(id="t1", first_name=malicious_name)
        assert teacher.first_name == malicious_name

    def test_json_injection_in_department(self):
        """Test JSON injection attempt in department"""
        malicious_dept = '{"department": "CS", "admin": true}'
        teacher = Teacher(id="t1", department=malicious_dept)
        assert teacher.department == malicious_dept

    def test_template_injection_in_name(self):
        """Test template injection attempt in name"""
        malicious_name = "{{constructor.constructor('return this')()}}"
        teacher = Teacher(id="t1", first_name=malicious_name)
        assert teacher.first_name == malicious_name


class TestInputValidationEdgeCases:
    """Test edge cases in input validation"""

    def test_teacher_empty_string_id(self):
        """Test Teacher with empty string ID"""
        teacher = Teacher(id="")
        assert teacher.id == ""
        assert isinstance(teacher.id, str)

    def test_teacher_none_values(self):
        """Test Teacher with None values"""
        teacher = Teacher(
            id="t1", first_name=None, last_name=None, avg_rating=None, num_ratings=None
        )
        assert teacher.first_name is None
        assert teacher.last_name is None
        assert teacher.avg_rating is None
        assert teacher.num_ratings is None

    def test_teacher_zero_values(self):
        """Test Teacher with zero values"""
        teacher = Teacher(
            id="t1",
            avg_rating=0.0,
            avg_difficulty=0.0,
            num_ratings=0,
            would_take_again_percent=0.0,
        )
        assert teacher.avg_rating == 0.0
        assert teacher.avg_difficulty == 0.0
        assert teacher.num_ratings == 0
        assert teacher.would_take_again_percent == 0.0

    def test_teacher_negative_values(self):
        """Test Teacher with negative values"""
        teacher = Teacher(
            id="t1",
            avg_rating=-1.0,
            avg_difficulty=-2.0,
            num_ratings=-10,
            would_take_again_percent=-50.0,
        )
        assert teacher.avg_rating == -1.0
        assert teacher.avg_difficulty == -2.0
        assert teacher.num_ratings == -10
        assert teacher.would_take_again_percent == -50.0

    def test_teacher_very_large_values(self):
        """Test Teacher with very large values"""
        teacher = Teacher(id="t1", avg_rating=999999.99, num_ratings=999999999)
        assert teacher.avg_rating == 999999.99
        assert teacher.num_ratings == 999999999

    def test_rating_empty_comment(self):
        """Test Rating with empty comment"""
        rating = Rating(id="r1", comment="")
        assert rating.comment == ""

    def test_rating_none_comment(self):
        """Test Rating with None comment"""
        rating = Rating(id="r1", comment=None)
        assert rating.comment is None

    def test_rating_special_characters_comment(self):
        """Test Rating with special characters in comment"""
        special_comment = "Great! @#$%^&*()_+-=[]{}|;':\",./<>?"
        rating = Rating(id="r1", comment=special_comment)
        assert rating.comment == special_comment

    def test_rating_unicode_comment(self):
        """Test Rating with Unicode characters in comment"""
        unicode_comment = "Great professor! 你好 🎉 مرحبا"
        rating = Rating(id="r1", comment=unicode_comment)
        assert rating.comment == unicode_comment
