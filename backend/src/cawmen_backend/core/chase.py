"""The chase: CaseState, the two-tier In-Game Clock, and the apply_move transition."""

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Literal

from cawmen_backend.core.route import FugitiveRoute, build_route

if TYPE_CHECKING:
    from cawmen_backend.core.location import LocationGraph

type LocationId = str
type Status = Literal["in_progress", "won", "lost"]

# The two-tier clock (issue #8): a 16h waking day from 06:00 to the 22:00 rest
# block, after which an 8h overnight rest relocates the fugitive and rolls the day.
WAKING_START = 6
REST_START = 22
# Flat Stage-2 action costs in waking hours (distance-scaling stays deferred).
MOVE_COST = 8
INTERVIEW_COST = 1


class IllegalMoveError(ValueError):
    """Raised when the target is non-adjacent, identical to current, or unknown."""


class BudgetExhaustedError(ValueError):
    """Raised when an action cannot finish before the 22:00 rest block."""


class CaseOverError(ValueError):
    """Raised when a move is attempted on an already-terminal Case."""


@dataclass(frozen=True, kw_only=True)
class CaseState:
    """The mutable facts of a Case, advanced by the two-tier (day, hour) In-Game Clock.

    `day` is 1-based; `hour` is the 24-hour waking time, an int in [6, 22].
    """

    day: int
    hour: int
    seed: str
    detective_location: LocationId
    status: Status


def fugitive_location(route: FugitiveRoute, state: CaseState) -> LocationId:
    """Return the Location the fugitive occupies on the clock's current day.

    Uses 1-indexed access: route[day] so that route[0] is reserved for the
    detective's origin and the fugitive has already fled when the detective arrives.
    The fugitive holds this Location for the whole waking day, moving only overnight.
    """
    return route.locations[state.day]


def can_afford(state: CaseState, cost: int) -> bool:
    """Report whether a `cost`-hour action fits before the 22:00 rest block."""
    return state.hour + cost <= REST_START


def advance_clock(state: CaseState, *, cost: int) -> CaseState:
    """Advance the waking clock by `cost` hours, rolling into the next day at 22:00.

    Reaching the 22:00 rest block ends the waking day: the day increments (the fugitive
    relocates overnight, since its position is keyed on `day`) and the clock resets to
    06:00. Callers must gate the action with `can_afford` first.
    """
    new_hour = state.hour + cost
    if new_hour >= REST_START:
        return replace(state, day=state.day + 1, hour=WAKING_START)
    return replace(state, hour=new_hour)


def has_escaped(route: FugitiveRoute, state: CaseState) -> bool:
    """Report whether the fugitive has reached the Escape Location (trail gone cold)."""
    return state.day >= len(route.locations) - 1


def _judge(route: FugitiveRoute, state: CaseState) -> Status:
    """Judge a post-overnight state: escape loses, walking onto the fugitive wins."""
    if has_escaped(route, state):
        return "lost"
    if state.detective_location == route.locations[state.day]:
        return "won"
    return "in_progress"


def apply_move(
    graph: LocationGraph, state: CaseState, *, target: LocationId
) -> tuple[CaseState, Status]:
    """Apply one detective Move, spend its 8h, and judge the outcome.

    Because the fugitive holds their Location through the waking day (relocating only
    overnight), resolution is two-phase:

      1. Validate the move (terminal check, adjacency, then waking-hours budget).
      2. If `target` is the fugitive's current-day spot, catch them there and then —
         before the clock is spent.
      3. Otherwise spend the 8h of travel. Reaching 22:00 rolls into the next day,
         whose overnight relocation may walk the fugitive onto the detective (a
         stake-out win) or off the map (escape).

    Raises:
        CaseOverError: if the Case is already terminal.
        IllegalMoveError: if `target` is unknown, equal to current location, or
            not adjacent to the detective's current location.
        BudgetExhaustedError: if 8h of travel cannot finish before the 22:00 rest block.

    """
    if state.status != "in_progress":
        raise CaseOverError(state.status)

    if target not in graph.neighbors(state.detective_location):
        raise IllegalMoveError(target)

    if not can_afford(state, MOVE_COST):
        raise BudgetExhaustedError(state.hour)

    route = build_route(graph, state.seed)

    if target == route.locations[state.day]:
        caught = replace(
            state,
            detective_location=target,
            hour=state.hour + MOVE_COST,
            status="won",
        )
        return (caught, "won")

    advanced = advance_clock(replace(state, detective_location=target), cost=MOVE_COST)
    outcome = _judge(route, advanced)
    return (replace(advanced, status=outcome), outcome)
