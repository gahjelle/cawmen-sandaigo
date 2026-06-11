"""Integration tests for the Stage 1 Case endpoints."""

from pathlib import Path
from typing import TYPE_CHECKING

import httpx
import pytest

from cawmen_backend.api.app import create_app

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

SCENARIOS = Path(__file__).resolve().parents[3] / "scenarios"

PRISM_LOCATIONS = {"paris", "rome", "madrid", "berlin", "london", "oslo"}


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    """Yield an httpx client backed by a fresh app instance with the real scenarios."""
    transport = httpx.ASGITransport(app=create_app(scenarios_dir=SCENARIOS))
    async with httpx.AsyncClient(transport=transport, base_url="http://backend") as c:
        yield c


async def test_post_cases_returns_case_id_and_named_locations(
    client: httpx.AsyncClient,
) -> None:
    """POST /cases returns the case id and the six named (non-escape) locations."""
    response = await client.post("/cases", json={"scenario": "minimal", "seed": "s1"})

    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "s1"
    assert len(data["locations"]) == 6
    paris = {"id": "paris", "name": "Paris", "neighbors": ["rome", "madrid", "berlin"]}
    assert paris in data["locations"]


async def test_post_cases_locations_include_neighbors(
    client: httpx.AsyncClient,
) -> None:
    """Each location in POST /cases carries its neighbor ids."""
    response = await client.post("/cases", json={"scenario": "minimal", "seed": "s2"})

    data = response.json()
    paris = next(loc for loc in data["locations"] if loc["id"] == "paris")
    assert set(paris["neighbors"]) == {"rome", "madrid", "berlin"}


async def test_post_cases_excludes_escape_location(
    client: httpx.AsyncClient,
) -> None:
    """POST /cases omits the Escape Location from the location list."""
    response = await client.post("/cases", json={"scenario": "minimal", "seed": "s3"})

    data = response.json()
    assert all(loc["id"] != "escape" for loc in data["locations"])
    assert all("escape" not in loc["neighbors"] for loc in data["locations"])


async def test_post_cases_has_no_connections_field(
    client: httpx.AsyncClient,
) -> None:
    """POST /cases no longer returns a top-level connections field."""
    response = await client.post("/cases", json={"scenario": "minimal", "seed": "s4"})

    assert "connections" not in response.json()


async def test_post_cases_same_seed_produces_same_result(
    client: httpx.AsyncClient,
) -> None:
    """POST /cases is deterministic: same seed → same locations."""
    r1 = await client.post("/cases", json={"scenario": "minimal", "seed": "same"})
    r2 = await client.post("/cases", json={"scenario": "minimal", "seed": "same"})

    assert r1.json()["locations"] == r2.json()["locations"]


async def test_get_case_returns_day_one_and_fugitive_location(
    client: httpx.AsyncClient,
) -> None:
    """GET /cases/{id} returns day 1 and a named location (Escape Location excluded)."""
    await client.post("/cases", json={"scenario": "minimal", "seed": "s5"})
    response = await client.get("/cases/s5")

    assert response.status_code == 200
    data = response.json()
    assert data["day"] == 1
    assert data["fugitive_location"] in PRISM_LOCATIONS


async def test_get_unknown_case_returns_404(client: httpx.AsyncClient) -> None:
    """GET /cases/{id} returns 404 for an unknown case id."""
    assert (await client.get("/cases/unknown")).status_code == 404


async def test_advance_increments_day(client: httpx.AsyncClient) -> None:
    """POST /cases/{id}/advance moves the clock forward by one day."""
    await client.post("/cases", json={"scenario": "minimal", "seed": "s6"})
    response = await client.post("/cases/s6/advance")

    assert response.status_code == 200
    assert response.json()["day"] == 2


async def test_advance_unknown_case_returns_404(client: httpx.AsyncClient) -> None:
    """POST /cases/{id}/advance returns 404 for an unknown case id."""
    assert (await client.post("/cases/unknown/advance")).status_code == 404


async def test_advance_after_escape_returns_409(client: httpx.AsyncClient) -> None:
    """POST /cases/{id}/advance returns 409 when the fugitive has escaped."""
    seed = "escape-test"
    await client.post("/cases", json={"scenario": "minimal", "seed": seed})
    for _ in range(20):
        r = await client.post(f"/cases/{seed}/advance")
        if r.status_code == 409:
            assert r.json()["detail"] == "trail_gone_cold"
            return
    msg = "Fugitive never escaped after 20 advances"
    raise AssertionError(msg)


async def test_escape_location_is_never_returned_as_fugitive_location(
    client: httpx.AsyncClient,
) -> None:
    """The fugitive_location field never exposes the Escape Location id."""
    seed = "no-escape-leak"
    await client.post("/cases", json={"scenario": "minimal", "seed": seed})

    for _ in range(5):
        response = await client.post(f"/cases/{seed}/advance")
        if response.status_code == 409:
            break
        assert response.json()["fugitive_location"] in PRISM_LOCATIONS
