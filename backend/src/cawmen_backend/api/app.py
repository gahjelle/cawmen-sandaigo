"""The FastAPI application factory and its routes."""

import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any

from fastapi import FastAPI, HTTPException
from pydantic import Field

from cawmen_backend.core.chase import (
    CaseOverError,
    CaseState,
    IllegalMoveError,
    apply_move,
)
from cawmen_backend.core.route import build_route
from cawmen_backend.models import FrozenModel
from cawmen_backend.shell.scenario import load_location_graph
from cawmen_backend.shell.state_store import CaseRecord, InMemoryStateStore

if TYPE_CHECKING:
    from cawmen_backend.core.location import LocationGraph


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
    neighbors: list[str] = Field(default_factory=list)


class CreateCaseResponse(FrozenModel):
    """Response for POST /cases."""

    case_id: str
    detective_location: str
    locations: list[LocationOut]


class CaseResponse(FrozenModel):
    """Blind in-progress response for GET /cases/{id} and POST /cases/{id}/move."""

    day: int
    detective_location: str
    status: str


class TerminalCaseResponse(FrozenModel):
    """Terminal response for POST /cases/{id}/move when the case is over."""

    day: int
    detective_location: str
    status: str
    fugitive_route: list[str]


class MoveRequest(FrozenModel):
    """Body for POST /cases/{id}/move."""

    target: str


class IllegalMoveErrorBody(FrozenModel):
    """400 body returned for non-adjacent / self / unknown move targets."""

    detail: str = "illegal_move"


class CaseOverErrorBody(FrozenModel):
    """409 body returned when the Case is already terminal."""

    detail: str = "case_over"


def _load_graph(scenarios_dir: Path, scenario: str) -> LocationGraph:
    """Load the Location Graph for `scenario` from the scenarios directory."""
    return load_location_graph(scenarios_dir / scenario / "graph.toml")


def create_app(scenarios_dir: Path = Path("scenarios")) -> FastAPI:
    """Build the FastAPI app exposing the Cawmen Sandaigo REST API."""
    app = FastAPI(title="Cawmen Sandaigo", version="0.0.0")
    store = InMemoryStateStore()

    @app.get("/health")
    def health() -> HealthResponse:
        """Report backend liveness."""
        return HealthResponse(status="ok")

    @app.post("/cases")
    def create_case(body: CreateCaseRequest) -> CreateCaseResponse:
        """Start a new Case: seed the fugitive Route and return the opening state."""
        seed = body.seed or str(uuid.uuid4())
        case_id = str(uuid.uuid4())
        graph = _load_graph(scenarios_dir, body.scenario)
        route = build_route(graph, seed)
        detective_start = route.locations[0]

        store.save(
            case_id,
            CaseRecord(
                state=CaseState(
                    day=1,
                    seed=seed,
                    detective_location=detective_start,
                    status="in_progress",
                ),
                scenario=body.scenario,
            ),
        )

        locations = [
            LocationOut(
                id=loc.id,
                name=loc.name,
                neighbors=[n for n in graph.neighbors(loc.id) if n != "escape"],
            )
            for loc in graph.locations
            if not loc.escape
        ]
        return CreateCaseResponse(
            case_id=case_id,
            detective_location=detective_start,
            locations=locations,
        )

    @app.get("/cases/{case_id}")
    def get_case(case_id: str) -> CaseResponse:
        """Return the blind in-progress state for `case_id`."""
        record = store.load(case_id)
        if record is None:
            raise HTTPException(status_code=404)
        return CaseResponse(
            day=record.state.day,
            detective_location=record.state.detective_location,
            status=record.state.status,
        )

    _move_responses: dict[int | str, dict[str, Any]] = {
        400: {"model": IllegalMoveErrorBody, "description": "Illegal move target"},
        409: {"model": CaseOverErrorBody, "description": "Case already finished"},
    }

    @app.post("/cases/{case_id}/move", responses=_move_responses)
    def move_case(
        case_id: str, body: MoveRequest
    ) -> CaseResponse | TerminalCaseResponse:
        """Apply a detective Move to `case_id`, returning the new or terminal state."""
        record = store.load(case_id)
        if record is None:
            raise HTTPException(status_code=404)

        graph = _load_graph(scenarios_dir, record.scenario)
        try:
            new_state, outcome = apply_move(graph, record.state, target=body.target)
        except CaseOverError as exc:
            raise HTTPException(status_code=409, detail="case_over") from exc
        except IllegalMoveError as exc:
            raise HTTPException(status_code=400, detail="illegal_move") from exc

        store.save(case_id, CaseRecord(state=new_state, scenario=record.scenario))

        if outcome in {"won", "lost"}:
            route = build_route(graph, new_state.seed)
            return TerminalCaseResponse(
                day=new_state.day,
                detective_location=new_state.detective_location,
                status=outcome,
                fugitive_route=route.locations,
            )

        return CaseResponse(
            day=new_state.day,
            detective_location=new_state.detective_location,
            status=outcome,
        )

    return app
