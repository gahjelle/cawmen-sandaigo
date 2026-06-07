# Wire Stage 0 API Endpoints

Status: ready-for-agent

Depends on: 01, 02, 03

Add the three Stage 0 endpoints to `backend/src/cawmen_backend/api/app.py` and wire
them to the pure core and shell. The `InMemoryStateStore` from `shell/state_store.py`
holds Case state for the lifetime of the process.

## Endpoints

### `POST /cases`

Body: `{ "scenario": "grand-tour", "seed": "<uuid>" }` (seed optional; defaults to `str(uuid.uuid4())`)

1. Load the `LocationGraph` from the Scenario file via `load_location_graph`
2. Derive the route RNG: `random.Random(derive_seed(seed, "route"))`
3. Call `generate_route(graph, rng)` → `FugitiveRoute`
4. Store initial `CaseState(day=1)` in the `InMemoryStateStore` under `seed` as `case_id`
5. Return `{ "case_id": seed, "locations": [...non-escape locations...], "connections": [...] }`

### `GET /cases/{case_id}`

1. Load `CaseState` from the store; 404 if unknown
2. Reconstruct `FugitiveRoute` from the seed (same deterministic derivation as creation)
3. Return `{ "day": state.day, "fugitive_location": fugitive_location(route, state) }`

Note: `fugitive_location` is scaffolding — removed in Stage 1.

### `POST /cases/{case_id}/advance`

1. Load `CaseState`; 404 if unknown
2. Reconstruct `FugitiveRoute`
3. If `has_escaped(route, state)`: return 409 `{ "detail": "trail_gone_cold" }`
4. `new_state = advance_clock(state)`; save to store
5. Return same shape as `GET /cases/{case_id}` with new state

## Acceptance criteria

- `POST /cases` with same seed always produces the same route (determinism via seed splitter)
- `GET` and `POST /cases/{id}/advance` return correct day and fugitive location
- Advancing past the Escape Location returns 409
- Unknown `case_id` returns 404
- `openapi.json` is regenerated and committed after implementation

## Last step

Write an article stub in `articles/00-the-fugitive-moves/` per `docs/agents/articles.md`.
