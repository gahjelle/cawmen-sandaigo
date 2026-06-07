"""Integration tests for the Stage 0 Case endpoints."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from cawmen_backend.api.app import create_app

SCENARIOS = Path(__file__).resolve().parents[3] / "scenarios"


@pytest.fixture
def client() -> TestClient:
    """Return a test client backed by a fresh app instance with the real scenarios."""
    return TestClient(create_app(scenarios_dir=SCENARIOS))


def test_post_cases_returns_case_id_and_named_locations(client: TestClient) -> None:
    """POST /cases returns the case id and the four named (non-escape) locations."""
    response = client.post("/cases", json={"scenario": "grand-tour", "seed": "s1"})

    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "s1"
    assert len(data["locations"]) == 4
    assert {"id": "paris", "name": "Paris"} in data["locations"]


def test_post_cases_excludes_escape_location_and_its_connection(
    client: TestClient,
) -> None:
    """POST /cases omits the Escape Location and connections leading to it."""
    response = client.post("/cases", json={"scenario": "grand-tour", "seed": "s2"})

    data = response.json()
    assert all(loc["id"] != "escape" for loc in data["locations"])
    assert all(c["to"] != "escape" for c in data["connections"])


def test_post_cases_same_seed_produces_same_result(client: TestClient) -> None:
    """POST /cases is deterministic: same seed → same locations and connections."""
    r1 = client.post("/cases", json={"scenario": "grand-tour", "seed": "same"})
    r2 = client.post("/cases", json={"scenario": "grand-tour", "seed": "same"})

    assert r1.json()["locations"] == r2.json()["locations"]
    assert r1.json()["connections"] == r2.json()["connections"]


def test_get_case_returns_day_one_and_fugitive_location(client: TestClient) -> None:
    """GET /cases/{id} returns day 1 and a valid fugitive location after creation."""
    client.post("/cases", json={"scenario": "grand-tour", "seed": "s3"})
    response = client.get("/cases/s3")

    assert response.status_code == 200
    data = response.json()
    assert data["day"] == 1
    assert data["fugitive_location"] in ["paris", "berlin", "rome", "madrid", "escape"]


def test_get_unknown_case_returns_404(client: TestClient) -> None:
    """GET /cases/{id} returns 404 for an unknown case id."""
    assert client.get("/cases/unknown").status_code == 404


def test_advance_increments_day(client: TestClient) -> None:
    """POST /cases/{id}/advance moves the clock forward by one day."""
    client.post("/cases", json={"scenario": "grand-tour", "seed": "s4"})
    response = client.post("/cases/s4/advance")

    assert response.status_code == 200
    assert response.json()["day"] == 2


def test_advance_unknown_case_returns_404(client: TestClient) -> None:
    """POST /cases/{id}/advance returns 404 for an unknown case id."""
    assert client.post("/cases/unknown/advance").status_code == 404


def test_advance_after_escape_returns_409(client: TestClient) -> None:
    """POST /cases/{id}/advance returns 409 once the fugitive has escaped."""
    seed = "escape-test"
    client.post("/cases", json={"scenario": "grand-tour", "seed": seed})
    # grand-tour has 4 non-escape locations; route length is 5; escape at day 5
    for _ in range(4):
        client.post(f"/cases/{seed}/advance")

    response = client.post(f"/cases/{seed}/advance")

    assert response.status_code == 409
    assert response.json()["detail"] == "trail_gone_cold"
