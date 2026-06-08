# Revisit bidirectional graph representation

Status: needs-triage

## Context

At Stage 0, connections are bidirectional by intent but the graph file lists each
direction as a separate explicit edge. The escape connection was initially authored as
one-way (`madrid → escape` only), which caused a connection leak — `escape → madrid`
slipped through the filter. The fix added the reverse edge to `graph.toml` and widened
the filter to `escape_id not in (c.to, c.from_)`.

This is a workaround, not a design. Some open questions deferred to Stage 1:

- Should the graph format declare edges once and treat them as undirected, with the
  loader expanding them into both directions? This would make the scenario file easier
  to author and prevent asymmetry bugs.
- Or should edges stay explicitly directed, and the authoring convention (+ a lint rule)
  require symmetric pairs?
- How does directionality interact with Move choices shown to the player? A directed
  graph could express one-way routes (e.g. a flight that doesn't return); an undirected
  one cannot.
- The escape location is a special case: should its edges be omitted from the graph file
  entirely and injected by the loader, rather than authored explicitly?

## What to do

Work through the above questions — probably as a grill session — before Stage 1 touches
the graph loader or adds Move UI. Document the decision in an ADR.

## Acceptance criteria

- An ADR records the chosen representation and the reasoning
- The graph loader and scenario files are consistent with that decision
- A repolint or schema check prevents asymmetric edge authoring (if explicit pairs are kept)

## Last step

Write an article stub under `articles/01-<stage-name>/bidirectional-graph.md` summarising
the decision and what changed.
