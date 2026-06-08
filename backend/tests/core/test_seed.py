"""Tests for the seed splitter."""

from cawmen_backend.core.seed import derive_seed

SEED = "case-abc-123"


def test_same_inputs_produce_same_output() -> None:
    """derive_seed is deterministic."""
    assert derive_seed(SEED, "route") == derive_seed(SEED, "route")


def test_different_purposes_produce_different_outputs() -> None:
    """Each purpose yields an independent sub-seed."""
    assert derive_seed(SEED, "route") != derive_seed(SEED, "suspects")


def test_known_output_is_stable() -> None:
    """Pin a fixed output so accidental algorithm changes are caught."""
    assert derive_seed(SEED, "route") == (
        "2057c4f73bd95737512d036e4abbb3de53f4660a147c7e96b78edea544adf87f"
    )
