"""Pilot tests driving the Textual app against the in-process backend."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from textual.widgets import Static

from cawmen_tui.app import CawmenApp
from cawmen_tui.client import (
    BackendClient,
    CaseCreated,
    CaseState,
    Health,
    Location,
    TrailGoneCold,
)

if TYPE_CHECKING:
    import httpx


# ---------------------------------------------------------------------------
# Fake client for spectator-screen unit tests
# ---------------------------------------------------------------------------

_LOCATIONS = [
    Location(id="paris", name="Paris"),
    Location(id="berlin", name="Berlin"),
    Location(id="rome", name="Rome"),
    Location(id="madrid", name="Madrid"),
]


@dataclass
class FakeClient:
    """Controllable stand-in for BackendClient used in spectator-screen tests."""

    locations: list[Location] = field(default_factory=lambda: list(_LOCATIONS))
    initial_state: CaseState = field(
        default_factory=lambda: CaseState(day=1, fugitive_location="paris")
    )
    advance_states: list[CaseState | TrailGoneCold] = field(default_factory=list)

    async def health(self) -> Health:
        """Return a hardcoded ok status."""
        return Health(status="ok")

    async def create_case(
        self,
        scenario: str,  # noqa: ARG002
        seed: str | None = None,  # noqa: ARG002
    ) -> CaseCreated:
        """Return a fixed case with the configured locations."""
        return CaseCreated(case_id="test-case", locations=self.locations)

    async def get_case(self, case_id: str) -> CaseState:  # noqa: ARG002
        """Return the configured initial state."""
        return self.initial_state

    async def advance_case(self, case_id: str) -> CaseState | TrailGoneCold:  # noqa: ARG002
        """Pop and return the next configured advance state."""
        return self.advance_states.pop(0)


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
# Spectator screen unit tests (FakeClient)
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


async def test_app_highlights_fugitive_location() -> None:
    """The fugitive's current location is tracked for rendering."""
    app = CawmenApp(FakeClient())
    async with app.run_test() as pilot:
        await pilot.pause()
        cawmen_app = pilot.app
        assert isinstance(cawmen_app, CawmenApp)
        assert cawmen_app._fugitive_location == "paris"


async def test_app_advances_state_on_tick() -> None:
    """After a tick the clock increments and the highlighted location updates."""
    next_state = CaseState(day=2, fugitive_location="berlin")
    app = CawmenApp(FakeClient(advance_states=[next_state]))
    async with app.run_test() as pilot:
        await pilot.pause()
        cawmen_app = pilot.app
        assert isinstance(cawmen_app, CawmenApp)
        await cawmen_app._tick()
        await pilot.pause()

        clock = cawmen_app.query_one("#clock", Static)
        assert "Day 2" in str(clock.render())
        assert cawmen_app._fugitive_location == "berlin"


async def test_app_shows_trail_gone_cold_on_escape() -> None:
    """When the fugitive escapes the location list is replaced with a message."""
    app = CawmenApp(FakeClient(advance_states=[TrailGoneCold()]))
    async with app.run_test() as pilot:
        await pilot.pause()
        cawmen_app = pilot.app
        assert isinstance(cawmen_app, CawmenApp)
        await cawmen_app._tick()
        await pilot.pause()

        locations = cawmen_app.query_one("#locations", Static)
        assert "Trail gone cold" in str(locations.render())
