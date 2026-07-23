# What does a Clue reveal?

Status: open
Labels: wayfinder:grilling
Assignee:
Parent: [Stage 2 map](../MAP.md)

## Question

Define the **information content of a Clue** returned by Interview:

- **What** it points at: the fugitive's exact next-hop Location, a direction/neighbour
  hint, or something fuzzier — and relative to **which day** (the fugitive has already
  fled to `route[day]` when the detective arrives; does the clue point to `route[day]`,
  `route[day+1]`, …?).
- **Truthfulness**: always accurate, or occasionally cold/misleading? (Lies are a Stage-3
  Person behaviour and out of scope — but a truthful-but-vague clue may still be a choice.)
- **On-trail vs off-trail** (the skill-defining property): does interviewing at a Location
  the **fugitive never passed through** yield a useless/"cold trail" clue, so the player
  must actually be on the trail to learn anything? This is what makes clue-following
  skillful rather than an oracle.

Output is a structured, language-free fact (rendered later by the TextProvider — see the
clue-text-rendering ticket). Resolve via `/grilling` + `/domain-modeling`.

## Blocked by

- [Does Interview cost a day?](./03-does-interview-cost-a-day.md)
