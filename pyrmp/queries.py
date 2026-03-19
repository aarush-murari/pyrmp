"""
GraphQL queries for RateMyProfessor API.

This module imports read-only queries from the local graphql_queries package.
Mutations are intentionally excluded to keep this package read-only.
"""

from graphql_queries.rmp_queries import (
    NEWSEARCHTEACHERS_QUERY,
    NEWSEARCHSCHOOLS_QUERY,
    TEACHERRATINGSPAGE_QUERY,
    SCHOOLRATINGSPAGE_QUERY,
    RATINGSLIST_QUERY,
    SCHOOLRATINGSLIST_QUERY,
    RATINGPAGE_QUERY,
)

__all__ = [
    "NEWSEARCHTEACHERS_QUERY",
    "NEWSEARCHSCHOOLS_QUERY",
    "TEACHERRATINGSPAGE_QUERY",
    "SCHOOLRATINGSPAGE_QUERY",
    "RATINGSLIST_QUERY",
    "SCHOOLRATINGSLIST_QUERY",
    "RATINGPAGE_QUERY",
]
