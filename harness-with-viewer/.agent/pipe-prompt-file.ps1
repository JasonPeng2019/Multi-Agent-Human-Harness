# Bridge the multi-agent launcher's file-path prompt delivery to a worker CLI
# that reads its prompt from stdin instead of a file-path argument (for
# example `claude -p` or `codex exec`, both documented to read stdin when no
# prompt argument is given). The launcher's schema requires {prompt_file} to
# appear literally in the command array; this script consumes that argument,
# then runs the real worker with the file's content on stdin.
#
# Usage: pipe-prompt-file.ps1 <prompt-file> <command> [args...]
#
# Deliberately no param() block. PowerShell's parameter binder tries to match
# any "-name"-shaped argument against declared parameters even without
# [CmdletBinding()] and even when none match by full name, silently dropping
# it instead of passing it through positionally. That would swallow a
# worker's own short flags (for example claude's -p). Reading the automatic,
# unparsed $args array instead passes every argument through untouched.
$ErrorActionPreference = 'Stop'

if ($args.Count -lt 2) {
    Write-Error 'usage: pipe-prompt-file.ps1 <prompt-file> <command> [args...]'
    exit 2
}

$promptFile = $args[0]
$executable = $args[1]
$remaining = if ($args.Count -gt 2) { $args[2..($args.Count - 1)] } else { @() }

if (-not (Test-Path -LiteralPath $promptFile -PathType Leaf)) {
    Write-Error "pipe-prompt-file: prompt file not found: $promptFile"
    exit 2
}

Get-Content -LiteralPath $promptFile -Raw -Encoding UTF8 | & $executable @remaining
exit $LASTEXITCODE
