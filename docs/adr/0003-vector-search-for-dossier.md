# Vector Search for Dossier Filtering

Suspect profiles in the Dossier are AI-generated prose — no structured trait fields. The detective filters the Dossier using natural language queries (e.g., "art connections", "fluent in Italian") matched semantically via a vector store. Multiple active filters are ANDed: each filter independently scores all Suspects and only those meeting a minimum score on all filters remain visible.

This allows Suspect profiles to stay fully AI-generated without requiring a predefined trait taxonomy. The trade-off is that the backend needs a vector store and embedding pipeline, and AND semantics require scoring each Suspect against each filter rather than a single compound query. Given the small Suspect roster per Campaign (tens, not thousands), this is tractable without optimisation.
