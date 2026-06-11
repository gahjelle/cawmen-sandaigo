"""Contract tests for the hand-rolled typed backend client (ADR-0009)."""

from typing import TYPE_CHECKING

from cawmen_tui.client import BackendClient, CaseCreated, CaseState, TrailGoneCold

if TYPE_CHECKING:
    import httpx

PRISM_LOCATIONS = {"paris", "rome", "madrid", "berlin", "london", "oslo"}


async def test_health_reports_the_backend_status(
    backend_http: httpx.AsyncClient,
) -> None:
    """The client reads the backend's health status into a typed result."""
    client = BackendClient(backend_http)

    health = await client.health()

    assert health.status == "ok"


async def test_create_case_returns_case_id_and_location_graph(
    backend_http: httpx.AsyncClient,
) -> None:
    """create_case maps POST /cases to a typed CaseCreated with neighbors."""
    client = BackendClient(backend_http)

    result = await client.create_case(scenario="minimal", seed="c1")

    assert isinstance(result, CaseCreated)
    assert result.case_id == "c1"
    assert len(result.locations) == 6
    assert any(loc.id == "paris" for loc in result.locations)
    assert any(loc.name == "Paris" for loc in result.locations)
    paris = next(loc for loc in result.locations if loc.id == "paris")
    assert set(paris.neighbors) == {"rome", "madrid", "berlin"}


async def test_create_case_has_no_connections(
    backend_http: httpx.AsyncClient,
) -> None:
    """create_case result no longer carries a connections list."""
    client = BackendClient(backend_http)

    result = await client.create_case(scenario="minimal", seed="c1b")

    assert not hasattr(result, "connections")


async def test_get_case_returns_day_and_fugitive_location(
    backend_http: httpx.AsyncClient,
) -> None:
    """get_case maps GET /cases/{id} to a typed CaseState."""
    client = BackendClient(backend_http)
    await client.create_case(scenario="minimal", seed="c2")

    result = await client.get_case("c2")

    assert isinstance(result, CaseState)
    assert result.day == 1
    assert result.fugitive_location in PRISM_LOCATIONS


async def test_advance_case_returns_incremented_day(
    backend_http: httpx.AsyncClient,
) -> None:
    """advance_case maps POST /cases/{id}/advance to a typed CaseState."""
    client = BackendClient(backend_http)
    await client.create_case(scenario="minimal", seed="c3")

    result = await client.advance_case("c3")

    assert isinstance(result, CaseState)
    assert result.day == 2
    assert result.fugitive_location in PRISM_LOCATIONS


async def test_advance_case_returns_trail_gone_cold_on_escape(
    backend_http: httpx.AsyncClient,
) -> None:
    """advance_case returns TrailGoneCold (not raises) when the fugitive escapes."""
    client = BackendClient(backend_http)
    await client.create_case(scenario="minimal", seed="c4")
    result = None
    for _ in range(20):
        result = await client.advance_case("c4")
        if isinstance(result, TrailGoneCold):
            return
    msg = "Fugitive never escaped after 20 advances"
    raise AssertionError(msg)
