"""A small hand-rolled, typed httpx client for the backend REST API.

Deliberately not generated from OpenAPI and not a shared schema package (ADR-0009): the
TUI consumes the same public contract any client would, with contract tests guarding the
client's expectations against the live schema.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx


@dataclass(frozen=True)
class Health:
    """The backend's reported liveness."""

    status: str


class BackendClient:
    """Typed REST client over an injected httpx ``AsyncClient`` (real wire or ASGI)."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        """Wrap the given httpx client; the caller owns its lifecycle."""
        self._http = http

    async def health(self) -> Health:
        """Fetch the backend's health status."""
        response = await self._http.get("/health")
        response.raise_for_status()
        return Health(status=response.json()["status"])
