# Rendering a clue keeps language a pure shell concern

The Interview action's whole point is the *clue* it returns — "they passed through here
two days ago." But a clue is a fact about the fugitive's trail, not a sentence. The core
that produces it never decides what language the player reads, or even that the answer is
prose. That line — fact in the core, words in the shell — is ADR-0008, and the clue
rendering is where Stage 2 has to hold it.

## The fact and the sentence are two different types

The core emits a `Clue`, a small language-free union:

```python
@dataclass(frozen=True, kw_only=True)
class Sighting:
    days_ago: int

@dataclass(frozen=True)
class ColdTrail: ...

type Clue = Sighting | ColdTrail
```

That's the entire vocabulary of a Stage 2 clue: *the fugitive was here `days_ago` days
ago*, or *no usable trace here*. Notice what isn't in it — no direction, no next hop, no
string. `Sighting` carries only freshness, and the gate that decides `Sighting` versus
`ColdTrail` (was the fugitive ever actually here?) is the skill of the mechanic. A
`ColdTrail` deliberately collapses two situations — never visited, and not-yet-reached —
into one fact, so the clue can't leak future knowledge by telling them apart.

`days_ago` is always at least 1. Zero would mean the detective is standing where the
fugitive stands *now* — that's a win, not a clue — so the type documents the invariant and
the producer upholds it.

## Rendering is a lookup plus a match

The `TextProvider` port grows one method beside `clock`:

```python
def clue(self, *, clue: Clue, language: str) -> str: ...
```

The templated implementation is deliberately dull — a per-language template table and a
`match` over the union:

```python
match clue:
    case Sighting(days_ago=days_ago):
        singular, plural = self._DAY_UNITS[lang]
        unit = singular if days_ago == 1 else plural
        return self._SIGHTING_TEMPLATES[lang].format(count=days_ago, unit=unit)
    case ColdTrail():
        return self._COLD_TRAIL[lang]
```

Two details earn their keep. The `match` is exhaustive over `Clue`, so when Stage 3 adds a
new clue variant the type checker flags every renderer that hasn't handled it — the union
is the checklist. And pluralization lives *here*, in the shell, not in the core: English
wants "day"/"days", Norwegian "dag"/"dager", and that's a language fact, so the core never
learns that one day is special.

## Why templated, and why it doesn't matter yet

An unknown language falls back to English, exactly as `clock` already does — the fallback
rule is a property of the provider, not of any one fact it renders. And the whole thing is
templated because Stage 5 swaps in an AI provider behind the same `clue(clue=..., ...)`
signature. The core hands over the same `Sighting(days_ago=2)` either way; only the shell
decides whether "two days ago" arrives as a template or a generated sentence. Keeping the
fact and the words on opposite sides of that port is what makes the swap a shell change and
nothing more.
