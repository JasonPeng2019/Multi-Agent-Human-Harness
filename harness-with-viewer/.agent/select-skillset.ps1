[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [ValidateSet('current', 'software', 'research')]
    [string]$Command
)

$ErrorActionPreference = 'Stop'
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    & $python.Path (Join-Path $PSScriptRoot 'select-skillset.py') $Command
    exit $LASTEXITCODE
}
$py = Get-Command py -ErrorAction SilentlyContinue
if ($py) {
    & $py.Path -3 (Join-Path $PSScriptRoot 'select-skillset.py') $Command
    exit $LASTEXITCODE
}
Write-Error 'select-skillset: Python 3 is required.'
