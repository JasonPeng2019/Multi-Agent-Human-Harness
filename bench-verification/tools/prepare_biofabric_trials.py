"""Prepare isolated public workspaces and native harness configuration; no model launch."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess
import sys

BASE=Path(__file__).resolve().parents[2]
BENCH=BASE/'bench-verification'
ASSETS=BENCH/'biofabric'
PRIMARY=BASE/'harness-single-run-version'
PYTHON=PRIMARY/'.venv/Scripts/python.exe'
CREDS=Path('C:/Users/Jason/Documents/Jason/Orchestrator_Harness-Bench-Testing/.secrets/creds')

def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2)+'\n',encoding='utf-8')

def git(w,*args):
    return subprocess.check_output(['git','-C',str(w),*args],stderr=subprocess.STDOUT).decode().strip()

def main():
    assets=json.loads((ASSETS/'ASSETS.json').read_text())
    assert assets.get('starter_compile_exit')==0
    assert not (BENCH/'root_runs').exists(), 'Preserve and inspect any existing preparation.'
    for name in ('h2','hx'):
        target=BENCH/name
        assert not target.exists()
        shutil.copytree(PRIMARY,target,ignore=shutil.ignore_patterns('.git','.venv','vendor','__pycache__','.pytest_cache','runtime','.agent-workspace','worktree','harness-config.json','local-config'))
        (target/'local-config').mkdir()
    now=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    original=(ASSETS/'workflow-seed/ROOT_RUN_PROMPT.md').read_text()
    operational=original.split('# Benchmark task')[0]
    operational=operational.replace('four hours','3 hours 45 minutes').replace('four-hour','3-hour-45-minute').replace('high effort','low effort').replace('effort=high','effort=low')
    operational=operational.replace('Do not alter fixed inputs or the Makefile','Do not alter fixed inputs or public API signatures')
    operational=operational.replace('Leave the runtime quiescent and OPEN for operator audit and grading. Do not replace the epoch. The operator performs native shutdown and usage finalization.', 'Finish native cleanup and shutdown to CLOSED before returning, as required by the installed Stop hook. Do not replace the epoch. If continued, reopen and retain this exact epoch ID, session and original collector deadline.')
    task=(ASSETS/'operator-only/instruction.md').read_text().replace('You have 10 hours. Run `bash /app/timer.sh` to check how much wall-clock time remains.','You have 3 hours 45 minutes, enforced by the CLI collector. Read the host collector budget helper for the actual remaining allowance; the upstream container timer is not authoritative for this shortened run.')
    public='''
\n# Public task execution and final audit

The host is Windows. The Rust starter, Java references under `reference/`, and public tests/goldens are present here. `/app` and `/reference` in the original task refer to the offline Linux public-check image; use workspace `reference/BioFabric/` and `reference/AlignmentPlugin/` when reading Java on the host. Do not use the internet, sibling experiments, benchmark source checkout, hidden tests, oracle or encrypted private payload.

Commit task changes before requesting public builds/tests with `.agent-workspace/public-check.py`. ROOT may run its candidate with `python PUBLIC_ADAPTER --worktree ROOT_WORKSPACE -- cargo test --workspace --no-fail-fast --offline --locked`. Use this deterministic bridge for Linux Rust checks, not Docker directly. Inputs and the registry are preloaded. Fixed manifests/lockfile, reference source, test fixtures and existing test files are immutable; only `crates/core/tests/parity_tests/runners.rs` is an editable existing test. Private helpers and focused tests go in task source or committed `scratch/`.

Reserve enough remaining time for the independent module validators and the final deterministic test validator plus semantic reviewer. Launch the final pair in parallel on the same integrated candidate, then inspect and formally accept both reports. Record their lane IDs, exact revision, checks, findings and formal acceptances in WORKFLOW_COMPLETION.md. Honest partial progress still requires this workflow unless the deadline or a documented blocker prevents it. ROOT coordinates and integrates; it does not implement task code. All Claude invocations use `--dangerously-skip-permissions` and Sonnet 5 / low effort. Preserve the first reported finish. Authorized workflow corrections resume this same session and epoch without resetting the allowance.
'''.replace('PUBLIC_ADAPTER',str(ASSETS/'support/public_check_adapter.py'))
    runs=[]
    for short,harness in [('b1',PRIMARY),('b2',BENCH/'h2'),('b0',None)]:
        rd=BENCH/'root_runs'/short;w=rd/'w';shutil.copytree(ASSETS/'template',w)
        run_id=f'biofabric-sonnet5-low-{short}-{now}'
        for bad in ('.git','.claude','.harness-runtime','.agent-workspace','private.enc'):
            assert not (w/bad).exists()
        (w/'.gitignore').write_text('target/\n.harness-runtime/\n.agent-workspace/\n.root-task-cards/\n.codex/\n.qwen/\n.claude/settings.json\n.claude/hooks/\n.claude/orchestrator-harness-binding.json\n.claude/skills/*\n'+''.join(f'!.claude/skills/{s}/\n' for s in ('plan','workflow-1','stay-current','principles')))
        if harness:
            for name in ('AGENTS.md','CLAUDE.md'):shutil.copyfile(ASSETS/'workflow-seed'/name,w/name)
            for skill in ('plan','workflow-1','stay-current','principles'):shutil.copytree(ASSETS/'workflow-seed/skills'/skill,w/'.claude/skills'/skill)
            prompt=operational+'# Benchmark task\n\n'+task+public
            prompt_path=w/'ROOT_RUN_PROMPT.md';prompt_path.write_text(prompt)
            write(harness/'harness-config.json',{'root_workspace':str(w),'managed_coordination':'enabled'})
            fixed=['Cargo.toml','Cargo.lock','tests','reference','timer.sh']
            fixed += [p.relative_to(w).as_posix() for p in (w/'crates').rglob('*') if p.is_file() and ('/tests/' in p.as_posix() or p.name=='Cargo.toml') and p.name!='runners.rs']
            adapter=ASSETS/'support/public_check_adapter.py'
            write(harness/'local-config/public-check-policy.json',{'schema':'public-check-policy/v2','adapter':{'path':str(adapter),'sha256':hashlib.sha256(adapter.read_bytes()).hexdigest()},'input_paths':['crates','tests','reference','Cargo.toml','Cargo.lock','timer.sh'],'optional_input_paths':['scratch'],'fixed_paths':fixed,'commands':{'build':['cargo','test','--workspace','--no-run','--locked','--offline'],'public':['cargo','test','--workspace','--no-fail-fast','--locked','--offline','--','--test-threads=4']},'allow_focused':True,'timeout_seconds':600,'max_parallel_checks':1})
        else:
            native='''You are implementing the real BioFabric task below. Break it into steps and use your own native Claude Code CLI subagents as you see fit. Choose your own delegation, checks and integration; use Sonnet 5 at low effort for yourself and every native subagent, with --dangerously-skip-permissions. You have 3 hours 45 minutes total, enforced by the collector watchdog; finish within the actual remaining allowance. Do not inspect sibling runs, benchmark source checkout, hidden tests, prior solutions, oracle or secrets. Use only the public starter, Java references and visible tests in this workspace. This is a native comparison, with no harness workflow or prescribed validator topology.\n\n'''
            native+=task+'\n\nThe host is Windows. Read Java under workspace reference/. Linux Rust builds/tests run through `python .baseline/check.py -- cargo test --workspace --no-fail-fast --locked --offline`; this is a deterministic offline environment bridge, not an agent harness. The upstream container timer is not authoritative; `python .baseline/check.py --time` reads the collector deadline. Do not change public API signatures, manifests, fixed fixtures or existing tests except crates/core/tests/parity_tests/runners.rs. Private helpers and focused tests may be added.\n'
            prompt_path=rd/'PROMPT.md';prompt_path.write_text(native)
            baseline=w/'.baseline';baseline.mkdir()
            (baseline/'check.py').write_text('''from pathlib import Path
import json,subprocess,sys
from datetime import datetime,timezone
w=Path(__file__).resolve().parents[1]
if sys.argv[1:]==['--time']:
 p=next((w.parent/'out').glob('*/launch.json'));r=json.loads(p.read_text());deadline=datetime.fromisoformat(r['watchdog_deadline_utc'].replace('Z','+00:00'));print(json.dumps({'deadline_utc':deadline.isoformat(),'remaining_minutes':max(0,(deadline-datetime.now(timezone.utc)).total_seconds()/60)}));raise SystemExit(0)
raise SystemExit(subprocess.call([sys.executable,ADAPTER,'--worktree',str(w),*sys.argv[1:]]))
'''.replace('ADAPTER',repr(str(ASSETS/'support/public_check_adapter.py'))))
        git(w,'init','-b','main');git(w,'config','user.name','Benchmark Operator');git(w,'config','user.email','benchmark@local.invalid');git(w,'config','core.longpaths','true');git(w,'config','core.autocrlf','false');git(w,'add','.');git(w,'commit','-m','Public BioFabric starter and independent trial instructions')
        record={'run_id':run_id,'task':'biofabric-rust-rewrite','workspace':str(w),'harness_dir':str(harness) if harness else None,'prompt_file':str(prompt_path),'results_dir':str(rd/'out'),'python_executable':str(PYTHON),'credential_root':str(CREDS),'provider':'claude-code','model':'claude-sonnet-5','effort':'low','worker_effort':'low','planner_model':'claude-sonnet-5','planner_effort':'low','watchdog_hours':3.75,'work_seconds':13500,'operator_assisted':bool(harness),'initial_revision':git(w,'rev-parse','HEAD'),'root_launches':0,'status':'PREPARED','arm':'harness' if harness else 'raw','workflow_supplied':bool(harness),'resume_policy':'Audit reported finishes; workflow correction retains session/epoch/remaining allowance. Usage-blocked unfinished runs resume at 06:40 Eastern with remaining allowance; native reported task finishes do not trigger workflow continuation.','input_sha256':{p.relative_to(w).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in w.rglob('*') if p.is_file() and '.git' not in p.relative_to(w).parts}}
        write(rd/'run.json',record);runs.append(record)
    sys.path.insert(0,str(PRIMARY/'src'))
    from pymongo import MongoClient
    from memory_harness.experience import ExperienceScope,EverOSAdapter
    uri=next(line.strip() for line in (CREDS/'MongoDB.txt').read_text(encoding='utf-8-sig').splitlines() if line.strip().startswith(('mongodb://','mongodb+srv://')))
    client=MongoClient(uri,serverSelectionTimeoutMS=15000)
    try:
        for run in runs:
            if not run['harness_dir']:continue
            collection='benchmark_run_'+hashlib.sha256(run['run_id'].encode()).hexdigest()
            count=client['memory-dev'][collection].count_documents({});assert count==0
            scope=ExperienceScope(application='memory-harness-benchmark',project=run['run_id'],namespace=run['run_id']+'-workers',owner='root-benchmark')
            memory_root=EverOSAdapter.memory_root_for_scope(Path(run['harness_dir'])/'runtime/memory/everos',scope)
            assert not memory_root.exists()
            run['memory']={'atlas_collection':collection,'atlas_count':count,'everos_root':str(memory_root),'everos_scope_exists':False,'verified_at_utc':datetime.now(timezone.utc).isoformat()};write(Path(run['workspace']).parent/'run.json',run)
    finally:client.close()
    write(ASSETS/'TRIAL_PREPARATION.json',{'status':'PASS','model_launches':0,'runs':[r['run_id'] for r in runs],'collector_accounting_tests_passed':14,'prepared_at_utc':datetime.now(timezone.utc).isoformat()})
    print(json.dumps({'status':'PASS','runs':[r['run_id'] for r in runs]}),flush=True)

if __name__=='__main__':main()
