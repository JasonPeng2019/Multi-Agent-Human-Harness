---
name: repro-guard
description: Check research code and experiment evidence for reproducibility, provenance, and accidental leakage. Use before reporting a result or committing research code.
---

# Reproducibility guard

Check and report, with file or artifact evidence:

- seeds and relevant deterministic settings;
- data identity, split provenance, preprocessing, and leakage boundaries;
- pinned environment and key dependency versions;
- tracked configuration, source revision, and saved run artifacts; and
- hardcoded local paths, secrets, or untracked result files.

State `REPRO: OK`, `PARTIAL`, or `BLOCKED`, with the exact missing evidence.
Reproducibility hygiene does not prove a scientific claim; use
`research-claim-review` for that question.
