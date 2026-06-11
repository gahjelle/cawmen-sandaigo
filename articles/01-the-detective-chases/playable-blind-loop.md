# The Playable Blind Loop

## CaseState reshape and seed/case_id separation

`CaseState` gained three fields: `seed` (the deterministic Case Seed, formerly doubling as the case id), `detective_location` (where the detective stands), and `status` (`in_progress` / `won` / `lost`). `case_id` is now a freshly-minted UUID independent of the seed, which means the same seed can be replayed under a different id without touching state reconstruction.

Route reconstruction uses `state.seed`, never `case_id`. This keeps seed-driven determinism (ADR-0001) intact while letting the API return an opaque identifier to clients.

## Fugitive indexing shift: route[0] as detective origin

The fugitive's indexing moved from `route[day - 1]` to `route[day]`. `route[0]` is now the detective's starting position — the scene of the crime — so on day 1 (`route[1]`) the fugitive has already fled. This guarantees the detective is never co-located with the fugitive at case creation, satisfying the "fugitive has already left" user story without any special-casing.

## apply_move resolution order

The pure-core `apply_move(graph, state, target)` follows a strict four-step order:

1. Validate (terminal check → adjacency; self-move and unknowns are non-adjacent by construction).
2. Detective relocates to `target`.
3. Clock advances one day (`new_day = day + 1`).
4. Fugitive relocates to `route[new_day]`; judge.

Judging after both move means stepping onto the location the fugitive is simultaneously departing is a miss: at the moment of judgment the fugitive is already one step further. A win requires true co-location at the end of the day.

## Blind API

In-progress responses for both `GET /cases/{id}` and `POST /cases/{id}/move` carry only `{ day, detective_location, status }` — no `fugitive_location`. The fugitive is invisible during play. On a terminal outcome (`won` or `lost`) the full `fugitive_route` is appended to the response, enabling post-game route reveal. Losing is a `200`, not an error; `409` is reserved for moves attempted after the case is already over (`case_over`).

## Error mapping

- Non-adjacent, self, or unknown target → `IllegalMoveError` in the core → `400 illegal_move` at the API.
- Move on a terminal case → `CaseOverError` in the core → `409 case_over` at the API.
- Unknown case id → `404`.
