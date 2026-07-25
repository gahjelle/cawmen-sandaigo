"""The templated TextProvider: structured facts rendered in a Language Preference.

Templated now; an AI provider slots in at Stage 5 (ADR-0008) without the core changing.
"""

from cawmen_backend.core.clue import ColdTrail, Sighting
from cawmen_backend.shell.text_provider import TemplatedTextProvider


def test_clock_renders_the_day_and_hour_in_english() -> None:
    """The clock renders day and 24-hour waking time with the English label."""
    provider = TemplatedTextProvider()

    assert provider.clock(day=3, hour=14, language="en") == "Day 3, 14:00"


def test_clock_zero_pads_the_morning_hour() -> None:
    """The waking-day start reads as a zero-padded 06:00."""
    provider = TemplatedTextProvider()

    assert provider.clock(day=1, hour=6, language="en") == "Day 1, 06:00"


def test_clock_renders_in_the_requested_language() -> None:
    """The clock honours the requested Language Preference."""
    provider = TemplatedTextProvider()

    assert provider.clock(day=3, hour=14, language="no") == "Dag 3, 14:00"


def test_unknown_language_falls_back_to_english() -> None:
    """An unsupported Language Preference falls back to English."""
    provider = TemplatedTextProvider()

    assert provider.clock(day=1, hour=6, language="xx") == "Day 1, 06:00"


def test_sighting_names_the_freshness_not_the_direction() -> None:
    """A Sighting reports how long ago, never where the fugitive went next."""
    provider = TemplatedTextProvider()

    rendered = provider.clue(clue=Sighting(days_ago=2), language="en")

    assert rendered == "They passed through here 2 days ago."


def test_sighting_uses_the_singular_unit_for_one_day() -> None:
    """A one-day-old Sighting reads 'day', not 'days'."""
    provider = TemplatedTextProvider()

    assert provider.clue(clue=Sighting(days_ago=1), language="en") == (
        "They passed through here 1 day ago."
    )


def test_sighting_renders_in_the_requested_language() -> None:
    """A Sighting honours the requested Language Preference, plural included."""
    provider = TemplatedTextProvider()

    assert provider.clue(clue=Sighting(days_ago=3), language="no") == (
        "De var innom her for 3 dager siden."
    )
    assert provider.clue(clue=Sighting(days_ago=1), language="no") == (
        "De var innom her for 1 dag siden."
    )


def test_cold_trail_renders_in_each_language() -> None:
    """A ColdTrail renders as a language-appropriate 'no sign here' report."""
    provider = TemplatedTextProvider()

    assert provider.clue(clue=ColdTrail(), language="en") == (
        "No sign of them here — the trail is cold."
    )
    assert provider.clue(clue=ColdTrail(), language="no") == (
        "Ingen spor av dem her — sporet er kaldt."
    )


def test_clue_falls_back_to_english_for_an_unknown_language() -> None:
    """An unsupported Language Preference falls back to English for clues too."""
    provider = TemplatedTextProvider()

    assert provider.clue(clue=Sighting(days_ago=2), language="xx") == (
        "They passed through here 2 days ago."
    )
    assert provider.clue(clue=ColdTrail(), language="xx") == (
        "No sign of them here — the trail is cold."
    )
