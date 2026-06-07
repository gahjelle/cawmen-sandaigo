# Monorepo via a uv Workspace, One Member per Python Context

The Python contexts — `backend/` and `frontend-tui/` — live in a single repository as members of one uv workspace: each is its own package with its own `pyproject.toml`, `CONTEXT.md`, and `docs/adr/`, but they share a single lockfile, virtual environment, and `uv sync`. This keeps strict per-context boundaries (the separation the vision wants validated from the first line of code) while keeping day-to-day developer ergonomics to a single sync and one shared dev toolchain.

## Considered Options

- **One flat package** with `backend`/`tui` as subpackages — rejected: blurs the context boundary and makes it easy to import backend internals into the TUI instead of going through the API.
- **Two fully independent uv projects** (separate lockfiles/venvs) — rejected: duplicated tool config and a second sync for no boundary benefit the workspace doesn't already give.

## Consequences

The Phoenix LiveView web frontend (`frontend-web/`, Stage 6) is **Elixir and lives outside the uv workspace** — an intentional, honest asymmetry, not a smell. A shared venv also means the backend's console script is on `PATH` for the TUI, which the launch decision (ADR-0007) relies on.
