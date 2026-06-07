"""The Textual application: a thin client that renders backend state.

Stage 0 stands up the skeleton — on mount it confirms the backend is reachable. The
game screens (graph, fugitive position) accrete here as later stages land.
"""

from typing import Self

import httpx
from textual.app import App, ComposeResult
from textual.widgets import Static

from cawmen_tui.client import BackendClient


class CawmenApp(App[None]):
    """The Cawmen Sandaigo terminal client."""

    def __init__(
        self,
        client: BackendClient,
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

    @classmethod
    def from_api_url(cls, api_url: str) -> Self:
        """Build an app that connects to an already-running backend over HTTP."""
        http = httpx.AsyncClient(base_url=api_url)
        return cls(BackendClient(http), owned_http=http)

    def compose(self) -> ComposeResult:
        """Lay out the initial widgets."""
        yield Static("Connecting to backend…", id="status")

    async def on_mount(self) -> None:
        """Confirm the backend is reachable and show its status."""
        health = await self._client.health()
        self.query_one("#status", Static).update(f"Backend: {health.status}")

    async def on_unmount(self) -> None:
        """Close the HTTP client if this app created it."""
        if self._owned_http is not None:
            await self._owned_http.aclose()
