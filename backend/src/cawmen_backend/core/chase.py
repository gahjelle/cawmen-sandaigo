"""The chase: CaseState, route indexing, and the apply_move transition."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from cawmen_backend.core.route import FugitiveRoute, build_route

if TYPE_CHECKING:
    from cawmen_backend.core.location import LocationGraph

type LocationId = str
type Status = Literal["in_progress", "won", "lost"]


class IllegalMoveError(ValueError):
    """Raised when the target is non-adjacent, identical to current, or unknown."""


class CaseOverError(ValueError):
    """Raised when a move is attempted on an already-terminal Case."""


@dataclass(frozen=True, kw_only=True)
class CaseState:
    """The mutable facts of a Case, advanced by the In-Game Clock (1-based day)."""

    day: int
    seed: str
    detective_location: LocationId
    status: Status


def fugitive_location(route: FugitiveRoute, state: CaseState) -> LocationId:
    """Return the Location the fugitive occupies on the clock's current day.

    Uses 1-indexed access: route[day] so that route[0] is reserved for the
    detective's origin and the fugitive has already fled when the detective arrives.
    """
    return route.locations[state.day]


def advance_clock(state: CaseState) -> CaseState:
    """Advance the In-Game Clock by one day, returning the new Case state."""
    return CaseState(
        day=state.day + 1,
        seed=state.seed,
        detective_location=state.detective_location,
        status=state.status,
    )


def has_escaped(route: FugitiveRoute, state: CaseState) -> bool:
    """Report whether the fugitive has reached the Escape Location (trail gone cold)."""
    return state.day >= len(route.locations) - 1


def apply_move(
    graph: LocationGraph, state: CaseState, *, target: LocationId
) -> tuple[CaseState, Status]:
    """Apply one detective Move, advance the clock, relocate the fugitive, then judge.

    Resolution order (per ADR-0008):
      1. Validate the move (terminal check, then adjacency).
      2. Detective relocates to `target`.
      3. Clock advances one day.
      4. Fugitive relocates to route[new_day].
      5. Judge: co-location → won; escape → lost; otherwise in_progress.

    Raises:
        CaseOverError: if the Case is already terminal.
        IllegalMoveError: if `target` is unknown, equal to current location, or
            not adjacent to the detective's current location.

    """
    if state.status != "in_progress":
        raise CaseOverError(state.status)

    if target not in graph.neighbors(state.detective_location):
        raise IllegalMoveError(target)

    route = build_route(graph, state.seed)

    new_day = state.day + 1

    if new_day >= len(route.locations) - 1:
        return (
            CaseState(
                day=new_day,
                seed=state.seed,
                detective_location=target,
                status="lost",
            ),
            "lost",
        )

    fug_loc = route.locations[new_day]
    if target == fug_loc:
        return (
            CaseState(
                day=new_day,
                seed=state.seed,
                detective_location=target,
                status="won",
            ),
            "won",
        )

    return (
        CaseState(
            day=new_day,
            seed=state.seed,
            detective_location=target,
            status="in_progress",
        ),
        "in_progress",
    )
