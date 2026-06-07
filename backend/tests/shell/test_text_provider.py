"""The templated TextProvider: structured facts rendered in a Language Preference.

Templated now; an AI provider slots in at Stage 5 (ADR-0008) without the core changing.
"""

from cawmen_backend.shell.text_provider import TemplatedTextProvider


def test_clock_renders_in_english() -> None:
    """The clock renders with the English label by default."""
    provider = TemplatedTextProvider()

    assert provider.clock(day=3, language="en") == "Day 3"


def test_clock_renders_in_the_requested_language() -> None:
    """The clock honours the requested Language Preference."""
    provider = TemplatedTextProvider()

    assert provider.clock(day=3, language="no") == "Dag 3"


def test_unknown_language_falls_back_to_english() -> None:
    """An unsupported Language Preference falls back to English."""
    provider = TemplatedTextProvider()

    assert provider.clock(day=1, language="xx") == "Day 1"
