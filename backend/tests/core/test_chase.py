"""Pure-core chase mechanics: the two-tier clock, fugitive movement, and apply_move."""

import pytest

from cawmen_backend.core.chase import (
    INTERVIEW_COST,
    MOVE_COST,
    BudgetExhaustedError,
    CaseOverError,
    CaseState,
    IllegalMoveError,
    Status,
    advance_clock,
    apply_move,
    can_afford,
    fugitive_location,
    has_escaped,
)
from cawmen_backend.core.location import LocationGraph
from cawmen_backend.core.route import FugitiveRoute

# ---------------------------------------------------------------------------
# Route structure: route[0] = detective origin; route[day] = fugitive on day d.
# The fugitive holds each spot for the whole waking day, relocating overnight.
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
    hour: int = 6,
    detective_location: str = "origin",
    status: Status = "in_progress",
    seed: str = "seed",
) -> CaseState:
    """Build a CaseState with sensible defaults, overriding only what a test needs."""
    return CaseState(
        day=day,
        hour=hour,
        seed=seed,
        detective_location=detective_location,
        status=status,
    )


# ---------------------------------------------------------------------------
# CaseState fields
# ---------------------------------------------------------------------------


def test_case_state_carries_the_two_tier_clock_seed_location_and_status() -> None:
    """CaseState holds day, hour, seed, detective_location, and status."""
    state = CaseState(
        day=1, hour=6, seed="abc", detective_location="origin", status="in_progress"
    )

    assert state.day == 1
    assert state.hour == 6
    assert state.seed == "abc"
    assert state.detective_location == "origin"
    assert state.status == "in_progress"


# ---------------------------------------------------------------------------
# Fugitive location indexing: route[day] (day 1 → index 1)
# ---------------------------------------------------------------------------


def test_fugitive_starts_at_route_index_one_on_day_one() -> None:
    """On day 1 the fugitive is at route[1]; route[0] is the detective's origin."""
    assert fugitive_location(_ROUTE, _state(day=1)) == "paris"


# ---------------------------------------------------------------------------
# The two-tier clock: hours accrue within a day, rolling over at 22:00
# ---------------------------------------------------------------------------


def test_advancing_within_the_waking_day_only_moves_the_hour() -> None:
    """A cost that finishes before 22:00 advances the hour and keeps the day."""
    advanced = advance_clock(_state(day=1, hour=6), cost=MOVE_COST)

    assert advanced.day == 1
    assert advanced.hour == 14


def test_reaching_the_rest_block_rolls_the_day_and_resets_to_morning() -> None:
    """Reaching 22:00 rolls the day over (fugitive relocates) and resets to 06:00."""
    advanced = advance_clock(_state(day=1, hour=14), cost=MOVE_COST)

    assert advanced.day == 2
    assert advanced.hour == 6
    assert fugitive_location(_ROUTE, advanced) == "berlin"


def test_an_interview_sized_hour_advances_the_clock_by_one() -> None:
    """A 1h interview cost nudges the clock forward within the waking day."""
    advanced = advance_clock(_state(day=1, hour=6), cost=INTERVIEW_COST)

    assert advanced.day == 1
    assert advanced.hour == 7


def test_can_afford_gates_actions_on_the_22_00_rest_block() -> None:
    """An action fits only when it finishes at or before 22:00."""
    assert can_afford(_state(hour=14), MOVE_COST)  # 14 + 8 == 22
    assert not can_afford(_state(hour=15), MOVE_COST)  # 15 + 8 == 23
    assert can_afford(_state(hour=21), INTERVIEW_COST)  # 21 + 1 == 22


# ---------------------------------------------------------------------------
# has_escaped
# ---------------------------------------------------------------------------


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

# Tests inject a known route by monkeypatching build_route in chase's namespace,
# keeping apply_move's logic testable without depending on specific seed behaviour.


def test_two_moves_fill_the_waking_day_and_relocate_the_fugitive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two 8h Moves reach the rest block, rolling the day and moving the fugitive."""
    # origin → berlin isn't adjacent, so use a wider route/graph where the detective
    # can miss on both hops. Fugitive: day 1 at "paris", day 2 at "berlin".
    route = FugitiveRoute(locations=["origin", "paris", "berlin", "oslo", "escape"])
    graph = LocationGraph(
        name="test",
        locations=[],
        connections=[
            ["origin", "rome"],
            ["rome", "madrid"],
            ["paris", "berlin"],
        ],
    )
    monkeypatch.setattr("cawmen_backend.core.chase.build_route", lambda *_: route)
    state = _state(day=1, hour=6, detective_location="origin")

    # Hop 1: origin → rome (miss, route[1] == "paris"), hour 6 → 14, day stays 1.
    after_first, first_outcome = apply_move(graph, state, target="rome")
    assert first_outcome == "in_progress"
    assert after_first.day == 1
    assert after_first.hour == 14

    # Hop 2: rome → madrid (miss), hour 14 → 22 → overnight → day 2, hour 6.
    after_second, second_outcome = apply_move(graph, after_first, target="madrid")
    assert second_outcome == "in_progress"
    assert after_second.day == 2
    assert after_second.hour == 6


def test_apply_move_wins_by_catching_the_stationary_fugitive_mid_day(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Stepping onto the fugitive's current-day spot catches them there and then."""
    # Day 1: fugitive at route[1] = "paris". Detective at origin moves to paris → won.
    monkeypatch.setattr("cawmen_backend.core.chase.build_route", lambda *_: _ROUTE)
    state = _state(day=1, hour=6, detective_location="origin")

    new_state, outcome = apply_move(_GRAPH, state, target="paris")

    assert outcome == "won"
    assert new_state.status == "won"
    assert new_state.detective_location == "paris"


def test_apply_move_wins_when_the_fugitive_flees_onto_a_staked_out_detective(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ending the day where the fugitive relocates overnight is a stake-out win."""
    # Fugitive: day 1 at "paris", day 2 at "berlin". Detective ends the day at berlin
    # on the second hop; overnight the fugitive relocates onto them → won.
    monkeypatch.setattr("cawmen_backend.core.chase.build_route", lambda *_: _ROUTE)
    state = _state(day=1, hour=14, detective_location="paris")

    new_state, outcome = apply_move(_GRAPH, state, target="berlin")

    assert outcome == "won"
    assert new_state.status == "won"
    assert new_state.day == 2
    assert new_state.detective_location == "berlin"


def test_apply_move_loses_when_the_fugitive_reaches_escape_overnight(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When the overnight roll takes the fugitive to Escape the case is lost."""
    # Day 2: fugitive is at route[2] = "berlin"; the detective misses (paris → origin).
    # Second hop: hour 14 → 22 → day 3, fugitive at route[3] = "escape" → lost.
    monkeypatch.setattr("cawmen_backend.core.chase.build_route", lambda *_: _ROUTE)
    state = _state(day=2, hour=14, detective_location="paris")

    new_state, outcome = apply_move(_GRAPH, state, target="origin")

    assert outcome == "lost"
    assert new_state.status == "lost"
    assert new_state.day == 3


# ---------------------------------------------------------------------------
# apply_move - error cases
# ---------------------------------------------------------------------------


def test_apply_move_raises_on_non_adjacent_target(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Moving to a non-adjacent location raises IllegalMoveError."""
    monkeypatch.setattr("cawmen_backend.core.chase.build_route", lambda *_: _ROUTE)
    state = _state(day=1, detective_location="origin")

    with pytest.raises(IllegalMoveError):
        apply_move(_GRAPH, state, target="berlin")


def test_apply_move_raises_on_self_move(monkeypatch: pytest.MonkeyPatch) -> None:
    """Moving to the current location raises IllegalMoveError."""
    monkeypatch.setattr("cawmen_backend.core.chase.build_route", lambda *_: _ROUTE)
    state = _state(day=1, detective_location="origin")

    with pytest.raises(IllegalMoveError):
        apply_move(_GRAPH, state, target="origin")


def test_apply_move_raises_on_unknown_location(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Moving to an unknown location raises IllegalMoveError."""
    monkeypatch.setattr("cawmen_backend.core.chase.build_route", lambda *_: _ROUTE)
    state = _state(day=1, detective_location="origin")

    with pytest.raises(IllegalMoveError):
        apply_move(_GRAPH, state, target="tokyo")


def test_apply_move_raises_when_travel_cannot_finish_before_the_rest_block(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A Move with too little of the waking day left raises BudgetExhaustedError."""
    monkeypatch.setattr("cawmen_backend.core.chase.build_route", lambda *_: _ROUTE)
    # hour 15: 15 + 8 == 23 > 22, so the 8h of travel would straddle the rest block.
    state = _state(day=1, hour=15, detective_location="origin")

    with pytest.raises(BudgetExhaustedError):
        apply_move(_GRAPH, state, target="paris")


def test_apply_move_raises_on_terminal_case(monkeypatch: pytest.MonkeyPatch) -> None:
    """Moving on a won or lost case raises CaseOverError."""
    monkeypatch.setattr("cawmen_backend.core.chase.build_route", lambda *_: _ROUTE)
    state = _state(day=1, detective_location="origin", status="won")

    with pytest.raises(CaseOverError):
        apply_move(_GRAPH, state, target="paris")
