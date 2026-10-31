[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

function Assert-That {
    param(
        [Parameter(Mandatory = $true)][bool]$Condition,
        [Parameter(Mandatory = $true)][string]$Message
    )

    if (-not $Condition) { throw $Message }
}

$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$hooksPath = Join-Path $repositoryRoot '.codex\hooks.json'
$scriptPath = Join-Path $repositoryRoot '.agent\hooks.py'

Assert-That (Test-Path -LiteralPath $hooksPath -PathType Leaf) 'Missing .codex/hooks.json.'
Assert-That (Test-Path -LiteralPath $scriptPath -PathType Leaf) 'Missing .agent/hooks.py.'
Assert-That ($null -ne (Get-Command py -ErrorAction SilentlyContinue)) 'Python launcher "py" is required for the Windows hook.'

$configuration = Get-Content -Raw -LiteralPath $hooksPath | ConvertFrom-Json
$sessionHooks = @($configuration.hooks.SessionStart[0].hooks)
$preToolHooks = @($configuration.hooks.PreToolUse[0].hooks)

Assert-That ($sessionHooks.Count -eq 1) 'SessionStart must not run the inactive Stop-verification baseline.'
Assert-That ($sessionHooks[0].commandWindows -eq 'py -3 .agent\hooks.py session-start') 'SessionStart must launch the Python hook directly.'
Assert-That ($preToolHooks[0].commandWindows -eq 'py -3 .agent\hooks.py pre-tool-use') 'PreToolUse must launch the Python hook directly.'
Assert-That ($sessionHooks[0].commandWindows -notmatch '(?i)powershell(?:\.exe)?') 'SessionStart must not start a nested PowerShell process.'
Assert-That ($preToolHooks[0].commandWindows -notmatch '(?i)powershell(?:\.exe)?') 'PreToolUse must not start a nested PowerShell process.'
Assert-That ($null -ne $configuration.hooks.Stop) 'The Stop verification hook must remain configured.'

$sessionPayload = @{ cwd = $repositoryRoot } | ConvertTo-Json -Compress
Push-Location $repositoryRoot
try {
    $elapsed = Measure-Command {
        $sessionOutput = $sessionPayload | & py -3 .agent\hooks.py session-start
        $sessionExitCode = $LASTEXITCODE
    }
    Assert-That ($sessionExitCode -eq 0) "SessionStart hook exited with $sessionExitCode."
    Assert-That ($elapsed.TotalSeconds -lt 3) ("SessionStart hook exceeded the 3-second deadline ({0:N3}s)." -f $elapsed.TotalSeconds)

    $sessionResult = $sessionOutput | ConvertFrom-Json
    Assert-That ($sessionResult.hookSpecificOutput.hookEventName -eq 'SessionStart') 'SessionStart did not produce SessionStart context.'
    Assert-That ($sessionResult.hookSpecificOutput.additionalContext -match 'Portable workflow active') 'SessionStart context is incomplete.'

    $deletePayload = @{
        cwd = $repositoryRoot
        tool_input = @{ command = 'Remove-Item -Recurse -Force C:\' }
    } | ConvertTo-Json -Compress -Depth 4
    $deleteOutput = $deletePayload | & py -3 .agent\hooks.py pre-tool-use
    Assert-That ($LASTEXITCODE -eq 0) "PreToolUse hook exited with $LASTEXITCODE."
    $deleteResult = $deleteOutput | ConvertFrom-Json
    Assert-That ($deleteResult.hookSpecificOutput.permissionDecision -eq 'deny') 'PreToolUse did not block recursive deletion of a filesystem root.'
}
finally {
    Pop-Location
}

Write-Output 'PASS: Windows SessionStart and PreToolUse launch hook scripts without a nested PowerShell process.'
