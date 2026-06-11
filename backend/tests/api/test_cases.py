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


# ---------------------------------------------------------------------------
# POST /cases
# ---------------------------------------------------------------------------


async def test_post_cases_returns_a_case_id_distinct_from_seed(
    client: httpx.AsyncClient,
) -> None:
    """POST /cases returns a unique case_id that is not the same as the seed."""
    response = await client.post("/cases", json={"scenario": "minimal", "seed": "s1"})

    assert response.status_code == 200
    data = response.json()
    assert "case_id" in data
    assert data["case_id"] != "s1"


async def test_post_cases_returns_six_named_locations(
    client: httpx.AsyncClient,
) -> None:
    """POST /cases returns the six named (non-escape) locations with neighbors."""
    response = await client.post("/cases", json={"scenario": "minimal", "seed": "s1"})

    data = response.json()
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


# ---------------------------------------------------------------------------
# GET /cases/{id}  — blind response
# ---------------------------------------------------------------------------


async def test_get_case_returns_day_one_detective_location_and_status(
    client: httpx.AsyncClient,
) -> None:
    """GET /cases/{id} is blind: day, detective_location, status — fugitive hidden."""
    r = await client.post("/cases", json={"scenario": "minimal", "seed": "g1"})
    case_id = r.json()["case_id"]

    response = await client.get(f"/cases/{case_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["day"] == 1
    assert data["detective_location"] in PRISM_LOCATIONS
    assert data["status"] == "in_progress"
    assert "fugitive_location" not in data


async def test_get_unknown_case_returns_404(client: httpx.AsyncClient) -> None:
    """GET /cases/{id} returns 404 for an unknown case id."""
    assert (await client.get("/cases/unknown")).status_code == 404


# ---------------------------------------------------------------------------
# POST /cases/{id}/move  — in-progress
# ---------------------------------------------------------------------------


async def test_move_advances_day_and_returns_blind_response(
    client: httpx.AsyncClient,
) -> None:
    """POST /cases/{id}/move advances the day and returns a blind response."""
    r = await client.post("/cases", json={"scenario": "minimal", "seed": "m1"})
    data = r.json()
    case_id = data["case_id"]
    detective_start = next(
        loc for loc in data["locations"] if loc["id"] == data["detective_location"]
    )
    first_neighbor = detective_start["neighbors"][0]

    response = await client.post(
        f"/cases/{case_id}/move", json={"target": first_neighbor}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["day"] == 2
    assert body["detective_location"] == first_neighbor
    assert body["status"] in {"in_progress", "won", "lost"}
    assert "fugitive_location" not in body


async def test_move_on_unknown_case_returns_404(client: httpx.AsyncClient) -> None:
    """POST /cases/{id}/move returns 404 for an unknown case."""
    response = await client.post("/cases/unknown/move", json={"target": "paris"})

    assert response.status_code == 404


async def test_move_to_non_adjacent_returns_400(client: httpx.AsyncClient) -> None:
    """Moving to a non-adjacent location returns 400 with detail 'illegal_move'."""
    r = await client.post("/cases", json={"scenario": "minimal", "seed": "m3"})
    data = r.json()
    case_id = data["case_id"]
    detective_start = data["detective_location"]
    # Find a location two hops away (not a direct neighbor)
    locations_map = {loc["id"]: loc for loc in data["locations"]}
    neighbors = set(locations_map[detective_start]["neighbors"])
    non_adjacent = next(
        loc_id
        for loc_id in PRISM_LOCATIONS
        if loc_id != detective_start and loc_id not in neighbors
    )

    response = await client.post(
        f"/cases/{case_id}/move", json={"target": non_adjacent}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "illegal_move"


async def test_move_to_current_location_returns_400(
    client: httpx.AsyncClient,
) -> None:
    """Moving to the detective's current location returns 400 (self-move)."""
    r = await client.post("/cases", json={"scenario": "minimal", "seed": "m4"})
    data = r.json()
    case_id = data["case_id"]

    response = await client.post(
        f"/cases/{case_id}/move", json={"target": data["detective_location"]}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "illegal_move"


async def test_move_on_terminal_case_returns_409(client: httpx.AsyncClient) -> None:
    """POST /cases/{id}/move on a finished case returns 409 with detail 'case_over'."""
    r = await client.post("/cases", json={"scenario": "minimal", "seed": "m5"})
    data = r.json()
    case_id = data["case_id"]
    locations_map = {loc["id"]: loc for loc in data["locations"]}

    # Run until the case ends
    current = data["detective_location"]
    for _ in range(30):
        target = locations_map[current]["neighbors"][0]
        resp = await client.post(f"/cases/{case_id}/move", json={"target": target})
        body = resp.json()
        if body.get("status") in {"won", "lost"}:
            break
        current = target

    # One more move should be rejected
    response = await client.post(f"/cases/{case_id}/move", json={"target": target})
    assert response.status_code == 409
    assert response.json()["detail"] == "case_over"


# ---------------------------------------------------------------------------
# POST /cases/{id}/move  — terminal responses
# ---------------------------------------------------------------------------


async def test_terminal_move_response_reveals_fugitive_route(
    client: httpx.AsyncClient,
) -> None:
    """A terminal (won or lost) move response includes the full fugitive_route."""
    r = await client.post("/cases", json={"scenario": "minimal", "seed": "t1"})
    data = r.json()
    case_id = data["case_id"]
    locations_map = {loc["id"]: loc for loc in data["locations"]}

    current = data["detective_location"]
    for _ in range(30):
        target = locations_map[current]["neighbors"][0]
        resp = await client.post(f"/cases/{case_id}/move", json={"target": target})
        body = resp.json()
        if body.get("status") in {"won", "lost"}:
            assert "fugitive_route" in body
            assert isinstance(body["fugitive_route"], list)
            assert len(body["fugitive_route"]) > 0
            return
        current = target

    msg = "Case never ended after 30 moves"
    raise AssertionError(msg)


async def test_lost_case_returns_200_not_409(client: httpx.AsyncClient) -> None:
    """Losing (fugitive escapes) returns 200, not an error status."""
    r = await client.post("/cases", json={"scenario": "minimal", "seed": "t2"})
    data = r.json()
    case_id = data["case_id"]
    locations_map = {loc["id"]: loc for loc in data["locations"]}

    current = data["detective_location"]
    for _ in range(30):
        target = locations_map[current]["neighbors"][0]
        resp = await client.post(f"/cases/{case_id}/move", json={"target": target})
        assert resp.status_code == 200
        body = resp.json()
        if body.get("status") == "lost":
            assert "fugitive_route" in body
            return
        if body.get("status") == "won":
            return
        current = target
