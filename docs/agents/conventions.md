# Tooling & conventions

## Tooling

Everything runs through `uv` (`uv run …` to invoke tools, `uv add …` / `uv add --dev …`
to add dependencies — never edit dependency lists by hand, and never `==`-pin in
`pyproject.toml`; let `uv.lock` own exact versions).

The full local gate is `just check` (or `just` alone). It runs:

- `ruff check` — `select = ["ALL"]`, with only `COM812`, `D203`, `D213` globally ignored.
- `ruff format`.
- `ty` — the only type checker (no mypy, no fallback). Full type annotations everywhere.
- the convention linter (below).
- `pytest`.
- the OpenAPI staleness check (`cawmen-backend openapi --check`, see ADR-0009).

Python is pinned to 3.14.

## Repo-specific conventions

Beyond what ruff and ty can express, these rules are enforced by
`uv run python -m tools.repolint` (pass `--fix` to apply the safe textual fixes; also
wired into pre-commit and CI):

- `CAW001` — no `from __future__ import annotations` (Python 3.14 evaluates annotations
  lazily via PEP 649, so `TYPE_CHECKING`-guarded imports work without it).
- `CAW002` — Pydantic models inherit `StrictModel` (`cawmen_backend/models.py`, which sets
  `ConfigDict(extra="forbid", frozen=True)`), never `BaseModel` directly.
- `CAW003` — `Protocol` methods omit `...`; the docstring is body enough.
- `CAW004` — docstrings use single backticks, never double.
- `CAW005` — homogeneous sequences are `list`, not `tuple[T, ...]`. Reserve `tuple` for
  heterogeneous, row-like data — and even then prefer a named container (model/dataclass).
- `CAW006` — return `typing.Self`, never a string forward-ref to the enclosing class.

`--fix` covers the safe textual rules (`CAW001`, `CAW004`); the rest report-only with a
hint, since they need import management.

## Style

- Docstrings are minimal one-liners that add intent — type hints and good parameter names
  already explain the signature, so docstrings never restate it.
- Prefer immutable *actions* (functions return new values rather than mutating in place),
  but do not enforce immutable *data structures*.
