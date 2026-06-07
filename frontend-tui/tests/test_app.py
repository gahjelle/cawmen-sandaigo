"""Pilot tests driving the Textual app against the in-process backend."""

from typing import TYPE_CHECKING

from textual.widgets import Static

from cawmen_tui.app import CawmenApp
from cawmen_tui.client import BackendClient

if TYPE_CHECKING:
    import httpx


async def test_app_shows_the_backend_connection_status(
    backend_http: httpx.AsyncClient,
) -> None:
    """On mount the app reports that the backend is reachable."""
    app = CawmenApp(BackendClient(backend_http))

    async with app.run_test() as pilot:
        await pilot.pause()
        status = pilot.app.query_one("#status", Static)

        assert "ok" in str(status.render())
