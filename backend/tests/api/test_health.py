"""Contract test for the health endpoint, driven in-process over the real ASGI app."""

import httpx
import pytest

from cawmen_backend.api.app import create_app


@pytest.fixture
def client() -> httpx.AsyncClient:
    """Provide an async HTTP client wired to the real ASGI app in-process."""
    transport = httpx.ASGITransport(app=create_app())
    return httpx.AsyncClient(transport=transport, base_url="http://backend")


async def test_health_reports_ok(client: httpx.AsyncClient) -> None:
    """The health endpoint reports an ok status the launcher can poll."""
    async with client:
        response = await client.get("/health")

    assert response.status_code == httpx.codes.OK
    assert response.json() == {"status": "ok"}
