"""Pure-core chase mechanics: the fugitive moving along its Fugitive Route."""

from cawmen_backend.core.chase import (
    CaseState,
    FugitiveRoute,
    advance_clock,
    fugitive_location,
    has_escaped,
)


def test_fugitive_starts_at_the_first_location_on_day_one() -> None:
    """The fugitive begins its Route at the first Location on day one."""
    route = FugitiveRoute(locations=("paris", "berlin", "escape"))
    state = CaseState(day=1)

    assert fugitive_location(route, state) == "paris"


def test_advancing_the_clock_moves_the_fugitive_to_the_next_location() -> None:
    """Advancing the In-Game Clock steps the fugitive to the next Location."""
    route = FugitiveRoute(locations=("paris", "berlin", "escape"))
    state = CaseState(day=1)

    advanced = advance_clock(state)

    assert advanced.day == 2
    assert fugitive_location(route, advanced) == "berlin"


def test_fugitive_has_not_escaped_while_still_on_a_reachable_location() -> None:
    """The fugitive has not escaped while still on a reachable Location."""
    route = FugitiveRoute(locations=("paris", "berlin", "escape"))

    assert not has_escaped(route, CaseState(day=2))


def test_fugitive_has_escaped_upon_reaching_the_escape_location() -> None:
    """Reaching the final Location is the Escape Location: the trail goes cold."""
    route = FugitiveRoute(locations=("paris", "berlin", "escape"))

    assert has_escaped(route, CaseState(day=3))
