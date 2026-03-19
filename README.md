# RateMyProfessor Python API Wrapper

A comprehensive, pythonic wrapper for the RateMyProfessor GraphQL API. Search for professors, schools, and retrieve ratings with ease.

## Features

- **Simple & Pythonic** - Clean API that feels native to Python
- **Type Safety** - Full type hints for better IDE support
- **Pagination Support** - Built-in pagination for large result sets
- **Data Models** - Python dataclasses instead of raw JSON
- **Error Handling** - Custom exceptions for different error types

## Installation

```bash
pip install pyrmp
```

Or install from source:

```bash
git clone https://github.com/yourusername/pyrmp.git
cd pyrmp
pip install -e .
```

## Quick Start

```python
from pyrmp import RateMyProfessorClient

# Create a client
client = RateMyProfessorClient()

# Search for teachers
results = client.search_teachers("Einstein", count=5)
print(f"Found {len(results.items)} teachers")

for teacher in results.items:
    print(f"  {teacher.full_name} at {teacher.school.name}")
    print(f"    Rating: {teacher.avg_rating}/5 ({teacher.num_ratings} ratings)")

# Get detailed information
if results.items:
    details = client.get_teacher_details(results.items[0].id)
    print(f"\nDetails for {details.full_name}:")
    print(f"  Department: {details.department}")
    print(f"  Difficulty: {details.avg_difficulty}/5")
    print(f"  Would take again: {details.would_take_again_percent}%")

# Get ratings
ratings = client.get_teacher_ratings(results.items[0].id, count=3)
for rating in ratings.items:
    print(f"  Rating: {rating.helpful_rating}/5 helpful")
    if rating.comment:
        print(f"    \"{rating.comment[:100]}...\"")

client.close()
```

## API Reference

### Client

#### RateMyProfessorClient

Main client for interacting with the RateMyProfessor API.

```python
client = RateMyProfessorClient()
```

##### Methods

###### search_teachers(query: str, count: int = 10, include_compare: bool = False) -> PaginatedResult

Search for teachers by name.

```python
results = client.search_teachers("Smith", count=10)
for teacher in results.items:
    print(teacher.full_name)
```

###### search_schools(query: str = None, count: int = 10, include_compare: bool = False) -> PaginatedResult

Search for schools by name.

```python
results = client.search_schools("Harvard", count=5)
for school in results.items:
    print(f"{school.name} - {school.city}, {school.state}")
```

###### get_teacher_details(teacher_id: str) -> Optional[Teacher]

Get detailed information about a teacher.

```python
teacher = client.get_teacher_details("VGVhY2hlci0xODE4NDA2")
print(teacher.full_name)
print(teacher.department)
print(teacher.school.name)
```

###### get_school_details(school_id: str) -> Optional[School]

Get detailed information about a school.

```python
school = client.get_school_details("U2Nob29sLTEyMzQ1")
print(school.name)
print(f"{school.city}, {school.state}")
```

###### get_teacher_ratings(teacher_id: str, count: int = 20, course_filter: str = None, cursor: str = None) -> PaginatedResult

Get ratings for a teacher.

```python
ratings = client.get_teacher_ratings(teacher_id, count=10)
for rating in ratings.items:
    print(f"Class: {rating.class_name}")
    print(f"Helpful: {rating.helpful_rating}/5")
    print(f"Comment: {rating.comment}")
```

###### get_school_ratings(school_id: str, count: int = 20, cursor: str = None) -> PaginatedResult

Get ratings for a school.

```python
ratings = client.get_school_ratings(school_id, count=10)
for rating in ratings.items:
    print(f"Overall: {rating.happiness_rating}/5")
    print(f"Comment: {rating.comment}")
```

### Data Models

#### Teacher

Represents a teacher/professor.

```python
@dataclass
class Teacher:
    id: str                                    # Unique identifier
    legacy_id: Optional[int]                   # Legacy ID
    first_name: Optional[str]                  # First name
    last_name: Optional[str]                   # Last name
    department: Optional[str]                 # Department
    department_id: Optional[int]              # Department ID
    school: Optional[School]                   # Associated school
    avg_rating: Optional[float]               # Average rating (0-5)
    avg_difficulty: Optional[float]           # Average difficulty (0-5)
    num_ratings: Optional[int]                # Number of ratings
    would_take_again_percent: Optional[float] # Would take again percentage
    ratings_distribution: Optional[Dict]      # Rating distribution
    course_codes: Optional[List[str]]          # Course codes taught
    lock_status: Optional[str]                 # Lock status
    is_saved: Optional[bool]                  # Is saved by user
    
    @property
    def full_name(self) -> Optional[str]        # Full name property
```

#### School

Represents a school/university.

```python
@dataclass
class School:
    id: str                         # Unique identifier
    legacy_id: Optional[int]         # Legacy ID
    name: Optional[str]              # School name
    city: Optional[str]             # City
    state: Optional[str]           # State
    country: Optional[str]         # Country
    num_ratings: Optional[int]     # Number of ratings
    avg_rating: Optional[float]    # Average rating
    avg_rating_rounded: Optional[float]  # Rounded average
    departments: Optional[List[Dict]]  # Departments
    summary: Optional[Dict]        # School summary
```

#### Rating

Represents a teacher rating.

```python
@dataclass
class Rating:
    id: str                      # Unique identifier
    legacy_id: Optional[int]      # Legacy ID
    teacher: Optional[Teacher]    # Associated teacher
    comment: Optional[str]       # Rating comment
    helpful_rating: Optional[float]    # Helpfulness rating (0-5)
    clarity_rating: Optional[float]   # Clarity rating (0-5)
    difficulty_rating: Optional[float]  # Difficulty rating (0-5)
    grade: Optional[str]         # Grade received
    class_name: Optional[str]    # Course name
    would_take_again: Optional[bool]  # Would take again
    is_for_credit: Optional[bool]     # For credit
    textbook_used: Optional[bool]     # Textbook used
    attendance_mandatory: Optional[bool]  # Attendance mandatory
    is_for_online_class: Optional[bool]   # Online class
    rating_tags: Optional[List[str]]  # Rating tags
    thumbs_up_total: Optional[int]    # Thumbs up count
    thumbs_down_total: Optional[int]  # Thumbs down count
    date: Optional[str]          # Rating date
    flag_status: Optional[str]   # Flag status
    created_by_user: Optional[bool]  # Created by user
```

#### SchoolRating

Represents a school rating.

```python
@dataclass
class SchoolRating:
    id: str                      # Unique identifier
    legacy_id: Optional[int]      # Legacy ID
    school: Optional[School]     # Associated school
    comment: Optional[str]        # Rating comment
    clubs_rating: Optional[float]       # Clubs rating (0-5)
    facilities_rating: Optional[float] # Facilities rating (0-5)
    food_rating: Optional[float]       # Food rating (0-5)
    happiness_rating: Optional[float]  # Happiness rating (0-5)
    internet_rating: Optional[float]   # Internet rating (0-5)
    location_rating: Optional[float]   # Location rating (0-5)
    opportunities_rating: Optional[float]  # Opportunities rating (0-5)
    reputation_rating: Optional[float]  # Reputation rating (0-5)
    safety_rating: Optional[float]     # Safety rating (0-5)
    social_rating: Optional[float]     # Social rating (0-5)
    date: Optional[str]           # Rating date
    thumbs_up_total: Optional[int]     # Thumbs up count
    thumbs_down_total: Optional[int]   # Thumbs down count
    flag_status: Optional[str]  # Flag status
    created_by_user: Optional[bool]  # Created by user
```

#### PaginatedResult

Represents paginated query results.

```python
@dataclass
class PaginatedResult:
    items: List[Any]           # List of results
    has_next_page: bool       # Whether there are more pages
    end_cursor: Optional[str] # Cursor for next page
    total_count: Optional[int] # Total number of results
```

### Exceptions

- `RateMyProfessorError` - Base exception
- `NotFoundError` - Resource not found
- `APIError` - API returned an error
- `PaginationError` - Pagination failed
- `InvalidQueryError` - Invalid query

## Advanced Usage

### Context Manager

```python
with RateMyProfessorClient() as client:
    teachers = client.search_teachers("Smith")
    for teacher in teachers.items:
        print(teacher.full_name)
# Client automatically closed
```

### Pagination

```python
# Get first page
results = client.search_teachers("Johnson", count=10)

# Check if there are more pages
while results.has_next_page:
    print(f"Got {len(results.items)} teachers")
    
    # Get next page using cursor
    results = client.search_teachers("Johnson", count=10, cursor=results.end_cursor)
```

### Error Handling

```python
from pyrmp import RateMyProfessorClient, RateMyProfessorError

try:
    client = RateMyProfessorClient()
    teachers = client.search_teachers("Nonexistent")
    
    if not teachers.items:
        print("No teachers found")
    else:
        for teacher in teachers.items:
            print(teacher.full_name)
            
except RateMyProfessorError as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    client.close()
```

### Quick Functions

For simple one-off queries:

```python
from pyrmp import search_teachers, search_schools

# Quick teacher search
teachers = search_teachers("Einstein", count=5)

# Quick school search
schools = search_schools("MIT")
```

## How It Works

### GraphQL Queries

The wrapper uses pre-defined GraphQL queries extracted from the RateMyProfessor website:

1. **NewSearchTeachersQuery** - Search for teachers
2. **NewSearchSchoolsQuery** - Search for schools  
3. **TeacherRatingsPageQuery** - Get teacher details
4. **SchoolRatingsPageQuery** - Get school details
5. **RatingsListQuery** - Get teacher ratings
6. **SchoolRatingsListQuery** - Get school ratings

### Request Flow

```
Python Code
    ↓
RateMyProfessorClient.search_teachers()
    ↓
Build GraphQL query variables
    ↓
Execute via gql library
    ↓
Parse JSON response
    ↓
Convert to Python dataclasses
    ↓
Return PaginatedResult
```

### Rate Limiting

The official RateMyProfessor API may have rate limits. If you encounter errors:

- Add delays between requests
- Use pagination to fetch data incrementally
- Consider caching results

## CLI

pyrmp includes a command-line interface:

```bash
# Search for teachers
pyrmp search "John Smith"

# Search with school filter
pyrmp search "John Smith" --school "MIT"

# Get teacher details
pyrmp teacher "Stanford" "Jane Doe"

# Get teacher ratings (by numeric ID)
pyrmp ratings 3125784

# Search schools
pyrmp schools "Arizona State"
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Links

- [RateMyProfessor](https://www.ratemyprofessors.com)
- [GraphQL](https://graphql.org)
- [gql library](https://github.com/graphql-python/gql)
