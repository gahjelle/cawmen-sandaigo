# From `.scratch` markdown to GitHub Issues

For its first two stages, this project tracked all of its work in flat markdown files
under `.scratch/`. No database, no web app, no API tokens — a feature was a directory, an
issue was a file, and triage state was a `Status:` line near the top. When we finished
mapping out Stage 2, we moved the whole tracker to GitHub Issues. This article is about
why the local convention was a good default, why we outgrew it, and what the move gained
and gave up.

## The local-markdown tracker

The setup was deliberately primitive:

```
.scratch/
  stage-1-player-moves/
    PRD.md
    issues/
      04-detective-moves-playable-blind-loop.md
      05-end-of-case-playback-and-new-case.md
```

Each issue file was plain markdown with a lightweight header — `Status: ready-for-agent`,
a `## Blocked by` section naming other files, a `## Comments` log appended at the bottom.
The engineering skills that drive this repo (`/to-tickets`, `/triage`, `/wayfinder`) were
told, via `docs/agents/issue-tracker.md`, to read and write files instead of calling an
API.

For a solo, agent-driven project this is a genuinely strong default, and it's worth being
honest about its virtues before dismissing them:

- **Version-controlled with the code.** An issue and the commit that resolved it lived in
  the same history. `git log` over `.scratch/` *was* the project's decision record.
- **Diffable and reviewable.** Editing an issue produced a diff. Charting the Stage 2 map
  was a pull request you could review like any other.
- **Zero dependencies, fully offline.** No network, no auth, no rate limits. `grep -r` was
  the query engine.
- **Trivially portable.** The whole tracker was text; nothing was locked inside a vendor.

None of these are small. The reason we moved is not that the local tracker was bad — it's
that the project's needs changed.

## Why we moved

The `.scratch` convention optimises for a single author working in one clone. The moment
work wants to be *seen* — by collaborators, by future contributors, by the humans who
review PRs — a text tree in a branch is the wrong shape. The specific pressures:

- **Dependency structure wanted a real UI.** The Stage 2 map is a graph: a `wayfinder:map`
  issue with eight child tickets, several blocked on others. In markdown that graph was a
  `## Blocked by` line you had to reconstruct by hand across a dozen files. GitHub has
  **native sub-issues** and **native issue dependencies** — the parent/child hierarchy and
  the blocked-by edges render in the UI, and "what's on the frontier?" becomes a query
  against `issue_dependencies_summary.blocked_by` rather than a manual read.
- **Claims and assignment.** "Who's working this ticket" is an assignee on GitHub. In the
  file world it was a convention we had to invent and remember.
- **PRs and issues share one space.** Cross-referencing a PR to the issue it closes,
  linking back from the issue — this is free on GitHub and bespoke plumbing anywhere else.
- **Discoverability.** An issue has a URL you can send someone. A file at
  `.scratch/stage-2-.../issues/03-...md` on an unmerged branch does not.

The tipping point was the shape of the Stage 2 map itself. A flat list of tasks is fine as
files; a *dependency graph you navigate* wants the tracker that renders graphs natively.

## What the migration looked like

We kept it surgical. The completed Stage 0–1 issues were **not** migrated — recreating
finished history as GitHub issues is busywork with no payoff. Instead `.scratch/` was
renamed to `.issue_tracker_legacy/` and the done stages stayed there as a frozen archive,
still in git, still greppable.

Only the live work moved. The Stage 2 wayfinder map was recreated on GitHub as issue #7,
its tickets as #8–#15 wired with real sub-issue and blocked-by relationships, and the one
deferred out-of-scope item became standalone issue #16. The wiring used `gh api` against
the sub-issues and dependencies endpoints — which need each issue's numeric **database
id**, not its `#number`, a small sharp edge worth writing down.

The documentation was rewired to match: `docs/agents/issue-tracker.md` was rewritten from
the GitHub template (including the `/wayfinder` operations), and the one-line pointer in
`AGENTS.md` now names GitHub. The skills that used to write files now call `gh`.

## What we gave up

Honesty demands the other column, because everything the local tracker was good at is now
a cost:

- **The decision record left git.** Issue bodies and comments live on GitHub's servers,
  not in the repo's history. `git log` no longer tells the whole story; you need the API
  to reconstruct it. (The archived stages are the exception — their history is still in
  the tree.)
- **Network and auth are now required.** Working the tracker means an authenticated `gh`
  and a connection. The offline, grep-it-locally workflow is gone for live issues.
- **Some operations got fiddlier, not simpler.** Native dependencies are lovely in the UI
  but are driven through `gh api` calls with database ids and specific endpoints — more
  moving parts than editing a `## Blocked by` line, even if the result is better.
- **A soft vendor tie.** The issues are portable in principle (they're just data behind an
  API) but no longer *trivially* so. Moving off GitHub would be an export-and-remap job,
  not a `git mv`.

## The general shape of the trade

This is the recurring tension between **local-and-versioned** and **hosted-and-shared**.
Text-in-git wins on portability, offline access, and keeping the record next to the code.
A hosted tracker wins on collaboration, native relationship modelling, and discoverability.
Neither is correct in the abstract; the right answer follows the work.

A solo prototype charting linear stages was well served by files — and the `.scratch`
history proves it, because Stages 0 and 1 shipped cleanly through it. A project whose next
stage is a dependency graph meant to be navigated and, eventually, collaborated on, is
better served by the tracker built to render graphs. We rode the cheap option exactly as
long as it was the right one, and archived rather than deleted it so the earlier chapters
stay legible.
