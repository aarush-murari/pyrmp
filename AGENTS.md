# AGENTS.md

## Setup commands
- Install deps: `uv sync --dev`
- Activate venv: `source .venv/bin/activate`
- Run all tests: `uv run pytest tests/`
- Run unit tests only: `uv run pytest tests/test_pyrmp.py tests/test_client_extended.py tests/test_cli.py`
- Run integration tests: `uv run pytest tests/test_integration.py`
- Run single test: `uv run pytest tests/test_pyrmp.py::TestModels::test_teacher_full_name_both -v`

## Code style
- Python 3.10+ (type hints required)
- Google-style docstrings (user-focused, not implementation-focused)
- Use dataclasses for models
- No comments unless asked
- Tests first, then implementation

## Project overview
Python wrapper for the RateMyProfessor GraphQL API. READ-ONLY by design.

```
pyrmp/
├── pyrmp/                    # Library code
│   ├── client.py            # RateMyProfessorClient (main API)
│   ├── models.py            # Teacher, School, Rating, PaginatedResult
│   ├── queries.py           # Imports from graphql_queries/
│   ├── exceptions.py        # Custom exceptions
│   └── cli.py               # CLI interface
├── tests/                   # Test suite
│   ├── test_pyrmp.py        # Unit tests (mocks)
│   ├── test_client_extended.py  # Extended tests
│   ├── test_integration.py  # Real API tests
│   └── test_cli.py          # CLI tests
├── docs/                    # Sphinx documentation
│   ├── source/conf.py       # Sphinx config
│   └── build/html/          # Built HTML (gitignored)
├── graphql_queries/         # Raw GraphQL queries (gitignored, dev only)
├── .github/workflows/       # CI/CD
│   ├── docs.yml             # Deploy docs on push to main
│   └── release.yml          # Publish to PyPI on GitHub release
├── pyproject.toml           # Package config
└── uv.lock                  # Dependency lock
```

## Dev environment tips
- Always use `uv run` prefix for commands (ensures venv)
- `graphql_queries/` is gitignored - contains raw queries extracted from RMP website, dev reference only
- Do NOT commit `graphql_queries/`, `queries.txt`, `rmp_cookies_sample.json`, `dist/`, `docs/build/`
- IDs returned by API are base64-encoded (e.g., `VGVhY2hlci05NDExNzQ=`). Library decodes to human-readable format (`Teacher-941174`) before returning to user.
- When adding dependencies: `uv add package-name` (dev: `uv add package-name --dev`)
- When testing: use `uv run pytest` not `pytest` directly

## Testing instructions
- All tests must pass before committing
- Mock tests (test_pyrmp.py, test_client_extended.py, test_cli.py) are fast - run these often
- Integration tests (test_integration.py) hit real API - slower, may timeout
- When adding new methods: add mock tests, then integration tests
- Test edge cases: empty strings, None values, boundary values, special characters
- Test both positive and negative inputs

## Key decisions
- GraphQL queries imported from `graphql_queries/` (gitignored). Mutations excluded intentionally.
- `include_compare=True` by default (returns ratings in search results)
- Human-readable IDs (`Teacher-941174`) instead of base64 (`VGVhY2hlci05NDExNzQ=`)
- No write operations in this library (separate pyrmp-write package)
- Sphinx for docs, auto-deploys to GitHub Pages

## PR instructions
- Run `uv run pytest tests/` before committing
- Run `uv run make html` in docs/ if docstrings changed
- Bump version in `pyproject.toml` and `docs/source/conf.py` before release
- Create GitHub release with tag `vX.Y.Z` to auto-publish to PyPI

## Build and publish
```bash
# Build
rm -rf dist/* && uv build

# Manual publish (need token)
UV_PUBLISH_TOKEN="pypi-token" uv publish

# Auto publish (trusted publishing via GitHub release)
# Just create release on GitHub with tag vX.Y.Z
```
