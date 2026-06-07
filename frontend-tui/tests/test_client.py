"""Contract tests for the hand-rolled typed backend client (ADR-0009)."""

from typing import TYPE_CHECKING

from cawmen_tui.client import BackendClient

if TYPE_CHECKING:
    import httpx


async def test_health_reports_the_backend_status(
    backend_http: httpx.AsyncClient,
) -> None:
    """The client reads the backend's health status into a typed result."""
    client = BackendClient(backend_http)

    health = await client.health()

    assert health.status == "ok"
