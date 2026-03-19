import pytest
from unittest.mock import patch, MagicMock
from pyrmp import RateMyProfessorClient
from pyrmp.models import School, Rating, SchoolRating, PaginatedResult
from pyrmp.exceptions import RateMyProfessorError, InvalidQueryError


class TestRateMyProfessorClientExtended:
    """Extended test suite for RateMyProfessorClient"""

    @pytest.fixture
    def client(self):
        client = RateMyProfessorClient()
        yield client
        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_search_schools_returns_paginated_result(self, mock_execute, client):
        """Test search_schools returns PaginatedResult"""
        mock_execute.return_value = {
            "newSearch": {
                "schools": {
                    "edges": [
                        {
                            "node": {
                                "id": "school1",
                                "name": "Test University",
                                "city": "Test City",
                                "state": "TS",
                            }
                        }
                    ],
                    "pageInfo": {"hasNextPage": True, "endCursor": "school_cursor"},
                }
            }
        }

        result = client.search_schools("Test", count=10)

        assert isinstance(result, PaginatedResult)
        assert len(result.items) == 1
        assert isinstance(result.items[0], School)
        assert result.items[0].name == "Test University"
        assert result.has_next_page is True
        assert result.end_cursor == "school_cursor"

    def test_search_schools_invalid_count(self, client):
        """Test search_schools validation"""
        with pytest.raises(InvalidQueryError):
            client.search_schools("Test", count=0)

        with pytest.raises(InvalidQueryError):
            client.search_schools("Test", count=101)

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_school_details_success(self, mock_execute, client):
        """Test get_school_details success"""
        mock_execute.return_value = {
            "school": {
                "__typename": "School",
                "id": "school1",
                "name": "Test University",
                "numRatings": 500,
                "avgRating": 3.5,
            }
        }

        school = client.get_school_details("school1")

        assert isinstance(school, School)
        assert school.id == "school1"
        assert school.name == "Test University"
        assert school.avg_rating == 3.5

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_school_details_not_found(self, mock_execute, client):
        """Test get_school_details when not found"""
        mock_execute.return_value = {"school": None}

        school = client.get_school_details("invalid_id")
        assert school is None

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_school_ratings_success(self, mock_execute, client):
        """Test get_school_ratings success"""
        mock_execute.return_value = {
            "node": {
                "__typename": "School",
                "id": "school1",
                "ratings": {
                    "edges": [
                        {
                            "node": {
                                "id": "rating1",
                                "comment": "Great school",
                                "safetyRating": 5.0,
                            }
                        }
                    ],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                },
            }
        }

        result = client.get_school_ratings("school1")

        assert isinstance(result, PaginatedResult)
        assert len(result.items) == 1
        assert isinstance(result.items[0], SchoolRating)
        assert result.items[0].comment == "Great school"
        assert result.items[0].safety_rating == 5.0

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_school_ratings_invalid_node(self, mock_execute, client):
        """Test get_school_ratings with invalid node type"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",  # Should be School
                "id": "teacher1",
            }
        }

        result = client.get_school_ratings("teacher1")
        assert len(result.items) == 0

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_rating_details_teacher_rating(self, mock_execute, client):
        """Test get_rating_details for a teacher rating"""
        mock_execute.return_value = {
            "rating": {
                "__typename": "Rating",
                "id": "rating1",
                "comment": "Good teacher",
                "teacher": {"id": "t1", "firstName": "John"},
            }
        }

        rating = client.get_rating_details("rating1")

        assert isinstance(rating, Rating)
        assert rating.comment == "Good teacher"
        assert rating.teacher is not None
        assert rating.teacher.first_name == "John"

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_rating_details_school_rating(self, mock_execute, client):
        """Test get_rating_details for a school rating"""
        mock_execute.return_value = {
            "rating": {
                "__typename": "SchoolRating",
                "id": "rating2",
                "comment": "Good school",
                "school": {"id": "s1", "name": "Uni"},
            }
        }

        rating = client.get_rating_details("rating2")

        assert isinstance(rating, SchoolRating)
        assert rating.comment == "Good school"
        assert rating.school is not None
        assert rating.school.name == "Uni"

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_get_rating_details_not_found(self, mock_execute, client):
        """Test get_rating_details when not found"""
        mock_execute.return_value = {"rating": None}

        rating = client.get_rating_details("missing")
        assert rating is None

    def test_error_handling_403(self, client):
        """Test handling of 403 error"""
        mock_query = "query Test { teacher { id } }"
        with patch.object(
            client.client, "execute", side_effect=Exception("403 Forbidden")
        ):
            with pytest.raises(RateMyProfessorError) as exc:
                client._execute_query(mock_query)
            assert "Access forbidden" in str(exc.value)

    def test_error_handling_429(self, client):
        """Test handling of 429 rate limit error"""
        mock_query = "query Test { teacher { id } }"
        with patch.object(
            client.client, "execute", side_effect=Exception("429 Too Many Requests")
        ):
            with pytest.raises(RateMyProfessorError) as exc:
                client._execute_query(mock_query)
            assert "Rate limited" in str(exc.value)

    def test_error_handling_invalid_base64(self, client):
        """Test handling of invalid ID error"""
        mock_query = "query Test { teacher { id } }"
        with patch.object(
            client.client, "execute", side_effect=Exception("invalid base64")
        ):
            with pytest.raises(RateMyProfessorError) as exc:
                client._execute_query(mock_query)
            assert "Invalid ID format" in str(exc.value)

    def test_error_handling_generic(self, client):
        """Test handling of generic errors"""
        with patch.object(
            client.client, "execute", side_effect=Exception("Something went wrong")
        ):
            with pytest.raises(RateMyProfessorError) as exc:
                client._execute_query("query")
            assert "GraphQL query failed" in str(exc.value)

    def test_client_closed_error(self, client):
        """Test querying a closed client raises error"""
        client.close()
        with pytest.raises(RateMyProfessorError) as exc:
            client._execute_query("query")
        assert "Client is closed" in str(exc.value)
