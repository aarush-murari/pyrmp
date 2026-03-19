"""
CLI interface for pyrmp.

Usage:
    pyrmp search <query> [--count N] [--school-id ID] [--no-ids]
    pyrmp teacher <name> [--school-id ID] [--count N]
    pyrmp ratings <teacher_id> [--count N]
    pyrmp schools <query> [--count N]

Examples:
    pyrmp search "John Smith"
    pyrmp search "John Smith" --count 20
    pyrmp search "John Smith" --school-id "School-824"
    pyrmp teacher "Richard Staff"
    pyrmp teacher "Richard Staff" --school-id "School-824"
    pyrmp ratings "Teacher-941174"
    pyrmp schools "Arizona State"
"""

import argparse
import json
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
        results = client.search_teachers(args.query, count=args.count)

        if not results.items:
            print("No results found.")
            return

        if args.json:
            out = []
            for t in results.items:
                out.append(
                    {
                        "id": t.id,
                        "name": t.full_name,
                        "school": t.school.name if t.school else None,
                        "department": t.department,
                    }
                )
            print(json.dumps(out, indent=2))
            return

        print(f"Found {len(results.items)} teachers:\n")
        for i, teacher in enumerate(results.items, 1):
            print(f"{i}. {teacher.full_name}")
            if not args.no_ids:
                print(f"   ID: {teacher.id}")
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
        args: Command-line arguments containing 'name'.
    """
    with RateMyProfessorClient() as client:
        results = client.search_teachers(args.name, count=args.count)

        if not results.items:
            print("No teachers found.")
            return

        teacher = results.items[0]

        # Get full details
        details = client.get_teacher_details(teacher.id)
        if details:
            teacher = details

        if args.json:
            data = {
                "id": teacher.id,
                "name": teacher.full_name,
                "school": teacher.school.name if teacher.school else None,
                "department": teacher.department,
                "rating": teacher.avg_rating,
                "num_ratings": teacher.num_ratings,
                "difficulty": teacher.avg_difficulty,
                "would_take_again": teacher.would_take_again_percent,
                "course_codes": teacher.course_codes,
            }
            print(json.dumps(data, indent=2))
            return

        print(f"Teacher: {teacher.full_name}")
        if not args.no_ids:
            print(f"ID: {teacher.id}")
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
        results = client.get_teacher_ratings(args.teacher_id, count=args.count)

        if not results.items:
            print("No ratings found.")
            return

        if args.json:
            out = []
            for r in results.items:
                out.append(
                    {
                        "id": r.id,
                        "clarity": r.clarity_rating,
                        "difficulty": r.difficulty_rating,
                        "grade": r.grade,
                        "class": r.class_name,
                        "date": str(r.date) if r.date else None,
                        "comment": r.comment,
                    }
                )
            print(json.dumps(out, indent=2))
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
        results = client.search_schools(args.query, count=args.count)

        if not results.items:
            print("No schools found.")
            return

        if args.json:
            out = []
            for s in results.items:
                out.append(
                    {
                        "id": s.id,
                        "name": s.name,
                        "city": s.city,
                        "state": s.state,
                        "country": s.country,
                        "num_ratings": s.num_ratings,
                        "avg_rating": s.avg_rating,
                    }
                )
            print(json.dumps(out, indent=2))
            return

        print(f"Found {len(results.items)} schools:\n")
        for school in results.items:
            print(f"- {school.name}")
            if not args.no_ids:
                print(f"  ID: {school.id}")
            print(
                f"  Location: {school.city or 'N/A'}, {school.state or 'N/A'}, {school.country or 'N/A'}"
            )
            print(f"  Ratings: {school.num_ratings or 0}")
            print()


def main() -> None:
    """
    Main entry point for the pyrmp CLI.

    Sets up argument parser and dispatches to appropriate command handlers.
    """
    parser = argparse.ArgumentParser(
        prog="pyrmp",
        description="pyrmp - Python wrapper for RateMyProfessor",
        epilog="Example: pyrmp search 'John Smith' --count 20",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # search
    search_parser = subparsers.add_parser(
        "search",
        help="Search for teachers by name",
    )
    search_parser.add_argument("query", help="Teacher name to search for")
    search_parser.add_argument(
        "--count", type=int, default=10, help="Number of results (default: 10)"
    )
    search_parser.add_argument("--school-id", help="Filter by school ID")
    search_parser.add_argument("--json", action="store_true", help="Output as JSON")
    search_parser.add_argument(
        "--no-ids", action="store_true", help="Hide IDs in output"
    )
    search_parser.set_defaults(func=cmd_search)

    # teacher
    teacher_parser = subparsers.add_parser(
        "teacher",
        help="Get teacher details",
    )
    teacher_parser.add_argument("name", help="Teacher name")
    teacher_parser.add_argument("--school-id", help="Filter by school ID")
    teacher_parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of search results to check (default: 10)",
    )
    teacher_parser.add_argument("--json", action="store_true", help="Output as JSON")
    teacher_parser.add_argument(
        "--no-ids", action="store_true", help="Hide IDs in output"
    )
    teacher_parser.set_defaults(func=cmd_teacher)

    # ratings
    ratings_parser = subparsers.add_parser(
        "ratings",
        help="Get teacher ratings",
    )
    ratings_parser.add_argument("teacher_id", help="Teacher ID")
    ratings_parser.add_argument(
        "--count", type=int, default=20, help="Number of ratings (default: 20)"
    )
    ratings_parser.add_argument("--json", action="store_true", help="Output as JSON")
    ratings_parser.set_defaults(func=cmd_ratings)

    # schools
    schools_parser = subparsers.add_parser(
        "schools",
        help="Search for schools",
    )
    schools_parser.add_argument("query", help="School name to search for")
    schools_parser.add_argument(
        "--count", type=int, default=10, help="Number of results (default: 10)"
    )
    schools_parser.add_argument("--json", action="store_true", help="Output as JSON")
    schools_parser.add_argument(
        "--no-ids", action="store_true", help="Hide IDs in output"
    )
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
