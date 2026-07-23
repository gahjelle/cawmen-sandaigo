"""The `TextProvider` port: turns the core's structured facts into prose.

The pure core never holds language; rendering text in the player's Language Preference
is entirely a shell concern (ADR-0008). Templated now, AI at Stage 5.
"""

from typing import ClassVar, Protocol

from cawmen_backend.core.clue import Clue, ColdTrail, Sighting


class TextProvider(Protocol):
    """Port rendering structured, language-free facts into Language-Preference prose."""

    def clock(self, *, day: int, language: str) -> str:
        """Render the In-Game Clock for the given day."""

    def clue(self, *, clue: Clue, language: str) -> str:
        """Render an Interview Clue as a freshness report."""


class TemplatedTextProvider:
    """A `TextProvider` backed by per-language templates (no AI)."""

    _DAY_LABELS: ClassVar[dict[str, str]] = {"en": "Day", "no": "Dag"}

    # Per language: the (singular, plural) unit and the "{count} {unit}" sighting frame.
    _DAY_UNITS: ClassVar[dict[str, tuple[str, str]]] = {
        "en": ("day", "days"),
        "no": ("dag", "dager"),
    }
    _SIGHTING_TEMPLATES: ClassVar[dict[str, str]] = {
        "en": "They passed through here {count} {unit} ago.",
        "no": "De var innom her for {count} {unit} siden.",
    }
    _COLD_TRAIL: ClassVar[dict[str, str]] = {
        "en": "No sign of them here — the trail is cold.",
        "no": "Ingen spor av dem her — sporet er kaldt.",
    }

    def clock(self, *, day: int, language: str) -> str:
        """Render the In-Game Clock for the given day, falling back to English."""
        label = self._DAY_LABELS.get(language, self._DAY_LABELS["en"])
        return f"{label} {day}"

    def clue(self, *, clue: Clue, language: str) -> str:
        """Render an Interview Clue, falling back to English for an unknown language."""
        lang = language if language in self._SIGHTING_TEMPLATES else "en"
        match clue:
            case Sighting(days_ago=days_ago):
                singular, plural = self._DAY_UNITS[lang]
                unit = singular if days_ago == 1 else plural
                return self._SIGHTING_TEMPLATES[lang].format(count=days_ago, unit=unit)
            case ColdTrail():
                return self._COLD_TRAIL[lang]
