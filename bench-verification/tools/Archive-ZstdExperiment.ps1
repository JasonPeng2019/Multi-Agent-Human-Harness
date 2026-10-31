[CmdletBinding()]
param()
$ErrorActionPreference='Stop'
$base=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$archive=[IO.Path]::GetFullPath((Join-Path $base 'archive\zstd-cancelled-20261031'))
if(Test-Path -LiteralPath $archive){throw 'Archive already exists; inspect the prior attempt.'}
$live=@(Get-CimInstance Win32_Process)
$checks=@()
foreach($short in @('s0','s1','s2')){
  $run=Join-Path $base "bench-verification\root_runs\$short"
  $stop=Join-Path $run 'OPERATOR_STOP_REQUEST.json'
  if($short -eq 's1'){$stop=Join-Path $run 'OPERATOR_STOP_EXACT_IDENTITY.json'}
  $record=Get-Content -LiteralPath $stop -Raw|ConvertFrom-Json
  foreach($owned in $record.owned_processes){
    $found=@($live|Where-Object ProcessId -eq $owned.pid)
    if($found.Count){
      $actual=(Get-Process -Id $owned.pid -ErrorAction Stop).StartTime.ToUniversalTime().ToString('o')
      if($actual -eq $owned.creation_time_utc){throw "Owned process still live: $($owned.pid)"}
    }
    $checks+=@{run=$short;pid=$owned.pid;recorded_creation=$owned.creation_time_utc;same_process_live=$false}
  }
  $state=Join-Path $run 'w\.harness-runtime\RUNTIME_STATE.json'
  if(Test-Path -LiteralPath $state){
    if((Get-Content -LiteralPath $state -Raw|ConvertFrom-Json).state -ne 'CLOSED'){throw "Runtime $short not closed"}
  }
}
$relative=@(
 'bench-verification\root_runs','bench-verification\h3',
 'bench-verification\benchmarks\swe-marathon\tasks\zstd-decoder',
 'bench-verification\benchmarks\task-templates\zstd-decoder',
 'bench-verification\images\zstd-decoder-asset-repair-v2-20261015.docker.tar',
 'bench-verification\reference','bench-verification\tools\grade_zstd_checkpoint.py',
 'bench-verification\tools\score_zstd_run.py',
 'harness-single-run-version\harness-config.json',
 'harness-single-run-version\local-config\public-check-policy.json',
 'harness-single-run-version\local-config\ROOT_RUN_PROMPT.md',
 'harness-single-run-version\task-tools\zstd_check_adapter.py',
 'harness-single-run-version\task-tools\test_zstd_check_adapter.py',
 'harness-single-run-version\task-tools\public-check-policy.v2.json',
 'harness-single-run-version\.agent-workspace','harness-single-run-version\worktree'
)
$research=Join-Path $base 'bench-verification\operator-research'
foreach($p in Get-ChildItem -LiteralPath $research -Force){
 if($p.Name -match 'zstd' -and $p.Name -notmatch 'haiku55-consistent'){
  $relative+=('bench-verification\operator-research\'+$p.Name)
 }
}
$sources=@()
foreach($rel in $relative){
 $source=[IO.Path]::GetFullPath((Join-Path $base $rel))
 $dest=[IO.Path]::GetFullPath((Join-Path $archive $rel))
 if(-not $source.StartsWith($base+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Unsafe archive source'}
 if(-not $dest.StartsWith($archive+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)){throw 'Unsafe archive destination'}
 if(Test-Path -LiteralPath $source){$sources+=@{relative=$rel;source=$source;destination=$dest}}
}
New-Item -ItemType Directory -Path $archive|Out-Null
$checks|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $archive 'STOP_VERIFICATION.json') -Encoding UTF8
$docs=Join-Path $archive 'prior-active-documents'
New-Item -ItemType Directory -Path $docs|Out-Null
foreach($name in @('AGENTS.md','CODING_AGENT_ENTRYPOINT.md','CURRENT_HARNESS.md','CODING_AGENT_HANDOFF.md','ACTIVE_RUNS.json','README.md')){
 Copy-Item -LiteralPath (Join-Path $base $name) -Destination (Join-Path $docs $name)
}
$manifest=@()
foreach($item in $sources){
 $source=Get-Item -LiteralPath $item.source -Force
 $files=if($source.PSIsContainer){@(Get-ChildItem -LiteralPath $item.source -File -Recurse -Force)}else{@($source)}
 foreach($file in $files){
  $rel=$file.FullName.Substring($base.Length+1)
  $manifest+=@{path=$rel;bytes=$file.Length;sha256=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()}
 }
}
@{schema='zstd-archive/v1';created_at_utc=[DateTime]::UtcNow.ToString('o');files=$manifest;targets=$sources.relative}|ConvertTo-Json -Depth 8|Set-Content -LiteralPath (Join-Path $archive 'MANIFEST.json') -Encoding UTF8
foreach($item in $sources){
 New-Item -ItemType Directory -Path (Split-Path -Parent $item.destination) -Force|Out-Null
 Move-Item -LiteralPath $item.source -Destination $item.destination
}
foreach($file in $manifest){
 $saved=Join-Path $archive $file.path
 if((Get-FileHash -LiteralPath $saved -Algorithm SHA256).Hash.ToLowerInvariant() -ne $file.sha256){throw "Archive hash mismatch: $($file.path)"}
}
@{status='PASS';files=$manifest.Count;bytes=($manifest|Measure-Object -Property bytes -Sum).Sum;verified_at_utc=[DateTime]::UtcNow.ToString('o');models_launched=0}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $archive 'ARCHIVE_VERIFICATION.json') -Encoding UTF8
@'
# Archived Zstd experiment

The user cancelled these trials and requested archiving their tasks and repositories.
Candidate Git repositories, transcripts, stopped runtime evidence, Zstd task sources,
image archive, reference material, scoring tools, isolated h3 harness and former
configuration are retained here. MANIFEST.json hashes every moved regular file.
Original paths inside historical receipts remain provenance; no trial was resumed.
The reusable primary harness, official dependency submodules, other SWE Marathon
tasks and the sibling original repository were preserved. Docker image cache was
retained. New BioFabric runs use fresh identities, workspaces and isolated memory.
'@|Set-Content -LiteralPath (Join-Path $archive 'README.md') -Encoding UTF8
Get-Content -LiteralPath (Join-Path $archive 'ARCHIVE_VERIFICATION.json')
