"""The `TextProvider` port: turns the core's structured facts into prose.

The pure core never holds language; rendering text in the player's Language Preference
is entirely a shell concern (ADR-0008). Templated now, AI at Stage 5.
"""

from typing import ClassVar, Protocol


class TextProvider(Protocol):
    """Port rendering structured, language-free facts into Language-Preference prose."""

    def clock(self, *, day: int, language: str) -> str:
        """Render the In-Game Clock for the given day."""


class TemplatedTextProvider:
    """A `TextProvider` backed by per-language templates (no AI)."""

    _DAY_LABELS: ClassVar[dict[str, str]] = {"en": "Day", "no": "Dag"}

    def clock(self, *, day: int, language: str) -> str:
        """Render the In-Game Clock for the given day, falling back to English."""
        label = self._DAY_LABELS.get(language, self._DAY_LABELS["en"])
        return f"{label} {day}"
