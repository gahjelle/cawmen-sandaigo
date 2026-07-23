"""Clues: the structured, language-free freshness facts an Interview yields.

An Interview at a Location returns a `Clue` reporting *when* the fugitive was last
there, never *where* they went next. The freshness gate — a `Sighting` only when the
fugitive actually passed through — is what makes the mechanic skillful (see issue #11).
The Clue is pure data with no language; rendering it into prose is a shell concern
(ADR-0008).
"""

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Sighting:
    """The fugitive passed through this Location `days_ago` days ago.

    Always `days_ago >= 1`: `days_ago == 0` would mean co-location, which is a win
    rather than a clue. `route[0]` (the detective's origin) is a valid, stale sighting.
    """

    days_ago: int


@dataclass(frozen=True, kw_only=True)
class ColdTrail:
    """No usable trace here — the fugitive was never here or has not yet reached it.

    One undifferentiated fact covers both cases so the clue leaks no future knowledge.
    """


type Clue = Sighting | ColdTrail
