"""The chase: where the fugitive is as the In-Game Clock advances."""

from dataclasses import dataclass

type LocationId = str


@dataclass(frozen=True)
class FugitiveRoute:
    """The fugitive's secret timed path; the final Location is the Escape Location."""

    locations: list[LocationId]


@dataclass(frozen=True)
class CaseState:
    """The mutable facts of a Case, advanced by the In-Game Clock (1-based day)."""

    day: int


def fugitive_location(route: FugitiveRoute, state: CaseState) -> LocationId:
    """Return the Location the fugitive occupies on the clock's current day."""
    return route.locations[state.day - 1]


def advance_clock(state: CaseState) -> CaseState:
    """Advance the In-Game Clock by one day, returning the new Case state."""
    return CaseState(day=state.day + 1)


def has_escaped(route: FugitiveRoute, state: CaseState) -> bool:
    """Report whether the fugitive has reached the Escape Location (trail gone cold)."""
    return state.day >= len(route.locations)
