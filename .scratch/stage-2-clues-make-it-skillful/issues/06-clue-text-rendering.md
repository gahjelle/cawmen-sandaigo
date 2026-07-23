# Clue text rendering (TextProvider)

Status: open
Labels: wayfinder:task
Assignee:
Parent: [Stage 2 map](../MAP.md)

## Question

Extend the `TextProvider` port (`backend/src/cawmen_backend/shell/text_provider.py`) with
a `clue(...)` method that renders the structured, language-free clue fact into
Language-Preference prose, plus the `TemplatedTextProvider` templates (en/no) that back it.

This is an **execution-task** (planning-only exception): there is little to *decide* once
the clue-semantics ticket fixes the structured fact — this ticket carries out the
rendering per those semantics. The shape of the `clue(...)` signature and its templates
follows directly from what a Clue reveals.

## Blocked by

- [What does a Clue reveal?](./04-what-a-clue-reveals.md)

## Last step

Write an article stub under `articles/02-clues-make-it-skillful/` covering the clue
rendering layer and how templated text keeps language a pure shell concern (ADR-0008).
