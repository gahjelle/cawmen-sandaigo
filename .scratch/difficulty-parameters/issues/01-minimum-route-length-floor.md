# Minimum Fugitive Route length floor

Status: needs-triage

## Context

The Fugitive Route is a seeded self-avoiding walk over the Location Graph that runs until
it can't extend, then appends the Escape Location (see `core/route.py`,
[ADR-0012](../../../docs/adr/0012-undirected-location-graph.md)). On the Stage-1 `minimal`
graph (a triangular prism) the shortest possible maximal walk is provably 5 cities, so a
length floor can never fire and would be untestable dead code — it was deliberately
deferred during the Stage-1 grill.

The floor becomes real once two things are true:

- Scenarios introduce graphs whose self-avoiding walks *can* terminate early (giving a
  brutally short blind deadline), and
- Route length becomes a tunable **difficulty parameter** rather than purely seed-driven.

## What to do

Introduce a minimum route length applied during generation — e.g. prefer extending the
walk, re-roll, or backtrack — so a Case's deadline never falls below a configured floor.
Wire the floor in as one of the Scenario/Case difficulty parameters.

## Acceptance criteria

- Route generation guarantees at least `min_length` real Locations before the escape
- The floor is a difficulty parameter, not a hard-coded constant
- A graph that *can* produce short walks is covered by a test proving the floor holds

## Last step

Write an article stub summarising the floor and its role as a difficulty parameter.
