"""
CLI interface for pyrmp.

Usage:
    pyrmp search <query>
    pyrmp teacher <school> <name>
    pyrmp ratings <teacher_id>
    pyrmp schools <query>

Example:
    pyrmp search "John Smith" --school "MIT"
    pyrmp teacher "Stanford" "Jane Doe"
    pyrmp ratings 3125784
    pyrmp schools "Arizona State"
"""

import argparse
import sys

from pyrmp import RateMyProfessorClient
from pyrmp.models import PaginatedResult


def cmd_search(args: argparse.Namespace) -> None:
    """
    Search for teachers by name and display results.

    Args:
        args: Command-line arguments containing 'query'.
    """
    with RateMyProfessorClient() as client:
        results = client.search_teachers(args.query)

        if not results.items:
            print("No results found.")
            return

        print(f"Found {len(results.items)} teachers:\n")
        for i, teacher in enumerate(results.items, 1):
            print(f"{i}. {teacher.full_name}")
            print(f"   School: {teacher.school.name if teacher.school else 'N/A'}")
            print(f"   Department: {teacher.department or 'N/A'}")
            if teacher.avg_rating is not None and teacher.num_ratings is not None:
                print(
                    f"   Rating: {teacher.avg_rating}/5 ({teacher.num_ratings} ratings)"
                )
            else:
                print(f"   Rating: N/A")
            print()


def cmd_teacher(args: argparse.Namespace) -> None:
    """
    Get detailed info about a specific teacher.

    Args:
        args: Command-line arguments containing 'school' and 'name'.
    """
    with RateMyProfessorClient() as client:
        results = client.search_teachers(args.name)

        if not results.items:
            print("No teachers found.")
            return

        teacher = results.items[0]

        # Get full details
        details = client.get_teacher_details(teacher.id)
        if details:
            teacher = details

        print(f"Teacher: {teacher.full_name}")
        print(f"School: {teacher.school.name if teacher.school else 'N/A'}")
        print(f"Department: {teacher.department or 'N/A'}")
        print(f"Rating: {teacher.avg_rating or 'N/A'}/5")
        print(f"Total Ratings: {teacher.num_ratings or 'N/A'}")
        print(
            f"Would Take Again: {teacher.would_take_again_percent if teacher.would_take_again_percent is not None else 'N/A'}%"
        )
        print(f"Difficulty: {teacher.avg_difficulty or 'N/A'}/5")
        print(
            f"Course Codes: {', '.join(teacher.course_codes) if teacher.course_codes else 'N/A'}"
        )
        print()


def cmd_ratings(args: argparse.Namespace) -> None:
    """
    Get ratings for a specific teacher.

    Args:
        args: Command-line arguments containing 'teacher_id'.
    """
    with RateMyProfessorClient() as client:
        results = client.get_teacher_ratings(args.teacher_id)

        if not results.items:
            print("No ratings found.")
            return

        print(f"Found {len(results.items)} ratings:\n")
        for rating in results.items:
            print(
                f"Rating: {rating.clarity_rating or 'N/A'}/5 | Difficulty: {rating.difficulty_rating or 'N/A'}/5"
            )
            print(
                f"Class: {rating.class_name or 'N/A'} | Grade: {rating.grade or 'N/A'}"
            )
            print(f"Date: {rating.date or 'N/A'}")
            comment = (
                rating.comment[:100] + "..."
                if rating.comment and len(rating.comment) > 100
                else rating.comment or "No comment"
            )
            print(f"Comment: {comment}")
            print()


def cmd_schools(args: argparse.Namespace) -> None:
    """
    Search for schools and display results.

    Args:
        args: Command-line arguments containing 'query'.
    """
    with RateMyProfessorClient() as client:
        results = client.search_schools(args.query)

        if not results.items:
            print("No schools found.")
            return

        print(f"Found {len(results.items)} schools:\n")
        for school in results.items:
            print(f"- {school.name}")
            print(f"  Location: {school.city}, {school.state}, {school.country}")
            print(f"  Ratings: {school.num_ratings or 0}")
            print()


def main() -> None:
    """
    Main entry point for the pyrmp CLI.

    Sets up argument parser and dispatches to appropriate command handlers.
    """
    parser = argparse.ArgumentParser(
        prog="pyrmp",
        description="pyrmp - A Python wrapper for the RateMyProfessor GraphQL API",
        epilog="Example: pyrmp search 'John Smith' --school 'MIT'",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    search_parser = subparsers.add_parser(
        "search",
        help="Search for teachers by name",
        description="Search for teachers by name, optionally filtered by school",
    )
    search_parser.add_argument("query", help="Search query (teacher name)")
    search_parser.add_argument(
        "--school",
        help="Filter results by school name",
        dest="school_filter",
    )
    search_parser.set_defaults(func=cmd_search)

    teacher_parser = subparsers.add_parser(
        "teacher",
        help="Get teacher details",
        description="Get detailed information about a specific teacher",
    )
    teacher_parser.add_argument("school", help="School name")
    teacher_parser.add_argument("name", help="Teacher name")
    teacher_parser.set_defaults(func=cmd_teacher)

    ratings_parser = subparsers.add_parser(
        "ratings",
        help="Get teacher ratings",
        description="Get ratings for a specific teacher",
    )
    ratings_parser.add_argument(
        "teacher_id", help="Teacher ID (numeric, e.g., 3125784)"
    )
    ratings_parser.set_defaults(func=cmd_ratings)

    schools_parser = subparsers.add_parser(
        "schools",
        help="Search for schools",
        description="Search for schools by name",
    )
    schools_parser.add_argument("query", help="School search query")
    schools_parser.set_defaults(func=cmd_schools)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
