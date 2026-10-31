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

def effective_deadline(run_dir:Path,*,now:datetime|None=None, as_of:datetime|None=None):
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
    return user_extensions(run_dir, launch, {'original_deadline_utc':original.isoformat(),
            'effective_deadline_utc':(original+paused).isoformat(),
            'paused_seconds':paused.total_seconds(),'receipts':references}, now=now, as_of=as_of)


def validate_launch_clock(launch_path: Path, launch: dict):
    """Bind an extended segment clock to independently checked original evidence."""
    recorded = launch.get("quota_clock")
    if recorded is None:
        return None
    launch_path = launch_path.resolve(strict=True)
    directory = launch_path.parent
    if directory.parent.name != "segments":
        raise ValueError("Quota recovery clock requires a native continuation segment")
    run_dir = directory.parent.parent
    verified = effective_deadline(run_dir, as_of=instant(launch['started_at_utc']))
    original = read(run_dir / "launch.json")
    if (recorded != verified or launch.get("run_id") != original.get("run_id")
            or launch.get("workspace") != original.get("workspace")
            or launch.get("watchdog_deadline_utc") != verified["effective_deadline_utc"]):
        raise ValueError("Quota recovery clock does not match its verified evidence")
    stops = [read(bound(read(bound(ref))["stop_audit"])) for ref in verified["receipts"]]
    if any(stop.get("root_session_id") != launch.get("resume_session_id") for stop in stops):
        raise ValueError("Quota continuation changed native ROOT session")
    return verified


def user_extensions(run_dir, launch, baseline, *, now, as_of=None):
    """Apply immutable, explicitly authorized extensions; historical clocks stay fixed."""
    prior = instant(baseline['effective_deadline_utc'])
    applied = prior
    refs = []
    total = 0
    session = None
    events = run_dir / 'claude-events.jsonl'
    if events.exists():
        with events.open(encoding='utf-8') as stream:
            for line in stream:
                event = json.loads(line)
                if event.get('type') == 'system' and event.get('subtype') == 'init':
                    session = event.get('session_id')
                    break
    for number, path in enumerate(sorted((run_dir / 'clock-extensions').glob('*.json')), 1):
        row = read(path)
        if (path.name != f'{number:04d}.json' or row.get('schema') != 'operator-user-clock-extension/v1'
                or row.get('run_id') != launch['run_id'] or row.get('root_session_id') != session
                or not session or bound(row['original_launch']) != run_dir / 'launch.json'):
            raise ValueError('Clock extension changed original run/session identity')
        auth = read(bound(row['authorization']))
        seconds = row.get('seconds')
        if (type(seconds) is not int or not 0 < seconds <= 86400
                or auth.get('schema') != 'operator-user-clock-authorization/v1'
                or auth.get('extensions', {}).get(launch['run_id']) != seconds):
            raise ValueError('Clock extension lacks explicit authorization')
        issued = instant(row['issued_at_utc'])
        if (issued > now or issued < instant(launch['started_at_utc']) or issued >= prior
                or instant(row['prior_effective_deadline_utc']) != prior
                or instant(row['effective_deadline_utc']) != prior + timedelta(seconds=seconds)):
            raise ValueError('Clock extension is late, future, or changed the prior clock')
        prior += timedelta(seconds=seconds)
        if as_of is None or issued <= as_of:
            applied = prior
            total += seconds
            refs.append({'path': str(path.resolve()), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    if not refs:
        return baseline
    return {**baseline, 'effective_deadline_utc': applied.isoformat(),
            'user_extension_seconds': total, 'user_extension_receipts': refs}


def extension_covers_expired_segment(directory, clock):
    """An older timer may fire after a user granted time it could not hot-load."""
    if not clock or not clock.get('user_extension_receipts'):
        return False
    launch = read(directory / 'launch.json')
    final = read(directory / 'manifest.json')
    deadline = instant(launch['watchdog_deadline_utc'])
    if (not final.get('watchdog_expired') or final.get('launch_error')
            or final.get('watchdog_stop_errors')
            or deadline >= instant(clock['effective_deadline_utc'])):
        return False
    old_refs = launch.get('quota_clock', {}).get('user_extension_receipts', [])
    return any(ref not in old_refs and instant(read(bound(ref))['issued_at_utc']) < deadline
               for ref in clock['user_extension_receipts'])
