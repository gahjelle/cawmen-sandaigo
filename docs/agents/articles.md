# Article stubs

Article stubs live under `articles/`. They are written alongside implementation work
and later combined into full articles per stage.

## Structure

```
articles/
  00-the-fugitive-moves/      ← stubs for Stage 0 tasks
    uv-workspace-setup.md
    openapi-scaffold.md
  00-the-fugitive-moves.md    ← combined article (written after the stage is done)
  01-the-detective-chases/
    ...
```

- Stage subdirectories use the same descriptive slug as the stage: `<NN>-<stage-name>/`
- Stub filenames are topic-named, not task-numbered: `uv-workspace-setup.md`, not `03-uv-setup.md`
- The combined article sits at `articles/<NN>-<stage-name>.md`, outside the subdirectory

## When to write a stub

After completing a task, while context is warm — as the last step of the task. Not every
task warrants a stub. Skip it when the task is purely mechanical with nothing interesting
to explain. When in doubt, write something short rather than nothing.

## What a stub contains

Stubs are written for developers who know basic Python and Elixir syntax. Do not explain
variables, for-loops, list comprehensions, or other fundamentals. Focus on what was built
and why the choices were made.

A stub typically contains:

- **What was built** — a short description of the thing that now exists
- **Why** — the interesting choices: trade-offs made, alternatives rejected, constraints honoured
- **Code excerpt** (optional) — a representative snippet when it makes the explanation concrete

This is a guide, not a rigid template. A task that touches several interesting design
decisions might warrant multiple sections. A task with one non-obvious choice might be a
single paragraph. Honour the content; don't fill a template for its own sake.

## Format

Plain GitHub-flavored markdown. No frontmatter.

## Combining stubs into an article

When a stage is complete, the stubs become raw material for a full article. The combined
article adds a proper introduction, a narrative arc, and a payoff — things the stubs lack
because they were written task by task. The stubs themselves are not deleted; they remain
as the working notes behind the published piece.
