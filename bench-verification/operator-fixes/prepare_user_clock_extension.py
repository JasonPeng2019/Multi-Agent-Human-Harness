"""Stage native clock support and write the explicitly authorized +15m receipts.

Operator preparation only: never launches or stops a model, and never installs
source into a live harness. Original launch/manifest/pause evidence is untouched.
"""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
REPO = BASE.parent
STAGE = BASE / 'operator-fixes/user-clock-extension-staged'

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def once(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')

EXTENSION_CODE = '''

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
'''

def main():
    now = datetime.now(timezone.utc).isoformat()
    auth_path = STAGE / 'AUTHORIZATION.json'
    runs = [read(BASE / 'root_runs' / name / 'run.json') for name in ('b1', 'b2')]
    authorization = {'schema':'operator-user-clock-authorization/v1',
        'recorded_at_utc':now,
        'user_request':'when you relaunch the 2 sonnet workers, launch them and all their workers in fast mode, and then also add 15 minutes to their clock?',
        'extensions':{run['run_id']:900 for run in runs},
        'fast_mode_status':'unsupported_for_sonnet; preserve Sonnet 5 LOW',
        'fast_mode_source':'https://code.claude.com/docs/en/fast-mode'}
    if auth_path.exists():
        existing = read(auth_path)
        assert existing['extensions'] == authorization['extensions']
        assert existing['user_request'] == authorization['user_request']
    else:
        once(auth_path, authorization)
    for run in runs:
        directory = Path(run['results_dir']) / run['run_id']
        launch_path = directory / 'launch.json'
        baseline = datetime.fromisoformat(run['effective_watchdog_deadline_utc'].replace('Z','+00:00'))
        once(directory / 'clock-extensions/0001.json', {
            'schema':'operator-user-clock-extension/v1', 'run_id':run['run_id'],
            'root_session_id':run['root_session_id'], 'seconds':900,
            'issued_at_utc':now, 'prior_effective_deadline_utc':baseline.isoformat(),
            'effective_deadline_utc':(baseline+timedelta(seconds=900)).isoformat(),
            'original_launch':{'path':str(launch_path.resolve()),'sha256':sha(launch_path)},
            'authorization':{'path':str(auth_path.resolve()),'sha256':sha(auth_path)}})
    native = REPO / 'harness-single-run-version'
    targets = ['orchestrator_harness/quota_clock.py', 'scripts/collect_codex_usage.py']
    for rel in targets:
        original = native / rel
        backup = STAGE / 'before' / rel
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(original.read_bytes())
        text = original.read_text(encoding='utf-8')
        if rel.endswith('quota_clock.py'):
            text = text.replace('now:datetime|None=None):', 'now:datetime|None=None, as_of:datetime|None=None):')
            text = text.replace("return {'original_deadline_utc':original.isoformat(),'effective_deadline_utc':(original+paused).isoformat(),\n            'paused_seconds':paused.total_seconds(),'receipts':references}",
                "return user_extensions(run_dir, launch, {'original_deadline_utc':original.isoformat(),\n            'effective_deadline_utc':(original+paused).isoformat(),\n            'paused_seconds':paused.total_seconds(),'receipts':references}, now=now, as_of=as_of)")
            text = text.replace('verified = effective_deadline(run_dir)', "verified = effective_deadline(run_dir, as_of=instant(launch['started_at_utc']))")
            text += EXTENSION_CODE
        else:
            text = text.replace('if any((run_dir / "quota-pauses").glob("*.json")):',
                'if any((run_dir / "quota-pauses").glob("*.json")) or any((run_dir / "clock-extensions").glob("*.json")):')
            text = text.replace('        if task.get("operator_assisted") and (final.get("launch_error")',
                '        from orchestrator_harness.quota_clock import extension_covers_expired_segment\n        extended_cutoff = extension_covers_expired_segment(directory, quota_clock)\n        if task.get("operator_assisted") and (final.get("launch_error")')
            text = text.replace('or (final.get("exit_code") != 0 and directory.resolve() not in quota_segments)):',
                'or (final.get("exit_code") != 0 and directory.resolve() not in quota_segments and not extended_cutoff)):')
            text = text.replace('if final.get("watchdog_expired"):\n            raise LedgerError',
                'if final.get("watchdog_expired") and not extended_cutoff:\n            raise LedgerError')
        staged = STAGE / rel
        staged.parent.mkdir(parents=True, exist_ok=True)
        staged.write_text(text, encoding='utf-8', newline='\n')
        compile(text, str(staged), 'exec')
    once(STAGE / 'STAGED.json', {'at_utc':now,'installed':False,
        'files':[{ 'relative_path':rel,'before_sha256':sha(native/rel),'after_sha256':sha(STAGE/rel)} for rel in targets],
        'install_policy':'Only after that harness ROOT and all owned providers are absent and collector manifests sealed. Native launcher only; same session/epoch. All ordinary gaps charged.'})
    print('Wrote two +900s receipts and staged native clock support; no live source changed.')

if __name__ == '__main__': main()
