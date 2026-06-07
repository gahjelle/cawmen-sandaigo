"""Seed splitter: derive independent sub-seeds from a Case Seed (ADR-0010)."""

import hashlib


def derive_seed(case_seed: str, purpose: str) -> str:
    """Derive a deterministic sub-seed for a named purpose from a Case Seed."""
    return hashlib.sha256(f"{case_seed}:{purpose}".encode()).hexdigest()
