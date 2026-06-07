# Seed Splitter

## What was built

`derive_seed(case_seed, purpose) -> str` in `core/seed.py`. Given a Case Seed and a named purpose (e.g. `"route"`, `"suspects"`), it returns a deterministic hex string via SHA-256 of `"{seed}:{purpose}"`. Each downstream randomized concern constructs its own `random.Random(derive_seed(case_seed, purpose))` rather than sharing a single RNG.

## Background: seeds and state

A pseudo-random number generator isn't actually random — it's a deterministic function that takes some internal state and produces a number plus a new state. The seed is just the initial value of that state. Given the same seed, you always get the same sequence of numbers; the sequence only diverges when the starting state differs.

The key word is *sequence*. Each call to `rng.choice(...)` or `rng.randint(...)` consumes one step of that sequence and advances the internal state. The second call picks up exactly where the first left off. If you insert a new call anywhere before the end, every subsequent draw shifts by one position — the route changes, the suspects change, everything downstream changes.

This makes a shared `random.Random` fragile across multiple independent concerns. The Fugitive Route, the Suspect selection, the Clue placement — each of these draws a different number of values depending on the scenario. If route generation draws three values and you later add a fourth, every subsequent concern sees a different stream, even though *their* logic hasn't changed at all.

## Why the splitter solves it

Instead of one shared sequence, each concern gets its own `random.Random` seeded independently:

```python
route_rng    = random.Random(derive_seed(case_seed, "route"))
suspect_rng  = random.Random(derive_seed(case_seed, "suspects"))
```

`derive_seed` produces a different 256-bit value for each purpose, so the two RNGs start from completely unrelated states. Whatever `route_rng` draws has no effect on `suspect_rng`'s sequence. Adding a new concern at any stage — or inserting extra draws inside an existing one — only affects that concern's own stream.

The splitter gives each concern a stable, independent sub-key so that adding a Stage 3 concern cannot disturb the Stage 0 Fugitive Route for the same seed.

The corollary for testability: functions that need randomness accept `random.Random` directly. Tests pass a seeded instance without involving `derive_seed` at all. The splitter is only exercised at the one boundary where a `random.Random` is constructed from a Case Seed.
