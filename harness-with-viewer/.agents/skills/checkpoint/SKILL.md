---
name: checkpoint
description: Create or refresh HANDOFF.md when the user asks to checkpoint, save state, pause, prepare for compaction, or hand work to another session. For a major plan or task divided into modules, call it immediately after every completed module, including an MI-* module. Do not create handoffs for ordinary completed or short tasks.
---

# Write a resumable handoff

Read current repository instructions, Git status/diff summary, the active task,
and existing `HANDOFF.md` before writing. Do not infer completed work or
verification from memory when repository evidence is available.

Write one concise root `HANDOFF.md` containing:

- **Objective:** the requested outcome.
- **Status:** current state without invented percentages.
- **Completed:** concrete changes and decisions already made.
- **Verification:** exact commands run and observed results.
- **Remaining:** unfinished work, failures, and unanswered questions.
- **Important assumptions:** only choices needed to resume correctly.
- **Relevant files:** the small working set.
- **Next action:** the exact next step and, when useful, next command.

Keep it roughly one screen when possible. It records state; it does not override
the user, repository instructions, or plan. Update rather than append stale
history. Never call unverified work verified.
