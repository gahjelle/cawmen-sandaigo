# Scenarios as Data Files, Runtime State in the Database

Authored content — Scenarios, comprising the Location Graph (with stages) and the Suspect roster (with prose profiles) — is stored as version-controlled data files loaded by the engine. Mutable runtime state — Players, Campaigns, Cases, and progress — lives in the database introduced at Stage 8. The Scenario Editor reads and writes the same file format the engine consumes, so the engine is indifferent to whether a Scenario was hand-authored or tool-generated.

Authored worlds are content that benefits from diffing, code review, and QA — exactly the "QA-able, editable" property that motivated separating Scenario from Campaign. Runtime state is per-player mutable data that belongs in a database. Storing both uniformly in the database was considered and rejected: it would lose version-control and reviewability and couple world authoring to the DB schema.

Consequence: a Scenario referenced by an in-progress Campaign must stay stable. If a Scenario file changes underneath a running Campaign, Case reproducibility (ADR-0001) can break, since the same Case Seed against a changed Scenario yields a different Case. Scenario versioning will need to be addressed when Campaigns become persistent at Stage 8.
