# The quality gate

> **Editor's note:** the homegrown `repolint` described below was later replaced by
> [Garuff](https://pypi.org/project/garuff/). This article preserves the stage-00 story as
> it shipped.

`just check` is the full local gate — what CI runs and what you run before pushing:

```
lint → fmt-check → typecheck → conventions → test → openapi-check
```

Each step is a `uv run` invocation: ruff for linting, ruff again for format verification,
`ty` for types, `repolint` for project-specific conventions, pytest for tests, and a
schema freshness check. `just` is the task runner that wires these into one command.

## `just`

`just` is a command runner. That is its whole job — it runs commands, with named recipes
and dependency ordering between them. It does not track file modification times, does not
rebuild targets, and does not attempt to be a build system. Where `make` conflates "task
runner" with "incremental build tool" (and silently does the wrong thing when a target
file happens to exist), `just` has no such ambiguity.

The syntax is close enough to a `Makefile` to read immediately, but without the
whitespace traps and implicit rules. A recipe is a name, optional dependencies, and a
shell command:

```just
# Run the full gate: lint, format, types, conventions, tests, schema freshness.
check: lint fmt-check typecheck conventions test openapi-check
```

Running `just check` executes each dependency recipe in order. Running `just` alone runs
the default recipe, which is set to `check` — so there is one thing to remember.

The practical reason to use `just` over a `Makefile` or a shell script: the
`justfile` is documented, version-controlled, and self-describing (`just --list` prints
every recipe with its comment). A shell script that strings together six commands in CI
tends to drift from what developers run locally. A `justfile` is the canonical definition
of both.

## `ruff` with `ALL`

Ruff's lint ruleset is opt-in: the default catches very little. This project opts into
everything — `select = ["ALL"]` — and then carves out a small list of rules that
genuinely conflict with each other or with the project's conventions:

```toml
[tool.ruff.lint]
select = ["ALL"]
ignore = ["COM812", "D203", "D213"]
```

`COM812` (missing trailing comma) conflicts with the formatter. `D203` and `D213` are
docstring-placement rules that contradict each other — you must pick one.

The value of starting from `ALL` is that new ruff releases bring new rules on by default.
You see them as failures, decide whether they fit, and either fix the code or add a narrow
ignore with a comment explaining why. The baseline is strict; every exception is
deliberate.

Per-file ignores relax a few rules for tests — `S101` (forbids `assert`) and `PLR2004`
(forbids magic literals in comparisons) would make tests significantly more verbose for no
safety gain.

## `ty` for type checking

`ty` is Astral's type checker, the same team that builds ruff. It is faster than
`mypy` and stricter by default than `pyright` in the configurations most projects use.
The choice here is partly practical — one toolchain for linting and types — and partly
because `ty` is willing to be unpleasant in ways that surface real mistakes early.

All type annotations are written without `from __future__ import annotations`. Python 3.14
evaluates annotations lazily by default, making the import unnecessary. (More on this in
the `repolint` section below.)

## `repolint`: conventions that ruff and ty can't express

Some project conventions are too structural for a linter operating on individual
expressions. `repolint` is a small AST-walking tool that encodes six rules specific to
this project, each with a `CAW00x` code to match ruff's output style:

- **CAW001** — forbid `from __future__ import annotations`. On Python 3.14 it is
  unnecessary clutter; removing it avoids confusion about which annotation behaviours are
  in play.

- **CAW002** — Pydantic models must inherit `FrozenModel`, not `BaseModel`. `FrozenModel`
  is a project-local base class that sets `extra="forbid"` (unknown fields are an error,
  not silently ignored) and `frozen=True` (instances are immutable after construction).
  Inheriting `BaseModel` directly bypasses both guarantees silently.

- **CAW003** — `Protocol` methods must not contain `...`. A Protocol method only needs a
  docstring; an `...` alongside it is noise.

- **CAW004** — docstrings use single backticks. Double backticks (` `` `) are RST
  convention; this codebase uses Markdown in prose, so single backticks are consistent.

- **CAW005** — homogeneous sequences use `list[T]`, not `tuple[T, ...]`. The `tuple[T,
  ...]` form signals "fixed-length, heterogeneous-friendly" to a reader; an unbounded
  homogeneous sequence should be `list`.

- **CAW006** — return `Self`, not a string forward reference to the enclosing class.
  Python 3.11 introduced `typing.Self`; string forward refs predate it and are now just
  noise.

`repolint` is implemented as a plain Python script that parses source files with the
`ast` module and checks for each pattern. It also supports `--fix` to auto-apply the
safe textual fixes (CAW001 and CAW004), following the same convention as `ruff --fix`.
