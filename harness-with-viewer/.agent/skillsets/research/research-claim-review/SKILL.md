---
name: research-claim-review
description: Critique whether experimental evidence supports a research claim separately from whether code runs. Use before presenting improvements, comparisons, or conclusions.
---

# Research claim review

Treat the claimed conclusion as unproven until the evidence supports it. Inspect
the exact baseline, data split, evaluation protocol, metric definition, sample
count/seeds, variance, and result artifacts. Look specifically for leakage,
protocol drift, cherry-picking, and conclusions broader than the measurements.

For consequential claims, request a fresh read-only review when the host can
provide one. Report:

```text
CLAIM: SUPPORTED | REVISE | BLOCKED
EVIDENCE CHECKED: <artifacts and commands>
RISKS: <leakage, variance, baseline, or protocol concerns>
NEXT EVIDENCE: <what would change the verdict>
```

Never turn an unavailable baseline or incomplete run record into a supported
claim.
