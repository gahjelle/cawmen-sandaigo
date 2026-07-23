# Does Interview cost a day?

Status: open
Labels: wayfinder:grilling
Assignee:
Parent: [Stage 2 map](../MAP.md)

## Question

Is **Interview** a clock-advancing action (like Move, it costs a day and lets the
fugitive flee one hop) or a **free look** the detective can take without advancing the
In-Game Clock?

This is the **root** of the Stage-2 mechanic. It reshapes difficulty (a free interview
means "scout, then commit"; a costed one forces "spend a day to learn where they went"),
the API (does the interview response advance and return new `CaseState`, or leave it
untouched?), and how much a single Clue must be worth. Resolve via `/grilling` +
`/domain-modeling`; consider ADR-0008's Move resolution order for consistency.

## Blocked by

_Nothing — frontier._
