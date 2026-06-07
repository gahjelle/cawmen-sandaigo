# Backend as a Functional Core / Imperative Shell with a Structured-Fact Core

The backend is structured as a pure **functional core** wrapped by a thin **imperative shell**, with FastAPI as a transport adapter on top. The core is a set of pure transition functions — `(scenario, case_state, action, seed) → (case_state', result)` — that own the chase mechanics and seed-driven Case generation, with the seed passed in as data; it performs no I/O, no mutation of external state, and holds no language. The shell does all I/O: it loads/saves state through a `StateStore` port (in-memory now, database at Stage 8) and renders narrative prose through a `TextProvider` port (templated now, AI at Stage 5), generating text in the player's Language Preference.

Crucially, the core returns **structured, language-free facts**, not prose — e.g. an Interview yields `ClueFact(kind=DIRECTION, to=<location>, staleness_days=2)`, and the shell turns that into text. This makes ADR-0001 (reproducible seed-driven generation) hold *by construction*: live AI is I/O and therefore cannot live in the pure core, so the deterministic generation path is AI-free without relying on discipline. It also makes "AI as a pure text layer" (the staging plan) literal — Stage 5 swaps the `TextProvider`, Stage 8 swaps the `StateStore`, and the core is untouched.

## Consequences

- Game rules are red-green tested as pure functions with plain pytest — no HTTP, no mocks, value-in/value-out.
- The structured result/`ClueFact` vocabulary must be designed as the game grows — but that vocabulary *is* the game model made explicit, which is a benefit, not overhead.
- The core never sees Language Preference; multilingual output is entirely a shell concern, consistent with text not being stored per-language.

## Relationship to other ADRs

Extends [ADR-0001](./0001-case-seed-for-reproducibility.md) (gives its "no non-deterministic logic in generation" a structural guarantee) and realizes [ADR-0005](./0005-scenarios-as-files-runtime-in-db.md)'s storage split through the `StateStore` port.
