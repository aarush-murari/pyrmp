"""
Integration tests comparing real API responses vs library methods.

Tests cover:
- Real professors from different universities
- Real universities
- Fake/non-existent professors and universities (edge cases)
- Mock data matching real API structure

Rate limiting handling:
- Waits 10s when rate limited (429 response)
- 1s delay between API calls
"""

import time
import pytest
import requests
from unittest.mock import patch, Mock
from pyrmp import RateMyProfessorClient
from pyrmp.models import Teacher, School, Rating, PaginatedResult

RMP_GRAPHQL = "https://www.ratemyprofessors.com/graphql"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.ratemyprofessors.com",
    "Referer": "https://www.ratemyprofessors.com/",
}


def make_api_call_with_retry(url: str, **kwargs) -> requests.Response:
    """
    Make API call with rate limiting and 403 handling.

    Handles:
    - 403 Forbidden: Waits 10s, retries (API blocking suspicious traffic)
    - 429 Too Many Requests: Waits 10s, retries (rate limiting)
    - Empty responses: Waits 5s, retries
    - 1s delay between all successful calls
    """
    kwargs.setdefault("timeout", 30)
    response = requests.post(url, **kwargs)

    # Check for blocking/rate limiting
    if response.status_code == 403:
        print(f"  403 Forbidden detected, waiting 10s before retry...")
        time.sleep(10)
        response = requests.post(url, **kwargs)

    elif response.status_code == 429:
        print(f"  429 Rate Limited, waiting 10s before retry...")
        time.sleep(10)
        response = requests.post(url, **kwargs)

    # Check for empty responses (likely blocked)
    elif response.status_code == 200 and not response.text:
        print(f"  Empty response detected, waiting 5s before retry...")
        time.sleep(5)
        response = requests.post(url, **kwargs)

    return response


# =============================================================================
# REAL DATA TESTS - Actual professors from different universities
# =============================================================================


class TestIntegrationRealProfessors:
    """Test with real professors from various universities"""

    def test_real_prof_mit(self):
        """Test real professor from MIT"""
        client = RateMyProfessorClient()
        result = client.search_teachers("Patrick Winston", count=5)

        assert len(result.items) > 0
        teacher = result.items[0]
        assert teacher.id is not None
        assert teacher.legacy_id is not None
        assert teacher.first_name == "Patrick"
        assert teacher.last_name == "Winston"
        assert teacher.school is not None

        client.close()

    def test_real_prof_stanford(self):
        """Test real professor from Stanford"""
        client = RateMyProfessorClient()
        result = client.search_teachers("Andrew Ng", count=5)

        assert len(result.items) > 0
        teacher = result.items[0]
        assert teacher.id is not None
        assert teacher.first_name == "Andrew"
        assert teacher.last_name == "Ng"

        client.close()

    def test_real_prof_berkeley(self):
        """Test real professor from UC Berkeley"""
        client = RateMyProfessorClient()
        result = client.search_teachers("John Kubiatowicz", count=5)

        assert len(result.items) > 0
        teacher = result.items[0]
        assert teacher.id is not None
        assert teacher.first_name == "John"

        client.close()

    def test_real_prof_multiple_results(self):
        """Test searching returns multiple professors"""
        client = RateMyProfessorClient()
        result = client.search_teachers("David Smith", count=20)

        assert len(result.items) > 0
        assert len(result.items) <= 20

        for teacher in result.items:
            assert teacher.id is not None
            assert teacher.full_name is not None

        client.close()


class TestIntegrationRealUniversities:
    """Test with real universities"""

    def test_real_uni_mit(self):
        """Test searching for MIT"""
        client = RateMyProfessorClient()
        result = client.search_schools("MIT", count=5)

        assert len(result.items) > 0
        school = result.items[0]
        assert school.id is not None
        assert "MIT" in school.name or "Massachusetts" in school.name

        client.close()

    def test_real_uni_stanford(self):
        """Test searching for Stanford"""
        client = RateMyProfessorClient()
        result = client.search_schools("Stanford", count=5)

        assert len(result.items) > 0
        school = result.items[0]
        assert school.id is not None
        assert "Stanford" in school.name

        client.close()

    def test_real_uni_berkeley(self):
        """Test searching for UC Berkeley"""
        client = RateMyProfessorClient()
        result = client.search_schools("UC Berkeley", count=5)

        assert len(result.items) > 0
        school = result.items[0]
        assert school.id is not None

        client.close()

    def test_real_uni_all_fields(self):
        """Test university returns all fields"""
        client = RateMyProfessorClient()
        result = client.search_schools("Yale", count=3)

        assert len(result.items) > 0
        school = result.items[0]
        assert school.id is not None
        assert school.name is not None
        assert school.city is not None or school.city == ""
        assert school.state is not None or school.state == ""

        client.close()


# =============================================================================
# FAKE / NON-EXISTENT DATA TESTS - Edge cases
# =============================================================================


class TestIntegrationFakeData:
    """Test with fake/non-existent professors and universities"""

    def test_fake_professor(self):
        """Test searching for a fake professor name"""
        client = RateMyProfessorClient()
        result = client.search_teachers("zxczxczxczxczxczxczxczxczxczxc", count=10)

        assert len(result.items) == 0
        assert result.has_next_page is False

        client.close()

    def test_fake_professor_random_string(self):
        """Test searching with random gibberish"""
        client = RateMyProfessorClient()
        result = client.search_teachers("asdfghjklqwertyuiop12345", count=10)

        assert len(result.items) == 0

        client.close()

    def test_fake_university(self):
        """Test searching for a fake university"""
        client = RateMyProfessorClient()
        result = client.search_schools("xyzfakecollege12345", count=10)

        assert len(result.items) == 0

        client.close()

    def test_empty_query(self):
        """Test searching with empty string"""
        client = RateMyProfessorClient()
        result = client.search_teachers("", count=5)

        assert result is not None

        client.close()


# =============================================================================
# REAL API VS LIBRARY COMPARISON TESTS
# =============================================================================


class TestIntegrationRealVsLibrary:
    """Compare real API responses with library methods"""

    def test_search_teachers_real_api_vs_library(self):
        """Compare raw API response vs library search_teachers"""
        search_query = "Patrick Winston"

        raw_query = """query {
            newSearch {
                teachers(query: {text: "Patrick Winston"}, first: 3) {
                    edges {
                        node {
                            id
                            legacyId
                            firstName
                            lastName
                            department
                            avgRating
                            avgDifficulty
                            numRatings
                            wouldTakeAgainPercentRounded
                            school {
                                id
                                name
                            }
                        }
                    }
                }
            }
        }"""
        raw_response = make_api_call_with_retry(
            RMP_GRAPHQL, json={"query": raw_query}, headers=HEADERS, timeout=30
        )
        time.sleep(1)

        if raw_response.status_code != 200:
            pytest.fail(
                f"API returned {raw_response.status_code}: {raw_response.text[:200]}"
            )
        if not raw_response.text or not raw_response.text.startswith("{"):
            pytest.fail(f"API returned non-JSON response: {raw_response.text[:200]}")

        raw_data = (
            raw_response.json()
            .get("data", {})
            .get("newSearch", {})
            .get("teachers", {})
            .get("edges", [])
        )

        client = RateMyProfessorClient()
        library_result = client.search_teachers(search_query, count=3)

        # Both should return results
        assert len(raw_data) > 0
        assert len(library_result.items) > 0

        # Check structure matches - not exact IDs (search is non-deterministic)
        for teacher in library_result.items:
            assert teacher.id is not None
            assert teacher.legacy_id is not None
            assert teacher.first_name is not None
            assert teacher.last_name is not None

        client.close()

    def test_teacher_details_real_api_vs_library(self):
        """Compare raw API response vs library get_teacher_details"""
        teacher_id = "VGVhY2hlci05NDExNzQ="

        raw_query = """query {
            node(id: "VGVhY2hlci05NDExNzQ=") {
                __typename
                ... on Teacher {
                    id
                    legacyId
                    firstName
                    lastName
                    department
                    avgRating
                    avgDifficulty
                    numRatings
                    wouldTakeAgainPercentRounded
                    school {
                        id
                        legacyId
                        name
                        city
                        state
                    }
                }
            }
        }"""
        raw_response = make_api_call_with_retry(
            RMP_GRAPHQL, json={"query": raw_query}, headers=HEADERS, timeout=30
        )
        time.sleep(1)

        if raw_response.status_code != 200:
            pytest.fail(
                f"API returned {raw_response.status_code}: {raw_response.text[:200]}"
            )
        if not raw_response.text or not raw_response.text.startswith("{"):
            pytest.fail(f"API returned invalid response: {raw_response.text[:200]}")

        raw_teacher = raw_response.json().get("data", {}).get("node")

        client = RateMyProfessorClient()
        library_teacher = client.get_teacher_details(teacher_id)

        assert library_teacher is not None
        assert raw_teacher is not None

        # Both should have same fields populated
        assert library_teacher.id == teacher_id
        assert library_teacher.first_name is not None
        assert library_teacher.last_name is not None
        assert library_teacher.avg_rating is not None

        # Raw API should also have these
        assert raw_teacher["id"] == teacher_id
        assert raw_teacher["firstName"] is not None

        client.close()

    def test_teacher_ratings_real_api_vs_library(self):
        """Compare raw API response vs library get_teacher_ratings"""
        teacher_id = "VGVhY2hlci05NDExNzQ="

        raw_query = """query RatingsListQuery($count: Int!, $id: ID!) {
            node(id: $id) {
                __typename
                ... on Teacher {
                    id
                    ratings(first: $count) {
                        edges {
                            node {
                                id
                                clarityRating
                                difficultyRating
                                grade
                            }
                        }
                    }
                }
            }
        }"""
        variables = {"count": 3, "id": teacher_id}
        raw_response = make_api_call_with_retry(
            RMP_GRAPHQL,
            json={"query": raw_query, "variables": variables},
            headers=HEADERS,
            timeout=30,
        )
        time.sleep(1)

        if raw_response.status_code != 200:
            pytest.fail(
                f"API returned {raw_response.status_code}: {raw_response.text[:200]}"
            )
        if not raw_response.text or not raw_response.text.startswith("{"):
            pytest.fail(f"API returned invalid response: {raw_response.text[:200]}")

        raw_ratings = (
            raw_response.json()
            .get("data", {})
            .get("node", {})
            .get("ratings", {})
            .get("edges", [])
        )

        client = RateMyProfessorClient()
        library_result = client.get_teacher_ratings(teacher_id, count=3)

        # Both should return results
        assert len(raw_ratings) > 0
        assert len(library_result.items) > 0

        # Check structure matches - ratings may differ if new ones added
        for rating in library_result.items:
            assert rating.id is not None
            assert rating.clarity_rating is not None
            assert rating.difficulty_rating is not None

        client.close()


# =============================================================================
# MOCK DATA TESTS - Using mocked responses
# =============================================================================


class TestMockData:
    """Test with mocked API responses matching real API structure"""

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_mock_teacher_search(self, mock_execute):
        """Test teacher search with mock data matching real API structure"""
        mock_execute.return_value = {
            "newSearch": {
                "teachers": {
                    "edges": [
                        {
                            "node": {
                                "id": "VGVhY2hlci0xMjM=",
                                "legacyId": 123,
                                "firstName": "Test",
                                "lastName": "Professor",
                                "department": "Computer Science",
                                "avgRating": 4.5,
                                "avgDifficulty": 2.5,
                                "numRatings": 100,
                                "wouldTakeAgainPercentRounded": 80.0,
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
                    ],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                }
            }
        }

        client = RateMyProfessorClient()
        result = client.search_teachers("Test Professor")

        assert len(result.items) == 1
        teacher = result.items[0]
        assert teacher.id == "VGVhY2hlci0xMjM="
        assert teacher.first_name == "Test"
        assert teacher.last_name == "Professor"
        assert teacher.avg_rating == 4.5
        assert teacher.school.name == "Test University"

        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_mock_school_search(self, mock_execute):
        """Test school search with mock data matching real API structure"""
        mock_execute.return_value = {
            "newSearch": {
                "schools": {
                    "edges": [
                        {
                            "node": {
                                "id": "U2Nob29sLTEyMw==",
                                "legacyId": 123,
                                "name": "Fake University",
                                "city": "Fake City",
                                "state": "FC",
                                "country": "USA",
                                "numRatings": 500,
                                "avgRatingRounded": 4.0,
                            }
                        }
                    ],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                }
            }
        }

        client = RateMyProfessorClient()
        result = client.search_schools("Fake University")

        assert len(result.items) == 1
        school = result.items[0]
        assert school.id == "U2Nob29sLTEyMw=="
        assert school.name == "Fake University"
        assert school.city == "Fake City"

        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_mock_teacher_ratings(self, mock_execute):
        """Test teacher ratings with mock data matching real API structure"""
        mock_execute.return_value = {
            "node": {
                "__typename": "Teacher",
                "id": "VGVhY2hlci0xMjM=",
                "firstName": "Test",
                "lastName": "Professor",
                "ratings": {
                    "edges": [
                        {
                            "node": {
                                "id": "UmF0aW5nLTEyMw==",
                                "legacyId": 123,
                                "comment": "Great teacher!",
                                "clarityRating": 5.0,
                                "difficultyRating": 3.0,
                                "grade": "A",
                                "class": "CS101",
                                "helpfulRating": 5,
                                "isForCredit": True,
                                "textbookIsUsed": False,
                                "attendanceMandatory": False,
                                "isForOnlineClass": False,
                                "wouldTakeAgain": True,
                                "ratingTags": ["amazing lectures", "fair grader"],
                                "thumbsUpTotal": 10,
                                "thumbsDownTotal": 1,
                                "date": "2024-01-15",
                                "flagStatus": "DEFAULT",
                                "createdByUser": False,
                            }
                        }
                    ],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                },
            }
        }

        client = RateMyProfessorClient()
        result = client.get_teacher_ratings("VGVhY2hlci0xMjM=", count=10)

        assert len(result.items) == 1
        rating = result.items[0]
        assert rating.id == "UmF0aW5nLTEyMw=="
        assert rating.comment == "Great teacher!"
        assert rating.clarity_rating == 5.0
        assert rating.difficulty_rating == 3.0
        assert rating.grade == "A"

        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_mock_school_ratings(self, mock_execute):
        """Test school ratings with mock data matching real API structure"""
        mock_execute.return_value = {
            "node": {
                "__typename": "School",
                "id": "U2Nob29sLTEyMw==",
                "name": "Test University",
                "ratings": {
                    "edges": [
                        {
                            "node": {
                                "id": "U2Nob29sUmF0aW5nLTEyMw==",
                                "legacyId": 123,
                                "comment": "Great campus!",
                                "clubsRating": 4.0,
                                "facilitiesRating": 5.0,
                                "foodRating": 3.5,
                                "happinessRating": 4.5,
                                "internetRating": 3.0,
                                "locationRating": 4.0,
                                "opportunitiesRating": 4.5,
                                "reputationRating": 5.0,
                                "safetyRating": 4.0,
                                "socialRating": 4.5,
                                "date": "2024-01-10",
                                "thumbsUpTotal": 5,
                                "thumbsDownTotal": 0,
                                "flagStatus": "DEFAULT",
                                "createdByUser": False,
                            }
                        }
                    ],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                },
            }
        }

        client = RateMyProfessorClient()
        result = client.get_school_ratings("U2Nob29sLTEyMw==", count=10)

        assert len(result.items) == 1
        school_rating = result.items[0]
        assert school_rating.id == "U2Nob29sUmF0aW5nLTEyMw=="
        assert school_rating.comment == "Great campus!"
        assert school_rating.facilities_rating == 5.0
        assert school_rating.safety_rating == 4.0

        client.close()

    @patch.object(RateMyProfessorClient, "_execute_query")
    def test_mock_not_found(self, mock_execute):
        """Test handling of non-existent resources"""
        mock_execute.return_value = {"node": None}

        client = RateMyProfessorClient()
        teacher = client.get_teacher_details("fake_id")
        assert teacher is None

        client.close()


# =============================================================================
# EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_very_long_search_query(self):
        """Test searching with a very long query string"""
        client = RateMyProfessorClient()
        long_query = "a" * 1000
        result = client.search_teachers(long_query)

        assert result is not None

        client.close()

    def test_special_characters_in_query(self):
        """Test searching with special characters"""
        client = RateMyProfessorClient()
        result = client.search_teachers("John O'Brien-Smith", count=5)

        assert result is not None

        client.close()

    def test_count_boundary_values(self):
        """Test with boundary values for count parameter"""
        client = RateMyProfessorClient()

        result_1 = client.search_teachers("John", count=1)
        assert len(result_1.items) <= 1

        result_100 = client.search_teachers("John", count=100)
        assert len(result_100.items) <= 100

        client.close()
