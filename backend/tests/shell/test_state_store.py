"""The in-memory StateStore port implementation (ADR-0008; DB arrives at Stage 8)."""

from cawmen_backend.core.chase import CaseState
from cawmen_backend.shell.state_store import CaseRecord, InMemoryStateStore


def test_saved_case_record_can_be_loaded_back() -> None:
    """A CaseRecord saved under a Case id is returned verbatim on load."""
    store = InMemoryStateStore()
    state = CaseState(day=3, seed="s", detective_location="paris", status="in_progress")
    record = CaseRecord(state=state, scenario="minimal")

    store.save("case-1", record)

    assert store.load("case-1") == record


def test_loading_an_unknown_case_returns_none() -> None:
    """Loading an unknown Case id yields None rather than raising."""
    store = InMemoryStateStore()

    assert store.load("missing") is None
