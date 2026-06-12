"""The `StateStore` port: where Case state is persisted.

In-memory now; a database implementation slots in at Stage 8 (ADR-0008) without the
pure core changing.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from cawmen_backend.core.chase import CaseState


@dataclass(frozen=True)
class CaseRecord:
    """A persisted Case: its mutable core state plus the Scenario it belongs to."""

    state: CaseState
    scenario: str


class StateStore(Protocol):
    """Port for loading and saving a CaseRecord by Case identifier."""

    def load(self, case_id: str) -> CaseRecord | None:
        """Return the stored record for `case_id`, or `None` if unknown."""

    def save(self, case_id: str, record: CaseRecord) -> None:
        """Persist `record` against `case_id`."""


class InMemoryStateStore:
    """A `StateStore` backed by a process-local dict (fixed-seed determinism)."""

    def __init__(self) -> None:
        """Start with no stored Cases."""
        self._records: dict[str, CaseRecord] = {}

    def load(self, case_id: str) -> CaseRecord | None:
        """Return the stored record for `case_id`, or `None` if unknown."""
        return self._records.get(case_id)

    def save(self, case_id: str, record: CaseRecord) -> None:
        """Persist `record` against `case_id`."""
        self._records[case_id] = record
