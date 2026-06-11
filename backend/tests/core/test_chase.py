"""Pure-core chase mechanics: CaseState, fugitive movement, and apply_move."""

import pytest

from cawmen_backend.core.chase import (
    CaseOverError,
    CaseState,
    FugitiveRoute,
    IllegalMoveError,
    Status,
    advance_clock,
    apply_move,
    fugitive_location,
    has_escaped,
)
from cawmen_backend.core.location import LocationGraph

# ---------------------------------------------------------------------------
# Route structure: route[0] = detective origin; route[day] = fugitive on day d
# ---------------------------------------------------------------------------

# A minimal route: origin → paris → berlin → escape
# - Detective starts at "origin" (route[0])
# - Fugitive on day 1 is at "paris" (route[1])
# - Fugitive on day 2 is at "berlin" (route[2])
# - Fugitive escapes on day 3 (route[3] = "escape")
_ROUTE = FugitiveRoute(locations=["origin", "paris", "berlin", "escape"])


def _state(
    *,
    day: int = 1,
    detective_location: str = "origin",
    status: Status = "in_progress",
    seed: str = "seed",
) -> CaseState:
    return CaseState(
        day=day,
        seed=seed,
        detective_location=detective_location,
        status=status,
    )


# ---------------------------------------------------------------------------
# CaseState fields
# ---------------------------------------------------------------------------


def test_case_state_carries_seed_detective_location_and_status() -> None:
    """CaseState holds seed, detective_location, and status alongside day."""
    state = CaseState(
        day=1, seed="abc", detective_location="origin", status="in_progress"
    )

    assert state.day == 1
    assert state.seed == "abc"
    assert state.detective_location == "origin"
    assert state.status == "in_progress"


# ---------------------------------------------------------------------------
# Fugitive location indexing: route[day] (day 1 → index 1)
# ---------------------------------------------------------------------------


def test_fugitive_starts_at_route_index_one_on_day_one() -> None:
    """On day 1 the fugitive is at route[1]; route[0] is the detective's origin."""
    state = _state(day=1)

    assert fugitive_location(_ROUTE, state) == "paris"


def test_advancing_the_clock_moves_the_fugitive_to_the_next_location() -> None:
    """Advancing the In-Game Clock steps the fugitive forward one route position."""
    state = _state(day=1)

    advanced = advance_clock(state)

    assert advanced.day == 2
    assert fugitive_location(_ROUTE, advanced) == "berlin"


def test_fugitive_has_not_escaped_while_still_on_a_reachable_location() -> None:
    """Day 2 is still within the route; the fugitive has not escaped."""
    assert not has_escaped(_ROUTE, _state(day=2))


def test_fugitive_has_escaped_upon_reaching_the_escape_location() -> None:
    """Day 3 exhausts the non-escape positions; the trail goes cold."""
    assert has_escaped(_ROUTE, _state(day=3))


# ---------------------------------------------------------------------------
# apply_move - legal move mechanics
# ---------------------------------------------------------------------------

# A tiny graph: origin ↔ paris ↔ berlin ↔ escape
# paris is the fugitive's day-1 spot; origin is the detective's start.
_GRAPH = LocationGraph(
    name="test",
    locations=[],
    connections=[["origin", "paris"], ["paris", "berlin"], ["berlin", "escape"]],
)

# seed "s" with purpose "route" happens to generate the _ROUTE above in tests;
# but apply_move is driven by graph + state alone in the core. We pass a
# pre-built route indirectly: tests use a graph + seed whose derived route
# matches _ROUTE.  For now we invoke apply_move via a helper that swaps in
# a known route by monkeypatching generate_route in each test.


def test_apply_move_relocates_detective_and_advances_day(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A legal move puts the detective at the target and increments the day."""
    monkeypatch.setattr("cawmen_backend.core.chase.generate_route", lambda *_: _ROUTE)
    state = _state(day=1, detective_location="origin")

    new_state, outcome = apply_move(_GRAPH, state, "paris")

    assert new_state.detective_location == "paris"
    assert new_state.day == 2
    assert outcome == "in_progress"
    assert new_state.status == "in_progress"


def test_apply_move_wins_when_detective_catches_fugitive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Detective co-located with fugitive after both move yields 'won'."""
    # After move on day 2: detective → berlin, fugitive → route[3] = "escape"?
    # No, let's set day=1, detective moves to berlin.
    # After move: day becomes 2, fugitive moves to route[2] = "berlin".
    # Detective is at berlin = fugitive → won.
    monkeypatch.setattr("cawmen_backend.core.chase.generate_route", lambda *_: _ROUTE)
    state = _state(day=1, detective_location="paris")

    new_state, outcome = apply_move(_GRAPH, state, "berlin")

    assert outcome == "won"
    assert new_state.status == "won"
    assert new_state.detective_location == "berlin"


def test_apply_move_does_not_win_when_stepping_onto_location_fugitive_is_leaving(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Stepping onto the location the fugitive is departing is a miss (not a win)."""
    # Day 1: fugitive at route[1]="paris". Detective at origin moves to paris.
    # After move: day=2, fugitive moves to route[2]="berlin".
    # Detective is at "paris", fugitive at "berlin" → no co-location → in_progress.
    monkeypatch.setattr("cawmen_backend.core.chase.generate_route", lambda *_: _ROUTE)
    state = _state(day=1, detective_location="origin")

    new_state, outcome = apply_move(_GRAPH, state, "paris")

    assert outcome == "in_progress"
    assert new_state.detective_location == "paris"


def test_apply_move_loses_when_fugitive_reaches_escape(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When the fugitive's next position is the escape location the case is lost."""
    # Day 2: fugitive at route[2]="berlin". Detective at paris moves to berlin.
    # After move: day=3, fugitive at route[3]="escape" → lost.
    # But detective is also at "berlin" ≠ "escape" → lost (not won).
    # Wait: after move day→3, fugitive at route[3]="escape". has_escaped → True.
    # But we need to check: is detective at "escape"? No → lost.
    monkeypatch.setattr("cawmen_backend.core.chase.generate_route", lambda *_: _ROUTE)
    state = _state(day=2, detective_location="paris")

    new_state, outcome = apply_move(_GRAPH, state, "berlin")

    assert outcome == "lost"
    assert new_state.status == "lost"


# ---------------------------------------------------------------------------
# apply_move - error cases
# ---------------------------------------------------------------------------


def test_apply_move_raises_on_non_adjacent_target(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Moving to a non-adjacent location raises IllegalMoveError."""
    monkeypatch.setattr("cawmen_backend.core.chase.generate_route", lambda *_: _ROUTE)
    state = _state(day=1, detective_location="origin")

    with pytest.raises(IllegalMoveError):
        apply_move(_GRAPH, state, "berlin")


def test_apply_move_raises_on_self_move(monkeypatch: pytest.MonkeyPatch) -> None:
    """Moving to the current location raises IllegalMoveError."""
    monkeypatch.setattr("cawmen_backend.core.chase.generate_route", lambda *_: _ROUTE)
    state = _state(day=1, detective_location="origin")

    with pytest.raises(IllegalMoveError):
        apply_move(_GRAPH, state, "origin")


def test_apply_move_raises_on_unknown_location(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Moving to an unknown location raises IllegalMoveError."""
    monkeypatch.setattr("cawmen_backend.core.chase.generate_route", lambda *_: _ROUTE)
    state = _state(day=1, detective_location="origin")

    with pytest.raises(IllegalMoveError):
        apply_move(_GRAPH, state, "tokyo")


def test_apply_move_raises_on_terminal_case(monkeypatch: pytest.MonkeyPatch) -> None:
    """Moving on a won or lost case raises CaseOverError."""
    monkeypatch.setattr("cawmen_backend.core.chase.generate_route", lambda *_: _ROUTE)
    state = _state(day=1, detective_location="origin", status="won")

    with pytest.raises(CaseOverError):
        apply_move(_GRAPH, state, "paris")
