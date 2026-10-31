"""Operator-only official hidden grading. Never launches a benchmark model."""
from __future__ import annotations
import argparse,hashlib,io,json,os,subprocess,sys,tarfile,uuid
from datetime import datetime,timezone
from pathlib import Path

BASE=Path(__file__).resolve().parents[2]
BENCH=BASE/'bench-verification'
PRIMARY=BASE/'harness-single-run-version'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
def command(args,*,data=None,timeout=60,check=True):
    r=subprocess.run(args,input=data,capture_output=True,timeout=timeout)
    if check and r.returncode:raise RuntimeError('Operator subprocess failed: '+args[0]+' '+args[1]+'; see preserved evaluation logs')
    return r
def git(w,*args):return command(['git','-C',str(w),*args]).stdout
def upload(container,path,data):
    # Stream bytes directly and verify the hash; do not trust a successful Docker copy alone.
    code='import sys,hashlib;from pathlib import Path;b=sys.stdin.buffer.read();p=Path(sys.argv[1]);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b);print(hashlib.sha256(p.read_bytes()).hexdigest())'
    result=command(['docker','exec','-i',container,'python3','-c',code,path],data=data)
    if result.stdout.decode().strip()!=hashlib.sha256(data).hexdigest():raise ValueError('Container upload hash mismatch')

def stopped(run,folder):
    audit=read(folder/'WORKFLOW_AUDIT.json') if run['arm']=='harness' else read(folder/'OPERATOR_STOP_AUDIT.json')
    if audit.get('all_owned_provider_processes_absent') is not True:raise ValueError('Operator must prove all owned provider processes absent before hidden grading')
    if run['arm']=='harness' and read(Path(run['workspace'])/'.harness-runtime/RUNTIME_STATE.json').get('state')!='CLOSED':raise ValueError('Native runtime must be CLOSED')
    manifests=list((folder/'out'/run['run_id']).glob('manifest.json'))+list((folder/'out'/run['run_id']/'segments').glob('*/manifest.json'))
    if not manifests or any(not read(p).get('ended_at_utc') for p in manifests):raise ValueError('Collector segments are not sealed')
    ids=read(folder/'PROCESS_IDENTITIES.json')
    sys.path.insert(0,str(PRIMARY))
    from orchestrator_harness.processes import process_alive,process_identity
    for row in ids['processes']:
        if process_alive(row['pid']):
            actual=process_identity(row['pid'])
            if actual is None or actual['creation_time']==row['creation_time']:raise ValueError('A recorded process is live or has unknown identity')

def grade(folder:Path|None,oracle_task:str|None):
    oracle=oracle_task is not None
    if oracle:
        task=oracle_task
        root=BENCH/('biofabric' if task=='biofabric-rust-rewrite' else 'excel')
        folder=root/'operator-only'/('engine-oracle-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
        run={'task':task,'run_id':'official-oracle','arm':'oracle'};w=None
    else:
        folder=folder.resolve(strict=True);run=read(folder/'run.json');task=run['task'];w=Path(run['workspace'])
        stopped(run,folder)
        root=BENCH/('biofabric' if task=='biofabric-rust-rewrite' else 'excel')
        if git(w,'status','--porcelain').strip():raise ValueError('Commit or settle candidate workspace before grading')
    if task not in ('biofabric-rust-rewrite','excel-clone'):raise ValueError('Unsupported benchmark task')
    assets=read(root/'ASSETS.json');image=assets['image'];image_id=assets['image_id']
    if command(['docker','image','inspect',image,'--format','{{.Id}}']).stdout.decode().strip()!=image_id:raise ValueError('Pinned task image changed')
    out=folder/'hidden-evaluation';out.mkdir(parents=True,exist_ok=False)
    prefix='tasks/biofabric-rust-rewrite/' if task=='biofabric-rust-rewrite' else ''
    verifier=root/'operator-only/tests/test.sh' if task=='biofabric-rust-rewrite' else root/'task/tests/test.sh'
    result={'schema':'benchmark-grade/v1','status':'RUNNING','run_id':run['run_id'],'task':task,'oracle':oracle,'feedback_to_live_roots':False,'image_id':image_id,'engine_sha256':sha(Path(__file__)),'verifier_sha256':sha(verifier),'started_at_utc':datetime.now(timezone.utc).isoformat(),'cleanup_proven':False}
    container='hidden-eval-'+uuid.uuid4().hex[:20];cid=None
    write(out/'grading.json',result)
    try:
        r=command(['docker','create','--pull','never','--name',container,'--label','benchmark.operator-eval='+container,'--network','bridge' if task=='excel-clone' else 'none','--cpus','4','--memory','16g','--pids-limit','1024',image,'bash','-lc','sleep 18000'])
        cid=r.stdout.decode().strip();result['container']=cid
        if len(cid)!=64:raise ValueError('Invalid evaluation container identity')
        command(['docker','start',cid])
        if task=='biofabric-rust-rewrite':
            upload(cid,'/tmp/operator-verifier.sh',verifier.read_bytes())
            if oracle:
                upload(cid,'/tmp/operator-oracle.sh',(root/'operator-only/solution/solve.sh').read_bytes())
                command(['docker','exec',cid,'bash','/tmp/operator-oracle.sh'])
            else:
                rev=git(w,'rev-parse','HEAD').decode().strip();result['candidate_revision']=rev
                candidate=git(w,'archive','--format=tar',rev,'--','crates','Cargo.toml','Cargo.lock');(out/'candidate.tar').write_bytes(candidate)
                command(['docker','exec',cid,'rm','-rf','/app/crates','/app/target'])
                command(['docker','exec','-i',cid,'tar','xf','-','-C','/app'],data=candidate)
            # No inherited/incremental build cache is accepted as verifier evidence.
            command(['docker','exec',cid,'rm','-rf','/app/target'])
            execution=command(['docker','exec','-e','CARGO_INCREMENTAL=0',cid,'bash','/tmp/operator-verifier.sh'],timeout=1200,check=False)
        else:
            if oracle:
                tree=root/'task/solution'
                buffer=io.BytesIO()
                with tarfile.open(fileobj=buffer,mode='w') as tar:tar.add(tree,arcname='solution')
                command(['docker','exec','-i',cid,'tar','xf','-','-C','/'],data=buffer.getvalue())
                command(['docker','exec',cid,'bash','/solution/solve.sh'],timeout=600)
            else:
                rev=git(w,'rev-parse','HEAD').decode().strip();result['candidate_revision']=rev
                candidate=git(w,'archive','--format=tar',rev,'--','app');(out/'candidate.tar').write_bytes(candidate)
                command(['docker','exec',cid,'rm','-rf','/app']);command(['docker','exec','-i',cid,'tar','xf','-','-C','/'],data=candidate)
            buffer=io.BytesIO()
            with tarfile.open(fileobj=buffer,mode='w') as tar:tar.add(root/'task/tests',arcname='tests')
            command(['docker','exec','-i',cid,'tar','xf','-','-C','/'],data=buffer.getvalue())
            # The API key remains in process memory/stdin; never serialize it into receipts or logs.
            key_path=assets.get('anthropic_key_file')
            if not key_path:raise ValueError('Excel official CUA grader requires a configured local Anthropic API key file')
            text=Path(key_path).read_text(encoding='utf-8-sig').strip()
            key=next((l.strip() for l in text.splitlines() if l.strip().startswith('sk-ant-')),None)
            if not key:raise ValueError('No Anthropic API key parsed from configured secret file')
            execution=command(['docker','exec','-i',cid,'bash','-lc','IFS= read -r ANTHROPIC_API_KEY; export ANTHROPIC_API_KEY; bash /tests/test.sh'],data=(key+'\n').encode(),timeout=8100,check=False)
            # Scrub any accidental echo by third-party verifier diagnostics before persistence.
            execution.stdout=execution.stdout.replace(key.encode(),b'[REDACTED]');execution.stderr=execution.stderr.replace(key.encode(),b'[REDACTED]')
        (out/'verifier.stdout.log').write_bytes(execution.stdout);(out/'verifier.stderr.log').write_bytes(execution.stderr)
        raw=command(['docker','exec',cid,'cat','/logs/verifier/metrics.json']).stdout
        (out/'metrics.json').write_bytes(raw);metrics=json.loads(raw)
        reward=command(['docker','exec',cid,'cat','/logs/verifier/reward.txt']).stdout.decode().strip()
        partial=metrics.get('partial_score')
        if type(partial) not in (int,float) or not 0<=partial<=1:raise ValueError('No valid official partial score')
        if execution.returncode or reward not in ('0','1'):raise ValueError('Verifier infrastructure failure; no accepted score')
        if task=='biofabric-rust-rewrite':
            if metrics.get('phase')!='complete':raise ValueError('Verifier setup did not complete')
            count=metrics['passed']+metrics['failed'];expected=metrics['passed']/count if count else 0
            if abs(expected-partial)>1e-10:raise ValueError('Official count/partial score mismatch')
        else:
            if not {'correctness_reward','cua_rubric_score'}<=metrics.keys():raise ValueError('Excel CUA grading not complete')
            if abs(partial-round(.5*metrics['correctness_reward']+.5*metrics['cua_rubric_score'],6))>1e-8:raise ValueError('Official Excel blend mismatch')
        if oracle and (partial!=1 or reward!='1'):raise ValueError('Official oracle did not pass 100%; calibration failed')
        result.update(status='GRADED',partial_score=partial,binary_reward=int(reward),metrics=metrics)
    except BaseException as exc:
        result.update(status='FAILED',failure_type=type(exc).__name__,failure_reason=str(exc)[:800])
        raise
    finally:
        if cid:
            result['cleanup_proven']=command(['docker','rm','-f',cid],check=False).returncode==0
        result['finished_at_utc']=datetime.now(timezone.utc).isoformat();write(out/'grading.json',result)
    if not result['cleanup_proven']:raise ValueError('Evaluation container cleanup unproven')
    print(json.dumps({'grading_file':str(out/'grading.json'),'partial_score':result['partial_score'],'binary_reward':result['binary_reward'],'cleanup_proven':True}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('run_folder',nargs='?',type=Path);p.add_argument('--oracle-task',choices=['biofabric-rust-rewrite','excel-clone']);a=p.parse_args()
    if (a.run_folder is None)==(a.oracle_task is None):p.error('Provide one run folder or --oracle-task')
    grade(a.run_folder,a.oracle_task)
