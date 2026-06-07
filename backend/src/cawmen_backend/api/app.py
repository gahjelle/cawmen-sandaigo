"""The FastAPI application factory and its routes."""

import random
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import FastAPI, HTTPException
from pydantic import Field

from cawmen_backend.core.chase import (
    CaseState,
    advance_clock,
    fugitive_location,
    has_escaped,
)
from cawmen_backend.core.route import generate_route
from cawmen_backend.core.seed import derive_seed
from cawmen_backend.models import FrozenModel
from cawmen_backend.shell.scenario import load_location_graph
from cawmen_backend.shell.state_store import InMemoryStateStore

if TYPE_CHECKING:
    from cawmen_backend.core.chase import FugitiveRoute


class HealthResponse(FrozenModel):
    """Liveness payload polled by the TUI launcher before it connects (ADR-0007)."""

    status: str


class CreateCaseRequest(FrozenModel):
    """Body for POST /cases."""

    scenario: str
    seed: str | None = None


class LocationOut(FrozenModel):
    """A named Location as returned to clients (Escape Location excluded)."""

    id: str
    name: str


class ConnectionOut(FrozenModel):
    """A connection between two named Locations as returned to clients."""

    from_: str = Field(alias="from")
    to: str


class CreateCaseResponse(FrozenModel):
    """Response for POST /cases."""

    case_id: str
    locations: list[LocationOut]
    connections: list[ConnectionOut]


class CaseResponse(FrozenModel):
    """Response for GET /cases/{id} and POST /cases/{id}/advance."""

    day: int
    fugitive_location: str


def create_app(scenarios_dir: Path = Path("scenarios")) -> FastAPI:
    """Build the FastAPI app exposing the Cawmen Sandaigo REST API."""
    app = FastAPI(title="Cawmen Sandaigo", version="0.0.0")
    store = InMemoryStateStore()
    case_scenarios: dict[str, str] = {}

    def _reconstruct_route(case_id: str, scenario: str) -> FugitiveRoute:
        graph = load_location_graph(scenarios_dir / scenario / "graph.toml")
        rng = random.Random(derive_seed(case_id, "route"))  # noqa: S311
        return generate_route(graph, rng)

    @app.get("/health")
    def health() -> HealthResponse:
        return HealthResponse(status="ok")

    @app.post("/cases")
    def create_case(body: CreateCaseRequest) -> CreateCaseResponse:
        seed = body.seed or str(uuid.uuid4())
        graph = load_location_graph(scenarios_dir / body.scenario / "graph.toml")
        rng = random.Random(derive_seed(seed, "route"))  # noqa: S311
        generate_route(graph, rng)
        store.save(seed, CaseState(day=1))
        case_scenarios[seed] = body.scenario
        escape_id = next(loc.id for loc in graph.locations if loc.escape)
        locations = [
            LocationOut(id=loc.id, name=loc.name)
            for loc in graph.locations
            if not loc.escape
        ]
        connections = [
            ConnectionOut.model_validate({"from": c.from_, "to": c.to})
            for c in graph.connections
            if c.to != escape_id
        ]
        return CreateCaseResponse(
            case_id=seed, locations=locations, connections=connections
        )

    @app.get("/cases/{case_id}")
    def get_case(case_id: str) -> CaseResponse:
        state = store.load(case_id)
        if state is None:
            raise HTTPException(status_code=404)
        route = _reconstruct_route(case_id, case_scenarios[case_id])
        return CaseResponse(
            day=state.day, fugitive_location=fugitive_location(route, state)
        )

    @app.post("/cases/{case_id}/advance")
    def advance_case(case_id: str) -> CaseResponse:
        state = store.load(case_id)
        if state is None:
            raise HTTPException(status_code=404)
        route = _reconstruct_route(case_id, case_scenarios[case_id])
        if has_escaped(route, state):
            raise HTTPException(status_code=409, detail="trail_gone_cold")
        new_state = advance_clock(state)
        store.save(case_id, new_state)
        return CaseResponse(
            day=new_state.day,
            fugitive_location=fugitive_location(route, new_state),
        )

    return app
