# Scenario size: does clue-following need a bigger graph?

Status: open
Labels: wayfinder:grilling
Assignee:
Parent: [Stage 2 map](../MAP.md)

## Question

The implementation plan flags that "real procedural variety becomes necessary at Stage 2,
where a memorizable fixed route would defeat clue-following." Today there is one Scenario
(`minimal` — a 6-node triangular prism) and the fugitive walks a seeded self-avoiding walk
over it.

Decide: **does clue-following on the prism genuinely demonstrate skill, or does Stage 2
need a larger / additional Location Graph** so that following clues meaningfully beats
brute-forcing a small memorizable graph?

- If the prism suffices, record that and note why (keeps Stage 2 lean).
- If not, decide the shape of the new/expanded scenario (size, connectivity) as data —
  the engine already loads authored graphs (`shell/scenario.py`, `graph.toml`).

This informs — but does not pull in — the out-of-scope route-length-floor issue. Resolve
via `/grilling` + `/domain-modeling`. Runs in parallel to the interview-mechanic spine.

## Blocked by

_Nothing — frontier._
