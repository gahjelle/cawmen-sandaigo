# TUI Frontend

The Python Textual terminal client. A thin client: it renders game state served by the
backend and sends the detective's actions over the REST API, holding no game state of
its own. It speaks only HTTP to the backend (see the [Context Map](../CONTEXT-MAP.md)).

## Language

_No presentation-specific terms yet._ The game-domain vocabulary this client renders
(Detective, Location, Clue, Interview, …) is owned by the
[backend glossary](../backend/CONTEXT.md). Terms unique to how the TUI *presents* the
game (screens, panels, key bindings, layout concepts) will accrete here as they are
resolved — do not redefine backend domain terms in this file.
