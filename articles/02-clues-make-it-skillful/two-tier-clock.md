# The two-tier clock and the discrete-budget rule

Stage 1 ran on a single-tier clock: one `day`, one Move, one fugitive relocation, all
in lockstep. The detective and the fugitive advanced together, so the chase could never
close — every hop the detective took, the fugitive took one too. That is fine for a
walking skeleton, but it is not a *game*: there is no way to gain ground, and no reason
to think before moving.

Stage 2 replaces that with a two-tier `(day, hour)` In-Game Clock, and the whole point
of the second tier is to let the detective act more often than the fugitive.

## What was built

`CaseState` gains an `hour` — a 24-hour waking time in `[6, 22]`. A day is a 16-hour
waking window from **06:00** to a **22:00** rest block, followed by an 8-hour overnight
rest. The fugitive holds their Location for the *whole* waking day and relocates only
overnight, when the day rolls over. The detective, meanwhile, spends waking hours:

- a **Move** costs a flat **8h**,
- an **Interview** costs a flat **1h**

(distance-scaled Move cost stays deferred — see the map). Because two 8-hour Moves fill
the day exactly (`06:00 → 14:00 → 22:00`), **two hops per day is the ceiling** — against
a fugitive who moves once. That asymmetry is what makes the chase winnable, and what
makes an Interview *cost* something: every hour spent asking questions is an hour not
spent travelling, and a single Interview drops you from two Moves that day to one.

## The discrete-budget rule

The rule that holds this together: **no action may start unless it can finish before the
22:00 rest block** — `hour + cost <= 22`. Nothing straddles the overnight. A Move needs
`hour <= 14`; an Interview needs `hour <= 21`. Reaching 22:00 exactly *is* the trigger:
the day increments, the clock resets to 06:00, and the fugitive relocates.

The relocation is implicit rather than stored. The fugitive's position is `route[day]`,
so incrementing `day` *is* the overnight move — there is no separate fugitive field to
mutate. `advance_clock` only ever touches `day` and `hour`:

```python
def advance_clock(state: CaseState, *, cost: int) -> CaseState:
    new_hour = state.hour + cost
    if new_hour >= REST_START:  # reached 22:00 → overnight rest
        return replace(state, day=state.day + 1, hour=WAKING_START)
    return replace(state, hour=new_hour)
```

## Two-phase judging

Making the fugitive stationary-by-day forces `apply_move` to judge a catch in **two
phases**, because there are now two distinct ways to end up co-located:

1. **Mid-day catch.** The fugitive sits at `route[day]` all day. If the detective's
   target *is* that spot, they are caught then and there — before the 8h is even spent.
   This check runs against the *current* day, before the clock advances.
2. **Stake-out catch (or escape).** If the Move misses, the 8h is spent. Should that
   tip the clock over 22:00, the day rolls and the fugitive relocates overnight — which
   may walk them straight onto a detective who ended the day in the right place (a win),
   or off the map to the Escape Location (a loss). This check runs *after* the advance.

Collapsing these into one post-advance check — the Stage-1 shape — would silently drop
the mid-day catch: the detective would walk into the room where the fugitive is standing
and nothing would happen until nightfall. The two phases keep the fiction honest.

## Rendering the clock backend-side

The migration folded in here also retires the TUI's home-grown `f"Day {day}"` string.
Clock prose is now rendered by the backend's `TextProvider` (ADR-0008) — the responses
carry both the structured `day`/`hour` ints *and* a rendered `clock` (`"Day 1, 14:00"`,
`"Dag 1, 14:00"` under `Accept-Language: no`). The thin TUI just displays the string.
This gives `TemplatedTextProvider.clock` its first real workout — day *and* hour, zero-
padded, language-aware — and keeps language a shell concern, exactly where the core/shell
split (ADR-0008) wants it. The visible hour matters: the whole reason to surface `hour`
is that the player must *see* the 1h an Interview costs, or the cost is not a mechanic.
