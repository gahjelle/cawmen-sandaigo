# Stage 2 — Clues make it skillful (map)

Labels: wayfinder:map

<!--
Local-markdown wayfinder conventions (no "Wayfinding operations" section exists in
docs/agents/issue-tracker.md, so these are established here):

- This file is the MAP (label `wayfinder:map`). Its tickets are the issue files in
  `./issues/`, each labelled `wayfinder:<type>` (research | prototype | grilling | task).
- A ticket header carries: `Status:` (open | claimed | closed), `Labels:`, `Assignee:`
  (the claim — empty means unclaimed), and `Parent:` (link back to this map).
- Blocking uses the `## Blocked by` body convention (this tracker has no native
  dependency edges). A ticket is UNBLOCKED when every ticket it lists is closed.
- The FRONTIER = open, unblocked, unclaimed tickets — the takeable edge.
- To CLAIM: set `Status: claimed` and fill `Assignee:` before doing any work.
- To RESOLVE: append a `## Resolution` section (date + answer) to the ticket, set
  `Status: closed`, and add a one-line pointer under "Decisions so far" below.
- This map is an INDEX. A decision lives in exactly one place — its ticket. The map
  only gists and links.
-->

## Destination

A **locked Stage 2 spec**: a PRD plus a wired set of implementation issues under
`.scratch/stage-2-clues-make-it-skillful/`, with every open Stage-2 design decision
resolved — ready to hand off to build agents. **Planning only**; no gameplay code is
written in this effort. Stage 2 delivers the **Interview** action returning a templated
**Clue** that points toward the fugitive's next hop, making the game skillful.

## Notes

- **Domain**: geography/detective game; authoritative Python backend (functional core +
  shell) exposing REST, thin Textual TUI. See `CONTEXT-MAP.md`, `backend/CONTEXT.md`,
  `docs/implementation-plan.md` (Stage 2), and the ADRs (esp. ADR-0008 core/shell +
  TextProvider, ADR-0012 undirected graph, ADR-0001 case seed).
- **Skills every session should consult**: `/grilling` + `/domain-modeling` for decision
  tickets; `/prototype` if a mechanic needs a concrete artifact to react to.
- **Standing preference**: planning only — produce decisions, not deliverables. Two
  tickets are deliberately flagged as **execution-tasks** that hand off (the refactors);
  they are the exception, not the rule.
- Current mechanic surface: `core/chase.py` (`apply_move`, clock), `core/route.py`
  (seeded self-avoiding walk), `api/app.py` (`POST /cases/{id}/move`),
  `shell/text_provider.py` (`TextProvider` port, templated).

## Decisions so far

<!-- the index — one line per closed ticket -->

_None yet — charting complete, tickets open._

## Not yet specified

<!-- in-scope fog; graduates into tickets as the frontier advances -->

- Whether **end-of-case playback should reveal the clue trail** (where clues pointed vs
  where the fugitive actually went). Dim until the clue-semantics ticket lands.
- **Clue template coverage across languages** beyond `en`/`no`. Shape depends on the
  clue-text-rendering ticket.

## Out of scope

<!-- ruled beyond this destination; never graduates -->

- **Minimum Fugitive Route length floor** — filed at `.scratch/difficulty-parameters/issues/01-minimum-route-length-floor.md`; downstream of the scenario-size decision and only bites once graphs can terminate early.
- **Persons / person-targeted Interview** — Stage 3. At Stage 2 clues come from the Location; no `person_id`. (Resolves the speculative `interview(case_id, person_id, …)` signature in the CaseActionHandler stub.)
- **AI-generated clue text** — Stage 5; templates only now.
- **Arrest / Wait actions and the fugitive lying** — Stage 3.
