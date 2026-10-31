"""Operator-only, explicitly labelled Excel host-adjusted/Claude CLI grading.

Preserves pinned official rubric, Computer1 runtime and blend. It changes only
the declared host timing thresholds and LLM transport, not candidate code.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import threading
import queue as thread_queue
import time
import uuid

from grade_run import BENCH, command as raw_command, git, read, sha, stopped, upload, write

ROOT = BENCH/'excel'
CODE = ROOT/'operator-only/cli_grader'
sys.path.insert(0, str(CODE))
from transport import serve_request, publish_response

OPERATIONS=None
OPERATION_NUMBER=0

def command(args,**kwargs):
    """Preserve deterministic setup failures as well as verifier output."""
    global OPERATION_NUMBER
    OPERATION_NUMBER+=1
    prefix=OPERATIONS/f'{OPERATION_NUMBER:03d}' if OPERATIONS else None
    check=kwargs.pop('check',True)
    try:
        r=raw_command(args,check=False,**kwargs)
    except subprocess.TimeoutExpired as exc:
        if prefix:
            prefix.with_suffix('.stdout.log').write_bytes(exc.stdout or b'')
            prefix.with_suffix('.stderr.log').write_bytes(exc.stderr or b'')
            write(prefix.with_suffix('.json'),{'args':args,'timed_out':True})
        raise
    if prefix:
        prefix.with_suffix('.stdout.log').write_bytes(r.stdout)
        prefix.with_suffix('.stderr.log').write_bytes(r.stderr)
        write(prefix.with_suffix('.json'),{'args':args,'exit_code':r.returncode})
    if check and r.returncode:raise RuntimeError(f'Grading setup failed; preserved operation {OPERATION_NUMBER:03d}')
    return r


def adjusted_perf():
    profile = read(ROOT/'operator-only/HOST_SCORING_PROFILE.json')
    data = (ROOT/'task/tests/test_perf.py').read_bytes()
    for name, value in profile['original_budgets_seconds'].items():
        old = f'{name} = {value:.1f}'.encode()
        new = f'{name} = {value*profile["performance_budget_multiplier"]:.1f}'.encode()
        if data.count(old) != 1:
            raise ValueError('Pinned performance source changed')
        data = data.replace(old, new)
    return data


def grade(folder, oracle=False):
    global OPERATIONS
    assets = read(ROOT/'ASSETS.json')
    profile = ROOT/'operator-only/HOST_SCORING_PROFILE.json'
    if oracle:
        folder = ROOT/'operator-only'/('cli-oracle-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
        run = {'run_id':'official-oracle-cli-variant','arm':'oracle','task':'excel-clone'}
        w = None
    else:
        folder = folder.resolve(strict=True)
        run = read(folder/'run.json')
        if run['task'] != 'excel-clone':raise ValueError('Excel task required')
        stopped(run, folder)
        w = Path(run['workspace'])
        if git(w,'status','--porcelain').strip():raise ValueError('Candidate must be committed and clean')
    out = folder/'hidden-evaluation'
    out.mkdir(parents=True,exist_ok=False)
    queue = out/'cli-requests';queue.mkdir()
    OPERATIONS=out/'operations';OPERATIONS.mkdir()
    result = {'schema':'benchmark-grade/v1','status':'RUNNING',
        'run_id':run['run_id'],'task':'excel-clone','oracle':oracle,
        'official_comparable':False,'scoring_profile':read(profile),
        'profile_sha256':sha(profile),'engine_sha256':sha(Path(__file__)),
        'transport_sha256':sha(CODE/'transport.py'),
        'container_entry_sha256':sha(CODE/'container_entry.py'),
        'image_id':assets['image_id'],'cleanup_proven':False,
        'started_at_utc':datetime.now(timezone.utc).isoformat(),
        'feedback_to_live_roots':False,'model_requests':0}
    cid = None
    verifier_process = None
    write(out/'grading.json',result)
    try:
        if command(['docker','image','inspect',assets['image'],'--format','{{.Id}}'],timeout=90).stdout.decode().strip()!=assets['image_id']:
            raise ValueError('Pinned grader image changed')
        result['container_name']='excel-cli-'+uuid.uuid4().hex[:18];write(out/'grading.json',result)
        cid = command(['docker','create','--pull','never','--name',result['container_name'],
            '--label','benchmark.operator-eval=excel-cli','--network','bridge','--cpus','4',
            '--memory','16g','--pids-limit','1024',
            assets['image'],'bash','-lc','sleep 18000'],timeout=300).stdout.decode().strip()
        result['container']=cid;write(out/'grading.json',result)
        if len(cid)!=64:raise ValueError('Invalid owned grader container')
        command(['docker','start',cid],timeout=90)
        buffer=io.BytesIO()
        with tarfile.open(fileobj=buffer,mode='w') as tar:
            tar.add(ROOT/'task/tests',arcname='tests')
            if oracle:tar.add(ROOT/'task/solution',arcname='solution')
        command(['docker','exec','-i',cid,'tar','xf','-','-C','/'],data=buffer.getvalue(),timeout=120)
        if oracle:
            setup=command(['docker','exec',cid,'bash','/solution/solve.sh'],timeout=600,check=False)
            (out/'oracle-setup.stdout.log').write_bytes(setup.stdout)
            (out/'oracle-setup.stderr.log').write_bytes(setup.stderr)
            if setup.returncode:raise RuntimeError('Oracle setup failed')
        else:
            rev=git(w,'rev-parse','HEAD').decode().strip();result['candidate_revision']=rev
            candidate=git(w,'archive','--format=tar',rev,'--','app')
            (out/'candidate.tar').write_bytes(candidate)
            command(['docker','exec',cid,'rm','-rf','/app'])
            command(['docker','exec','-i',cid,'tar','xf','-','-C','/'],data=candidate)
        perf=adjusted_perf();upload(cid,'/tests/test_perf.py',perf)
        (out/'host-adjusted-test_perf.py').write_bytes(perf)
        stage=(ROOT/'task/tests/cua_stage.sh').read_bytes()
        old=b'"$PYBIN" /tests/cua_verifier.py --config "$CONFIG" --out-dir "$OUT_DIR"'
        new=b'"$PYBIN" /tmp/operator_cli_entry.py /tests/cua_verifier.py --config "$CONFIG" --out-dir "$OUT_DIR"'
        if stage.count(old)!=1:raise ValueError('Pinned CUA stage entry changed')
        stage=stage.replace(old,new);upload(cid,'/tests/cua_stage.sh',stage)
        upload(cid,'/tmp/operator_cli_entry.py',(CODE/'container_entry.py').read_bytes())
        (out/'cli-cua_stage.sh').write_bytes(stage)
        started=time.monotonic()
        packets=thread_queue.Queue()
        with (out/'verifier.stdout.log').open('w',encoding='utf-8') as stdout,(out/'verifier.stderr.log').open('wb') as stderr:
            verifier_process=subprocess.Popen(['docker','exec','-i',cid,'bash','/tests/test.sh'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr,text=True,encoding='utf-8',errors='replace')
            def read_stdout():
                try:
                    for line in verifier_process.stdout:
                        prefix='@@OPERATOR_CLI_REQUEST@@'
                        if line.startswith(prefix):
                            packets.put(json.loads(line[len(prefix):]))
                            stdout.write('[operator] native CLI grading request received\n')
                        else:stdout.write(line)
                        stdout.flush()
                except BaseException as exc:packets.put({'reader_error':type(exc).__name__})
            reader=threading.Thread(target=read_stdout,daemon=True);reader.start()
            while verifier_process.poll() is None or reader.is_alive() or not packets.empty():
                if time.monotonic()-started>8100:
                    raise TimeoutError('Full grader exceeded its original 8100s infrastructure allowance')
                try:packet=packets.get(timeout=.25)
                except thread_queue.Empty:continue
                if 'reader_error' in packet:raise RuntimeError('Grader stdout reader failed')
                key=packet['id']
                if len(key)!=32 or any(c not in '0123456789abcdef' for c in key):raise ValueError('Invalid grading request identity')
                request=queue/(key+'.request.json')
                if request.exists():raise ValueError('Duplicate grading request; refusing replay')
                write(request,packet['request'])
                try:
                    value=serve_request(request,Path('C:/Users/Jason/.local/bin/claude.exe'),timeout=min(540,max(1,int(8100-(time.monotonic()-started)))))
                except Exception as exc:
                    value={'error':type(exc).__name__+': '+str(exc)}
                publish_response(request,value)
                verifier_process.stdin.write(json.dumps(value)+'\n');verifier_process.stdin.flush()
                result['model_requests']+=1;write(out/'grading.json',result)
        if verifier_process.returncode:
            raise RuntimeError('CLI-variant grader infrastructure failure; see preserved logs')
        command(['docker','cp',cid+':/logs/verifier',str(out/'verifier-artifacts')],timeout=180)
        metrics=read(out/'verifier-artifacts/metrics.json')
        reward=(out/'verifier-artifacts/reward.txt').read_text().strip()
        partial=metrics.get('partial_score')
        if type(partial) not in (int,float) or not 0<=partial<=1 or reward not in ('0','1'):
            raise ValueError('No complete CLI-variant blended score')
        if not {'correctness_reward','cua_rubric_score'}<=metrics.keys():
            raise ValueError('Visual grading stage incomplete')
        if abs(partial-round(.5*metrics['correctness_reward']+.5*metrics['cua_rubric_score'],6))>1e-8:
            raise ValueError('Pinned 50:50 blend mismatch')
        result.update(status='GRADED',partial_score=partial,binary_reward=int(reward),metrics=metrics)
        if oracle:
            result['oracle_passed_100_percent']=partial==1 and reward=='1'
            if not result['oracle_passed_100_percent']:
                result['calibration_limitation']='Measured oracle is below 100%; no perfect calibration claim.'
    except BaseException as exc:
        result.update(status='FAILED',failure_type=type(exc).__name__,failure_reason=str(exc)[:800])
        raise
    finally:
        if cid:
            if verifier_process is not None and verifier_process.poll() is None:
                # Removing this exact owned grading container stops its exec and desktop.
                pass
            cleanup=command(['docker','rm','-f',cid],timeout=90,check=False)
            result['cleanup_proven']=cleanup.returncode==0
        result['finished_at_utc']=datetime.now(timezone.utc).isoformat()
        write(out/'grading.json',result)
    print(json.dumps({'record':str(out/'grading.json'),'status':result['status'],
        'partial_score':result.get('partial_score'),'official_comparable':False,
        'cleanup_proven':result['cleanup_proven']}),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('run_folder',nargs='?',type=Path)
    p.add_argument('--oracle',action='store_true')
    a=p.parse_args()
    if (a.run_folder is None)==(not a.oracle):p.error('Provide a run folder or --oracle')
    grade(a.run_folder,a.oracle)
