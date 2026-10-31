"""Validate operator quota pauses without rewriting original collector evidence.

Staged native collector change. Install only between stopped provider segments.
"""
from __future__ import annotations
import hashlib,json
from datetime import datetime,timedelta,timezone
from pathlib import Path

def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def instant(value):
    stamp=datetime.fromisoformat(value.replace('Z','+00:00'))
    if stamp.utcoffset() is None:raise ValueError('Quota timestamps require a timezone')
    return stamp

def bound(reference):
    path=Path(reference['path']).resolve(strict=True)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=reference['sha256']:
        raise ValueError('Quota evidence changed')
    return path

def effective_deadline(run_dir:Path,*,now:datetime|None=None):
    """Return deadline plus validated pause evidence, never infer a fresh allowance."""
    now=now or datetime.now(timezone.utc)
    run_dir=run_dir.resolve(strict=True)
    launch=read(run_dir/'launch.json')
    original=instant(launch['watchdog_deadline_utc'])
    first=instant(launch['started_at_utc'])
    prior_end=first
    paused=timedelta()
    references=[]
    receipts=sorted((run_dir/'quota-pauses').glob('*.json'))
    for number,path in enumerate(receipts,1):
        if path.name!=f'{number:04d}.json':raise ValueError('Quota pause receipts must be consecutive')
        row=read(path)
        if row.get('schema')!='operator-quota-pause/v1' or row.get('run_id')!=launch['run_id']:
            raise ValueError('Quota pause belongs to another run')
        if row.get('original_deadline_utc')!=launch['watchdog_deadline_utc']:
            raise ValueError('Quota pause changed original deadline')
        stop_path=bound(row['stop_audit'])
        if not stop_path.is_relative_to(run_dir.parent.parent):raise ValueError('Quota stop audit is outside its trial')
        stop=read(stop_path)
        if (stop.get('schema')!='operator-quota-stop/v1' or stop.get('run_id')!=launch['run_id']
                or stop.get('all_owned_provider_processes_absent') is not True
                or stop.get('collector_sealed') is not True):
            raise ValueError('Quota pause lacks a sealed stopped process audit')
        segment=bound(stop['segment_launch'])
        if not segment.parent.is_relative_to(run_dir):raise ValueError('Quota segment belongs to another trial')
        segment_launch=read(segment)
        manifest=bound(stop['segment_manifest'])
        if manifest.parent!=segment.parent:raise ValueError('Quota manifest belongs to another segment')
        final=read(manifest)
        transcript=bound(stop['transcript'])
        if transcript.parent!=segment.parent:raise ValueError('Quota transcript belongs to another segment')
        if segment_launch.get('run_id')!=launch['run_id'] or final.get('run_id')!=launch['run_id']:
            raise ValueError('Quota source run identity differs')
        if final.get('watchdog_expired') or not final.get('ended_at_utc'):
            raise ValueError('Quota pause cannot revive an expired or unsealed allowance')
        events=[json.loads(line) for line in transcript.read_text(encoding='utf-8').splitlines() if line.strip()]
        top=[event for event in events if not event.get('parent_tool_use_id')]
        sessions={event['session_id'] for event in top if event.get('session_id')}
        if sessions!={stop.get('root_session_id')}:
            raise ValueError('Quota evidence changed native session')
        if row.get('root_session_id')!=stop.get('root_session_id'):
            raise ValueError('Quota pause changed native session')
        quota=[event for event in top if event.get('type')=='rate_limit_event'
               and event.get('rate_limit_info',{}).get('status') in ('rejected','blocked')]
        if not quota:raise ValueError('No native rejected usage-limit evidence')
        reset=quota[-1]['rate_limit_info'].get('resetsAt')
        if not isinstance(reset,(int,float)) or isinstance(reset,bool):raise ValueError('Quota reset is missing')
        start=instant(row['paused_at_utc']);end=instant(row['clock_resumed_at_utc'])
        stopped=instant(stop['stopped_at_utc']);sealed=instant(final['ended_at_utc'])
        if start<max(first,prior_end,stopped,sealed) or end<=start or end>now:
            raise ValueError('Quota pause is future, overlapping, or includes active work')
        if end!=datetime.fromtimestamp(reset,timezone.utc):
            raise ValueError('Quota pause must end at the provider reset; operator delay is charged')
        if start>=original+paused:raise ValueError('Allowance expired before quota pause')
        paused+=end-start;prior_end=end
        references.append({'path':str(path.resolve()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    return {'original_deadline_utc':original.isoformat(),'effective_deadline_utc':(original+paused).isoformat(),
            'paused_seconds':paused.total_seconds(),'receipts':references}
