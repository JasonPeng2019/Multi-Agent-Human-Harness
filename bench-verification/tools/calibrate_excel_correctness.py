"""Operator-only Excel oracle component check; does not claim full CUA calibration."""
from __future__ import annotations
import argparse,io,json,tarfile,uuid
from datetime import datetime,timezone
from pathlib import Path
from grade_run import BENCH,command,read,write,sha,upload

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--perf-only',action='store_true',help='Diagnose the unchanged official performance gate in isolation')
parser.add_argument('--host-adjusted',action='store_true',help='Calibrate the explicitly authorized, separately labelled host timing profile')
args=parser.parse_args()
root=BENCH/'excel'
assets=read(root/'ASSETS.json')
out=root/'operator-only'/('correctness-oracle-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
out.mkdir(parents=True,exist_ok=False)
verifier=root/'task/tests/test.sh'
original=verifier.read_bytes()
line=b'bash /tests/cua_blend.sh'
assert original.count(line)==1
component=original.replace(line,b'# CUA deliberately omitted: correctness component check only')
if args.perf_only:
    component=b'''#!/usr/bin/env bash
set -euo pipefail
export PATH=/opt/venv/bin:$PATH
mkdir -p /logs/verifier
bash /app/start.sh >/logs/verifier/server.log 2>&1 &
server=$!
trap 'kill "$server" 2>/dev/null || true' EXIT
for i in $(seq 1 120); do curl -fsS http://127.0.0.1:8000/api/health >/dev/null && break; sleep 1; done
uvx --with pytest==8.4.1 --with pytest-json-ctrf==0.3.5 --with requests==2.32.3 pytest /tests/test_perf.py -rA -v --tb=short --ctrf /logs/verifier/perf_pytest.json
'''
record={'schema':'excel-oracle-component/v1','status':'RUNNING','full_calibration':False,'visual_stage':'NOT_RUN_API_KEY_PENDING','official_verifier_sha256':sha(verifier),'image_id':assets['image_id'],'started_at_utc':datetime.now(timezone.utc).isoformat(),'cleanup_proven':False}
record['component']='unchanged-official-perf-gate' if args.perf_only else 'all-18-correctness-gates'
if args.host_adjusted:
    profile=root/'operator-only/HOST_SCORING_PROFILE.json'
    record.update(scoring_profile=read(profile),profile_sha256=sha(profile),official_comparable=False)
write(out/'calibration.json',record)
cid=None
try:
    assert command(['docker','image','inspect',assets['image'],'--format','{{.Id}}']).stdout.decode().strip()==assets['image_id']
    cid=command(['docker','create','--pull','never','--name','excel-component-'+uuid.uuid4().hex[:16],'--label','benchmark.operator-eval=excel-correctness','--network','bridge','--cpus','4','--memory','16g','--pids-limit','1024',assets['image'],'bash','-lc','sleep 18000']).stdout.decode().strip()
    record['container']=cid;write(out/'calibration.json',record)
    command(['docker','start',cid])
    buffer=io.BytesIO()
    with tarfile.open(fileobj=buffer,mode='w') as tar:
        tar.add(root/'task/solution',arcname='solution')
        tar.add(root/'task/tests',arcname='tests')
    command(['docker','exec','-i',cid,'tar','xf','-','-C','/'],data=buffer.getvalue())
    if args.host_adjusted:
        perf=(root/'task/tests/test_perf.py').read_bytes()
        profile=record['scoring_profile']
        for symbol,budget in profile['original_budgets_seconds'].items():
            before=f'{symbol} = {budget:.1f}'.encode()
            after=f'{symbol} = {budget*profile["performance_budget_multiplier"]:.1f}'.encode()
            if perf.count(before)!=1:raise ValueError('Unexpected pinned performance threshold')
            perf=perf.replace(before,after)
        upload(cid,'/tests/test_perf.py',perf)
        (out/'host-adjusted-test_perf.py').write_bytes(perf)
    setup=command(['docker','exec',cid,'bash','/solution/solve.sh'],timeout=600,check=False)
    (out/'oracle-setup.stdout.log').write_bytes(setup.stdout);(out/'oracle-setup.stderr.log').write_bytes(setup.stderr)
    if setup.returncode:raise RuntimeError('Official oracle setup failed; see logs')
    upload(cid,'/tmp/correctness-only.sh',component)
    execution=command(['docker','exec',cid,'bash','/tmp/correctness-only.sh'],timeout=8100,check=False)
    (out/'verifier.stdout.log').write_bytes(execution.stdout);(out/'verifier.stderr.log').write_bytes(execution.stderr)
    metrics=command(['docker','exec',cid,'cat','/logs/verifier/perf_pytest.json' if args.perf_only else '/logs/verifier/metrics.json']).stdout
    (out/'metrics.json').write_bytes(metrics)
    m=json.loads(metrics);record['metrics']=m
    if args.perf_only:
        if execution.returncode:raise RuntimeError('Official oracle performance gate failed in isolation')
        record['status']='PERF_COMPONENT_PASS'
    else:
        reward=command(['docker','exec',cid,'cat','/logs/verifier/reward.txt']).stdout.decode().strip()
        if execution.returncode or reward!='1' or m.get('gates_passed')!=18:raise RuntimeError('Official oracle did not pass all 18 correctness gates')
        record['status']='CORRECTNESS_COMPONENT_PASS'
except BaseException as exc:
    record.update(status='FAILED',failure_type=type(exc).__name__,failure_reason=str(exc))
    raise
finally:
    if cid:record['cleanup_proven']=command(['docker','rm','-f',cid],check=False).returncode==0
    record['finished_at_utc']=datetime.now(timezone.utc).isoformat();write(out/'calibration.json',record)
print(json.dumps({'record':str(out/'calibration.json'),'status':record['status'],'full_calibration':False,'cleanup_proven':record['cleanup_proven']}))
