# Add Stage 0 Methods to BackendClient

Status: done

Depends on: 04

Extend `frontend-tui/src/cawmen_tui/client.py` with typed methods for the three Stage 0
endpoints. The client is hand-rolled (ADR-0009) — no code generation.

## Methods to add

```python
async def create_case(self, scenario: str, seed: str | None = None) -> CaseCreated:
    """POST /cases — returns case_id and location graph."""

async def get_case(self, case_id: str) -> CaseState:
    """GET /cases/{case_id} — returns day and fugitive_location."""

async def advance_case(self, case_id: str) -> CaseState | TrailGoneCold:
    """POST /cases/{case_id}/advance — returns new state or trail-gone-cold sentinel."""
```

Define `CaseCreated`, `CaseState`, and `TrailGoneCold` as frozen dataclasses in the
client module. `TrailGoneCold` is returned (not raised) when the server responds 409 —
keeps the calling code in `app.py` pattern-matchable.

## Acceptance criteria

- All three methods are typed end-to-end
- `advance_case` returns `TrailGoneCold` (not raises) on 409
- Contract tests use `httpx.ASGITransport` against the real FastAPI app to verify the
  client's assumptions match the live schema (ADR-0009)

## Last step

Write an article stub in `articles/00-the-fugitive-moves/` per `docs/agents/articles.md`.

## Comments

2026-06-08 97ac32e — Added CaseCreated, CaseState, TrailGoneCold dataclasses and create_case/get_case/advance_case methods; advance_case returns TrailGoneCold on 409; contract tests via httpx.ASGITransport.
