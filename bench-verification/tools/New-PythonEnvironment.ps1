[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$Destination,
    [string]$BasePython = 'python'
)
$ErrorActionPreference = 'Stop'
$bundleRoot = Split-Path -Parent $PSScriptRoot
$harnessPath = (Resolve-Path -LiteralPath (Join-Path $bundleRoot '../harness-single-run-version')).Path
$destinationPath = [IO.Path]::GetFullPath($Destination)
if (Test-Path -LiteralPath $destinationPath) { throw 'Destination already exists; use a new environment path.' }
& $BasePython -c 'import sys; assert sys.version_info >= (3, 12), "Python 3.12+ is required"'
if ($LASTEXITCODE -ne 0) { throw 'Base Python version check failed.' }
& $BasePython -m venv $destinationPath
if ($LASTEXITCODE -ne 0) { throw 'Environment creation failed; preserve it and diagnose before another attempt.' }
$pythonPath = Join-Path $destinationPath 'Scripts/python.exe'
& $pythonPath -m pip install -r (Join-Path $bundleRoot 'requirements-snapshot.txt')
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed; preserve evidence and diagnose.' }
& $pythonPath -m pip install --no-deps -e $harnessPath -e (Join-Path $harnessPath 'vendor/everos') -e (Join-Path $harnessPath 'vendor/langchain-mongodb')
if ($LASTEXITCODE -ne 0) { throw 'Local package installation failed; preserve evidence and diagnose.' }
Write-Output "Environment created: $pythonPath"
Write-Output 'Select this Python path in the intended fresh run.json. No native setup or benchmark was launched.'
