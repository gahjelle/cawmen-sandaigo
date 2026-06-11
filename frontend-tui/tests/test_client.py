"""Contract tests for the hand-rolled typed backend client (ADR-0009)."""

from typing import TYPE_CHECKING

from cawmen_tui.client import BackendClient, CaseCreated, CaseState, TerminalState

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
    """create_case maps POST /cases to a typed CaseCreated with detective_location."""
    client = BackendClient(backend_http)

    result = await client.create_case(scenario="minimal", seed="c1")

    assert isinstance(result, CaseCreated)
    assert result.case_id != "c1"
    assert len(result.locations) == 6
    assert result.detective_location in PRISM_LOCATIONS
    paris = next(loc for loc in result.locations if loc.id == "paris")
    assert set(paris.neighbors) == {"rome", "madrid", "oslo"}


async def test_create_case_has_no_connections(
    backend_http: httpx.AsyncClient,
) -> None:
    """create_case result no longer carries a connections list."""
    client = BackendClient(backend_http)

    result = await client.create_case(scenario="minimal", seed="c1b")

    assert not hasattr(result, "connections")


async def test_get_case_returns_blind_state(
    backend_http: httpx.AsyncClient,
) -> None:
    """get_case maps GET /cases/{id} to a blind CaseState (no fugitive_location)."""
    client = BackendClient(backend_http)
    created = await client.create_case(scenario="minimal", seed="c2")

    result = await client.get_case(created.case_id)

    assert isinstance(result, CaseState)
    assert result.day == 1
    assert result.detective_location in PRISM_LOCATIONS
    assert result.status == "in_progress"
    assert not hasattr(result, "fugitive_location")


async def test_move_case_returns_incremented_day(
    backend_http: httpx.AsyncClient,
) -> None:
    """move_case maps POST /cases/{id}/move to a CaseState or TerminalState."""
    client = BackendClient(backend_http)
    created = await client.create_case(scenario="minimal", seed="c3")
    neighbors = next(
        loc.neighbors
        for loc in created.locations
        if loc.id == created.detective_location
    )

    result = await client.move_case(created.case_id, neighbors[0])

    assert isinstance(result, (CaseState, TerminalState))
    assert result.day == 2
    assert result.detective_location == neighbors[0]


async def test_move_case_returns_terminal_state_with_route_on_end(
    backend_http: httpx.AsyncClient,
) -> None:
    """move_case returns TerminalState with fugitive_route when the case ends."""
    client = BackendClient(backend_http)
    created = await client.create_case(scenario="minimal", seed="c4")
    locations_map = {loc.id: loc for loc in created.locations}

    current = created.detective_location
    for _ in range(30):
        target = locations_map[current].neighbors[0]
        result = await client.move_case(created.case_id, target)
        if isinstance(result, TerminalState):
            assert result.status in {"won", "lost"}
            assert isinstance(result.fugitive_route, list)
            assert len(result.fugitive_route) > 0
            return
        current = target

    msg = "Case never ended after 30 moves"
    raise AssertionError(msg)
