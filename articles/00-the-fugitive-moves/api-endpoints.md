# Stage 0 API Endpoints

## What was built

Three endpoints wired to the pure core and shell:

- `POST /cases` — creates a Case from a scenario and seed, returns the named locations and connections
- `GET /cases/{case_id}` — returns the current day and the fugitive's location
- `POST /cases/{case_id}/advance` — advances the clock; returns 409 once the fugitive has escaped

## Route reconstruction, not storage

The `FugitiveRoute` is not stored. On every GET and advance, it is recomputed from the Case Seed using the same deterministic derivation (`derive_seed` + `generate_route`). This keeps the `StateStore` simple — it only holds `CaseState(day)` — and means the route is never stale.

The one thing that *does* need storing alongside the case state is the scenario name, since the route reconstruction needs to load the right graph. `create_app` keeps a `case_scenarios: dict[str, str]` next to the `InMemoryStateStore` for this.

## Hiding the Escape Location

`POST /cases` filters both the location list and the connection list before returning them to the client — anything where `escape=True` or `to==escape_id` is dropped. The client sees only the four named locations and the ring of connections between them.

## The `from` field

The `Connection` domain model uses `from_` in Python (since `from` is a keyword) with a Pydantic alias of `"from"`. FastAPI serializes response models with `by_alias=True` by default, so clients receive `{"from": "paris", "to": "berlin"}` without any extra configuration.
