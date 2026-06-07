# Seed Splitter

## What was built

`derive_seed(case_seed, purpose) -> str` in `core/seed.py`. Given a Case Seed and a named purpose (e.g. `"route"`, `"suspects"`), it returns a deterministic hex string via SHA-256 of `"{seed}:{purpose}"`. Each downstream randomized concern constructs its own `random.Random(derive_seed(case_seed, purpose))` rather than sharing a single RNG.

## Why

A single `random.Random` threaded through all generation steps breaks reproducibility the moment a new step is inserted anywhere but the end — every downstream draw shifts. The splitter gives each concern a stable, independent sub-key so that adding a Stage 3 concern cannot disturb the Stage 0 Fugitive Route for the same seed.

The corollary for testability: functions that need randomness accept `random.Random` directly. Tests pass a seeded instance without involving `derive_seed` at all. The splitter is only exercised at the one boundary where a `random.Random` is constructed from a Case Seed.
