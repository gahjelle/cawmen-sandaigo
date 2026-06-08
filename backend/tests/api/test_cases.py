"""Integration tests for the Stage 0 Case endpoints."""

from pathlib import Path
from typing import TYPE_CHECKING

import httpx
import pytest

from cawmen_backend.api.app import create_app

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

SCENARIOS = Path(__file__).resolve().parents[3] / "scenarios"


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    """Yield an httpx client backed by a fresh app instance with the real scenarios."""
    transport = httpx.ASGITransport(app=create_app(scenarios_dir=SCENARIOS))
    async with httpx.AsyncClient(transport=transport, base_url="http://backend") as c:
        yield c


async def test_post_cases_returns_case_id_and_named_locations(
    client: httpx.AsyncClient,
) -> None:
    """POST /cases returns the case id and the four named (non-escape) locations."""
    response = await client.post(
        "/cases", json={"scenario": "grand-tour", "seed": "s1"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "s1"
    assert len(data["locations"]) == 4
    assert {"id": "paris", "name": "Paris"} in data["locations"]


async def test_post_cases_excludes_escape_location_and_its_connection(
    client: httpx.AsyncClient,
) -> None:
    """POST /cases omits the Escape Location and connections leading to it."""
    response = await client.post(
        "/cases", json={"scenario": "grand-tour", "seed": "s2"}
    )

    data = response.json()
    assert all(loc["id"] != "escape" for loc in data["locations"])
    assert all(c["to"] != "escape" for c in data["connections"])


async def test_post_cases_same_seed_produces_same_result(
    client: httpx.AsyncClient,
) -> None:
    """POST /cases is deterministic: same seed → same locations and connections."""
    r1 = await client.post("/cases", json={"scenario": "grand-tour", "seed": "same"})
    r2 = await client.post("/cases", json={"scenario": "grand-tour", "seed": "same"})

    assert r1.json()["locations"] == r2.json()["locations"]
    assert r1.json()["connections"] == r2.json()["connections"]


async def test_get_case_returns_day_one_and_fugitive_location(
    client: httpx.AsyncClient,
) -> None:
    """GET /cases/{id} returns day 1 and a named location (Escape Location excluded)."""
    await client.post("/cases", json={"scenario": "grand-tour", "seed": "s3"})
    response = await client.get("/cases/s3")

    assert response.status_code == 200
    data = response.json()
    assert data["day"] == 1
    assert data["fugitive_location"] in ["paris", "berlin", "rome", "madrid"]


async def test_get_unknown_case_returns_404(client: httpx.AsyncClient) -> None:
    """GET /cases/{id} returns 404 for an unknown case id."""
    assert (await client.get("/cases/unknown")).status_code == 404


async def test_advance_increments_day(client: httpx.AsyncClient) -> None:
    """POST /cases/{id}/advance moves the clock forward by one day."""
    await client.post("/cases", json={"scenario": "grand-tour", "seed": "s4"})
    response = await client.post("/cases/s4/advance")

    assert response.status_code == 200
    assert response.json()["day"] == 2


async def test_advance_unknown_case_returns_404(client: httpx.AsyncClient) -> None:
    """POST /cases/{id}/advance returns 404 for an unknown case id."""
    assert (await client.post("/cases/unknown/advance")).status_code == 404


async def test_advance_after_escape_returns_409(client: httpx.AsyncClient) -> None:
    """POST /cases/{id}/advance returns 409 when the fugitive would escape."""
    seed = "escape-test"
    await client.post("/cases", json={"scenario": "grand-tour", "seed": seed})
    # 4 named locations → 3 successful advances (days 2, 3, 4), 4th hits the escape
    for _ in range(3):
        await client.post(f"/cases/{seed}/advance")

    response = await client.post(f"/cases/{seed}/advance")

    assert response.status_code == 409
    assert response.json()["detail"] == "trail_gone_cold"


async def test_escape_location_is_never_returned_as_fugitive_location(
    client: httpx.AsyncClient,
) -> None:
    """The fugitive_location field never exposes the Escape Location id."""
    seed = "no-escape-leak"
    await client.post("/cases", json={"scenario": "grand-tour", "seed": seed})

    named = ["paris", "berlin", "rome", "madrid"]
    for _ in range(3):
        response = await client.post(f"/cases/{seed}/advance")
        assert response.json()["fugitive_location"] in named
