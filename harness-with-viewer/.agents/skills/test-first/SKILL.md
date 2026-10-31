---
name: test-first
description: Implement a feature or bug fix from a focused executable behavior contract when a useful automated test is practical. Do not force test-first work onto documentation, exploration, generated artifacts, or behavior that cannot be meaningfully automated.
---

# Work test first

1. State the smallest observable behavior contract and why it matters.
2. Find the nearest existing test style and fixture boundary.
3. Add or select one focused test that fails for the intended reason.
4. Run it and observe the expected failure; fix a bad test if it fails for another
   reason.
5. Make the smallest production change that satisfies the contract.
6. Run the focused test to green.
7. Refactor only when it improves the requested change without weakening the test.
8. Run relevant neighboring checks, then use the verify skill before completion.

For timing, concurrency, or process lifecycle behavior, test observable identities
and state transitions instead of relying only on sleeps. Keep tests deterministic
and avoid copying the implementation into the assertion. Report red and green
commands and results honestly.
