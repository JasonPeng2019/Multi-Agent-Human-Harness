"""Archive measured whole-tree counters after user cancellation; no new allowance."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
name=sys.argv[1];assert name in ('b1','b2','e1')
p=BASE/'root_runs'/name
def read(q):return json.loads(q.read_text(encoding='utf-8-sig'))
def ref(q):return {'path':str(q.resolve()),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()}
def once(q,d):
    q.parent.mkdir(parents=True,exist_ok=True)
    with q.open('x',encoding='utf-8') as f:json.dump(d,f,indent=2)
run=read(p/'run.json');h=Path(run['harness_dir'])
sys.path[:0]=[str(h),str(h/'scripts')]
from token_ledger import build_snapshot,extract_usage,finalize
from orchestrator_harness import processes
audit=read(p/'WORKFLOW_AUDIT.json');assert audit['all_owned_provider_processes_absent'] is True
for d in read(p/'PROCESS_IDENTITIES.json')['processes']:
    assert processes.exact_process_is_gone(d['pid'],d['creation_time']),d
task=Path(run['collector_task_file']);snapshot=build_snapshot(task)
assert not snapshot['in_flight_invocations']
assert snapshot['errors'] and all(e.endswith(': terminal_error_usage_unverified') for e in snapshot['errors']),snapshot['errors']
bad={e.split(': ',1)[0] for e in snapshot['errors']}
rows=[row for row in snapshot['rows'] if row['invocation_id'] in bad]
assert len(rows)==len(bad)==1 and rows[0]['role']=='root'
source=Path(rows[0]['transcript_path']);segment=source.parent
launch=segment/'launch.json';manifest=segment/'manifest.json'
assert read(manifest).get('ended_at_utc') and not read(manifest).get('watchdog_expired')
assert not read(manifest).get('launch_error')
proofdir=p/'quota-stop-0002';proofdir.mkdir(exist_ok=False)
archive=proofdir/'root-native-transcript.jsonl';archive.write_bytes(source.read_bytes())
stop_path=p/'QUOTA_STOP_0002.json'
stop={'schema':'operator-quota-stop/v1','run_id':run['run_id'],'root_session_id':run['root_session_id'],
      'all_owned_provider_processes_absent':True,'collector_sealed':True,'not_task_reported_finish':True,
      'stopped_at_utc':read(manifest)['ended_at_utc'],'operator_verified_at_utc':datetime.now(timezone.utc).isoformat(),
      'segment_launch':ref(launch),'segment_manifest':ref(manifest),'transcript':ref(source),
      'workflow_stop_audit':ref(p/'WORKFLOW_AUDIT.json'),
      'prior_reported_task_finish_preserved':name!='e1','further_continuation_cancelled_by_user':True,
      'clock_pause_or_fresh_allowance_published':False,'worker_stop_evidence':[]}
once(stop_path,stop)
entries=[]
for row in rows:
    usage=extract_usage(source,completed=True,segment_index=row.get('transcript_segment_index'),provider_id='claude-code')
    assert usage['status']=='terminal_error_usage_unverified'
    entry={k:row.get(k) for k in ('invocation_id','role','thread_id','lane_id','lane_run_id')}
    entry.update({k:usage[k] for k in ('transcript_segment_sha256','input_tokens','output_tokens','comparison_total_tokens')})
    entry.update(archived_transcript=ref(archive),transcript_segment_index=row.get('transcript_segment_index'))
    entries.append(entry)
directory=Path(run['results_dir'])/run['run_id']
once(directory/'quota-accounting/0002.json',{'schema':'operator-quota-accounting/v1','run_id':run['run_id'],
    'stop_audit':ref(stop_path),'invocations':entries,'known_whole_tree_prefix_only':True,
    'token_count_claimed_exact':False,'recorded_at_utc':datetime.now(timezone.utc).isoformat()})
result=finalize(task,p/'token-evidence')
print(name,json.dumps({k:result.get(k) for k in ('known_output_tokens','known_total_tokens','errors','in_flight_invocations','output_tokens_are_exact')}))
