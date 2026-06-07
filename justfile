# Task runner for Cawmen Sandaigo. Run `just` for the full local gate.

# Run the full check gate (what CI runs).
default: check

# Sync the workspace venv from the lockfile.
sync:
    uv sync

# Lint with ruff (ALL ruleset).
lint:
    uv run ruff check .

# Format the codebase with ruff.
fmt:
    uv run ruff format .

# Verify formatting without rewriting.
fmt-check:
    uv run ruff format --check .

# Type-check with ty (Astral).
typecheck:
    uv run ty check

# Run the test suite.
test:
    uv run pytest

# Regenerate the committed OpenAPI schema.
openapi:
    uv run cawmen-backend openapi

# Fail if the committed OpenAPI schema is stale (ADR-0009).
openapi-check:
    uv run cawmen-backend openapi --check

# The full gate: lint, format, types, tests, schema freshness.
check: lint fmt-check typecheck test openapi-check

# Run the pre-commit hooks across all files via prek.
hooks:
    uv run prek run --all-files

# Serve the backend REST API (pass e.g. `just serve --port 9000`).
serve *args:
    uv run cawmen-backend serve {{args}}

# Launch the TUI against a running backend (pass e.g. `just tui --api-url ...`).
tui *args:
    uv run cawmen-tui {{args}}
