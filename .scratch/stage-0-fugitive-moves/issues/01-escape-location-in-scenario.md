# Add Escape Location to grand-tour Scenario

Status: done

Add a hidden Escape Location to `scenarios/grand-tour/graph.toml`. It must be defined
in the file (so `load_location_graph` loads it) but distinguished from the named
Locations so the API can exclude it from the location list it returns to clients.

## Acceptance criteria

- A 5th location exists in `graph.toml` with a field that marks it as the Escape Location (e.g. `escape = true`, or a sentinel `stage` value — pick whichever fits `load_location_graph` cleanly)
- It is connected from Madrid (the last named location in the ring)
- `load_location_graph` parses it correctly
- The `Location` model can distinguish it from regular Locations

## Last step

Write an article stub in `articles/00-the-fugitive-moves/` per `docs/agents/articles.md`.

## Comments

2026-06-08 — Implemented in c1110ac. Added `escape = true` location to `graph.toml` connected from Madrid; `Location` model gains `escape: bool = False`; article stub written at `articles/00-the-fugitive-moves/escape-location-in-scenario.md`.
