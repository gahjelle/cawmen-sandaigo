# Store seed in CaseState

Status: superseded

> **Superseded by `04-detective-moves-playable-blind-loop.md`**, which folds this into the
> broader `CaseState` reshape (adds `detective_location` and `status` alongside `seed`, and
> makes `case_id` a distinct UUID). Kept for history; do not implement separately.

## Context

In Stage 0, `case_id` and `seed` are the same string — the user-supplied (or randomly
generated) seed is used directly as the case identifier. `_reconstruct_route` relies on
this by passing `case_id` to `derive_seed(..., "route")`.

When persistence is introduced, `case_id` will become a stable identifier (e.g. a
database row ID) that is independent of the user-supplied seed. At that point,
`_reconstruct_route` will silently generate routes from the wrong value — routes will
still be reproducible, just not the intended ones.

## What to do

Add `seed: str` to `CaseState` and persist it alongside the rest of the case state.
Update `_reconstruct_route` (and any other callers of `derive_seed`) to read `seed` from
the stored state rather than forwarding `case_id`.

## Acceptance criteria

- `CaseState` carries a `seed` field
- `_reconstruct_route` derives the RNG from `state.seed`, not `case_id`
- All existing tests pass; route reproducibility is unchanged
- `case_id` and `seed` can diverge without affecting route generation

## Last step

Write an article stub under `articles/01-<stage-name>/seed-in-case-state.md` summarising
the change and why `case_id` and `seed` were separated.
