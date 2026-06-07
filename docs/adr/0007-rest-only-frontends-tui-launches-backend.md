# Frontends Speak REST Only; the TUI May Subprocess-Launch the Backend

Every frontend communicates with the backend **only over the REST API**, on a real HTTP wire, from day one — no frontend shares the backend's in-process objects or types. To still give one-command play, the TUI **subprocess-launches** the backend (`cawmen-backend serve`) on a free port, polls `/health`, then connects over `http://localhost:<port>`. The launch is a thin convenience layer over an "assume-running" client: passing `--api-url` skips the spawn and connects to an already-running backend.

The point is that the day-one principle — strict backend/frontend separation — is exercised honestly: the network/REST boundary is real at runtime, not just in tests, and the TUI consumes the API exactly the way the Elixir web client (Stage 6) will, so it is a faithful stand-in for "any client."

## Considered Options

- **In-process ASGI transport at runtime** (TUI imports the FastAPI app, drives it via `httpx.ASGITransport`) — rejected for the *run path*: it couples the TUI to backend Python, can't be the Elixir model, and never exercises the real wire. It is retained as a *test* tool (see ADR-0009 and the TUI test strategy), where it belongs.
- **Always assume an externally-started backend** — viable and kept as the explicit `--api-url` fallback, but rejected as the *default* because it loses the one-command experience.

## Consequences

Because both the spawn and the fallback use the identical HTTP wire, "assume-running" can ship first and auto-spawn can be added later as a self-contained launcher with **zero rework** to the client. The TUI package depends on the backend only to put its console script on `PATH` (ADR-0006) — never for domain types.
