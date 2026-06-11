"""The Textual application: a thin client that renders backend state.

Stage 1: the player controls the detective. On mount a case is created and the
detective's starting location with its neighbours is presented as a selectable
list. The player presses Enter to move; the app sends POST /move and updates
the display. The fugitive is never shown during play; the full route is revealed
on a terminal outcome.
"""

import uuid
from typing import Self

import httpx
from textual.app import App, ComposeResult
from textual.widgets import Label, ListItem, ListView, Static

from cawmen_tui.client import (
    AbstractClient,
    BackendClient,
    CaseState,
    TerminalState,
)


class CawmenApp(App[None]):
    """The Cawmen Sandaigo terminal client."""

    CSS = "#status { dock: bottom; }"

    def __init__(
        self,
        client: AbstractClient,
        *,
        owned_http: httpx.AsyncClient | None = None,
    ) -> None:
        """Build the app around an injected backend client (ADR-0007/0009)."""
        super().__init__()
        self._client = client
        self._owned_http = owned_http
        self._case_id: str | None = None
        self._detective_location: str | None = None
        self._locations_map: dict[str, list[str]] = {}
        self._location_names: dict[str, str] = {}
        self._current_neighbors: list[str] = []

    @classmethod
    def from_api_url(cls, api_url: str) -> Self:
        """Build an app that connects to an already-running backend over HTTP."""
        http = httpx.AsyncClient(base_url=api_url)
        return cls(BackendClient(http), owned_http=http)

    def compose(self) -> ComposeResult:
        """Lay out the initial widgets."""
        yield Static("Connecting to backend…", id="status")
        yield Static("", id="clock")
        yield Static("", id="locations")
        yield ListView(id="neighbors")

    async def on_mount(self) -> None:
        """Confirm backend reachability, create a case, and enter play mode."""
        health = await self._client.health()
        self.query_one("#status", Static).update(f"Backend: {health.status}")

        case = await self._client.create_case(
            scenario="minimal", seed=str(uuid.uuid4())
        )
        self._case_id = case.case_id
        self._detective_location = case.detective_location
        for loc in case.locations:
            self._locations_map[loc.id] = loc.neighbors
            self._location_names[loc.id] = loc.name

        state = await self._client.get_case(self._case_id)
        self._render_state(state)

    def _render_state(self, state: CaseState | TerminalState) -> None:
        """Update clock, location list, and neighbour list to reflect state."""
        self._detective_location = state.detective_location
        self.query_one("#clock", Static).update(f"Day {state.day}")

        lines = [
            f"[reverse]{name}[/reverse]" if loc_id == state.detective_location else name
            for loc_id, name in self._location_names.items()
        ]
        self.query_one("#locations", Static).update("\n".join(lines))

        neighbors_widget = self.query_one("#neighbors", ListView)
        neighbors_widget.clear()

        if isinstance(state, TerminalState):
            if state.status == "won":
                self.query_one("#locations", Static).update(
                    f"Case won! Fugitive route: {' → '.join(state.fugitive_route)}"
                )
            else:
                self.query_one("#locations", Static).update(
                    f"Case lost. Fugitive route: {' → '.join(state.fugitive_route)}"
                )
            self._current_neighbors = []
        else:
            neighbors = self._locations_map.get(state.detective_location, [])
            self._current_neighbors = neighbors
            for neighbor_id in neighbors:
                name = self._location_names.get(neighbor_id, neighbor_id)
                neighbors_widget.append(ListItem(Label(name)))
            if neighbors:
                neighbors_widget.index = 0

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Fire a move to the selected neighbour."""
        idx = event.index
        if idx < len(self._current_neighbors):
            await self._move(self._current_neighbors[idx])

    async def _move(self, target: str) -> None:
        """Send a move to the backend and update the display."""
        if self._case_id is None:
            return
        result = await self._client.move_case(self._case_id, target)
        if isinstance(result, (CaseState, TerminalState)):
            self._render_state(result)

    async def on_unmount(self) -> None:
        """Close the HTTP client if this app created it."""
        if self._owned_http is not None:
            await self._owned_http.aclose()
