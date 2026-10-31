[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$RunId,
    [Parameter(Mandatory)] [string]$Task,
    [Parameter(Mandatory)] [string]$Workspace,
    [Parameter(Mandatory)] [string]$PromptFile,
    [string]$AtlasCollection,
    [string]$PythonExecutable,
    [string]$CredentialRoot,
    [string]$ResultsDir,
    [string]$AtlasDatabase = 'memory-dev',
    [string]$AtlasIndex = 'vector_benchmark_memory_v1',
    [string]$AtlasTextKey = 'search_text',
    [string]$AtlasEmbeddingKey = 'procedure_embedding',
    [string]$EverosApplication = 'memory-harness-benchmark',
    [string]$EverosProject,
    [string]$EverosNamespace,
    [string]$EverosOwner = 'root-benchmark',
    [ValidateSet('codex', 'claude-code')] [string]$Provider = 'codex',
    [string]$Model,
    [string]$PlannerModel,
    [ValidateSet('low', 'medium', 'high', 'xhigh', 'max', 'ultra')] [string]$PlannerReasoningEffort,
    [ValidateSet('low', 'medium', 'high', 'xhigh', 'max', 'ultra')] [string]$ReasoningEffort = 'high',
    [ValidateSet('low', 'medium', 'high', 'xhigh', 'max', 'ultra')] [string]$WorkerReasoningEffort,
    [ValidateSet('auto', 'default', 'flex', 'priority')] [string]$ServiceTier = 'default',
    [double]$WatchdogHours = 2,
    [switch]$OperatorAssistedContinuation,
    [string]$ResumeTaskFile,
    [switch]$PrepareOnly
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

if ($RunId -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]*$') {
    throw "RunId must contain only letters, digits, periods, underscores, and hyphens"
}
if ($Task -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]*$') {
    throw "Task must be a stable identifier containing only letters, digits, periods, underscores, and hyphens"
}
if ($AtlasDatabase -notmatch '^[A-Za-z0-9_][A-Za-z0-9_-]*$') {
    throw "AtlasDatabase contains unsupported characters"
}
# Keep benchmark memory isolated by exact run identity. A fresh scope must be
# verified empty during preparation; never clear or adopt a historical store.
if (-not $AtlasCollection) {
    $runScopeHasher = [Security.Cryptography.SHA256]::Create()
    try {
        $runScopeHash = [BitConverter]::ToString(
            $runScopeHasher.ComputeHash([Text.Encoding]::UTF8.GetBytes($RunId))
        ).Replace('-', '').ToLowerInvariant()
    } finally {
        $runScopeHasher.Dispose()
    }
    $AtlasCollection = "benchmark_run_$runScopeHash"
}
foreach ($value in @($AtlasCollection, $AtlasIndex, $AtlasTextKey, $AtlasEmbeddingKey)) {
    if ($value -notmatch '^[A-Za-z0-9_][A-Za-z0-9_.-]*$') {
        throw "Atlas collection, index, and field names must be nonempty simple identifiers"
    }
}
if (-not $EverosProject) { $EverosProject = $RunId }
if (-not $EverosNamespace) { $EverosNamespace = "$RunId-workers" }
if (-not $Model) { $Model = if ($Provider -eq 'claude-code') { 'claude-haiku-5-5' } else { 'gpt-5.6-terra' } }
if (-not $WorkerReasoningEffort) { $WorkerReasoningEffort = $ReasoningEffort }
if (-not $PlannerModel) { $PlannerModel = $Model }
if (-not $PlannerReasoningEffort) { $PlannerReasoningEffort = $WorkerReasoningEffort }
if ($WatchdogHours -le 0) { throw "WatchdogHours must be positive" }
$harness = Split-Path -Parent $PSScriptRoot
$productRoot = $harness
$repoRoot = $productRoot
$workspacePath = (Resolve-Path -LiteralPath $Workspace).Path
$promptPath = (Resolve-Path -LiteralPath $PromptFile).Path
if (-not $PythonExecutable) {
    $localPython = Join-Path $productRoot '.venv\Scripts\python.exe'
    $PythonExecutable = if (Test-Path -LiteralPath $localPython) { $localPython } else { 'python' }
}
if (-not $CredentialRoot) { $CredentialRoot = Join-Path $productRoot '.secrets\creds' }
if (-not $ResultsDir) { $ResultsDir = Join-Path $productRoot 'runtime\results' }
if (-not $ResumeTaskFile -and (Test-Path -LiteralPath (Join-Path $ResultsDir $RunId))) {
    throw "ROOT run $RunId already has launch evidence; use a fresh run ID and workspace"
}
$python = $PythonExecutable
$collector = Join-Path $productRoot 'scripts\collect_codex_usage.py'
$runtime = Join-Path $workspacePath '.harness-runtime'
$harnessConfigPath = Join-Path $harness 'harness-config.json'

if (-not (Get-Command $python -ErrorAction SilentlyContinue) -and -not (Test-Path -LiteralPath $python)) {
    throw "Python executable is missing: $python"
}
$pythonCommand = Get-Command $python -ErrorAction Stop
$pythonDirectory = Split-Path -Parent $pythonCommand.Source
$env:PATH = "$pythonDirectory$([IO.Path]::PathSeparator)$env:PATH"
$env:PYTHONDONTWRITEBYTECODE = '1'
foreach ($requiredPath in @($collector, (Join-Path $CredentialRoot 'MongoDB.txt'), (Join-Path $CredentialRoot 'DeepInfra.txt'))) {
    if (-not (Test-Path -LiteralPath $requiredPath)) {
        throw "Required launch input is missing: $requiredPath"
    }
}
$harnessConfig = Get-Content -LiteralPath $harnessConfigPath -Raw | ConvertFrom-Json
if ([IO.Path]::GetFullPath($harnessConfig.root_workspace) -ine $workspacePath -or
    $harnessConfig.managed_coordination -ne 'enabled') {
    throw "harness-config.json must select the fresh ROOT workspace with managed coordination enabled"
}
$prompt = Get-Content -LiteralPath $promptPath -Raw -Encoding UTF8
if ($prompt -match 'memory-recall\.md|operator.*preflight') {
    throw "The fresh ROOT prompt must not tell ROOT to read operator-prepared memory"
}
$agentsPath = Join-Path $workspacePath 'AGENTS.md'
if ((Test-Path -LiteralPath $agentsPath) -and
    ((Get-Content -LiteralPath $agentsPath -Raw) -match 'memory-recall\.md|operator.*preflight')) {
    throw "The fresh AGENTS.md must not tell ROOT to read operator-prepared memory"
}

$mongoUri = Get-Content -LiteralPath (Join-Path $CredentialRoot 'MongoDB.txt') |
    ForEach-Object { $_.Trim() } |
    Where-Object { $_ -match '^mongodb(?:\+srv)?://' } |
    Select-Object -First 1
$deepInfraApiKey = Get-Content -LiteralPath (Join-Path $CredentialRoot 'DeepInfra.txt') |
    ForEach-Object { $_.Trim() } |
    Where-Object { $_ -and -not $_.StartsWith('#') } |
    Select-Object -First 1
if (-not $mongoUri -or -not $deepInfraApiKey) {
    throw "The Atlas or embedder credential could not be loaded"
}

$memoryRuntime = Join-Path $productRoot 'runtime'

# The elevated Windows sandbox validates executables below LOCALAPPDATA.
# Desktop CUA runtimes can be in use and locked; give this CLI run its own
# cache root without changing the user's environment or relaxing isolation.
if ($Provider -eq 'codex') {
    $env:LOCALAPPDATA = Join-Path $memoryRuntime 'host-localappdata'
    New-Item -ItemType Directory -Path $env:LOCALAPPDATA -Force | Out-Null
    # Inspection only. Never initiate or repeat sandbox setup from a launcher.
    & $python -B (Join-Path $productRoot 'scripts\check_windows_sandbox.py') `
        --harness-dir $harness --workspace $workspacePath
    if ($LASTEXITCODE -ne 0) { throw 'Windows sandbox preflight failed; diagnose before another launch' }
}

$env:MEMORY_HARNESS_RUN_ID = $RunId
$env:MEMORY_HARNESS_TASK_ID = $Task
$env:MEMORY_HARNESS_ATLAS_URI = $mongoUri
$env:MEMORY_HARNESS_ATLAS_DATABASE = $AtlasDatabase
$env:MEMORY_HARNESS_ATLAS_COLLECTION = $AtlasCollection
$env:MEMORY_HARNESS_ATLAS_INDEX = $AtlasIndex
$env:MEMORY_HARNESS_ATLAS_TEXT_KEY = $AtlasTextKey
$env:MEMORY_HARNESS_ATLAS_EMBEDDING_KEY = $AtlasEmbeddingKey
$env:MEMORY_HARNESS_EVEROS_APPLICATION = $EverosApplication
$env:MEMORY_HARNESS_EVEROS_PROJECT = $EverosProject
$env:MEMORY_HARNESS_EVEROS_NAMESPACE = $EverosNamespace
$env:MEMORY_HARNESS_EVEROS_OWNER = $EverosOwner
$env:DEEPINFRA_API_KEY = $deepInfraApiKey
$env:EVEROS_EMBEDDING__MODEL = 'Qwen/Qwen3-Embedding-4B'
$env:EVEROS_EMBEDDING__API_KEY = $deepInfraApiKey
$env:EVEROS_EMBEDDING__BASE_URL = 'https://api.deepinfra.com/v1/openai'
$env:PYTHONPATH = "$(Join-Path $productRoot 'src');$harness"
$env:MEMORY_HARNESS_EVEROS_BASE_ROOT = Join-Path $memoryRuntime 'memory\everos'

$env:MEMORY_HARNESS_MONITOR_LOG_PATH = Join-Path $runtime 'monitor\MONITOR.log'
$env:MEMORY_HARNESS_DETAIL_LOG_PATH = Join-Path $runtime 'monitor\MONITOR_DETAIL.log'
$env:MEMORY_HARNESS_IMPORTANT_LOG_PATH = Join-Path $runtime 'monitor\MONITOR_IMPORTANT.log'
$env:MEMORY_HARNESS_OPERATOR_LOG_PATH = Join-Path $runtime 'monitor\MONITOR_OPERATOR_MEMORY.log'
$env:MEMORY_HARNESS_WORKER_RECALL = '1'
Remove-Item Env:MEMORY_HARNESS_ALWAYS_CONTEXT_PATH -ErrorAction SilentlyContinue
Remove-Item Env:MEMORY_HARNESS_REQUIRE_ROOT_RECALL -ErrorAction SilentlyContinue
Remove-Item Env:MEMORY_HARNESS_ACTOR -ErrorAction SilentlyContinue

# Native ROOT hooks are discovered when Codex starts, so setup must be an
# operator action before the collector starts the ROOT process.
$preparationArgs = @('--harness-dir', $harness, '--workspace', $workspacePath, '--run-id', $RunId, '--provider', $Provider)
if ($ResumeTaskFile) { $preparationArgs += @('--resume-task-file', $ResumeTaskFile) }
& $python -B (Join-Path $productRoot 'scripts\prepare_root_launch.py') @preparationArgs
if ($LASTEXITCODE -ne 0) { throw 'Native harness setup failed before ROOT launch' }

if ($ResumeTaskFile) {
    if ($PrepareOnly) { Write-Output 'Prepared ROOT continuation; no ROOT process was launched.'; exit 0 }
    # The collector writes its artifact location to stderr even on success.
    # Preserve its actual exit code, as the fresh-launch branch does below.
    $ErrorActionPreference = 'Continue'
    & $python -B $collector resume --task-file $ResumeTaskFile --prompt-file $promptPath --continue-open-runtime
    exit $LASTEXITCODE
}

$effectivePrompt = Join-Path $workspacePath '.agent-workspace\ROOT_WORKER_MEMORY_PROMPT.md'
New-Item -ItemType Directory -Path (Split-Path -Parent $effectivePrompt) -Force | Out-Null
@"
# Run settings

RUN_ID: $RunId
ROOT_WORKSPACE: $workspacePath
HARNESS_DIR: $harness
ROOT_PROVIDER: $Provider
ROOT_MODEL: $Model
ROOT_REASONING_EFFORT: $ReasoningEffort
PLANNER_MODEL: $PlannerModel
PLANNER_REASONING_EFFORT: $PlannerReasoningEffort
WORKER_MODEL: $Model
WORKER_PROVIDER: $Provider
WORKER_REASONING_EFFORT: $WorkerReasoningEffort
SERVICE_TIER: $(if ($Provider -eq 'codex') { $ServiceTier } else { 'not-applicable' })
RUN_TIME_LIMIT_MINUTES: $($WatchdogHours * 60)
RUN_BUDGET_FILE: $(Join-Path $workspacePath '.agent-workspace\RUN_BUDGET.json')
OPERATOR_ASSISTED_CONTINUATION: $($OperatorAssistedContinuation.IsPresent)

$prompt
"@ | Set-Content -LiteralPath $effectivePrompt -Encoding UTF8

if ($PrepareOnly) {
    Write-Output "Prepared ROOT run $RunId; no $Provider ROOT process was launched."
    exit 0
}

$ErrorActionPreference = 'Continue'
$continuationArgs = @()
if ($OperatorAssistedContinuation) { $continuationArgs = @('--operator-assisted') }
if ($Provider -eq 'codex') { $continuationArgs += @('--service-tier', $ServiceTier) }
& $python $collector run `
    --run-id $RunId `
    --task $Task `
    --arm harness `
    --cwd $workspacePath `
    --prompt-file $effectivePrompt `
    --results-dir $ResultsDir `
    --model $Model `
    --provider $Provider `
    --reasoning-effort $ReasoningEffort `
    --sandbox danger-full-access `
    --harness-runtime $runtime `
    --harness-dir $harness `
    --watchdog-hours $WatchdogHours `
    --trust-project-hooks @continuationArgs
exit $LASTEXITCODE
