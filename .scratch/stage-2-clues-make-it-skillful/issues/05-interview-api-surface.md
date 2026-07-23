# Interview API surface

Status: open
Labels: wayfinder:grilling
Assignee:
Parent: [Stage 2 map](../MAP.md)

## Question

Design the REST surface for Interview: presumably `POST /cases/{case_id}/interview`.

- **Request body**: empty (clue always comes from the detective's current Location at
  Stage 2 — no `person_id`, per Out of scope) or a target field?
- **Response shape**: does it carry the rendered clue text, the structured clue fact, the
  updated `CaseState` (day/status — depends on the interview-cost decision), and the
  terminal-case variant (can an interview *end* a case, e.g. by advancing into escape)?
- **Error cases**: interviewing a terminal case (409, mirroring `CaseOverError`), unknown
  case (404), any illegal-interview condition.

Keep endpoints thin HTTP translators; the orchestration lands in the CaseActionHandler
(see the extraction task, which is blocked on this decision). Resolve via `/grilling`.

## Blocked by

- [Does Interview cost a day?](./03-does-interview-cost-a-day.md)
- [What does a Clue reveal?](./04-what-a-clue-reveals.md)
