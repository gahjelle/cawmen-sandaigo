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
    Location(id="paris", name="Paris", neighbors=["berlin", "rome"]),
    Location(id="berlin", name="Berlin", neighbors=["paris", "london"]),
    Location(id="rome", name="Rome", neighbors=["paris", "madrid"]),
    Location(id="madrid", name="Madrid", neighbors=["rome", "oslo"]),
]


@dataclass
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

        assert cawmen_app._detective_location == "paris"
        assert not hasattr(cawmen_app, "_fugitive_location") or (
            cawmen_app._fugitive_location is None  # type: ignore[attr-defined]
        )


async def test_app_shows_neighbors_of_detective_location() -> None:
    """The neighbour list shows the detective's current location's neighbours."""
    paris = Location(id="paris", name="Paris", neighbors=["berlin", "rome"])
    berlin = Location(id="berlin", name="Berlin", neighbors=["paris"])
    rome = Location(id="rome", name="Rome", neighbors=["paris"])
    locations = [paris, berlin, rome]
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

        assert any("Berlin" in t for t in labels)
        assert any("Rome" in t for t in labels)


async def test_pressing_enter_on_first_neighbour_sends_move() -> None:
    """Pressing Enter on a highlighted neighbour fires the move to that location."""
    # paris neighbours: ["berlin", "rome"]; first item highlighted by default → berlin
    next_state = CaseState(day=2, detective_location="berlin", status="in_progress")
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

        assert cawmen_app._detective_location == "berlin"


async def test_pressing_down_then_enter_moves_to_second_neighbour() -> None:
    """Pressing Down then Enter selects the second neighbour."""
    # paris neighbours: ["berlin", "rome"]; down moves to rome
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
        await pilot.press("down")
        await pilot.press("enter")
        await pilot.pause(delay=0.1)

        assert cawmen_app._detective_location == "rome"


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
        assert cawmen_app._detective_location == "berlin"


async def test_app_shows_terminal_message_on_won() -> None:
    """When the detective wins, the status is shown."""
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

        rendered = str(cawmen_app.query_one("#locations", Static).render())
        assert "won" in rendered.lower() or "caught" in rendered.lower()


async def test_app_shows_terminal_message_on_lost() -> None:
    """When the fugitive escapes, the status is shown."""
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

        rendered = str(cawmen_app.query_one("#locations", Static).render())
        assert "lost" in rendered.lower() or "escaped" in rendered.lower()
