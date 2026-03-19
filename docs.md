# pyrmp Documentation

Python wrapper for the RateMyProfessor GraphQL API.

## Table of Contents

- [Installation](#installation)
- [Client](#client)
- [Methods](#methods)
- [Models](#models)
- [CLI](#cli)
- [Exceptions](#exceptions)
- [Advanced](#advanced)

## Installation

```bash
pip install pyrmp
```

## Client

```python
from pyrmp import RateMyProfessorClient

# Default settings
client = RateMyProfessorClient()

# With context manager (recommended)
with RateMyProfessorClient() as client:
    # Use client here
    pass
```

## Methods

### search_teachers(query, count=10, include_compare=True)

Search for teachers by name. The search is fuzzy - you don't need to spell the name exactly.

**Args:**
- `query` (str): Teacher name to search for (e.g., "John Smith", "Smith", "J. Smith")
- `count` (int): How many results to return (1-100). Defaults to 10.
- `include_compare` (bool): Whether to include ratings data in results. Defaults to True.
  - `True`: Returns `avg_rating`, `avg_difficulty`, `num_ratings`, `would_take_again_percent`
  - `False`: Returns only name, department, school

**Returns:** `PaginatedResult` with `Teacher` objects in `.items`

**Example:**
```python
# With ratings (default)
results = client.search_teachers("John Smith")
teacher = results.items[0]
print(teacher.avg_rating)        # 4.5
print(teacher.num_ratings)       # 100
print(teacher.avg_difficulty)    # 2.1

# Without ratings (faster, less data)
results = client.search_teachers("John Smith", include_compare=False)
teacher = results.items[0]
print(teacher.full_name)         # "John Smith"
print(teacher.avg_rating)        # None
```

### search_schools(query=None, count=10, include_compare=True)

Search for schools by name.

**Args:**
- `query` (str, optional): School name to search for
- `count` (int): How many results (1-100). Defaults to 10.
- `include_compare` (bool): Include ratings data. Defaults to True.

**Returns:** `PaginatedResult` with `School` objects in `.items`

**Example:**
```python
results = client.search_schools("MIT")
for school in results.items:
    print(f"{school.name} - {school.city}, {school.state}")
    print(f"  {school.num_ratings} ratings")
```

### get_teacher_details(teacher_id)

Get detailed information about a specific teacher.

**Args:**
- `teacher_id` (str): The teacher's ID from a previous search (e.g., "Teacher-941174")

**Returns:** `Teacher` object if found, `None` otherwise

**Example:**
```python
results = client.search_teachers("John Smith")
if results.items:
    details = client.get_teacher_details(results.items[0].id)
    print(f"Department: {details.department}")
    print(f"Would take again: {details.would_take_again_percent}%")
    print(f"School: {details.school.name}")
```

### get_school_details(school_id)

Get detailed information about a specific school.

**Args:**
- `school_id` (str): The school's ID from a previous search

**Returns:** `School` object if found, `None` otherwise

### get_teacher_ratings(teacher_id, count=20, course_filter=None, cursor=None)

Get ratings/reviews for a specific teacher.

**Args:**
- `teacher_id` (str): The teacher's ID
- `count` (int): How many ratings (1-100). Defaults to 20.
- `course_filter` (str, optional): Only get ratings for a specific course (e.g., "CS101")
- `cursor` (str, optional): Pagination cursor for fetching the next page

**Returns:** `PaginatedResult` with `Rating` objects in `.items`

**Example:**
```python
ratings = client.get_teacher_ratings(teacher_id, count=10)
for rating in ratings.items:
    print(f"Clarity: {rating.clarity_rating}/5")
    print(f"Difficulty: {rating.difficulty_rating}/5")
    print(f"Grade: {rating.grade}")
    print(f"Comment: {rating.comment}")
```

### get_school_ratings(school_id, count=20, cursor=None)

Get ratings/reviews for a specific school.

**Args:**
- `school_id` (str): The school's ID
- `count` (int): How many ratings (1-100). Defaults to 20.
- `cursor` (str, optional): Pagination cursor

**Returns:** `PaginatedResult` with `SchoolRating` objects in `.items`

### get_rating_details(rating_id)

Get full details for a specific rating.

**Args:**
- `rating_id` (str): The rating's ID

**Returns:** `Rating` or `SchoolRating` object, or `None` if not found

## Models

### Teacher

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Unique identifier (e.g., "Teacher-941174") |
| `legacy_id` | int \| None | Original numeric ID |
| `first_name` | str \| None | First name |
| `last_name` | str \| None | Last name |
| `department` | str \| None | Department (e.g., "Computer Science") |
| `department_id` | int \| None | Department ID |
| `school` | School \| None | Associated school |
| `avg_rating` | float \| None | Average rating (0-5) |
| `avg_difficulty` | float \| None | Average difficulty (0-5) |
| `num_ratings` | int \| None | Number of ratings |
| `would_take_again_percent` | float \| None | Would take again % |
| `ratings_distribution` | dict \| None | Rating distribution |
| `course_codes` | list[str] \| None | Course codes taught |
| `lock_status` | str \| None | Lock status |
| `is_saved` | bool \| None | Saved by current user |

**Properties:**
- `full_name` → `"John Smith"` or `None`

### School

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Unique identifier (e.g., "School-824") |
| `legacy_id` | int \| None | Original numeric ID |
| `name` | str \| None | School name |
| `city` | str \| None | City |
| `state` | str \| None | State |
| `country` | str \| None | Country |
| `num_ratings` | int \| None | Number of ratings |
| `avg_rating` | float \| None | Average rating |
| `avg_rating_rounded` | float \| None | Rounded average |
| `departments` | list[dict] \| None | Departments |
| `summary` | dict \| None | School summary |

### Rating

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Unique identifier (e.g., "Rating-123") |
| `legacy_id` | int \| None | Original numeric ID |
| `teacher` | Teacher \| None | Associated teacher |
| `comment` | str \| None | Written review |
| `helpful_rating` | float \| None | Helpfulness (1-5) |
| `clarity_rating` | float \| None | Clarity (1-5) |
| `difficulty_rating` | float \| None | Difficulty (1-5) |
| `grade` | str \| None | Grade received |
| `class_name` | str \| None | Class name |
| `would_take_again` | bool \| None | Would take again |
| `is_for_credit` | bool \| None | For credit |
| `textbook_used` | bool \| None | Textbook used |
| `attendance_mandatory` | bool \| None | Attendance mandatory |
| `is_for_online_class` | bool \| None | Online class |
| `rating_tags` | list[str] \| None | Tags |
| `thumbs_up_total` | int \| None | Thumbs up |
| `thumbs_down_total` | int \| None | Thumbs down |
| `date` | str \| datetime \| None | Date posted |
| `flag_status` | str \| None | Flag status |
| `created_by_user` | bool \| None | Created by current user |

### SchoolRating

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Unique identifier |
| `legacy_id` | int \| None | Original numeric ID |
| `school` | School \| None | Associated school |
| `comment` | str \| None | Written review |
| `clubs_rating` | float \| None | Clubs (1-5) |
| `facilities_rating` | float \| None | Facilities (1-5) |
| `food_rating` | float \| None | Food (1-5) |
| `happiness_rating` | float \| None | Happiness (1-5) |
| `internet_rating` | float \| None | Internet (1-5) |
| `location_rating` | float \| None | Location (1-5) |
| `opportunities_rating` | float \| None | Opportunities (1-5) |
| `reputation_rating` | float \| None | Reputation (1-5) |
| `safety_rating` | float \| None | Safety (1-5) |
| `social_rating` | float \| None | Social (1-5) |
| `date` | str \| datetime \| None | Date posted |
| `thumbs_up_total` | int \| None | Thumbs up |
| `thumbs_down_total` | int \| None | Thumbs down |
| `flag_status` | str \| None | Flag status |
| `created_by_user` | bool \| None | Created by current user |

### PaginatedResult

| Field | Type | Description |
|-------|------|-------------|
| `items` | list | Items in current page |
| `has_next_page` | bool | Whether more pages exist |
| `end_cursor` | str \| None | Cursor for next page |
| `total_count` | int \| None | Total items (if available) |

**Methods:**
- `len(result)` → Number of items in current page
- `bool(result)` → `True` if any items

## CLI

### search

```bash
pyrmp search "John Smith" [--count N] [--json] [--no-ids]
```

### teacher

```bash
pyrmp teacher "John Smith" [--count N] [--json] [--no-ids]
```

### ratings

```bash
pyrmp ratings "Teacher-941174" [--count N] [--json]
```

### schools

```bash
pyrmp schools "MIT" [--count N] [--json] [--no-ids]
```

### Global Flags

- `--json`: Output as JSON
- `--no-ids`: Hide IDs in output
- `--count N`: Number of results

## Exceptions

All exceptions inherit from `RateMyProfessorError`:

```python
from pyrmp.exceptions import (
    RateMyProfessorError,
    NotFoundError,
    APIError,
    PaginationError,
    InvalidQueryError,
)
```

- `RateMyProfessorError` - Base exception
- `NotFoundError` - Resource not found
- `APIError` - API returned an error (has `status_code` and `response_data` attributes)
- `PaginationError` - Pagination failed
- `InvalidQueryError` - Invalid query parameters

## Advanced

### Pagination

```python
results = client.search_teachers("Johnson", count=10)
while results.has_next_page:
    print(f"Got {len(results.items)} teachers")
    results = client.search_teachers("Johnson", count=10)
```

### Quick Functions

```python
from pyrmp import search_teachers, search_schools

teachers = search_teachers("Einstein", count=5)
schools = search_schools("MIT")
```

### Rate Limiting

The library handles rate limiting internally with a 0.5s delay between requests.
