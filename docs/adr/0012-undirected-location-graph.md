# Undirected Location Graph, Escape as Un-authored Terminus

Connections in a Scenario's Location Graph are **undirected**. Each edge is authored once in `graph.toml` (e.g. `paris — london`) and the loader expands it into travel in both directions. There are no one-way routes anywhere in the game, now or later: every connection a detective can cross, they can cross back.

The **Escape Location** has no authored connections. It is not a navigable node — the detective can never travel to it — so it does not appear in the connection list at all. The route generator appends it as the pure terminus of the Fugitive Route: "the node the fugitive vanishes to after its last real stop."

## Context

At Stage 0 connections were authored as explicit directed pairs, and the escape connection was authored one-way (`madrid → escape`). The reverse edge (`escape → madrid`) leaked through the client-facing filter, exposing the escape node. The fix bolted on a reverse edge and widened the filter — a workaround, not a design ([issue stage-1/02]).

Two alternatives were weighed:

- **Explicit directed pairs + a lint rule** enforcing symmetry. Rejected: it keeps the asymmetry-bug class alive and merely polices it, and authoring every edge twice is noise.
- **Directed edges to support one-way routes** (e.g. a flight that doesn't return). Rejected: deliberately out of scope — the chase is symmetric by design, and one-way edges would also make a blind Stage-1 chase unwinnable in more graph shapes.

## Consequences

- Scenario files are roughly half the size and cannot encode an asymmetric (illegal) graph.
- The escape node's special-casing disappears from the connection layer; it is handled solely as a route terminus.
- Winnability of the blind Stage-1 chase depends on the graph being navigable in both directions: the detective starts at the crime scene one hop behind ([the fugitive has already fled]), and only bidirectional edges let them go the other way round to intercept rather than trail forever. The Stage-1 `minimal` graph is therefore a connected 3-regular graph (a triangular prism over six Locations) rather than a single one-way cycle.

## Relationship to other ADRs

Supports the blind chase's winnability alongside [ADR-0011](./0011-day-hour-clock-and-action-cost-model.md) (the clock) and feeds the route generator, whose Hamiltonian-path generation over this graph replaces the Stage-0 greedy walk.
