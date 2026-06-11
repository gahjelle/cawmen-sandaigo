# The detective Moves: the playable blind loop

Status: ready-for-agent

## Parent

PRD: `.scratch/stage-1-player-moves/PRD.md`. Folds in stub `01-store-seed-in-case-state.md`.

## What to build

Turn the spectator into a player: the detective becomes a movable entity and the Case
can be won or lost — blind, by guesswork.

- Reshape `CaseState`: add `detective_location` (starts at the route origin `route[0]`),
  `seed` (folds stub #01), and `status` (`in_progress`/`won`/`lost`, stored). `case_id`
  becomes its own UUID, **distinct from** `seed`; route reconstruction derives from
  `state.seed`, never `case_id`.
- The fugitive has already fled: its position on day `d` is `route[d]` (day 1 → `route[1]`),
  so the detective is never co-located at creation.
- Add a pure-core transition `apply_move(graph, state, target) -> (new_state, outcome)`
  per [ADR-0008](../../../docs/adr/0008-functional-core-imperative-shell.md): detective
  relocates → clock advances one day → fugitive relocates → **then** judge. Co-location is
  judged after both move (stepping onto the Location the fugitive is leaving is a miss).
  Adjacency is enforced in the core. Outcomes (`in_progress`/`won`/`lost`) are returned as
  data; illegal input is raised as a domain error.
- Replace `POST /cases/{id}/advance` with `POST /cases/{id}/move` (body `{ target }`).
  In-progress `move`/`GET` responses are **blind**: `{ day, detective_location, status }`,
  no `fugitive_location`. On a terminal outcome the response also carries the revealed
  `fugitive_route` (ordered, incl. escape).
- Error mapping: illegal Move (non-adjacent, self-move, unknown Location) → `400`
  `illegal_move`; Move on a terminal Case → `409` `case_over`; unknown Case → `404`.
  Escaping is a `200` with `status: lost`, not an error.
- TUI: drop the auto-tick; highlight the detective's Location; present the current
  Location's `neighbors` as a focusable selectable list; send `POST /move` on selection;
  show `Day N` + status. The fugitive is never highlighted during play.
- Regenerate `openapi.json`.

## Acceptance criteria

- [ ] `CaseState` carries `detective_location`, `seed`, `status`; `case_id` is a distinct
      UUID and route derives from `state.seed`
- [ ] `apply_move`: legal Move advances the day and relocates both; co-location after both
      move yields `won`; stepping onto the Location the fugitive is leaving does **not**
      win; reaching escape yields `lost`
- [ ] Non-adjacent / self / unknown targets and Moves on a terminal Case are rejected
      (raised in core; `400`/`409` at the API); unknown Case → `404`
- [ ] In-progress responses contain no `fugitive_location`; terminal responses reveal the
      full route; losing is a `200`, not a `409`
- [ ] The TUI is playable: select a neighbour to Move, win and lose are reachable, the
      fugitive is hidden during play
- [ ] `openapi.json` is current and `just check` passes

## Blocked by

- `03-undirected-prism-graph-and-adjacency-api.md`

## Last step

Write an article stub under `articles/01-the-detective-chases/playable-blind-loop.md`
covering the `CaseState` reshape, the `apply_move` resolution order, the blind API, and
case/seed separation.
