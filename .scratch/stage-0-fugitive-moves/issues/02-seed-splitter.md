# Implement Seed Splitter (ADR-0010)

Status: ready-for-agent

Add `derive_seed(case_seed: str, purpose: str) -> str` to the backend pure core. This
is the foundation for all randomized Case generation — see ADR-0010.

## Implementation

```python
import hashlib

def derive_seed(case_seed: str, purpose: str) -> str:
    return hashlib.sha256(f"{case_seed}:{purpose}".encode()).hexdigest()
```

Lives in `backend/src/cawmen_backend/core/` (pure, no I/O).

## Acceptance criteria

- Same inputs always produce the same output (determinism)
- Different purposes produce different outputs for the same seed (independence)
- Unit tests cover both properties with a fixed seed
- Functions that consume randomness accept `random.Random` directly — the splitter is
  only called at the boundary where a `random.Random` is constructed

## Last step

Write an article stub in `articles/00-the-fugitive-moves/` per `docs/agents/articles.md`.
