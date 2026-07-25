"""A small hand-rolled, typed httpx client for the backend REST API.

Deliberately not generated from OpenAPI and not a shared schema package (ADR-0009): the
TUI consumes the same public contract any client would, with contract tests guarding the
client's expectations against the live schema.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import httpx

_HTTP_CASE_OVER = 409
_HTTP_ILLEGAL_MOVE = 400


@dataclass(frozen=True, kw_only=True)
class Health:
    """The backend's reported liveness."""

    status: str


@dataclass(frozen=True, kw_only=True)
class Location:
    """A named location in the case's location graph (Escape Location excluded)."""

    id: str
    name: str
    neighbors: list[str] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True)
class CaseCreated:
    """Returned by create_case: the new case id, detective start, and location graph."""

    case_id: str
    detective_location: str
    locations: list[Location]


@dataclass(frozen=True, kw_only=True)
class CaseState:
    """Blind in-progress state: rendered clock, detective position, status.

    The clock arrives as backend-rendered prose (ADR-0008) so the thin client never
    builds the string itself; the fugitive is hidden.
    """

    clock: str
    detective_location: str
    status: str


@dataclass(frozen=True, kw_only=True)
class TerminalState:
    """Terminal case state: rendered clock, won/lost status, and the fugitive route."""

    clock: str
    detective_location: str
    status: str
    fugitive_route: list[str]


@dataclass(frozen=True, kw_only=True)
class CaseOver:
    """Returned (not raised) when the server signals the case is already finished."""


@dataclass(frozen=True, kw_only=True)
class IllegalMove:
    """Returned (not raised) when the server rejects an illegal move target (400)."""


class AbstractClient(Protocol):
    """Port: any object that can talk to the backend."""

    async def health(self) -> Health:
        """Fetch the backend's health status."""

    async def create_case(self, scenario: str, seed: str | None = None) -> CaseCreated:
        """POST /cases — returns case_id, detective_location, and location graph."""

    async def get_case(self, case_id: str) -> CaseState:
        """GET /cases/{case_id} — returns blind state (no fugitive location)."""

    async def move_case(
        self, case_id: str, target: str
    ) -> CaseState | TerminalState | CaseOver | IllegalMove:
        """POST /cases/{case_id}/move — new state, terminal, or error sentinel."""


class BackendClient:
    """Typed REST client over an injected httpx `AsyncClient` (real wire or ASGI)."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        """Wrap the given httpx client; the caller owns its lifecycle."""
        self._http = http

    async def health(self) -> Health:
        """Fetch the backend's health status."""
        response = await self._http.get("/health")
        response.raise_for_status()
        return Health(status=response.json()["status"])

    async def create_case(self, scenario: str, seed: str | None = None) -> CaseCreated:
        """POST /cases — returns case_id, detective_location, and location graph."""
        body: dict[str, str] = {"scenario": scenario}
        if seed is not None:
            body["seed"] = seed
        response = await self._http.post("/cases", json=body)
        response.raise_for_status()
        data = response.json()
        locations = [
            Location(id=loc["id"], name=loc["name"], neighbors=loc["neighbors"])
            for loc in data["locations"]
        ]
        return CaseCreated(
            case_id=data["case_id"],
            detective_location=data["detective_location"],
            locations=locations,
        )

    async def get_case(self, case_id: str) -> CaseState:
        """GET /cases/{case_id} — returns blind state (no fugitive location)."""
        response = await self._http.get(f"/cases/{case_id}")
        response.raise_for_status()
        data = response.json()
        return CaseState(
            clock=data["clock"],
            detective_location=data["detective_location"],
            status=data["status"],
        )

    async def move_case(
        self, case_id: str, target: str
    ) -> CaseState | TerminalState | CaseOver | IllegalMove:
        """POST /cases/{case_id}/move — new state, terminal, or error sentinel."""
        response = await self._http.post(
            f"/cases/{case_id}/move", json={"target": target}
        )
        if response.status_code == _HTTP_CASE_OVER:
            return CaseOver()
        if response.status_code == _HTTP_ILLEGAL_MOVE:
            return IllegalMove()
        response.raise_for_status()
        data = response.json()
        if "fugitive_route" in data:
            return TerminalState(
                clock=data["clock"],
                detective_location=data["detective_location"],
                status=data["status"],
                fugitive_route=data["fugitive_route"],
            )
        return CaseState(
            clock=data["clock"],
            detective_location=data["detective_location"],
            status=data["status"],
        )
