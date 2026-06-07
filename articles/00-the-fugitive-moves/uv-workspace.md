# The `uv` workspace

Cawmen Sandaigo is a monorepo with three distinct Python packages: the backend, the TUI
frontend, and a `tools/` module for repo-specific checks. Each package has its own
`pyproject.toml` and its own set of runtime dependencies. They share a single virtual
environment and a single lockfile.

## What a workspace is

A workspace is a collection of packages that are developed together and share a single
virtual environment and a single lockfile. Each member package has its own
`pyproject.toml` declaring its own name, version, and runtime dependencies — it is a
fully installable Python package on its own. What the workspace adds is a root that pulls
them all together.

The concept is borrowed from Cargo (Rust) and npm/pnpm, where monorepos with multiple
packages are first-class citizens. In Python, the equivalent used to require reaching for
Poetry or PDM; `uv` brings it to the standard `pyproject.toml` toolchain.

The key property: every member sees every other member as an editable install. The backend
and TUI can import from each other without `pip install -e` gymnastics. More importantly,
the lockfile covers the entire dependency graph — if the backend needs `fastapi==0.136.3`
and the TUI also depends on `httpx`, both are pinned in one place. There is no risk of
the two packages resolving different transitive versions in different environments.

This is a `uv` workspace. The root `pyproject.toml` declares the members:

```toml
[tool.uv.workspace]
members = ["backend", "frontend-tui"]
```

`uv sync` installs every member and all their dependencies in one step — no manual
environment juggling between packages. The lockfile (`uv.lock`) pins the entire
dependency graph across all members, so the TUI and backend always agree on transitive
versions.

## Why `uv` over the alternatives

`uv` replaces the whole `pip` + `venv` + `pip-tools` (or Poetry, or PDM) stack with a
single tool. It's meaningfully faster, and its resolver is stricter — it refuses to
produce an inconsistent lock rather than silently picking a winner. For a monorepo with
multiple packages sharing a dependency graph, having one tool own the whole picture from
`uv add` through `uv sync` removes an entire category of "works on my machine" problems.

Dev-only dependencies (pytest, ruff, ty) live in a `[dependency-groups]` block at the
root, so they are available everywhere without being declared by any individual package:

```toml
[dependency-groups]
dev = [
    "pytest>=9.0.3",
    "ruff>=0.15.16",
    "ty>=0.0.44",
    ...
]
```

Adding a runtime dependency to a package is `uv add --package cawmen-backend fastapi`.
Adding a dev tool is `uv add --dev pytest-something`. Neither ever touches a lockfile by
hand.
