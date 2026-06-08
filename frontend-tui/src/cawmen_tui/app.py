"""The Textual application: a thin client that renders backend state.

Stage 0 stands up the skeleton — on mount it confirms the backend is reachable. The
game screens (graph, fugitive position) accrete here as later stages land.
"""

import uuid
from typing import TYPE_CHECKING, Self

import httpx
from textual.app import App, ComposeResult
from textual.widgets import Static

from cawmen_tui.client import (
    AbstractClient,
    BackendClient,
    CaseState,
    Location,
    TrailGoneCold,
)

if TYPE_CHECKING:
    from textual.timer import Timer


class CawmenApp(App[None]):
    """The Cawmen Sandaigo terminal client."""

    CSS = "#status { dock: bottom; }"

    def __init__(
        self,
        client: AbstractClient,
        *,
        owned_http: httpx.AsyncClient | None = None,
    ) -> None:
        """Build the app around an injected backend client (ADR-0007/0009).

        `owned_http` is the client's transport when the app created it itself (the run
        path) and must therefore close it on exit; injected clients (tests) own theirs.
        """
        super().__init__()
        self._client = client
        self._owned_http = owned_http
        self._case_id: str | None = None
        self._locations: list[Location] = []
        self._fugitive_location: str | None = None
        self._tick_timer: Timer | None = None

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

    async def on_mount(self) -> None:
        """Confirm backend reachability, create a case, and start the spectator view."""
        health = await self._client.health()
        self.query_one("#status", Static).update(f"Backend: {health.status}")

        case = await self._client.create_case(
            scenario="grand-tour", seed=str(uuid.uuid4())
        )
        self._case_id = case.case_id
        self._locations = case.locations

        state = await self._client.get_case(self._case_id)
        self._render_state(state)

        self._tick_timer = self.set_interval(2, self._tick)

    def _render_state(self, state: CaseState) -> None:
        """Update clock and location list to reflect the given case state."""
        self._fugitive_location = state.fugitive_location
        self.query_one("#clock", Static).update(f"Day {state.day}")
        lines = [
            f"[reverse]{loc.name}[/reverse]"
            if loc.id == state.fugitive_location
            else loc.name
            for loc in self._locations
        ]
        self.query_one("#locations", Static).update("\n".join(lines))

    async def _tick(self) -> None:
        """Advance the case by one step and update the display."""
        if self._case_id is None:
            return
        result = await self._client.advance_case(self._case_id)
        if isinstance(result, TrailGoneCold):
            if self._tick_timer is not None:
                self._tick_timer.stop()
            self.query_one("#locations", Static).update("Trail gone cold")
        else:
            self._render_state(result)

    async def on_unmount(self) -> None:
        """Close the HTTP client if this app created it."""
        if self._owned_http is not None:
            await self._owned_http.aclose()
