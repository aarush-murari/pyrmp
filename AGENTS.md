# AGENTS.md

Quick reference for developers and AI agents working on pyrmp.

## What is this?

**pyrmp** is a Python wrapper for the RateMyProfessor GraphQL API. It lets you search for teachers, schools, and read ratings programmatically.

- **PyPI**: `pip install pyrmp`
- **GitHub**: `aarush-murari/pyrmp`
- **Docs**: https://aarush-murari.github.io/pyrmp/

## Project Structure

```
pyrmp/
├── pyrmp/                    # Main library
│   ├── __init__.py          # Package exports
│   ├── client.py            # RateMyProfessorClient (GraphQL)
│   ├── models.py            # Teacher, School, Rating, PaginatedResult
│   ├── queries.py           # GraphQL query strings
│   ├── exceptions.py        # Custom exceptions
│   └── cli.py               # CLI interface (argparse)
├── tests/                   # Test suite
│   ├── test_pyrmp.py        # Unit tests
│   ├── test_client_extended.py  # Extended tests
│   ├── test_integration.py  # Real API tests
│   └── test_cli.py          # CLI tests
├── docs/                    # Sphinx documentation
│   ├── source/              # Source files
│   └── build/               # Built HTML (gitignored)
├── .github/workflows/       # GitHub Actions
│   ├── docs.yml             # Deploy docs to gh-pages
│   └── release.yml          # Publish to PyPI on release
├── pyproject.toml           # Package config + dependencies
├── uv.lock                  # Dependency lock file
└── README.md                # Quick start guide
```

## Development Setup

### Prerequisites
- Python 3.10+
- uv (package manager)

### Install dependencies
```bash
uv sync --dev
```

### Activate venv
```bash
source .venv/bin/activate
```

### Run tests
```bash
# All tests
uv run pytest tests/

# Unit tests only (fast)
uv run pytest tests/test_pyrmp.py tests/test_client_extended.py

# CLI tests
uv run pytest tests/test_cli.py

# Integration tests (hit real API, slower)
uv run pytest tests/test_integration.py

# Specific test
uv run pytest tests/test_pyrmp.py::TestModels::test_teacher_full_name_both -v
```

### Add a dependency
```bash
# Production dependency
uv add package-name

# Dev dependency (testing, docs, etc.)
uv add package-name --dev

# After adding, uv.lock auto-updates
```

### Build package
```bash
rm -rf dist/*
uv build
```

### Publish to PyPI
```bash
# Manual publish (need API token)
UV_PUBLISH_TOKEN="pypi-your-token" uv publish

# Auto publish via GitHub release
# Just create a release on GitHub with tag vX.Y.Z
# The release.yml workflow handles it via trusted publishing
```

## Version Bumping

1. Edit `pyproject.toml` → `version = "X.Y.Z"`
2. Edit `docs/source/conf.py` → `release = "X.Y.Z"`
3. `uv sync`
4. Commit and push
5. Create GitHub release with tag `vX.Y.Z`

## Documentation

### Build docs locally
```bash
cd docs
uv run make html
# Output: docs/build/html/
```

### Docs deployment
- Auto-deploys to GitHub Pages on push to main
- URL: https://aarush-murari.github.io/pyrmp/

## CLI Usage

```bash
# Search teachers
pyrmp search "John Smith" --count 10

# Teacher details
pyrmp teacher "John Smith"

# Teacher ratings
pyrmp ratings "Teacher-941174"

# Search schools
pyrmp schools "MIT"

# JSON output
pyrmp search "John Smith" --json

# Hide IDs
pyrmp search "John Smith" --no-ids
```

## Key Decisions

### Why `uv`?
Fast dependency resolution and package management. Drop-in replacement for pip+virtualenv.

### Why GraphQL?
RMP API is GraphQL. We wrap it with Python dataclasses for clean API.

### Why human-readable IDs?
API returns base64-encoded IDs like `VGVhY2hlci05NDExNzQ=`. We decode to `Teacher-941174` for user-friendliness. Library handles encoding/decoding internally.

### Why `include_compare=True`?
Search returns ratings (avgRating, numRatings, difficulty) by default. Set to `False` for faster searches without rating data.

### Why `graphql_queries/` is gitignored?
Contains raw GraphQL queries extracted from RMP website. Not needed in the published package, only for development.

## Common Pitfalls

1. **Tests timeout**: Real API tests can timeout. Use `--timeout` or skip integration tests.
2. **403 errors**: RMP blocks requests without proper headers. Our client adds User-Agent, Referer, etc.
3. **SSH push fails**: Switch to HTTPS or check SSH key.
4. **Version already exists**: Bump version in pyproject.toml before republishing.
5. **Docstrings matter**: Sphinx auto-generates docs from docstrings. Keep them user-focused (not implementation details).

## License

MPL-2.0 (Mozilla Public License 2.0)
- Modifications to this library must be shared
- Static linking is allowed without restrictions
- See LICENSE file for full text
