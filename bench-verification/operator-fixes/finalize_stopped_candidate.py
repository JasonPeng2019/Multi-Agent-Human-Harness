"""One-shot operator proof for a stopped candidate; never starts a model."""
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone

BASE=Path(__file__).resolve().parents[1]
name=sys.argv[1]
assert name in ('b1','b2','e1')
p=BASE/'root_runs'/name
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
run=read(p/'run.json');h=Path(run['harness_dir'])
sys.path.insert(0,str(h));sys.path.insert(0,str(h/'scripts'))
from orchestrator_harness import processes
rt=Path(run['workspace'])/'.harness-runtime'
assert read(rt/'RUNTIME_STATE.json')['state']=='CLOSED'
out=Path(run['results_dir'])/run['run_id']
segments=[out,*sorted((out/'segments').glob('[0-9]*'))]
for segment in segments:
    assert read(segment/'manifest.json').get('ended_at_utc'),segment
identities=read(p/'PROCESS_IDENTITIES.json')
for op in p.glob('OPERATOR_CONTINUATION_*.json'):
    d=read(op)
    if d.get('pid'):identities['processes'].append({k:d[k] for k in ('pid','creation_time')})
lanes=[]
for q in rt.glob('epochs/*/lanes/*/lane.json'):
    lane=read(q);status=read(Path(lane['controller_status_path']))
    assert lane['lifecycle']=='retired' and status.get('cleanup_proven') is True,q
    assert processes.process_boundary_is_gone(status['process_boundary'],native_cleanup_proven=True),q
    for identity in (lane.get('process'),status.get('provider_state')):
        if identity and identity.get('pid'):identities['processes'].append({k:identity[k] for k in ('pid','creation_time')})
    result_path=Path(lane['result_path'])
    result=read(result_path) if result_path.exists() else None
    lanes.append({'lane_id':lane['lane_id'],'run_id':lane['run_id'],'result':result,
                  'acceptance_advancement':lane.get('acceptance_advancement'),
                  'lane_sha256':sha(q),'result_path':str(result_path)})
for relative in ('operator-only/public-check-service/service.json','monitor/MONITOR.json'):
    d=read(rt/relative)
    if d.get('pid'):identities['processes'].append({k:d[k] for k in ('pid','creation_time')})
for identity in identities['processes']:
    assert processes.exact_process_is_gone(identity['pid'],identity['creation_time']),identity
identities['processes']=list({(d['pid'],d['creation_time']):d for d in identities['processes']}.values())
(p/'PROCESS_IDENTITIES.json').write_text(json.dumps(identities,indent=2),encoding='utf-8')
for relative,digest in read(p/'operator-final-candidate/source-sha256.json').items():
    assert sha(Path(run['workspace'])/relative)==digest,relative
missing=(['CLI implementation','independent validators for all modules','final parallel test-validator and semantic-reviewer pair']
         if name=='b1' else ['final parallel test-validator and semantic-reviewer pair','ROOT disposition/acceptance of latest module-validator findings']
         if name=='b2' else ['unfinished integration and module workflow','final parallel test-validator and semantic-reviewer pair'])
audit={'schema':'operator-workflow-audit/v1','run_id':run['run_id'],'status':'INCOMPLETE',
       'all_owned_provider_processes_absent':True,'collector_sealed':True,'runtime_closed':True,
       'recorded_at_utc':datetime.now(timezone.utc).isoformat(),'root_session_id':run['root_session_id'],
       'epoch_id':run['epoch_id'],'missing':missing,
       'operator_shutdown_is_not_root_acceptance':True,
       'continuations_cancelled_by_user':True,'grade_candidate':name!='e1',
       'candidate_source_hashes':str(p/'operator-final-candidate/source-sha256.json'),
       'latest_manifest_sha256':sha(segments[-1]/'manifest.json'),
       'workflow_record_sha256':sha(Path(run['workspace'])/'WORKFLOW_COMPLETION.md'),
       'lanes':lanes}
with (p/'WORKFLOW_AUDIT.json').open('x',encoding='utf-8') as f:json.dump(audit,f,indent=2)
print(json.dumps({k:v for k,v in audit.items() if k!='lanes'}))
