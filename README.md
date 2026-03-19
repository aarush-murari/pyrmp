# pyrmp

Python wrapper for the RateMyProfessor GraphQL API.

## Install

```bash
pip install pyrmp
```

## Quick Start

```python
from pyrmp import RateMyProfessorClient

with RateMyProfessorClient() as client:
    # Search for teachers (returns ratings by default)
    teachers = client.search_teachers("John Smith")
    for teacher in teachers.items:
        print(f"{teacher.full_name} - {teacher.avg_rating}/5 ({teacher.num_ratings} ratings)")

    # Get teacher details
    details = client.get_teacher_details(teachers.items[0].id)
    print(f"Department: {details.department}")
    print(f"Would take again: {details.would_take_again_percent}%")

    # Get ratings
    ratings = client.get_teacher_ratings(details.id, count=5)
    for rating in ratings.items:
        print(f"  {rating.clarity_rating}/5 - {rating.comment[:50]}")
```

## CLI

```bash
# Search teachers (includes ratings)
pyrmp search "John Smith" --count 10

# Get teacher details
pyrmp teacher "John Smith"

# Get ratings for a teacher
pyrmp ratings "Teacher-941174"

# Search schools
pyrmp schools "MIT"

# JSON output (pipe to jq)
pyrmp search "John Smith" --json | jq '.[] | .name'

# Hide IDs
pyrmp search "John Smith" --no-ids
```

## Documentation

See [the SPhynx documentation]([docs.md](https://aarush-murari.github.io/pyrmp/api.html#exceptions)) for full API reference, examples, and advanced usage.

## License

MPL-2.0
