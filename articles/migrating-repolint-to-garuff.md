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

That reasoning was sound. The idea was good enough, in fact, that it didn't stay in this
repo.

## Why we replaced it

Here's the thing the tidy "we adopted a library" story would get wrong:
[Garuff](https://pypi.org/project/garuff/) is not some third-party project we found. It's
the same tool, by the same author, extracted and given a home. The name says so —
**GA**ruff is *Geir Arne's extra ruff-inspired linter*. It still encodes exactly one
person's opinions about how code should be written. We didn't outsource our conventions;
we packaged them.

The problem `repolint` had was not quality — it was **multiplication**. A convention linter
that proves its worth in one repo is a convention linter you want in the *next* repo, and
the one after that. And the way that spreads, absent a package, is copy-paste. Before long
there was a `tools/repolint` in several projects, each a slightly-drifted fork of the
others, and keeping them in sync was a manual chore performed entirely from memory:

- Add a rule in one repo, and you had to remember to paste it into the rest.
- Fix a false positive in another, and the fix lived only there until you carried it over.
- Every project's linter slowly diverged from every other's, for no reason anyone chose.

That does not scale. Three copies is annoying; ten is untenable. So the copies were
collected into **one** tool — maintained in one place, released to PyPI, installed as a
normal dev dependency. That garuff's rule catalog is a **superset** of this repo's `CAW`
rules is no coincidence: it's the *union* of what the various projects' repolints had each
grown to need, with the `CAW` six sitting inside it as `GAC` equivalents and a batch of
newer ones (`GAC007`–`GAC011`) alongside. Garuff is this repo's idea, extended scalably to
every repo.

The wins are the ordinary wins of DRY, just applied to tooling instead of application code:

- **One source of truth.** A rule is written, fixed, and documented once. Every project on
  the same garuff version gets the same behaviour — no drift, no re-paste.
- **Versioned distribution.** `uv add --dev garuff` and a pinned `uv.lock` entry, exactly
  like any other dependency. Upgrades are deliberate, per repo.
- **The catalog documents itself.** `uv run garuff rule --all` prints every rule with its
  *why* and its *fix*. Our hand-maintained rule list in `docs/agents/conventions.md` was a
  second source of truth that could drift; we deleted it and pointed at the tool.

## What the swap actually cost

Centralising a tool is not free, and this migration made the costs concrete in one commit:

- **The superset is stricter, so it surfaced old debt.** The moment garuff ran, the build
  failed on rules `repolint` never had. We fixed what it found: a keyword-only `target` on
  `apply_move` (`GAC008`), `kw_only=True` added to **eleven** dataclasses (`GAC009`), and
  one-line docstrings written for **eight** previously undocumented functions (`GAC010`).
  A shared linter carries the accumulated opinions of *all* the repos it was distilled
  from, so adopting it here meant paying for conventions this repo hadn't enforced yet.
- **Second-order churn.** Those new docstrings weren't inert. FastAPI turns route-handler
  docstrings into OpenAPI operation descriptions, so `openapi.json` had to be regenerated.
  A convention change rippled into a generated artifact — a good reminder that the gate's
  steps are not independent.
- **A shared tool must be configurable, not forked.** When one repo needs a rule tuned, the
  answer can no longer be "edit the script" — that would desync it again, the very problem
  we were escaping. It has to be a knob. So per-repo differences now live in
  `[tool.garuff]` in `pyproject.toml` (here, `GAC008`'s `max_positional_args = 2`) rather
  than in a local edit.
- **A rule change is now a release, not a save.** Improving a rule means editing garuff,
  cutting a PyPI version, and bumping the dependency in each consuming repo — slower than
  patching an in-tree script. That latency is the price of one canonical implementation,
  and it's usually worth paying. What we did *not* give up is control or opinion: the tool
  is still ours, the rules are still ours.

The plumbing itself was mechanical: point `just conventions`, pre-commit, and CI at
`garuff check`; add garuff to the dev group; delete the entire `tools/` tree and drop
`tools/tests` from the pytest `testpaths`.

## The tell for "extract this into a package"

The signal here was not "a maintained project appeared that does what ours does." It was
"I've copy-pasted the same bespoke tool into three repos and I'm hand-syncing them." That
is the moment a per-project script wants to become an installed package: not because the
idea was wrong, but because the idea was *right enough to reuse*, and copy-paste is not a
reuse strategy. `repolint` earned its keep by proving, in one repo, that these conventions
were worth enforcing at all. Garuff is what that proof looks like once it has to hold for
many.

We left one breadcrumb rather than rewriting history: the Stage 0
[quality-gate article](./00-the-fugitive-moves/quality-gate.md) still describes `repolint`
as it shipped, with an editor's note pointing here. The story of *why* we built our own is
worth keeping even after the tool moved out.
