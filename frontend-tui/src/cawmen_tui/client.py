"""A small hand-rolled, typed httpx client for the backend REST API.

Deliberately not generated from OpenAPI and not a shared schema package (ADR-0009): the
TUI consumes the same public contract any client would, with contract tests guarding the
client's expectations against the live schema.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx

_HTTP_TRAIL_GONE_COLD = 409


@dataclass(frozen=True)
class Health:
    """The backend's reported liveness."""

    status: str


@dataclass(frozen=True)
class Location:
    """A named location in the case's location graph (Escape Location excluded)."""

    id: str
    name: str


@dataclass(frozen=True)
class Connection:
    """A directed edge between two named locations."""

    from_: str
    to: str


@dataclass(frozen=True)
class CaseCreated:
    """Returned by create_case: the new case id and its location graph."""

    case_id: str
    locations: list[Location]
    connections: list[Connection]


@dataclass(frozen=True)
class CaseState:
    """Current state of a case: the day counter and the fugitive's location."""

    day: int
    fugitive_location: str


@dataclass(frozen=True)
class TrailGoneCold:
    """Returned (not raised) when the server signals the fugitive has escaped (409)."""


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
        """POST /cases — returns case_id and location graph."""
        body: dict[str, str] = {"scenario": scenario}
        if seed is not None:
            body["seed"] = seed
        response = await self._http.post("/cases", json=body)
        response.raise_for_status()
        data = response.json()
        locations = [
            Location(id=loc["id"], name=loc["name"]) for loc in data["locations"]
        ]
        connections = [
            Connection(from_=conn["from"], to=conn["to"])
            for conn in data["connections"]
        ]
        return CaseCreated(
            case_id=data["case_id"],
            locations=locations,
            connections=connections,
        )

    async def get_case(self, case_id: str) -> CaseState:
        """GET /cases/{case_id} — returns day and fugitive_location."""
        response = await self._http.get(f"/cases/{case_id}")
        response.raise_for_status()
        data = response.json()
        return CaseState(day=data["day"], fugitive_location=data["fugitive_location"])

    async def advance_case(self, case_id: str) -> CaseState | TrailGoneCold:
        """POST /cases/{case_id}/advance — new state, or TrailGoneCold on 409."""
        response = await self._http.post(f"/cases/{case_id}/advance")
        if response.status_code == _HTTP_TRAIL_GONE_COLD:
            return TrailGoneCold()
        response.raise_for_status()
        data = response.json()
        return CaseState(day=data["day"], fugitive_location=data["fugitive_location"])
