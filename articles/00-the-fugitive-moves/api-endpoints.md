# Stage 0 API Endpoints

## Background: REST, GET, and POST

REST (Representational State Transfer) is a convention for structuring HTTP APIs around *resources* — things the server knows about, identified by URLs. This API has one resource type: Cases, at `/cases`.

HTTP verbs express what you want to do with a resource. The two used here:

- **GET** — read the current state of a resource without changing it. Safe to call repeatedly; the server state is unchanged.
- **POST** — submit data to create or update a resource. Not idempotent: calling it twice may produce two different outcomes.

`POST /cases` creates a new Case. `GET /cases/{id}` reads it. `POST /cases/{id}/advance` mutates it.

## HTTP status codes

Status codes are three-digit numbers grouped by their first digit: 2xx means success, 4xx means the client did something wrong, 5xx means the server failed.

The codes used here:

- **200 OK** — the request succeeded and the response body contains the result.
- **404 Not Found** — the resource identified by the URL doesn't exist (unknown `case_id`).
- **409 Conflict** — the request is valid but conflicts with the current state of the resource. Used here when a client tries to advance a Case whose fugitive has already escaped: the request is well-formed, but the Case is over.

## What was built

Three endpoints wired to the pure core and shell:

- `POST /cases` — creates a Case from a scenario and seed, returns the named locations and connections
- `GET /cases/{case_id}` — returns the current day and the fugitive's location
- `POST /cases/{case_id}/advance` — advances the clock; returns 409 if the next step would reach the Escape Location

## Route reconstruction, not storage

The `FugitiveRoute` is not stored. On every GET and advance, it is recomputed from the Case Seed using the same deterministic derivation (`derive_seed` + `generate_route`). This keeps the `StateStore` simple — it only holds `CaseState(day)` — and means the route is never stale.

The one thing that *does* need storing alongside the case state is the scenario name, since the route reconstruction needs to load the right graph. `create_app` keeps a `case_scenarios: dict[str, str]` next to the `InMemoryStateStore` for this.

## Hiding the Escape Location

`POST /cases` filters both the location list and the connection list before returning them to the client — anything where `escape=True` or `to==escape_id` is dropped. The client sees only the four named locations and the ring of connections between them.

## The `from` field

The `Connection` domain model uses `from_` in Python (since `from` is a keyword) with a Pydantic alias of `"from"`. FastAPI serializes response models with `by_alias=True` by default, so clients receive `{"from": "paris", "to": "berlin"}` without any extra configuration.
