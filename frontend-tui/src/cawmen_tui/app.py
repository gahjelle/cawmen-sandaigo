"""The Textual application: a thin client that renders backend state.

Stage 1: the player controls the detective. On mount a case is created and the
detective's starting location with its neighbours is presented as a selectable
list. The player presses Enter to move; the app sends POST /move and updates
the display. The fugitive is never shown during play; the full route is revealed
on a terminal outcome.

Two live pieces of state hang off the app, each in its own dataclass so the
concerns stay separate as Stage 2 grows them: a `GameSession` for the active
case, and a `PlaybackState` for the post-game route animation.
"""

import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar, Self

import httpx
from textual.app import App, ComposeResult
from textual.widgets import Label, ListItem, ListView, Static

if TYPE_CHECKING:
    from textual.timer import Timer

from cawmen_tui.client import (
    AbstractClient,
    BackendClient,
    CaseCreated,
    CaseState,
    TerminalState,
)


@dataclass(kw_only=True)
class GameSession:
    """Live-game state for the active case: the world and the detective in it."""

    case_id: str
    detective_location: str
    locations_map: dict[str, list[str]]
    location_names: dict[str, str]
    current_neighbors: list[str] = field(default_factory=list)


@dataclass(kw_only=True)
class PlaybackState:
    """Post-game animation state for revealing the fugitive's route."""

    route: list[str]
    step: int = 0
    current_stop: str | None = None
    status: str | None = None
    timer: Timer | None = None


class CawmenApp(App[None]):
    """The Cawmen Sandaigo terminal client."""

    CSS = "#status { dock: bottom; }"
    BINDINGS: ClassVar = [("n", "new_case", "New case"), ("q", "quit_app", "Quit")]

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
        self._session: GameSession | None = None
        self._playback: PlaybackState | None = None

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
        yield Static("", id="route")
        yield Static("", id="banner")

    def _start_session(self, case: CaseCreated) -> None:
        """Build the live-game session from a freshly created case."""
        self._session = GameSession(
            case_id=case.case_id,
            detective_location=case.detective_location,
            locations_map={loc.id: loc.neighbors for loc in case.locations},
            location_names={loc.id: loc.name for loc in case.locations},
        )

    async def on_mount(self) -> None:
        """Confirm backend reachability, create a case, and enter play mode."""
        health = await self._client.health()
        self.query_one("#status", Static).update(f"Backend: {health.status}")

        case = await self._client.create_case(
            scenario="minimal", seed=str(uuid.uuid4())
        )
        self._start_session(case)

        state = await self._client.get_case(case.case_id)
        self._render_state(state)

    def _render_state(self, state: CaseState | TerminalState) -> None:
        """Update clock, location list, and neighbour list to reflect state."""
        if self._session is None:
            return
        self._session.detective_location = state.detective_location
        self.query_one("#clock", Static).update(f"Day {state.day}")

        lines = [
            f"[reverse]{name}[/reverse]" if loc_id == state.detective_location else name
            for loc_id, name in self._session.location_names.items()
        ]
        self.query_one("#locations", Static).update("\n".join(lines))

        neighbors_widget = self.query_one("#neighbors", ListView)
        neighbors_widget.clear()

        if isinstance(state, TerminalState):
            self._session.current_neighbors = []
            self._playback = PlaybackState(
                route=state.fugitive_route, status=state.status
            )
            self.query_one("#route", Static).update("")
            self._playback.timer = self.set_interval(1.0, self._advance_playback)
        else:
            neighbors = self._session.locations_map.get(state.detective_location, [])
            self._session.current_neighbors = neighbors
            for neighbor_id in neighbors:
                name = self._session.location_names.get(neighbor_id, neighbor_id)
                neighbors_widget.append(ListItem(Label(name)))
            if neighbors:
                neighbors_widget.index = 0

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Fire a move to the selected neighbour."""
        idx = event.index
        if self._session is not None and idx < len(self._session.current_neighbors):
            await self._move(self._session.current_neighbors[idx])

    async def _move(self, target: str) -> None:
        """Send a move to the backend and update the display."""
        if self._session is None:
            return
        result = await self._client.move_case(self._session.case_id, target)
        if isinstance(result, (CaseState, TerminalState)):
            self._render_state(result)

    def _advance_playback(self) -> None:
        """Advance playback by one step; show banner after the last route position."""
        # Playback only exists alongside a session (both set together on the terminal
        # outcome), so guarding here lets the helpers take non-None values.
        if self._playback is None or self._session is None:
            return
        session, playback = self._session, self._playback
        if playback.step < len(playback.route):
            loc_id = playback.route[playback.step]
            playback.current_stop = loc_id
            playback.step += 1
            self._render_playback_locations(session, playback)
            self._append_route_step(session.location_names.get(loc_id, loc_id))
            if playback.step == len(playback.route):
                if playback.timer is not None:
                    playback.timer.stop()
                self._show_end_banner()

    def _append_route_step(self, name: str) -> None:
        """Append the given hop name to the #route widget."""
        route_widget = self.query_one("#route", Static)
        current = str(route_widget.render())
        if current:
            route_widget.update(f"{current} → {name}")
        else:
            route_widget.update(name)

    def _render_playback_locations(
        self, session: GameSession, playback: PlaybackState
    ) -> None:
        """Refresh #locations to highlight the current playback position."""
        lines = []
        for loc_id, name in session.location_names.items():
            if loc_id == session.detective_location:
                lines.append(f"[reverse]{name}[/reverse]")
            elif loc_id == playback.current_stop:
                lines.append(f"[bold red]{name}[/bold red]")
            else:
                lines.append(name)
        self.query_one("#locations", Static).update("\n".join(lines))

    def _show_end_banner(self) -> None:
        """Show the win/loss banner and N/Q instructions."""
        status = self._playback.status if self._playback else None
        if status == "won":
            message = "Caught them!\n[N] New case  [Q] Quit"
        else:
            message = "The trail went cold.\n[N] New case  [Q] Quit"
        self.query_one("#banner", Static).update(message)

    async def action_new_case(self) -> None:
        """Start a fresh case with a new random seed on the same scenario."""
        if self._playback is None:
            return
        if self._playback.timer is not None:
            self._playback.timer.stop()
        self._playback = None
        self.query_one("#banner", Static).update("")
        self.query_one("#route", Static).update("")

        case = await self._client.create_case(
            scenario="minimal", seed=str(uuid.uuid4())
        )
        self._start_session(case)

        state = await self._client.get_case(case.case_id)
        self._render_state(state)

    def action_quit_app(self) -> None:
        """Exit the application."""
        self.exit()

    async def on_unmount(self) -> None:
        """Close the HTTP client if this app created it."""
        if self._owned_http is not None:
            await self._owned_http.aclose()
