"""One-shot operator asset extraction and oracle calibration; launches no model."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess
import uuid

BASE = Path(__file__).resolve().parents[2]
OUT = BASE / 'bench-verification/biofabric'
SOURCE = Path('C:/Users/Jason/Documents/Jason/Orchestrator_Harness-Bench-Testing/benchmarks/swe-marathon')
REV = 'f34867643bf07aec5208a861e667e01df0942099'
IMAGE = 'swe-marathon-biofabric-rust-rewrite:host-lock-20260925'
IMAGE_ID = 'sha256:375a34a80ed17c7d577d7896edd346331bb4bda2e550868806b0e37d6554c9dc'

def command(argv, timeout=60):
    return subprocess.run(argv, check=True, capture_output=True, timeout=timeout).stdout

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')

def main():
    assert not OUT.exists(), 'One preparation attempt only; preserve and diagnose failures.'
    OUT.mkdir(parents=True)
    actual=command(['docker','image','inspect',IMAGE,'--format','{{.Id}}']).decode().strip()
    assert actual == IMAGE_ID
    operator=OUT/'operator-only'
    operator.mkdir()
    for name in ['instruction.md','task.toml','tests/test.sh','solution/solve.sh']:
        data=command(['git','-C',str(SOURCE),'show',f'{REV}:tasks/biofabric-rust-rewrite/{name}'])
        path=operator/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
    seed=OUT/'workflow-seed'
    seed.mkdir()
    old=BASE/'bench-verification/root_runs/s2/w'
    for name in ['CLAUDE.md','AGENTS.md','ROOT_RUN_PROMPT.md']:
        shutil.copyfile(old/name,seed/name)
    shutil.copytree(old/'.claude/skills',seed/'skills')
    container='biofabric-preparation-'+uuid.uuid4().hex[:12]
    state={'schema':'biofabric-assets/v1','status':'PREPARING','image':IMAGE,'image_id':IMAGE_ID,
           'source_revision':REV,'container':container,'model_launches':0,
           'started_at_utc':datetime.now(timezone.utc).isoformat(),'cleanup_proven':False}
    write(OUT/'ASSETS.json',state)
    try:
        command(['docker','create','--pull','never','--name',container,'--label','harness.operator=biofabric-preparation',
                 '--network','none','--cpus','4','--memory','16g','--pids-limit','512',IMAGE,'bash','-lc','sleep 7200'])
        command(['docker','start',container])
        template=OUT/'template';template.mkdir()
        command(['docker','cp',f'{container}:/app/.',str(template)],timeout=120)
        reference=template/'reference';reference.mkdir()
        command(['docker','cp',f'{container}:/reference/.',str(reference)],timeout=120)
        assert not (template/'tests/hidden').exists()
        assert not (template/'private.enc').exists()
        assert not (template/'.git').exists()
        assert (template/'Cargo.lock').is_file()
        assert b'todo!' in (template/'crates/core/tests/parity_tests/runners.rs').read_bytes()
        result=subprocess.run(['docker','exec',container,'cargo','test','--workspace','--no-run','--locked','--offline'],capture_output=True,timeout=600)
        (operator/'starter-compile.stdout.log').write_bytes(result.stdout)
        (operator/'starter-compile.stderr.log').write_bytes(result.stderr)
        state['starter_compile_exit']=result.returncode
        assert result.returncode == 0, 'Starter public tests must compile offline before model launch.'
        command(['docker','cp',str(operator/'solution/solve.sh'),f'{container}:/tmp/oracle.sh'])
        command(['docker','cp',str(operator/'tests/test.sh'),f'{container}:/tmp/verifier.sh'])
        result=subprocess.run(['docker','exec',container,'bash','-lc','bash /tmp/oracle.sh && bash /tmp/verifier.sh'],capture_output=True,timeout=1200)
        (operator/'oracle.stdout.log').write_bytes(result.stdout)
        (operator/'oracle.stderr.log').write_bytes(result.stderr)
        command(['docker','cp',f'{container}:/logs/verifier',str(operator/'oracle-verifier')])
        metrics=json.loads((operator/'oracle-verifier/metrics.json').read_text())
        state['oracle_metrics']=metrics
        assert result.returncode==0 and metrics['phase']=='complete' and metrics['reward']==1 and metrics['partial_score']==1
        state['public_input_sha256']={p.relative_to(template).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in template.rglob('*') if p.is_file()}
        state['status']='PASS'
    except BaseException as exc:
        state['status']='FAILED'
        state['failure_type']=type(exc).__name__
        raise
    finally:
        removed=subprocess.run(['docker','rm','-f',container],capture_output=True,timeout=60)
        state['cleanup_proven']=removed.returncode==0
        state['finished_at_utc']=datetime.now(timezone.utc).isoformat()
        write(OUT/'ASSETS.json',state)
        print(json.dumps({k:v for k,v in state.items() if k!='public_input_sha256'}),flush=True)

if __name__=='__main__':
    main()
