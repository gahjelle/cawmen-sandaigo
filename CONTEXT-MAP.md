# Context Map

Cawmen Sandaigo is a geography and detective game where a player takes the role of a
detective chasing a fugitive across locations by gathering clues. The system is split
into one authoritative backend and one or more thin frontends that talk to it over REST.

## Contexts

- [Backend](./backend/CONTEXT.md) — owns all game state and the game-domain language: the chase, the Dossier, Scenarios, Campaigns, and the Campaign arc. Exposes a REST API.
- [TUI Frontend](./frontend-tui/CONTEXT.md) — Python Textual terminal client. Renders backend state and sends actions.
- Web Frontend (`frontend-web/`, Phoenix LiveView) — introduced at Stage 6 (see [ADR-0004](./docs/adr/0004-phoenix-liveview-web-frontend.md)). Not yet created.

## Relationships

- **Frontends → Backend**: every frontend is a thin client that communicates with the backend **only over the REST API** — they send actions and render responses, holding no game state of their own. The wire is real HTTP from day one.
- **TUI → Backend (launch)**: the TUI may subprocess-launch the backend for one-command play, but still speaks to it over HTTP. Gameplay coupling is REST-only; see the relevant ADR.
- **Shared vocabulary**: the game-domain terms (Case, Fugitive, Clue, Suspect, …) are **owned by the backend** and defined once in `backend/CONTEXT.md`. Frontends render these concepts but do not redefine them; their own glossaries hold only presentation-specific language.

## Architecture

- **Backend (Python)** — the authoritative source of all game state. Exposes a REST API. Runs all game logic, AI calls, and vector search. Issues JWT tokens for authentication.
- **TUI Frontend (Python Textual)** — terminal client consuming the REST API.
- **Web Frontend (Phoenix LiveView / Elixir)** — browser client consuming the same REST API (Stage 6).
- **Authentication** — username + password, JWT tokens shared across frontends.
- **Frontends are thin clients** — all state lives on the backend.

## AI Responsibilities

- **Location discovery**: given a Campaign scope (e.g. "inside Barcelona"), AI proposes candidate Locations.
- **Narrative text**: Clue descriptions, Location atmosphere, Crime narratives, and Suspect profiles are AI-generated.
- **Multilingual output**: AI generates game text directly in the target language (not post-hoc translation).

## Non-AI Responsibilities

- Travel graph construction between Locations.
- Case route planning and Crime setup.
- Case generation from Scenario + Case Seed.
