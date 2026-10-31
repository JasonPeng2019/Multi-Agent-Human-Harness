"""Install the staged native clock change only into one proven quiescent arm."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
STAGE=BASE/'operator-fixes/user-clock-extension-staged'
name=sys.argv[1]
assert name in ('b1','b2')
trial=BASE/'root_runs'/name
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
run=read(trial/'run.json')
harness=Path(run['harness_dir'])
sys.path.insert(0,str(harness))
sys.path.insert(0,str(harness/'scripts'))
from orchestrator_harness import processes
from token_ledger import build_snapshot
directory=Path(run['results_dir'])/run['run_id']
segments=[directory,*sorted((directory/'segments').glob('[0-9]*'))]
for path in segments:
    final=read(path/'manifest.json')
    assert final.get('ended_at_utc') and not final.get('launch_error'),path
state=read(trial/'w/.harness-runtime/RUNTIME_STATE.json')
assert state['state']=='CLOSED'
identities=read(trial/'PROCESS_IDENTITIES.json')
for op in sorted(trial.glob('OPERATOR_CONTINUATION_*.json')):
    d=read(op)
    if d.get('pid'):identities['processes'].append({k:d[k] for k in ('pid','creation_time')})
for lane_path in (trial/'w/.harness-runtime/epochs').glob('*/lanes/*/lane.json'):
    lane=read(lane_path)
    assert lane['lifecycle']=='retired',lane_path
    status=read(Path(lane['controller_status_path']))
    assert status.get('cleanup_proven') is True,lane_path
    for identity in (lane.get('process'),status.get('provider_state')):
        if identity and identity.get('pid'):identities['processes'].append({k:identity[k] for k in ('pid','creation_time')})
for relative in ('operator-only/public-check-service/service.json','monitor/MONITOR.json'):
    d=read(trial/'w/.harness-runtime'/relative)
    if d.get('pid'):identities['processes'].append({k:d[k] for k in ('pid','creation_time')})
for identity in identities['processes']:
    pid,creation=identity['pid'],identity['creation_time']
    assert not processes.identity_matches(pid,creation),identity
    assert not (processes.process_alive(pid) and processes.process_identity(pid) is None),identity
snapshot=build_snapshot(Path(run['collector_task_file']))
assert not snapshot['errors'] and not snapshot['in_flight_invocations'],snapshot['errors']
audit={'schema':'operator-workflow-audit/v1','run_id':run['run_id'],'status':'INCOMPLETE',
       'all_owned_provider_processes_absent':True,'collector_sealed':True,'runtime_closed':True,
       'recorded_at_utc':datetime.now(timezone.utc).isoformat(),
       'native_session':run['root_session_id'],'epoch_id':run['epoch_id'],
       'latest_manifest_sha256':sha(segments[-1]/'manifest.json'),
       'workflow_record_sha256':sha(trial/'w/WORKFLOW_COMPLETION.md'),
       'missing':['independent module validators and final parallel validator/reviewer pair'],
       'clock_extension_authorized_seconds':900,'known_output_tokens':snapshot['known_output_tokens']}
auditpath=trial/f'WORKFLOW_AUDIT_{segments[-1].name}.json'
with auditpath.open('x',encoding='utf-8') as stream:json.dump(audit,stream,indent=2)
(trial/'PROCESS_IDENTITIES.json').write_text(json.dumps(identities,indent=2),encoding='utf-8')
installed=[]
for row in read(STAGE/'STAGED.json')['files']:
    target=harness/row['relative_path']
    assert sha(target)==row['before_sha256'],str(target)
    target.write_bytes((STAGE/row['relative_path']).read_bytes())
    assert sha(target)==row['after_sha256']
    installed.append({**row,'target':str(target)})
receipt={'at_utc':datetime.now(timezone.utc).isoformat(),'run_id':run['run_id'],
         'quiescent_audit':str(auditpath),'audit_sha256':sha(auditpath),'files':installed}
with (STAGE/f'INSTALL_{name}.json').open('x',encoding='utf-8') as stream:json.dump(receipt,stream,indent=2)
print(json.dumps(audit))
