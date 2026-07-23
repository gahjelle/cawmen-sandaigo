# Stage 1 — The Detective Chases (a game, but blind)

Status: ready-for-agent

## Problem Statement

At Stage 0 the player is a spectator: the fugitive walks its route automatically and its
location is shown on screen. There is no game — nothing to do, nothing to win or lose.
The player wants to actually *play*: to take the role of the detective, move across the
world in pursuit, and either catch the fugitive or lose it to the trail going cold.

## Solution

The detective becomes a movable entity the player controls. The player issues a **Move**
along the Location Graph; each Move costs one day, after which the fugitive relocates
overnight. The Case is **won** when the detective and fugitive end a day co-located, and
**lost** when the fugitive reaches the Escape Location. There are no Clues yet, so play is
deliberately **blind** — the fugitive's position is hidden during play and the player wins
or loses by guesswork. On any outcome the full Fugitive Route is revealed so the player
can replay the chase and see where they went wrong.

## User Stories

1. As a detective, I want to start a Case at the scene of the crime, so that my pursuit
   begins where the trail begins.
2. As a detective, I want the fugitive to have already fled when I arrive, so that there
   is a real chase rather than an instant capture.
3. As a detective, I want to see the world around me — my current Location and the
   Locations I can travel to — so that I can decide where to go.
4. As a detective, I want to Move to an adjacent Location, so that I can pursue the
   fugitive across the world.
5. As a detective, I want each Move to advance the In-Game Clock by a day, so that time
   pressure is real and the fugitive keeps moving.
6. As a detective, I want to be told the current day, so that I have a sense of elapsed
   time.
7. As a detective, I want the fugitive's location hidden while I play, so that the game is
   a genuine chase by deduction rather than following a marker.
8. As a detective, I want to win when I end a day in the same Location as the fugitive, so
   that catching up to the fugitive is the goal.
9. As a detective, I want to lose when the fugitive reaches the Escape Location, so that
   dithering has a cost and the deadline is real.
10. As a detective, I want the loss to arrive without a visible countdown, so that urgency
    is felt rather than calculated.
11. As a detective, I want to be unable to catch a fugitive by stepping onto the Location
    it is simultaneously leaving, so that the chase rewards predicting where it is going,
    not where it was.
12. As a detective, I want my Move rejected if I pick a non-adjacent Location, so that the
    rules of travel are enforced.
13. As a detective, I want my Move rejected if I try to "move" to my current Location, so
    that staying put is not a backdoor Wait action (which arrives later).
14. As a detective, I want the game to refuse further Moves once the Case is over, so that
    a finished Case stays finished.
15. As a detective, I want the full Fugitive Route revealed when the Case ends, so that I
    can replay the chase and understand the outcome.
16. As a detective in the TUI, I want to choose my next Location from a list of where I can
    go, so that moving is simple and unambiguous.
17. As a detective in the TUI, I want to watch the fugitive's route play back after the
    Case ends, so that I can see how near or far I was.
18. As a detective in the TUI, I want to start a New Case after one ends, so that I can
    keep playing without restarting the app.
19. As a detective starting a New Case, I want the same Scenario but a fresh, different
    Case, so that I keep exploring the same world with new chases.
20. As a detective, I want the same Case Seed to always produce the same Case, so that a
    chase is reproducible and could later be shared.
21. As a developer, I want the fugitive's location absent from the in-progress API, so that
    no client can accidentally leak it and break the blind chase.
22. As a developer, I want Scenario graphs authored as undirected edges once, so that I
    cannot introduce asymmetric-edge bugs.
23. As a developer, I want the API to serve ready-to-navigate adjacency, so that each
    client does not re-implement edge expansion.

## Implementation Decisions

### Domain / mechanics

- The detective is a movable entity. It starts at the **route origin** `route[0]` (the
  crime scene). The fugitive has already fled: its position on day `d` is `route[d]`
  (day 1 → `route[1]`). This structurally guarantees no co-location at Case creation.
- A single **Move** resolves as: detective relocates to the chosen Location → the In-Game
  Clock advances one day → the fugitive relocates to its new day's Location → **then**
  the outcome is judged. Co-location is judged *after both have moved* ("passing in
  transit": stepping onto a Location the fugitive is leaving is a miss).
- **Case Outcome** is `in_progress`, `won` (detective co-located with fugitive — the
  Stage-1 stand-in for the Stage-3 Arrest), or `lost` (fugitive reaches the Escape
  Location). Losing is a normal terminal state, not an error.
- Stage 1 is **day-only** (the day+hour clock and Action Costs are deferred — see
  [ADR-0011](../../docs/adr/0011-day-hour-clock-and-action-cost-model.md)). No `Wait`,
  no move-to-self.

### Clock (ADR-0011)

- The full clock model (day + hour, overnight fugitive movement, hour-based Action Costs,
  forced rest, the info-vs-speed arc) is recorded but **not implemented** this stage. The
  hour dimension arrives with Stage 2's Interview.

### Location Graph (ADR-0012)

- Connections are **undirected**, authored **once** as unordered pairs in `graph.toml`
  (`connections = [["paris", "london"], ...]`), dropping the old `from`/`to` fields. The
  loader expands them. No one-way routes exist anywhere in the game.
- The **Escape Location** has no authored connections; it is appended by the route
  generator as the terminus and is never navigable.
- The `minimal` Scenario becomes a 6-Location **triangular prism** so the blind chase is
  winnable by interception rather than only trailing:
  - Triangle A: Paris — London — Madrid (— Paris)
  - Triangle B: Berlin — Rome — Oslo (— Berlin)
  - Rungs: Paris—Berlin, London—Rome, Madrid—Oslo
  - Plus the Escape Location (no edges).

### Route generation

- Replace the Stage-0 greedy "first unvisited neighbor" walk (which dead-ends on a
  3-regular graph) with a **seeded self-avoiding walk**: from a seeded origin, step to a
  seeded-random *unvisited* neighbor until the walk cannot extend, then append the Escape
  Location. No backtracking; it can never error; route length varies naturally (honoring
  the hidden deadline of
  [ADR-0002](../../docs/adr/0002-hidden-deadline-via-escape-location.md)).
- A minimum-route-length floor is **deferred** (future difficulty parameter; stub filed
  under `.scratch/difficulty-parameters/`).

### Case state (functional core — ADR-0008)

- `CaseState` gains `detective_location`, `seed` (issue 01), and `status`
  (`in_progress`/`won`/`lost`, stored, set by the core transition). `day` stays.
- `case_id` becomes its own UUID, **distinct from** `seed`; route reconstruction derives
  from `state.seed`, never from `case_id`.
- The pure core gains a transition `apply_move(graph, state, target) -> (new_state,
  outcome)`. It enforces adjacency (a chase rule, so it lives in the core); illegal input
  is raised as a domain error, normal outcomes are returned as data.

### API contract

- `POST /cases` response changes to **per-Location adjacency**:
  `{ "case_id", "locations": [{ "id", "name", "neighbors": [id, ...] }, ...] }`. The
  separate `connections` field is dropped; the Escape Location is absent (never a key,
  never a neighbor).
- `POST /cases/{id}/advance` is **removed** and replaced by `POST /cases/{id}/move` with
  body `{ "target": "<location_id>" }`.
- In-progress `move`/`GET` response is **blind**: `{ "day", "detective_location",
  "status" }` — no `fugitive_location`.
- On a terminal outcome the response additionally carries the revealed route, e.g.
  `{ "day", "detective_location", "status": "won"|"lost", "fugitive_route": [id, ...] }`
  (ordered, including the escape terminus).
- Error mapping: illegal Move (non-adjacent, self-move, unknown Location) → `400`
  `illegal_move`; Move on a terminal Case → `409` `case_over` (repurposed from the
  Stage-0 `trail_gone_cold`); unknown Case → `404`. Escaping is **not** an error — it is a
  `200` with `status: lost`.
- The committed `openapi.json` is regenerated and stays current (ADR-0009).

### TUI

- The spectator auto-tick is removed. On launch, create a Case against `minimal` with a
  fresh UUID seed and render the opening position.
- Render: a status line (`Day N`, current Location, status); the detective's current
  Location highlighted; the current Location's `neighbors` as a focusable selectable list.
  The fugitive is never highlighted during play.
- Selecting a neighbor sends `POST /move` and re-renders.
- On a terminal outcome: stop accepting Moves and **play the revealed route back** day by
  day on a timer (the one surviving use of `set_interval`), then show a banner
  ("Caught them!" / "The trail went cold.") and offer **[N]ew case / [Q]uit**.
- **New case** reuses the same Scenario (`minimal`) with a fresh random seed.
- The hand-rolled client (ADR-0009) gains a `move` method and drops the client-side
  `Connection` type in favour of per-Location `neighbors`.

## Testing Decisions

- A good test asserts **external behavior**, not implementation details: value-in/
  value-out for the core, HTTP request/response for the API, rendered state and sent
  requests for the TUI.
- **Core (`backend/tests/core/`)** — the highest-value new seam. Test `apply_move`
  directly with seeded states: legal Move advances day and relocates both; co-location
  after both move yields `won`; stepping onto the Location the fugitive is leaving does
  *not* win; reaching escape yields `lost`; non-adjacent/self/unknown targets raise;
  Moves on a terminal state raise. Test the route generator: same seed → same route;
  every route is a valid adjacent path; never visits a Location twice; ends with the
  escape terminus; never errors on the prism. Prior art: `test_chase.py`, `test_route.py`,
  `test_seed.py`.
- **Shell (`backend/tests/shell/`)** — the loader parses undirected pairs and the graph
  exposes symmetric adjacency; the Escape Location carries no neighbors. Prior art:
  `test_scenario.py`.
- **API (`backend/tests/api/`)** — `create_case` returns per-Location adjacency with no
  escape and no `connections`; in-progress responses are blind; `move` returns the right
  status and reveals the route on terminal; `400`/`409`/`404` mapping; OpenAPI schema is
  current. Prior art: `test_cases.py`, `test_schema.py`.
- **TUI (`frontend-tui/tests/`)** — the `move` client method against the live schema
  (contract test); the app renders the opening position, sends a Move on selection,
  hides the fugitive in play, plays the route back on a terminal outcome, and starts a
  New Case with a fresh seed on the same Scenario. Prior art: `test_client.py`,
  `test_app.py`.

## Out of Scope

- Clues, the Interview action, Persons, Suspects, identity, the Dossier (Stages 2–4+).
- The `Wait` and explicit `Arrest` actions (Stage 3) — co-location is a temporary win
  trigger.
- The hour dimension of the clock, Action Costs, distance-scaled Move costs, forced rest
  (ADR-0011; arrive at Stage 2).
- Minimum-route-length floor and difficulty parameters (deferred stub).
- AI narrative and Language Preference (Stage 5; the `TextProvider` port already exists).
- Authentication, accounts, database persistence, reproduction-by-UUID across sessions
  (Stage 8). The generator is seeded now, but seeds are not persisted.
- A graphical node/edge graph layout in the TUI — the list-based view is sufficient.

## Further Notes

- The blind chase's winnability depends on the bidirectional prism graph: the detective
  starts one hop behind, so only a graph navigable in both directions lets it go the other
  way round and intercept rather than trail forever (see ADR-0012).
- Decisions captured this session: ADR-0011 (clock), ADR-0012 (undirected graph); new
  glossary terms In-Game Clock (revised), Action Cost, Day, Case Outcome in
  `backend/CONTEXT.md`. Pre-existing stubs issues 01 (seed in `CaseState`) and 02
  (graph representation) are folded into this stage.
