#!/usr/bin/env bash
# Regenerate .claude/skills/ from the canonical .agents/skills/ catalog.
#
# Claude Code only discovers project skills from a fixed .claude/skills/*/SKILL.md
# location; it cannot be pointed at another directory. .agents/skills/ remains the
# single edited source of truth. Run this after adding, editing, or removing a
# skill so the two directories do not drift.
set -euo pipefail

# Resolve the workflow root as the parent of this script's own .agent/ directory
# rather than the enclosing Git repository root: the two are not always the same
# directory (for example while this template is developed inside a larger
# repository), but .agent/, .agents/, and .claude/ are always siblings by
# construction once the workflow is copied into a host repository.
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
source_dir="$root/.agents/skills"
dest_dir="$root/.claude/skills"

[[ -d "$source_dir" ]] || { printf 'Missing canonical skill catalog: %s\n' "$source_dir" >&2; exit 1; }

rm -rf "$dest_dir"
mkdir -p "$dest_dir"
cp -R "$source_dir/." "$dest_dir/"

# Codex-only per-skill provider policy (e.g. commit/agents/openai.yaml) has no
# Claude Code equivalent and must not be mirrored.
for provider_dir in "$dest_dir"/*/agents; do
  [[ -d "$provider_dir" ]] || continue
  rm -rf "$provider_dir"
done

count=$(find "$dest_dir" -name SKILL.md | wc -l | tr -d ' ')
printf 'Synced %s skill(s) from %s to %s\n' "$count" "$source_dir" "$dest_dir"
