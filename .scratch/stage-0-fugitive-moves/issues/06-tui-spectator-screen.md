# TUI Spectator Screen

Status: ready-for-agent

Depends on: 05

Update `frontend-tui/src/cawmen_tui/app.py` to implement the Stage 0 spectator view:
create a Case on mount, render the location list and In-Game Clock, tick every 2 seconds,
and display "Trail gone cold" when the fugitive escapes.

## Behaviour

1. **On mount**: call `create_case(scenario="grand-tour")` with a fresh `uuid.uuid4()` seed;
   store the returned `case_id` and location list
2. **Render**: In-Game Clock at the top (use `TemplatedTextProvider.clock(day=..., language="en")`);
   below it, the list of named Locations — the fugitive's current location highlighted
   (e.g. bold or `[reverse]` markup in Textual)
3. **Timer**: every 2 seconds call `advance_case(case_id)`:
   - `CaseState` → update the display
   - `TrailGoneCold` → stop the timer, replace the location list with "Trail gone cold"
4. **`--api-url` flag**: passed through from `__main__.py`; the existing `from_api_url`
   classmethod already handles it

## Acceptance criteria

- The fugitive's location advances visibly through the location list
- The In-Game Clock increments each tick
- "Trail gone cold" appears and ticking stops once the fugitive reaches the Escape Location
- The existing health-check behaviour on startup is preserved

## Last step

Write an article stub in `articles/00-the-fugitive-moves/` per `docs/agents/articles.md`.
