# Route Generator

## What was built

`generate_route(graph, rng) -> FugitiveRoute` in `core/route.py`. It picks a random starting Location, walks the graph's connections in authored order until all non-escape Locations are visited, then appends the Escape Location as the final entry.

The function accepts a `random.Random` directly so callers control seeding. The seed splitter (`derive_seed`) is invoked once upstream to construct that `random.Random`; `generate_route` itself is oblivious to Case Seeds.

## Moving the models to the core

`Location`, `Connection`, and `LocationGraph` started life in `shell/scenario.py` alongside the file-loading code. Once `generate_route` needed them in the pure core, keeping them in the shell would have inverted the dependency — the core importing from the shell. They're pure data with no I/O, so they belong in `core/location.py`. The shell's `load_location_graph` now imports them from the core and returns them; the data types flow inward, the I/O stays at the edge.

## The walk algorithm

The route is a deterministic walk: from the current Location, follow the first outgoing connection (in the order connections are authored in `graph.toml`) that leads to an unvisited non-escape Location. The starting Location is the only random choice — `rng` is consumed exactly once. For the minimal ring this always produces a full traversal, because every Location has exactly one outgoing non-escape edge.
