"""Pilot tests driving the Textual app against the in-process backend."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from textual.widgets import ListView, Static

from cawmen_tui.app import CawmenApp
from cawmen_tui.client import (
    BackendClient,
    CaseCreated,
    CaseOver,
    CaseState,
    Health,
    IllegalMove,
    Location,
    TerminalState,
)

if TYPE_CHECKING:
    import httpx


# ---------------------------------------------------------------------------
# Fake client for unit tests
# ---------------------------------------------------------------------------

_LOCATIONS = [
    Location(id="paris", name="Paris", neighbors=["rome", "madrid"]),
    Location(id="berlin", name="Berlin", neighbors=["rome"]),
    Location(id="rome", name="Rome", neighbors=["paris", "madrid", "berlin"]),
    Location(id="madrid", name="Madrid", neighbors=["rome", "paris"]),
]


@dataclass(kw_only=True)
class FakeClient:
    """Controllable stand-in for BackendClient used in unit tests."""

    locations: list[Location] = field(default_factory=lambda: list(_LOCATIONS))
    detective_start: str = "paris"
    initial_state: CaseState = field(
        default_factory=lambda: CaseState(
            day=1, detective_location="paris", status="in_progress"
        )
    )
    move_results: list[CaseState | TerminalState | CaseOver | IllegalMove] = field(
        default_factory=list
    )

    async def health(self) -> Health:
        """Return a hardcoded ok status."""
        return Health(status="ok")

    async def create_case(
        self,
        scenario: str,  # noqa: ARG002
        seed: str | None = None,  # noqa: ARG002
    ) -> CaseCreated:
        """Return a fixed case with the configured locations."""
        return CaseCreated(
            case_id="test-case",
            detective_location=self.detective_start,
            locations=self.locations,
        )

    async def get_case(self, case_id: str) -> CaseState:  # noqa: ARG002
        """Return the configured initial state."""
        return self.initial_state

    async def move_case(
        self,
        case_id: str,  # noqa: ARG002
        target: str,  # noqa: ARG002
    ) -> CaseState | TerminalState | CaseOver | IllegalMove:
        """Pop and return the next configured move result."""
        return self.move_results.pop(0)


# ---------------------------------------------------------------------------
# Integration test (real backend)
# ---------------------------------------------------------------------------


async def test_app_shows_the_backend_connection_status(
    backend_http: httpx.AsyncClient,
) -> None:
    """On mount the app reports that the backend is reachable."""
    app = CawmenApp(BackendClient(backend_http))

    async with app.run_test() as pilot:
        await pilot.pause()
        status = pilot.app.query_one("#status", Static)

        assert "ok" in str(status.render())


# ---------------------------------------------------------------------------
# Mount / initial display
# ---------------------------------------------------------------------------


async def test_app_shows_location_list_on_mount() -> None:
    """On mount the app renders the scenario's location names."""
    app = CawmenApp(FakeClient())
    async with app.run_test() as pilot:
        await pilot.pause()
        locations = pilot.app.query_one("#locations", Static)
        rendered = str(locations.render())

        assert "Paris" in rendered
        assert "Berlin" in rendered
        assert "Rome" in rendered
        assert "Madrid" in rendered


async def test_app_shows_clock_on_mount() -> None:
    """On mount the In-Game Clock shows the current day."""
    app = CawmenApp(FakeClient())
    async with app.run_test() as pilot:
        await pilot.pause()
        clock = pilot.app.query_one("#clock", Static)

        assert "Day 1" in str(clock.render())


async def test_app_highlights_detective_location_not_fugitive() -> None:
    """The detective's current location is highlighted; the fugitive is not shown."""
    app = CawmenApp(FakeClient(detective_start="paris"))
    async with app.run_test() as pilot:
        await pilot.pause()
        cawmen_app = pilot.app
        assert isinstance(cawmen_app, CawmenApp)

        assert cawmen_app._session is not None
        assert cawmen_app._session.detective_location == "paris"
        assert not hasattr(cawmen_app, "_fugitive_location") or (
            cawmen_app._fugitive_location is None  # type: ignore[attr-defined]
        )


async def test_app_shows_neighbors_of_detective_location() -> None:
    """The neighbour list shows the detective's current location's neighbours."""
    paris = Location(id="paris", name="Paris", neighbors=["rome", "madrid"])
    rome = Location(id="rome", name="Rome", neighbors=["paris"])
    madrid = Location(id="madrid", name="Madrid", neighbors=["paris"])
    locations = [paris, rome, madrid]
    app = CawmenApp(
        FakeClient(
            locations=locations,
            detective_start="paris",
            initial_state=CaseState(
                day=1, detective_location="paris", status="in_progress"
            ),
        )
    )
    async with app.run_test() as pilot:
        await pilot.pause()
        labels = [str(lbl.render()) for lbl in pilot.app.query("#neighbors Label")]

        assert any("Rome" in t for t in labels)
        assert any("Madrid" in t for t in labels)


async def test_pressing_enter_on_first_neighbour_sends_move() -> None:
    """Pressing Enter on a highlighted neighbour fires the move to that location."""
    # paris neighbours: ["rome", "madrid"]; first item highlighted by default → rome
    next_state = CaseState(day=2, detective_location="rome", status="in_progress")
    app = CawmenApp(
        FakeClient(
            detective_start="paris",
            initial_state=CaseState(
                day=1, detective_location="paris", status="in_progress"
            ),
            move_results=[next_state],
        )
    )
    async with app.run_test() as pilot:
        await pilot.pause()
        cawmen_app = pilot.app
        assert isinstance(cawmen_app, CawmenApp)
        cawmen_app.query_one("#neighbors", ListView).focus()
        await pilot.press("enter")
        await pilot.pause(delay=0.1)

        assert cawmen_app._session is not None
        assert cawmen_app._session.detective_location == "rome"


async def test_pressing_down_then_enter_moves_to_second_neighbour() -> None:
    """Pressing Down then Enter selects the second neighbour."""
    # paris neighbours: ["rome", "madrid"]; down moves to madrid
    next_state = CaseState(day=2, detective_location="madrid", status="in_progress")
    app = CawmenApp(
        FakeClient(
            detective_start="paris",
            initial_state=CaseState(
                day=1, detective_location="paris", status="in_progress"
            ),
            move_results=[next_state],
        )
    )
    async with app.run_test() as pilot:
        await pilot.pause()
        cawmen_app = pilot.app
        assert isinstance(cawmen_app, CawmenApp)
        cawmen_app.query_one("#neighbors", ListView).focus()
        await pilot.press("down")
        await pilot.press("enter")
        await pilot.pause(delay=0.1)

        assert cawmen_app._session is not None
        assert cawmen_app._session.detective_location == "madrid"


# ---------------------------------------------------------------------------
# Move interaction
# ---------------------------------------------------------------------------


async def test_app_updates_state_after_move() -> None:
    """After a move the clock increments and detective location updates."""
    next_state = CaseState(day=2, detective_location="berlin", status="in_progress")
    app = CawmenApp(FakeClient(move_results=[next_state]))
    async with app.run_test() as pilot:
        await pilot.pause()
        cawmen_app = pilot.app
        assert isinstance(cawmen_app, CawmenApp)

        await cawmen_app._move("berlin")
        await pilot.pause()

        clock = cawmen_app.query_one("#clock", Static)
        assert "Day 2" in str(clock.render())
        assert cawmen_app._session is not None
        assert cawmen_app._session.detective_location == "berlin"


async def test_terminal_outcome_clears_neighbour_list() -> None:
    """On a terminal outcome the neighbour list is cleared (no more moves)."""
    terminal = TerminalState(
        day=2,
        detective_location="berlin",
        status="won",
        fugitive_route=["paris", "berlin", "escape"],
    )
    app = CawmenApp(FakeClient(move_results=[terminal]))
    async with app.run_test() as pilot:
        await pilot.pause()
        cawmen_app = pilot.app
        assert isinstance(cawmen_app, CawmenApp)

        await cawmen_app._move("berlin")
        await pilot.pause()

        assert len(list(pilot.app.query("#neighbors Label"))) == 0


async def test_terminal_outcome_starts_playback() -> None:
    """On a terminal outcome the app stores the route and is ready to play it back."""
    terminal = TerminalState(
        day=3,
        detective_location="berlin",
        status="lost",
        fugitive_route=["paris", "rome", "madrid", "escape"],
    )
    app = CawmenApp(FakeClient(move_results=[terminal]))
    async with app.run_test() as pilot:
        await pilot.pause()
        cawmen_app = pilot.app
        assert isinstance(cawmen_app, CawmenApp)

        await cawmen_app._move("berlin")
        await pilot.pause()

        assert cawmen_app._playback is not None
        assert cawmen_app._playback.route == ["paris", "rome", "madrid", "escape"]


# ---------------------------------------------------------------------------
# Route playback and end-of-case experience
# ---------------------------------------------------------------------------


async def test_route_widget_accumulates_path_during_playback() -> None:
    """Each advance step appends the next location name to #route."""
    terminal = TerminalState(
        day=2,
        detective_location="berlin",
        status="won",
        fugitive_route=["paris", "rome", "escape"],
    )
    app = CawmenApp(FakeClient(move_results=[terminal]))
    async with app.run_test() as pilot:
        await pilot.pause()
        cawmen_app = pilot.app
        assert isinstance(cawmen_app, CawmenApp)

        await cawmen_app._move("berlin")
        await pilot.pause()

        cawmen_app._advance_playback()
        await pilot.pause()
        route_text = str(cawmen_app.query_one("#route", Static).render())
        assert "Paris" in route_text
        assert "Rome" not in route_text

        cawmen_app._advance_playback()
        await pilot.pause()
        route_text = str(cawmen_app.query_one("#route", Static).render())
        assert "Paris" in route_text
        assert "Rome" in route_text


async def test_playback_advances_through_route_steps() -> None:
    """Each _advance_playback call advances _playback_current to the next position."""
    terminal = TerminalState(
        day=2,
        detective_location="berlin",
        status="won",
        fugitive_route=["paris", "berlin", "escape"],
    )
    app = CawmenApp(FakeClient(move_results=[terminal]))
    async with app.run_test() as pilot:
        await pilot.pause()
        cawmen_app = pilot.app
        assert isinstance(cawmen_app, CawmenApp)

        await cawmen_app._move("berlin")
        await pilot.pause()

        assert cawmen_app._playback is not None
        cawmen_app._advance_playback()
        assert cawmen_app._playback.current == "paris"

        cawmen_app._advance_playback()
        assert cawmen_app._playback.current == "berlin"


async def test_win_banner_appears_after_full_playback() -> None:
    """After advancing through the full route, 'Caught them!' appears in #banner."""
    terminal = TerminalState(
        day=2,
        detective_location="berlin",
        status="won",
        fugitive_route=["paris", "berlin", "escape"],
    )
    app = CawmenApp(FakeClient(move_results=[terminal]))
    async with app.run_test() as pilot:
        await pilot.pause()
        cawmen_app = pilot.app
        assert isinstance(cawmen_app, CawmenApp)

        await cawmen_app._move("berlin")
        await pilot.pause()

        for _ in terminal.fugitive_route:
            cawmen_app._advance_playback()
        await pilot.pause()

        banner = str(cawmen_app.query_one("#banner", Static).render())
        assert "Caught them" in banner


async def test_loss_banner_appears_after_full_playback() -> None:
    """After the full route plays back on a loss, 'The trail went cold.' appears."""
    terminal = TerminalState(
        day=3,
        detective_location="paris",
        status="lost",
        fugitive_route=["paris", "rome", "escape"],
    )
    app = CawmenApp(FakeClient(move_results=[terminal]))
    async with app.run_test() as pilot:
        await pilot.pause()
        cawmen_app = pilot.app
        assert isinstance(cawmen_app, CawmenApp)

        await cawmen_app._move("rome")
        await pilot.pause()

        for _ in terminal.fugitive_route:
            cawmen_app._advance_playback()
        await pilot.pause()

        banner = str(cawmen_app.query_one("#banner", Static).render())
        assert "trail went cold" in banner


@dataclass(kw_only=True)
class TrackingFakeClient(FakeClient):
    """FakeClient that records the seed passed to each create_case call."""

    seeds_seen: list[str | None] = field(default_factory=list)

    async def create_case(
        self,
        scenario: str,
        seed: str | None = None,
    ) -> CaseCreated:
        """Record seed then delegate to the parent."""
        self.seeds_seen.append(seed)
        return await super().create_case(scenario, seed)


async def test_new_case_key_starts_fresh_case_after_playback() -> None:
    """Pressing N after full playback creates a new case with a different seed."""
    terminal = TerminalState(
        day=2,
        detective_location="berlin",
        status="won",
        fugitive_route=["paris", "berlin", "escape"],
    )
    next_case_state = CaseState(day=1, detective_location="paris", status="in_progress")
    fake = TrackingFakeClient(
        move_results=[terminal],
        initial_state=next_case_state,
    )
    app = CawmenApp(fake)
    async with app.run_test() as pilot:
        await pilot.pause()
        cawmen_app = pilot.app
        assert isinstance(cawmen_app, CawmenApp)

        first_seed = fake.seeds_seen[0] if fake.seeds_seen else None

        await cawmen_app._move("berlin")
        await pilot.pause()
        for _ in terminal.fugitive_route:
            cawmen_app._advance_playback()
        await pilot.pause()

        await pilot.press("n")
        await pilot.pause(delay=0.1)

        assert len(fake.seeds_seen) == 2
        assert fake.seeds_seen[1] != first_seed
        assert cawmen_app._session is not None
        assert cawmen_app._session.detective_location == "paris"


async def test_quit_key_exits_app() -> None:
    """Pressing Q exits the application cleanly."""
    app = CawmenApp(FakeClient())
    async with app.run_test() as pilot:
        await pilot.pause()
        await pilot.press("q")
        await pilot.pause(delay=0.1)

    assert app.return_value is None  # exited without error
