# Seed Splitter for Independent RNG Streams

Case generation has multiple independent random concerns (Fugitive Route, Suspect selection, Crime, Clue placement, Person placement). Rather than threading a single `random.Random` instance through all of them in sequence, each concern derives its own `random.Random` from the Case Seed via `hashlib.sha256(f"{seed}:{purpose}".encode())`.

This keeps Case Seeds stable across stages: adding a new randomized concern at Stage 3 does not shift the Fugitive Route that Stage 0 established for the same seed — each concern always derives the same sub-key regardless of what else is added. It also makes unit tests straightforward: any function that needs randomness accepts a `random.Random` directly, so tests pass a seeded instance without touching the splitter at all.

## Considered Options

- **Single sequential `random.Random(seed)`** — rejected because inserting a new randomized call early in the generation sequence shifts every downstream draw, silently breaking the reproducibility guarantee of ADR-0001 with every new stage.
