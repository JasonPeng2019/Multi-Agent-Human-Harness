---
name: worktree
description: Create, inspect, or close an isolated Git worktree for an independent implementation task or experiment. Use only when isolation is useful; never remove a dirty worktree or assume worktrees make overlapping ownership safe.
---

# Manage an isolated worktree

Confirm the repository root, current branch, existing worktrees, task name, branch
name, and destination before mutation.

Create with ordinary Git:

```text
git worktree list --porcelain
git worktree add -b <branch> <path> <start-point>
```

Choose a path outside the main worktree but inside a clearly named task-worktree
parent. Resolve the absolute path and ensure it does not already contain unrelated
data. Give parallel writers disjoint ownership even when they use worktrees.

Before closing:

1. Run `git -C <path> status --short --branch`.
2. Refuse removal when tracked or untracked work remains.
3. Confirm the branch/commits or patch have been integrated or deliberately
   retained.
4. Run `git worktree remove <path>` without `--force`.
5. Use `git worktree prune` only for genuinely stale administrative records.

Never delete the directory manually as a substitute for Git worktree removal.
Report the branch and path created or removed. The primary agent owns integration
and final verification.
