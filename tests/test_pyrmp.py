"""
Tests for pyrmp package
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from pyrmp import RateMyProfessorClient
from pyrmp.models import Teacher, School, Rating, PaginatedResult
from pyrmp.exceptions import RateMyProfessorError, InvalidQueryError


class TestRateMyProfessorClient:
    """Test suite for RateMyProfessorClient"""

    def test_client_initialization(self):
        """Test client can be initialized"""
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
        """Test closing client multiple times"""
        client = RateMyProfessorClient()
        client.close()
        client.close()  # Should not raise

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_search_teachers_returns_paginated_result(self, mock_execute):
        """Test search_teachers returns PaginatedResult"""
        mock_execute.return_value = {
            "newSearch": {
                "teachers": {
                    "edges": [{"node": {"id": "1", "firstName": "John", "lastName": "Smith"}}],
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
        """Test search with no results"""
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

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_teacher_details(self, mock_execute):
        """Test get_teacher_details"""
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
        """Test get_teacher_details with invalid ID"""
        mock_execute.return_value = {"node": None}

        client = RateMyProfessorClient()
        teacher = client.get_teacher_details("invalid")

        assert teacher is None
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_teacher_ratings(self, mock_execute):
        """Test get_teacher_ratings"""
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


class TestModels:
    """Test suite for data models"""

    def test_teacher_full_name(self):
        """Test Teacher.full_name property"""
        teacher = Teacher(id="1", first_name="John", last_name="Smith")
        assert teacher.full_name == "John Smith"

    def test_teacher_full_name_missing(self):
        """Test Teacher.full_name with missing names"""
        teacher = Teacher(id="1")
        assert teacher.full_name is None

    def test_teacher_repr(self):
        """Test Teacher __repr__"""
        teacher = Teacher(id="1", first_name="John", last_name="Smith")
        assert "John Smith" in repr(teacher)

    def test_school_str(self):
        """Test School __str__"""
        school = School(id="1", name="Test U", city="Boston", state="MA")
        assert "Test U" in str(school)
        assert "Boston" in str(school)

    def test_paginated_result_len(self):
        """Test PaginatedResult __len__"""
        result = PaginatedResult(items=[1, 2, 3], has_next_page=False)
        assert len(result) == 3

    def test_paginated_result_bool(self):
        """Test PaginatedResult __bool__"""
        result_empty = PaginatedResult(items=[], has_next_page=False)
        result_full = PaginatedResult(items=[1], has_next_page=False)

        assert bool(result_empty) is False
        assert bool(result_full) is True


class TestExceptions:
    """Test suite for exceptions"""

    def test_rate_my_professor_error(self):
        """Test base exception"""
        with pytest.raises(RateMyProfessorError):
            raise RateMyProfessorError("Test error")

    def test_invalid_query_error(self):
        """Test InvalidQueryError"""
        with pytest.raises(InvalidQueryError) as exc_info:
            raise InvalidQueryError("Invalid count")

        assert "Invalid count" in str(exc_info.value)
