# Implement Seeded Route Generator

Status: ready-for-agent

Depends on: 01 (Escape Location in scenario), 02 (seed splitter)

Add `generate_route(graph: LocationGraph, rng: random.Random) -> FugitiveRoute` to the
backend pure core. The function accepts a `random.Random` directly (injected by the
caller via the seed splitter) so it is trivially testable without touching `derive_seed`.

## Algorithm

1. Collect all non-escape Locations from the graph
2. Pick a random starting Location using `rng`
3. Walk edges in graph order until all non-escape Locations are visited
4. Append the Escape Location as the final entry

The resulting `FugitiveRoute.locations` has `len(non_escape_locations) + 1` entries.

## Acceptance criteria

- `generate_route(graph, random.Random(seed))` is deterministic for a fixed seed
- The final entry in `FugitiveRoute.locations` is always the Escape Location
- All non-escape Locations appear exactly once before the Escape Location
- `has_escaped` from `core/chase.py` returns `True` when `state.day >= len(route.locations)`
- Unit tests pass a seeded `random.Random` directly — no seed splitter involved

## Last step

Write an article stub in `articles/00-the-fugitive-moves/` per `docs/agents/articles.md`.
