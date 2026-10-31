[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Agent,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Role,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Task,

    [string]$WorkingDirectory = (Get-Location).Path,
    [string]$Scope = '',
    [string]$Owner = '',
    [string]$AcceptanceCheck = '',
    [int]$HeartbeatIntervalSeconds = 0,
    [switch]$Background,
    [switch]$DryRun,
    [switch]$AllowSharedWorkspace
)

$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot 'multi_agent.py'
$python = Get-Command python -ErrorAction SilentlyContinue
if ($null -eq $python) {
    throw 'Python 3 is required to launch a portable multi-agent worker.'
}

$arguments = @(
    $scriptPath,
    'launch',
    '--agent', $Agent,
    '--role', $Role,
    '--task', $Task,
    '--working-directory', $WorkingDirectory
)
if ($Scope) { $arguments += @('--scope', $Scope) }
if ($Owner) { $arguments += @('--owner', $Owner) }
if ($AcceptanceCheck) { $arguments += @('--acceptance-check', $AcceptanceCheck) }
if ($HeartbeatIntervalSeconds -gt 0) { $arguments += @('--heartbeat-interval-seconds', $HeartbeatIntervalSeconds) }
if ($Background) { $arguments += '--background' }
if ($DryRun) { $arguments += '--dry-run' }
if ($AllowSharedWorkspace) { $arguments += '--allow-shared-workspace' }

& $python.Source @arguments
exit $LASTEXITCODE
