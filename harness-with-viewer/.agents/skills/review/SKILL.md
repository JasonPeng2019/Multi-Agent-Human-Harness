---
name: review
description: Obtain a fresh, read-only critique of an explicit plan, diff, design choice, or named files. Use when requested or when a change is broad, consequential, hard to reverse, security-sensitive, or materially benefits from independent judgment; not after every routine edit.
---

# Run an independent review

Select exactly one review target: a named plan/document, working diff, staged
diff, design decision, or explicit files. State the intended outcome and relevant
acceptance criteria.

Prefer a fresh native read-only subagent. If unavailable, launch a read-only
`codex exec` or `claude -p` worker through the bounded runner with explicit tool
and write restrictions. The reviewer must not edit, stage, commit, or run
destructive commands.

Ask the reviewer to:

1. Inspect the target and necessary nearby context.
2. Read the stated acceptance criteria, repository contract, or user outcome
   before judging the artifact. If none exists, say so rather than inventing one.
3. Check correctness, missed requirements, regressions, unsafe assumptions,
   compatibility, recovery, test strength, and verification gaps in proportion to
   risk.
4. Cite file and line evidence where available. For each material finding, state
   the evidence, why it violates the contract, the consequence, and the smallest
   useful correction.
5. Separate confirmed defects from questions and optional improvements.
6. Avoid style-only or speculative findings unless they affect the requested
   outcome.

For a release, public API, onboarding flow, or externally used tool, select one
relevant audience lens as well: evaluator, integrator, new maintainer, operator,
or reproducer. Look specifically for an adoption blocker such as a missing setup
step, example, migration path, support boundary, or recovery instruction. This
is advisory unless the target's acceptance criteria make it mandatory.

Return findings first, ordered by consequence:

```text
REVIEW: SHIP | REVISE | BLOCK
Findings:
  - <severity> <file:line> — <problem, impact, and smallest useful correction>
Contract coverage:
  - <criterion> — met | partial | unmet — <evidence>
Questions:
  - <material uncertainty only>
Verification gaps:
  - <missing evidence>
```

`SHIP` means no material defect was found; it is not verification proof. `REVISE`
means correctable issues remain. `BLOCK` means the target cannot safely proceed
without a missing decision, authority, or fundamental redesign. Do not persist a
review database or freshness hash.
