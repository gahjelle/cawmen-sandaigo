# Escape Location in the Scenario Graph

The `minimal` scenario has four named locations the player sees — Paris, Berlin, Rome, Madrid — plus a fifth that only the game knows about: the Escape Location.

## What was built

An `escape` field (boolean, default `False`) on the `Location` model. The `graph.toml` authors it like any other location but sets `escape = true`:

```toml
[[locations]]
id = "escape"
name = "Escape"
stage = 0
escape = true

[[connections]]
from = "madrid"
to = "escape"
```

`load_location_graph` picks it up automatically — no special parsing needed. The API layer can filter it out with `[l for l in graph.locations if not l.escape]`.

## Why this shape

Keeping the Escape Location inside `graph.locations` (rather than a separate top-level key like `escape_location = ...`) means:

- Connections referencing it parse without special-casing — the connection table just names an id that exists in the locations list.
- The `FugitiveRoute` and graph-walk logic don't need to know whether the destination is "escape" or not; they treat it as a regular node.
- The flag approach (`escape = true`) is cheaper than a sentinel `stage` value (e.g. `stage = -1`) because it's self-documenting and won't interfere if stage values gain meaning later.
