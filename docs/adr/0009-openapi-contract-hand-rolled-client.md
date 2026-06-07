# OpenAPI as the API Contract, Hand-Rolled Client, Committed Schema

The FastAPI backend's auto-generated **OpenAPI schema is the source of truth for the client/server contract**. The TUI consumes it via a small **hand-written, typed `httpx` client** plus contract tests asserting the client's expectations match the live schema — deliberately *not* a shared Pydantic schema package, because that would make the TUI a privileged Python insider and undercut the Stage-6 goal of proving the API is genuinely frontend-agnostic (the Elixir web client will consume the same OpenAPI). To get migration-like rigor, the generated `openapi.json` is **committed as an artifact** and a prek/CI step regenerates it and fails if it is stale, so every contract change surfaces as a reviewable diff in its PR.

## Considered Options

- **Generate the client from OpenAPI** (e.g. `openapi-python-client`) — deferred, not rejected: at Stage 0's handful of endpoints it adds a regen step and generated-code ergonomics for near-zero benefit, and since both styles consume the same committed `openapi.json`, codegen can be adopted later for any client that outgrows the hand-rolled one.
- **Shared Pydantic schema package** imported by backend and TUI — rejected: Python-only (Elixir can't share it) and it defeats the frontend-agnostic proof.

## Consequences

A breaking-change gate (e.g. `oasdiff`) and API versioning (`/v1`) are **deferred until a frozen baseline exists** — Stage 6 (a second client) or Stage 8 (persisted/shareable Cases). Until then there is one in-repo client regenerated in lockstep, so every break is expected and self-controlled; re-baselining on an intentional break is then just regenerating and committing the schema. The committed schema + staleness check ships from day one regardless.
