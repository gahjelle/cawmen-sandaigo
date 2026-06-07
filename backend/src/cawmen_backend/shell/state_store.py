"""The StateStore port: where Case state is persisted.

In-memory now; a database implementation slots in at Stage 8 (ADR-0008) without the
pure core changing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from cawmen_backend.core.chase import CaseState


class StateStore(Protocol):
    """Port for loading and saving Case state by Case identifier."""

    def load(self, case_id: str) -> CaseState | None:
        """Return the stored state for ``case_id``, or ``None`` if unknown."""
        ...

    def save(self, case_id: str, state: CaseState) -> None:
        """Persist ``state`` against ``case_id``."""
        ...


class InMemoryStateStore:
    """A ``StateStore`` backed by a process-local dict (fixed seed determinism)."""

    def __init__(self) -> None:
        """Start with no stored Cases."""
        self._states: dict[str, CaseState] = {}

    def load(self, case_id: str) -> CaseState | None:
        """Return the stored state for ``case_id``, or ``None`` if unknown."""
        return self._states.get(case_id)

    def save(self, case_id: str, state: CaseState) -> None:
        """Persist ``state`` against ``case_id``."""
        self._states[case_id] = state
