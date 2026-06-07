# Stage 0 — The Fugitive Moves

## Goal

Prove the full stack end-to-end: the backend owns game state, the REST API serves it,
and the TUI renders it. No player interaction. A spectator watches the fugitive travel
its route in the terminal as the In-Game Clock advances automatically.

## What this stage delivers

- The `grand-tour` Scenario extended with a hidden Escape Location
- A seed splitter (`derive_seed`) so each randomized concern gets its own independent RNG stream
- A route generator that produces a seeded walk through the Location Graph
- Three REST endpoints exposing Case state and clock advancement
- A TUI that auto-ticks, renders the location list with the fugitive highlighted, shows the In-Game Clock, and displays "Trail gone cold" when the fugitive escapes

## What is explicitly deferred

- Player interaction (Move, Interview, Wait, Arrest)
- Clues, Persons, Suspects, identity
- Authentication and persistence
- The `fugitive_location` field in state is scaffolding — it is removed in Stage 1

## API

### `POST /cases`

**Body**: `{ "scenario": "grand-tour", "seed": "<uuid>" }` (seed is optional; defaults to a random UUID)

**Response**: `{ "case_id": "<uuid>", "locations": [{ "id": "paris", "name": "Paris" }, ...], "connections": [{ "from": "paris", "to": "berlin" }, ...] }`

- Only named (non-escape) Locations are included in `locations`
- The Escape Location is never exposed

### `GET /cases/{case_id}`

**Response**: `{ "day": 1, "fugitive_location": "paris" }`

- `fugitive_location` is scaffolding for Stage 0 spectator mode; removed in Stage 1

### `POST /cases/{case_id}/advance`

Advances the In-Game Clock by one day.

**Response**: same shape as `GET /cases/{case_id}`

- If the fugitive has already escaped, returns a 409 with `{ "detail": "trail_gone_cold" }`

## Seed splitter (ADR-0010)

```python
derive_seed(case_seed: str, purpose: str) -> str
```

Uses `hashlib.sha256(f"{case_seed}:{purpose}".encode()).hexdigest()`. Route generation
calls `derive_seed(seed, "route")` and constructs a `random.Random` from the result.
Functions that need randomness accept a `random.Random` directly — tests pass a seeded
instance without touching the splitter.

## Route generation

A seeded walk through the Location Graph:
1. Derive `random.Random` from `derive_seed(seed, "route")`
2. Pick a random starting Location from the non-escape Locations
3. Walk edges in graph order, visiting all non-escape Locations once
4. Append the Escape Location as the final entry

The resulting `FugitiveRoute` has `len(non_escape_locations) + 1` entries.

## TUI behaviour

- On launch: `POST /cases` with `scenario="grand-tour"` and a fresh UUID seed
- Renders: In-Game Clock (top) + location list (body, fugitive's current location highlighted)
- Every 2 seconds: `POST /cases/{id}/advance`; re-render with the new state
- On escape: stop ticking, display "Trail gone cold" in place of the location list

## Out of scope

- Language Preference (hardcoded English at Stage 0; the `TextProvider` port is already
  in place for when it matters at Stage 5)
- Connection display in the TUI (Stage 1 concern, when Move choices need to be shown)
