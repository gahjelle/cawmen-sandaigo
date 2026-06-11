# Undirected prism graph, self-avoiding route gen, adjacency API

Status: closed

## Parent

PRD: `.scratch/stage-1-player-moves/PRD.md`. Supersedes stub `02-bidirectional-graph-representation.md`.

## What to build

Move the `minimal` Scenario and the whole graph layer to the undirected model of
[ADR-0012](../../../docs/adr/0012-undirected-location-graph.md), and serve ready-to-navigate
adjacency to clients — while keeping the existing spectator demoable on the new graph.

- Rewrite `minimal` as a 6-Location **triangular prism** plus the Escape Location:
  - Triangle A: Paris—Rome—Madrid; Triangle B: Berlin—London—Oslo;
    rungs Paris—Berlin, Rome—London, Madrid—Oslo. Escape has no edges.
- Author connections **once** as unordered pairs (`connections = [["paris","rome"], ...]`),
  dropping `from`/`to`. The loader expands them undirected; the Escape Location is never a
  neighbour.
- Replace the greedy "first unvisited neighbour" route walk (it dead-ends on a 3-regular
  graph) with a **seeded self-avoiding walk**: from a seeded origin, step to a
  seeded-random unvisited neighbour until it cannot extend, then append the Escape
  Location. No backtracking; never errors; length varies naturally.
- `POST /cases` returns per-Location adjacency:
  `{ case_id, locations: [{ id, name, neighbors: [id, ...] }] }`, dropping the separate
  `connections` field. The Escape Location is absent.
- Update the TUI client + app to consume `neighbors` (drop the client-side `Connection`
  type); the spectator still auto-advances and renders the prism.
- Regenerate `openapi.json`.

## Acceptance criteria

- [x] `minimal` is the 6-Location prism authored as undirected pairs; no `from`/`to`
- [x] The loader exposes symmetric adjacency; the Escape Location has no neighbours
- [x] Route generation is a seeded self-avoiding walk: same seed → same route, every route
      is a valid adjacent path, no Location repeats, ends with the escape terminus, never
      errors on the prism
- [x] `POST /cases` returns per-Location `{id, name, neighbors}` with no escape and no
      `connections` field
- [x] TUI renders the prism and still spectates; client no longer has a `Connection` type
- [x] `openapi.json` is current and `just check` passes

## Blocked by

None - can start immediately.

## Last step

Write an article stub under `articles/01-the-detective-chases/undirected-prism-graph.md`
summarising the undirected graph, the prism, and the self-avoiding route generator.
