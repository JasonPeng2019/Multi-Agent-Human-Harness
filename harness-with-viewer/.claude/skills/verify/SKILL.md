---
name: verify
description: Discover and run the host repository's authoritative checks, then report focused, relevant, or full evidence. Use after implementation and when asked to test, verify, lint, format-check, type-check, build, or confirm correctness.
---

# Verify repository work

Run the least expensive checks that honestly support the current claim.

## Choose the verification level

- **Focused:** directly covers the changed files or behavior.
- **Relevant:** covers the owning package, service, or subsystem.
- **Full:** runs the repository's documented complete gate.

Use focused checks during implementation. Before completing non-trivial work, run
at least focused verification and usually relevant verification. Run the full gate
when the user requests it, repository policy requires it, or breadth/risk justifies
it.

## Discover commands in this order

1. The exact command or check requested by the user.
2. Commands documented in repository instructions, README, contributing docs, or
   CI configuration.
3. Existing task-runner entries clearly named for test, lint, type-check, build,
   check, or verify.
4. Conventional ecosystem commands supported by authoritative project files such
   as `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, solution/project
   files, Makefiles, or task files.
5. Commands in `.agent/verify.toml`, if present.

Do not guess when several plausible full gates exist. Ask or report the ambiguity.
Do not install missing tools or dependencies without authorization.

## Execute safely

- Route a long or failure-prone check through the bounded-run skill.
- Prefer changed-file or named-test selection only when the tool supports it
  reliably.
- Include staged, unstaged, and relevant untracked work when making a claim about
  the current tree.
- Rerun checks after integration if verified bytes changed.
- An empty check set is not a successful full verification.

## Report

State:

```text
VERIFY: PASS | FAIL | INCOMPLETE
Level: focused | relevant | full
Commands:
  - <exact command>
Results:
  - <check>: <observed result>
Skipped/Unavailable:
  - <check and reason>
Next: <action if anything failed or remains uncertain>
```

`PASS` means every check needed for the stated level ran and passed. Missing tools,
ambiguous commands, timeouts, and skipped required checks produce `INCOMPLETE`, not
`PASS`. Documentation-only or read-only work may need no automated check; say so.
