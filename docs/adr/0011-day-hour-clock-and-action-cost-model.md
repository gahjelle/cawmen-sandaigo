# Day + Hour Clock and Action-Cost Model

The In-Game Clock tracks both **day** and **hour** (e.g. "Monday 14:00"). The fugitive moves once per **day**, overnight — it occupies exactly one Location for the whole of each day, so the fugitive's position stays a pure function of the day. The detective, by contrast, acts in **hours**: each action carries an Action Cost (Move scales with travel distance, Interview costs roughly an hour). When the day's hours are exhausted — including a fixed block reserved for the detective to rest — the clock rolls to the next day and the fugitive relocates.

This asymmetry is the deliberate engine of the Case's tension. Early on, the detective must spend many hours gathering Clues, which burns days and lets the fugitive pull ahead. Later, a well-informed detective spends fewer hours per decision and can travel faster, closing the gap. The hidden deadline of [ADR-0002](./0002-hidden-deadline-via-escape-location.md) is felt through this economy rather than a countdown.

## Staging

The hour dimension is **not implemented at Stage 1**. Stage 1 has a single action (Move) and the fugitive moves daily, so an hour budget has nothing to vary against and nothing testable to assert. Stage 1 therefore runs a **day-only clock**: one Move = one overnight day-advance, after which win/lose is judged. This is a deliberate floor, not an oversight.

The hour dimension arrives with the **second time-consuming action** (Stage 2's Interview), which is the first point where competing Action Costs become observable and testable. Forced rest and distance-scaled Move costs land in the same era. Adding the hour component later is an additive, localized change to the clock transition and the Case response — unlike seed-threading ([ADR-0001](./0001-case-seed-for-reproducibility.md)), it carries no pervasive retrofit, so there is no reason to build it speculatively now.

## Consequences

- Stage 1 state and API carry only `day`; the `hour` component is introduced at Stage 2.
- The fugitive's position remains a pure function of the day across all stages, so the core's chase logic is unaffected by the later hour split.
- The core stays AI-free and deterministic: Action Costs are structured data resolved in the functional core ([ADR-0008](./0008-functional-core-imperative-shell.md)), not narrative.
