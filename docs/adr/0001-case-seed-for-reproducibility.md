# Case Seed for Reproducible Generation

Each Case is assigned a UUID at creation that acts as the random seed for all procedural generation. Given the same Seed and the same preset parameters (Location list, Campaign roster), the Case always produces the same Suspect, crime, and travel path.

This enables sharing and replaying specific Cases by UUID, and makes debugging generation issues deterministic. The trade-off is that case generation must be strictly seed-driven — any non-deterministic logic (e.g., live AI calls in the generation path) would break reproducibility and must be kept out of the structural generation step.
