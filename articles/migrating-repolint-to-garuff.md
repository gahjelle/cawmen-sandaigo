# From a homegrown linter to Garuff

Every project accumulates conventions that a general-purpose linter can't express. Ruff is
excellent at the universe of rules that apply to *all* Python — unused imports, shadowed
builtins, mutable default arguments. But "Pydantic models in this codebase must inherit
`FrozenModel`, never `BaseModel`" is not a fact about Python; it's a fact about *this*
repo. Nobody upstream is going to ship that rule.

So early in Stage 0 we wrote our own. This is the story of that tool, why we replaced it
three commits later, and what the swap cost.

## The homegrown tool

`repolint` was a small AST-walking Python script living in `tools/repolint`. It parsed
each source file with the standard-library `ast` module and checked for six patterns,
each numbered `CAW00x` to echo ruff's `E501`-style codes:

- **CAW001** — no `from __future__ import annotations` (Python 3.14 evaluates annotations
  lazily via PEP 649, so the import is dead clutter).
- **CAW002** — Pydantic models inherit `FrozenModel` (which sets `frozen=True` and
  `extra="forbid"`), never `BaseModel` directly.
- **CAW003** — `Protocol` methods carry a docstring, not `...`.
- **CAW004** — single backticks in docstrings (Markdown, not RST).
- **CAW005** — `list[T]` over `tuple[T, ...]` for homogeneous sequences.
- **CAW006** — return `Self`, not a stringized forward reference to the enclosing class.

It even mirrored ruff's ergonomics: a `--fix` flag auto-applied the two textually safe
repairs (CAW001 and CAW004). For a hundred lines of Python, it did real work — it caught
the mistakes that code review kept flagging, and it wired cleanly into `just conventions`
as one more step in the gate.

### Why write it at all

The alternative to a convention linter is a style guide that humans (and agents) are meant
to remember. Style guides rot. A rule that isn't enforced by a machine is a rule that is
followed until the moment someone is in a hurry. Encoding the conventions as executable
checks made them non-negotiable and — importantly for an agent-driven project — gave the
agent immediate, mechanical feedback instead of a reviewer's after-the-fact "we don't do
it that way here."

That reasoning was sound. What it missed is that *maintaining* the enforcement tool is
itself work, and that work never appears on the roadmap.

## Why we replaced it

[Garuff](https://pypi.org/project/garuff/) is a maintained, off-the-shelf convention linter
that happens to encode almost exactly the rules we'd hand-rolled — and then some. Its
catalog is a **superset**: the six `CAW` rules have direct `GAC` equivalents, plus a batch
of extra opinionated ones (`GAC007`–`GAC011`) we hadn't gotten around to writing.

The motivations were the ordinary ones behind any "delete our code, adopt the library"
decision, and they're worth naming because the trade-off recurs constantly:

- **The tool was undifferentiated.** `repolint` was not part of the product. It was
  scaffolding. Every hour spent extending it — adding a rule, fixing a false positive,
  teaching it a new `--fix` — was an hour not spent on the game. A dependency moves that
  maintenance onto someone else.
- **The superset was strictly more valuable.** `GAC009` (keyword-only dataclasses) and
  `GAC010` (docstrings on every function) were conventions we *wanted* but hadn't
  enforced. Adopting garuff got them for free, along with a configurable positional-arg
  cap (`GAC008`).
- **The catalog documents itself.** `uv run garuff rule --all` prints every rule with its
  *why* and its *fix*. Our hand-maintained rule list in `docs/agents/conventions.md` was a
  second source of truth that could drift from the code. We deleted it and pointed at the
  tool.

## What the swap actually cost

"Adopt the library" is never free, and this migration made the hidden costs visible in one
commit:

- **New rules surface old violations.** Garuff's superset immediately failed the build.
  We had to fix what it found: a keyword-only `target` on `apply_move` (`GAC008`),
  `kw_only=True` added to **eleven** dataclasses (`GAC009`), and one-line docstrings
  written for **eight** previously undocumented functions (`GAC010`). That's the price of
  a stricter baseline — you pay the accumulated debt the moment you turn it on.
- **Second-order churn.** Those new docstrings weren't inert. FastAPI turns route-handler
  docstrings into OpenAPI operation descriptions, so `openapi.json` had to be regenerated.
  A convention change rippled into a generated artifact — a good reminder that the gate's
  steps are not independent.
- **You inherit someone else's opinions.** With `repolint` we could add or bend any rule
  in an afternoon. With garuff, the catalog is theirs. When their defaults and ours
  disagree, the escape hatch is configuration (`[tool.garuff]` in `pyproject.toml`, where
  `GAC008`'s `max_positional_args = 2` now lives), not a code edit. That's less control,
  traded for zero maintenance — usually the right trade, but a real one.

The plumbing itself was mechanical: point `just conventions`, pre-commit, and CI at
`garuff check`; add garuff to the dev group; delete the entire `tools/` tree and drop
`tools/tests` from the pytest `testpaths`.

## The tell for "delete our code"

The cleanest signal that a homegrown tool has outlived its purpose is when a maintained
project appears that does a **superset** of what yours does. At that point your version is
pure liability: the same value, plus a maintenance burden, minus the extra rules and the
community fixing bugs you haven't hit yet. `repolint` earned its keep by proving the
conventions were worth enforcing at all — and the moment garuff existed, the best thing it
could do was get out of the way.

We left one breadcrumb rather than rewriting history: the Stage 0
[quality-gate article](./00-the-fugitive-moves/quality-gate.md) still describes `repolint`
as it shipped, with an editor's note pointing here. The story of *why* we built our own is
worth keeping even after the tool is gone.
