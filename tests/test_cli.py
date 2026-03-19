"""
Tests for pyrmp CLI.

Tests CLI argument parsing and command execution.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from pyrmp.cli import main
from pyrmp.models import Teacher, School, PaginatedResult
import sys


class TestCLISearch:
    """Test search command"""

    @patch("pyrmp.cli.RateMyProfessorClient")
    def test_search_basic(self, mock_client_class, capsys):
        """Test basic search output"""
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        mock_client.search_teachers.return_value = PaginatedResult(
            items=[
                Teacher(
                    id="Teacher-123",
                    first_name="John",
                    last_name="Smith",
                    department="CS",
                    avg_rating=4.5,
                    num_ratings=100,
                    school=School(id="School-1", name="MIT"),
                )
            ],
            has_next_page=False,
        )

        sys.argv = ["pyrmp", "search", "John Smith"]
        main()

        captured = capsys.readouterr()
        assert "John Smith" in captured.out
        assert "Teacher-123" in captured.out
        assert "MIT" in captured.out
        assert "4.5/5" in captured.out

    @patch("pyrmp.cli.RateMyProfessorClient")
    def test_search_no_ids(self, mock_client_class, capsys):
        """Test search with --no-ids"""
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        mock_client.search_teachers.return_value = PaginatedResult(
            items=[
                Teacher(
                    id="Teacher-123",
                    first_name="John",
                    last_name="Smith",
                    department="CS",
                    school=School(id="School-1", name="MIT"),
                )
            ],
            has_next_page=False,
        )

        sys.argv = ["pyrmp", "search", "John Smith", "--no-ids"]
        main()

        captured = capsys.readouterr()
        assert "John Smith" in captured.out
        assert "Teacher-123" not in captured.out

    @patch("pyrmp.cli.RateMyProfessorClient")
    def test_search_json(self, mock_client_class, capsys):
        """Test search with --json"""
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        mock_client.search_teachers.return_value = PaginatedResult(
            items=[
                Teacher(
                    id="Teacher-123",
                    first_name="John",
                    last_name="Smith",
                    department="CS",
                    school=School(id="School-1", name="MIT"),
                )
            ],
            has_next_page=False,
        )

        sys.argv = ["pyrmp", "search", "John Smith", "--json"]
        main()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data) == 1
        assert data[0]["name"] == "John Smith"
        assert data[0]["id"] == "Teacher-123"

    @patch("pyrmp.cli.RateMyProfessorClient")
    def test_search_empty(self, mock_client_class, capsys):
        """Test search with no results"""
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        mock_client.search_teachers.return_value = PaginatedResult(
            items=[], has_next_page=False
        )

        sys.argv = ["pyrmp", "search", "nonexistent123"]
        main()

        captured = capsys.readouterr()
        assert "No results found" in captured.out


class TestCLITeacher:
    """Test teacher command"""

    @patch("pyrmp.cli.RateMyProfessorClient")
    def test_teacher_basic(self, mock_client_class, capsys):
        """Test teacher details output"""
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        teacher = Teacher(
            id="Teacher-123",
            first_name="John",
            last_name="Smith",
            department="CS",
            avg_rating=4.5,
            num_ratings=100,
            avg_difficulty=2.0,
            would_take_again_percent=80.0,
            course_codes=["CS101", "CS201"],
            school=School(id="School-1", name="MIT"),
        )

        mock_client.search_teachers.return_value = PaginatedResult(
            items=[teacher], has_next_page=False
        )
        mock_client.get_teacher_details.return_value = teacher

        sys.argv = ["pyrmp", "teacher", "John Smith"]
        main()

        captured = capsys.readouterr()
        assert "John Smith" in captured.out
        assert "4.5/5" in captured.out
        assert "100" in captured.out
        assert "2.0/5" in captured.out
        assert "80.0%" in captured.out
        assert "CS101" in captured.out

    @patch("pyrmp.cli.RateMyProfessorClient")
    def test_teacher_json(self, mock_client_class, capsys):
        """Test teacher with --json"""
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        teacher = Teacher(
            id="Teacher-123",
            first_name="John",
            last_name="Smith",
            department="CS",
            avg_rating=4.5,
            num_ratings=100,
            school=School(id="School-1", name="MIT"),
        )

        mock_client.search_teachers.return_value = PaginatedResult(
            items=[teacher], has_next_page=False
        )
        mock_client.get_teacher_details.return_value = teacher

        sys.argv = ["pyrmp", "teacher", "John Smith", "--json"]
        main()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["name"] == "John Smith"
        assert data["rating"] == 4.5


class TestCLIRatings:
    """Test ratings command"""

    @patch("pyrmp.cli.RateMyProfessorClient")
    def test_ratings_basic(self, mock_client_class, capsys):
        """Test ratings output"""
        from pyrmp.models import Rating

        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        mock_client.get_teacher_ratings.return_value = PaginatedResult(
            items=[
                Rating(
                    id="Rating-1",
                    clarity_rating=5.0,
                    difficulty_rating=2.0,
                    grade="A",
                    class_name="CS101",
                    date="2024-01-01",
                    comment="Great professor!",
                )
            ],
            has_next_page=False,
        )

        sys.argv = ["pyrmp", "ratings", "Teacher-123"]
        main()

        captured = capsys.readouterr()
        assert "5.0/5" in captured.out
        assert "CS101" in captured.out
        assert "Great professor!" in captured.out


class TestCLISchools:
    """Test schools command"""

    @patch("pyrmp.cli.RateMyProfessorClient")
    def test_schools_basic(self, mock_client_class, capsys):
        """Test schools output"""
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        mock_client.search_schools.return_value = PaginatedResult(
            items=[
                School(
                    id="School-1",
                    name="MIT",
                    city="Cambridge",
                    state="MA",
                    country="USA",
                    num_ratings=5000,
                )
            ],
            has_next_page=False,
        )

        sys.argv = ["pyrmp", "schools", "MIT"]
        main()

        captured = capsys.readouterr()
        assert "MIT" in captured.out
        assert "School-1" in captured.out
        assert "Cambridge" in captured.out

    @patch("pyrmp.cli.RateMyProfessorClient")
    def test_schools_json(self, mock_client_class, capsys):
        """Test schools with --json"""
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        mock_client.search_schools.return_value = PaginatedResult(
            items=[
                School(
                    id="School-1",
                    name="MIT",
                    city="Cambridge",
                    state="MA",
                )
            ],
            has_next_page=False,
        )

        sys.argv = ["pyrmp", "schools", "MIT", "--json"]
        main()

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data[0]["name"] == "MIT"


class TestCLIArguments:
    """Test CLI argument parsing"""

    @patch("pyrmp.cli.RateMyProfessorClient")
    def test_search_count(self, mock_client_class, capsys):
        """Test search with --count"""
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        mock_client.search_teachers.return_value = PaginatedResult(
            items=[], has_next_page=False
        )

        sys.argv = ["pyrmp", "search", "John", "--count", "50"]
        main()

        mock_client.search_teachers.assert_called_once()
        call_args = mock_client.search_teachers.call_args
        assert call_args[1]["count"] == 50
