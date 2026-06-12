# Extract a CaseActionHandler for action orchestration

Status: needs-triage

## Context

Architecture review (2026-06-12) identified that `move_case` in `api/app.py` inlines a
fixed choreography: load context → load graph → call core function → handle domain errors
→ save state → optionally build route → return response. With one action this is fine.
Stage 2 adds **Interview**, which will repeat the same pattern and also wire in the
`TextProvider`. By the time **Wait** and **Arrest** land at Stage 3, the pattern will
exist in four endpoints with no shared home.

## What to build

When implementing the **Interview** action at Stage 2, extract a `CaseActionHandler`
in the shell layer rather than writing a second endpoint that duplicates `move_case`'s
orchestration.

- Create `backend/src/cawmen_backend/shell/case_handler.py` with a `CaseActionHandler`
  class that holds the `StateStore`, graph-loader, and `TextProvider`.
- `CaseActionHandler.move(case_id, target)` replaces the inline body of `move_case`.
- `CaseActionHandler.interview(case_id, person_id, language)` goes here directly,
  not inline in its endpoint.
- Endpoints become thin HTTP translators: call the handler, map domain errors to status
  codes, return the response model.
- The handler raises the same domain exceptions (`CaseOverError`, `IllegalMoveError`);
  the endpoint layer catches and converts them.

## Acceptance criteria

- [ ] A `CaseActionHandler` class exists in the shell layer owning the
      load/call/save pattern
- [ ] `move_case` endpoint body is `≤ 10 lines` (HTTP translation only)
- [ ] `interview_case` endpoint body matches the same slim profile
- [ ] Handler is directly testable without spinning up FastAPI (plain Python calls)
- [ ] `just check` passes

## Blocked by

The Interview feature issue (not yet written — this stub is written ahead of the PRD).

## Last step

Write an article stub under `articles/02-clues-make-it-skillful/` covering the
`CaseActionHandler` extraction and how it concentrates the load/call/save pattern.
