# Claude Code instructions

@AGENTS.md

Use the repository instructions above as the shared policy. If this repository
contains the portable workspace files, `.agents/skills/` is their editable source
and `.claude/skills/` is Claude's generated mirror; edit the former and run
`.agent/sync-claude-skills.ps1` or `.agent/sync-claude-skills.sh`. Do not hand-edit
the mirror. Repository-specific Claude configuration belongs in `.claude/`.
