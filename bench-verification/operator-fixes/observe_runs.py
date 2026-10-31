"""Single read-only observation of authorized trials; never launches a model."""
import json
from pathlib import Path
from datetime import datetime, timezone

BASE=Path(__file__).resolve().parents[1]/'root_runs'

def tail_events(path):
    if not path.exists():return []
    with path.open('rb') as f:
        f.seek(max(0,path.stat().st_size-250000))
        lines=f.read().decode('utf-8',errors='replace').splitlines()
    found=[]
    for line in lines:
        try:e=json.loads(line)
        except (ValueError,TypeError):continue
        if e.get('type')=='assistant':
            for b in e.get('message',{}).get('content',[]):
                if b.get('type')=='text':found.append(b.get('text','')[:650])
        elif e.get('type')=='result':found.append('RESULT: '+str(e.get('result',''))[:650])
        elif e.get('type')=='rate_limit_event':
            info=e.get('rate_limit_info',{})
            if info.get('status')!='allowed':found.append('RATE LIMIT: '+str(info))
    return found[-2:]

now=datetime.now(timezone.utc)
print(now.isoformat())
for name in ('b0','b1','b2','e1'):
    p=BASE/name;run=json.loads((p/'run.json').read_text(encoding='utf-8-sig'))
    deadline=datetime.fromisoformat(run['effective_watchdog_deadline_utc'].replace('Z','+00:00'))
    logs=sorted(p.glob('continuation-*.stdout.log'))
    row={'run':name,'minutes_remaining':round((deadline-now).total_seconds()/60,1),'status':run.get('status'),'segment_log':logs[-1].name if logs else None,'latest':tail_events(logs[-1]) if logs else []}
    manifests=sorted((p/'out'/run['run_id']).glob('segments/*/manifest.json'))
    row['sealed_continuations']=[m.parent.name for m in manifests if json.loads(m.read_text()).get('ended_at_utc')]
    lanes=[]
    for lane in (p/'w/.harness-runtime/epochs').glob('*/lanes/*/lane.json'):
        d=json.loads(lane.read_text())
        if d.get('lifecycle')!='retired':lanes.append([lane.parent.name,d.get('lifecycle')])
    row['nonretired_lanes']=lanes
    print(json.dumps(row,ensure_ascii=True))
