"""Prepare public Excel task inputs, workflow and isolated memory; launches no model."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess,sys

BASE=Path(__file__).resolve().parents[2]
BENCH=BASE/'bench-verification'
PRIMARY=BASE/'harness-single-run-version'
EXCEL=BENCH/'excel'

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

def main():
    rd=BENCH/'root_runs/e1';w=rd/'w';h=BENCH/'hx'
    assert not rd.exists()
    (w/'app/data').mkdir(parents=True)
    (w/'app/.gitkeep').write_text('')
    shutil.copytree(EXCEL/'task/environment/dev_tests',w/'dev_tests')
    seed=BENCH/'biofabric/workflow-seed'
    for n in ('AGENTS.md','CLAUDE.md'):shutil.copyfile(seed/n,w/n)
    for s in ('plan','workflow-1','stay-current','principles'):shutil.copytree(seed/'skills'/s,w/'.claude/skills'/s)
    (w/'.gitignore').write_text('.harness-runtime/\n.agent-workspace/\n.root-task-cards/\n.codex/\n.qwen/\n.claude/settings.json\n.claude/hooks/\n.claude/orchestrator-harness-binding.json\n.claude/skills/*\n'+''.join(f'!.claude/skills/{s}/\n' for s in ('plan','workflow-1','stay-current','principles'))+'app/data/*\napp/node_modules/\napp/.venv/\n**/__pycache__/\n')
    operational=(seed/'ROOT_RUN_PROMPT.md').read_text().split('# Benchmark task')[0]
    operational=operational.replace('claude-sonnet-5','claude-haiku-5-5').replace('high effort','max effort').replace('effort=high','effort=max')
    operational=operational.replace('Do not alter fixed inputs or the Makefile','Do not alter fixed inputs or the public test harness')
    operational=operational.replace('Leave the runtime quiescent and OPEN for operator audit and grading. Do not replace the epoch. The operator performs native shutdown and usage finalization.','Finish native cleanup and shutdown to CLOSED before returning as required by the installed Stop hook. Preserve this exact epoch ID and native session on any authorized continuation; the original remaining allowance is shared across all segments.')
    task=(EXCEL/'task/instruction.md').read_text().replace('You have 6 hours. Run `bash /app/timer.sh` to check how much wall-clock time remains.','You have four hours, enforced by the CLI collector watchdog. Read the host collector budget helper for the actual remaining allowance; the original container timer is not authoritative for this shortened run.')
    public='''
\n# Host task layout, public execution and final audit

This host is Windows. Implement the actual product entirely under the Git workspace's `app/` directory; it is copied to `/app/` in the Linux task container. The required product entrypoint is therefore host `app/start.sh`, exposed in the container as `/app/start.sh`. Preserve `dev_tests/` as read-only public test documentation; the image supplies the authoritative `/dev_tests/` bytes. The product has no starter implementation and no prior solution.

Commit before checking. Native workers request public tests with `.agent-workspace/public-check.py`. ROOT may use `python EXCEL_ADAPTER --worktree ROOT_WORKSPACE -- bash /dev_tests/run.sh`, or focused shell commands in the same container. Dependencies can be installed in this public task environment; make start.sh self-contained/reproducible and preserve all durable app data under /app/data. Use the deterministic environment bridge, never Docker directly. No hidden tests, verifier, oracle, prior solutions, sibling runs, credentials or benchmark checkout may be inspected.

All ROOT and worker invocations use claude-haiku-5-5, max effort, and --dangerously-skip-permissions. ROOT plans, delegates and integrates; it does not implement task code. Reserve time for independent per-module deterministic validators and the final deterministic validator plus semantic reviewer. Launch the final pair in parallel on the same integrated candidate, inspect their evidence, formally accept both, and record lane IDs, candidate revision, checks/findings and acceptance references in WORKFLOW_COMPLETION.md. Preserve the first reported finish. If the operator identifies missing workflow, continue this same native session and epoch within the remaining allowance. An implementer checkpoint or public checks alone do not replace the independent final pair.
'''.replace('EXCEL_ADAPTER',str(EXCEL/'support/public_check_adapter.py'))
    (w/'ROOT_RUN_PROMPT.md').write_text(operational+'# Benchmark task\n\n'+task+public)
    for args in [('init','-b','main'),('config','user.name','Benchmark Operator'),('config','user.email','benchmark@local.invalid'),('config','core.longpaths','true'),('config','core.autocrlf','false'),('add','.'),('commit','-m','Public Excel starter, visible tests and workflow instructions')]:subprocess.run(['git','-C',str(w),*args],check=True,capture_output=True)
    rev=subprocess.check_output(['git','-C',str(w),'rev-parse','HEAD'],text=True).strip()
    now=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');run_id='excel-haiku55-max-e1-'+now
    run={'run_id':run_id,'task':'excel-clone','arm':'harness','workspace':str(w),'harness_dir':str(h),'prompt_file':str(w/'ROOT_RUN_PROMPT.md'),'results_dir':str(rd/'out'),'python_executable':str(PRIMARY/'.venv/Scripts/python.exe'),'credential_root':'C:/Users/Jason/Documents/Jason/Orchestrator_Harness-Bench-Testing/.secrets/creds','model':'claude-haiku-5-5','provider':'claude-code','effort':'max','worker_effort':'max','planner_model':'claude-haiku-5-5','planner_effort':'max','watchdog_hours':4,'work_seconds':14400,'root_launches':0,'operator_assisted':True,'workflow_supplied':True,'status':'PREPARED_WAITING_IMAGE','initial_revision':rev,'resume_policy':'Audit workflow, continue same session/epoch within remaining allowance. Resume unfinished usage-blocked run at 06:40 Eastern; do not reset allowance.'}
    sys.path.insert(0,str(PRIMARY/'src'))
    from pymongo import MongoClient
    from memory_harness.experience import ExperienceScope,EverOSAdapter
    creds=Path(run['credential_root']);uri=next(l.strip() for l in (creds/'MongoDB.txt').read_text(encoding='utf-8-sig').splitlines() if l.strip().startswith(('mongodb://','mongodb+srv://')))
    collection='benchmark_run_'+hashlib.sha256(run_id.encode()).hexdigest();client=MongoClient(uri,serverSelectionTimeoutMS=15000)
    try:count=client['memory-dev'][collection].count_documents({});assert count==0
    finally:client.close()
    scope=ExperienceScope(application='memory-harness-benchmark',project=run_id,namespace=run_id+'-workers',owner='root-benchmark');memory=EverOSAdapter.memory_root_for_scope(h/'runtime/memory/everos',scope);assert not memory.exists()
    run['memory']={'atlas_collection':collection,'atlas_count':count,'everos_root':str(memory),'everos_scope_exists':False,'verified_at_utc':datetime.now(timezone.utc).isoformat()}
    write(rd/'run.json',run);write(h/'harness-config.json',{'root_workspace':str(w),'managed_coordination':'enabled'})
    print(json.dumps({'status':run['status'],'run_id':run_id}),flush=True)

if __name__=='__main__':main()
