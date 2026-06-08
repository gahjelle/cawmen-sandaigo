# Stage 0 Methods on the TUI Backend Client

The TUI's `BackendClient` is a hand-rolled, typed wrapper around an injected `httpx.AsyncClient` — no code generation, no shared schema package (ADR-0009). Stage 0 adds three methods covering the case lifecycle: `create_case`, `get_case`, and `advance_case`.

## Returning rather than raising on 409

The most deliberate choice was making `advance_case` return `TrailGoneCold` when the server responds 409, rather than raising an exception. A sentinel return value keeps the calling code in `app.py` pattern-matchable with a plain `match` statement, without needing a `try/except` block inline. It also makes the 409 path visible in the return type annotation:

```python
async def advance_case(self, case_id: str) -> CaseState | TrailGoneCold:
```

The type annotation itself communicates that "trail gone cold" is an expected outcome, not an error.

## Contract tests via ASGITransport

Tests use `httpx.ASGITransport` wired to the real FastAPI app — no mocks, no HTTP server. This is the same transport the TUI uses in production (with a real server replacing the ASGI app). The test boundary is the client's public interface, not the HTTP wire: if the backend schema changes and the client's assumptions break, the contract tests fail.

## `list[T]` not `tuple[T, ...]`

The `CaseCreated` dataclass stores locations and connections as `list[Location]` and `list[Connection]` rather than tuples, per the repo's convention (CAW005): homogeneous sequences are `list[T]`. The dataclass is still `frozen=True` — which prevents field reassignment but doesn't make the list contents immutable, a small trade-off accepted for consistency.
