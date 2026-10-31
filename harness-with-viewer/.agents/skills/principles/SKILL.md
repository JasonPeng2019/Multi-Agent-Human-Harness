---
name: principles
description: Apply the repository's engineering decision charter before writing a specification or plan, changing architecture, making broad edits, or choosing a consequential design. Do not use for simple questions, read-only status, or trivial mechanical edits.
---

# Apply the engineering principles

Use this charter in the context of the actual request and repository. It guides
judgment; it does not expand product scope or turn every desirable property into
a universal requirement.

## Decision order

1. Understand the requested outcome, authority boundary, and definition of done.
2. Inspect the live code, tests, instructions, and tooling that govern the area.
3. Identify material ambiguity. Ask only when the answer changes architecture,
   public behavior, persistence, safety, compatibility, or scope; otherwise make
   and state a reasonable assumption.
4. Choose the smallest complete solution that fits observed reality.
5. Verify the behavior at the least expensive level that supports the claim.
6. Report what happened, including failures, skipped checks, and uncertainty.

## Principles

### Correctness

- Implement the behavior the idea promises, not an approximation that merely
  looks plausible.
- A write-and-verify operation must do both. Failure must not be reported as
  success.
- Do not fabricate results, infer success from missing evidence, or hide errors.
- Correctness beats convenience when the two genuinely conflict.

### Simplicity

- Prefer direct control flow, established project tools, and focused units.
- Do not add speculative abstractions, unused configuration, duplicated guards,
  or framework machinery for a single case.
- Complexity must solve a recurring realistic problem worth its implementation,
  maintenance, coordination, and failure cost.
- Remove unnecessary complexity discovered inside the requested scope, but do not
  turn a feature change into an unrelated cleanup campaign.

### Scope discipline

- Preserve working code and unrelated user changes.
- Do not weaken required behavior to simplify implementation.
- Do not silently add features, migrations, dependencies, public APIs, or policy.
- Existing repository decisions and conventions outrank personal preference unless
  the task explicitly changes them.

### Proportionality

- Match planning, review, tests, and safeguards to realistic consequence and
  uncertainty.
- Small local changes should remain small. Broad, irreversible, stateful, or
  externally visible changes deserve more evidence.
- Handle common failures and credible caller mistakes. Do not promote contrived
  cases into requirements without a real trust, correctness, or product reason.

### Portability to intended environments

- Avoid accidental machine-specific paths, usernames, credentials, versions, and
  resource assumptions.
- Detect what varies, accept configuration where detection is ambiguous, and
  report a limitation when neither is reliable.
- Portability means the environments the project intends to support; it does not
  require turning every internal program into a universal cross-platform product.

### Maintainability and usability

- Put each responsibility in one clear home and name it predictably.
- Document public contracts, important assumptions, and recovery from realistic
  failures according to the host project's conventions.
- Prefer a design a future maintainer can understand in one sitting.

## Mistake guards

Guard a verified contradiction or a likely unintended target: the wrong database,
artifact, path, repository, stale state, or unbounded retry. Report the concrete
mismatch and recovery.

Do not block an explicitly authorized, correctly targeted risky operation merely
because it is risky. The user owns intended risk; the workflow catches mistakes.
Do not claim a mismatch when the target could not be verified.

## Conflict rules

- Correctness over convenience.
- Explicit scope over speculative generality.
- Observed repository truth over memory.
- Existing project conventions over personal taste.
- Honest uncertainty over guessing.
- The smallest effective guard over broad paternalistic policy.

## Completion check

Before declaring the work done, confirm:

- the requested outcome is complete;
- relevant checks ran and their actual results are reported;
- material assumptions and uncertainty are visible;
- unrelated work remains intact;
- every new abstraction, guard, limit, and configuration value earns its cost.

## Deep decision charter

For a durable architecture, public product contract, cross-environment behavior,
or a difficult guard-versus-usability decision, also read
[the detailed charter](references/detailed-decision-charter.md). It restores the
useful reasoning detail from `always-keep-in-mind` without making ordinary work
load it by default.
