---
name: commit
description: Inspect, stage deliberately, and create a local Git commit only when the user explicitly asks to commit. Never invoke implicitly, never push, and never include unrelated changes.
---

# Create a deliberate local commit

This skill is user-triggered only.

1. Read repository commit conventions.
2. Run `git status --short --branch`, inspect the unstaged diff, and inspect the
   staged diff.
3. Identify exactly which files belong to the requested change. Preserve unrelated
   tracked and untracked work.
4. Confirm relevant verification is current for the bytes to be committed. If it
   is not, run the verify skill or report the gap.
5. Stage named files or hunks deliberately. Never use `git add -A` blindly.
6. Reinspect `git diff --cached` for scope, generated artifacts, credentials, and
   accidental files.
7. Create one concise message consistent with repository conventions and focused
   on the change's purpose.
8. Report the commit hash and any work intentionally left uncommitted.

Do not amend, rebase, push, publish, open a pull request, bypass hooks, or discard
changes unless the user separately authorizes that action.
