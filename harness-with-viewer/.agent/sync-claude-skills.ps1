# Regenerate .claude/skills/ from the canonical .agents/skills/ catalog.
#
# Claude Code only discovers project skills from a fixed .claude/skills/*/SKILL.md
# location; it cannot be pointed at another directory. .agents/skills/ remains the
# single edited source of truth. Run this after adding, editing, or removing a
# skill so the two directories do not drift.
$ErrorActionPreference = 'Stop'

# Resolve the workflow root as the parent of this script's own .agent/ directory
# rather than the enclosing Git repository root: the two are not always the same
# directory (for example while this template is developed inside a larger
# repository), but .agent/, .agents/, and .claude/ are always siblings by
# construction once the workflow is copied into a host repository.
$root = (Get-Item -LiteralPath (Join-Path $PSScriptRoot '..')).FullName
$sourceDir = Join-Path $root '.agents/skills'
$destDir = Join-Path $root '.claude/skills'

if (-not (Test-Path -LiteralPath $sourceDir -PathType Container)) {
    Write-Error "Missing canonical skill catalog: $sourceDir"
    exit 1
}

if (Test-Path -LiteralPath $destDir) {
    Remove-Item -LiteralPath $destDir -Recurse -Force
}
New-Item -ItemType Directory -Path $destDir -Force | Out-Null
Copy-Item -Path (Join-Path $sourceDir '*') -Destination $destDir -Recurse -Force

# Codex-only per-skill provider policy (e.g. commit/agents/openai.yaml) has no
# Claude Code equivalent and must not be mirrored.
Get-ChildItem -LiteralPath $destDir -Recurse -Directory -Filter 'agents' |
    Remove-Item -Recurse -Force

$count = @(Get-ChildItem -LiteralPath $destDir -Recurse -Filter 'SKILL.md').Count
Write-Output "Synced $count skill(s) from $sourceDir to $destDir"
