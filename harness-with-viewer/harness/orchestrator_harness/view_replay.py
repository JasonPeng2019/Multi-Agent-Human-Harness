"""Timestamped, immutable TUI observations and read-only playback.

Recording samples native records; it never schedules, acknowledges or launches work.
Snapshots include rendered artifacts so playback never consults present-day worktrees.
"""
from __future__ import annotations

import bisect
import copy
import hashlib
import json
import math
import sqlite3
import threading
import time
import zlib
from dataclasses import asdict
from contextlib import closing, ExitStack
from pathlib import Path
from typing import Any

SCHEMA = 'harness-replay/v1'
SAMPLE_SECONDS = 1.0


def freeze(state: dict) -> dict:
    from . import view_artifacts, view_events
    state = copy.deepcopy(state)
    state.pop('collected_at', None)
    state.get('monitor', {}).pop('age_seconds', None)
    for lane in state.get('lanes', []):
        lane.pop('elapsed_seconds', None)
        lane['_recorded'] = {
            'prompt': view_artifacts.panel_text(lane, 'prompt'),
            'result': view_artifacts.panel_text(lane, 'result'),
            'blocks': [asdict(block) for block in view_artifacts.output_blocks(lane)],
            'events': view_events.mailbox_data(lane),
        }
    if state.get('root'):
        root = state['root']
        root['workers'] = state['lanes']
        root['_recorded'] = {
            'prompt': view_artifacts.panel_text(root, 'prompt'),
            'result': view_artifacts.panel_text(root, 'result'),
            'blocks': [asdict(block) for block in view_artifacts.output_blocks(root)],
            'events': view_events.mailbox_data(root),
        }
        root.pop('workers', None)  # Avoid storing every worker twice; playback reconnects them.
    # These ages change even when nothing observable has happened.
    state.pop('run_seconds', None)
    for item in state.get('needs_you', []):
        item.pop('age_seconds', None)
    return state



def latest_run(rt: Path) -> dict | None:
    """Small identity read, independent of transcripts and replay payloads."""
    from .epochs import read_current_epoch
    from .view_state import _latest_epoch
    try:
        marker = read_current_epoch(rt)
        if marker:
            epoch = str(marker['epoch_id'])
            if Path(epoch).name != epoch or epoch in ('.', '..'):
                return None
            state = json.loads((rt / 'epochs' / epoch / 'epoch-state.json').read_text(encoding='utf-8-sig'))
        else:
            latest = _latest_epoch(rt)
            if latest is None:
                return None
            epoch, state = latest
        if Path(epoch).name != epoch or epoch in ('.', '..'):
            return None
        if not isinstance(state, dict) or not isinstance(state.get('opened_at'), str):
            return None
        return {'runtime_root': str(rt.resolve()), 'epoch_id': epoch, 'opened_at': state['opened_at'], 'lifecycle': state.get('lifecycle')}
    except (OSError, ValueError, KeyError, TypeError):
        return None


def read_latest(path: Path | None) -> dict | None:
    if path is None:
        return None
    try:
        record = json.loads(path.read_text(encoding='utf-8-sig'))
        if (record.get('schema') == 'latest-replay/v1'
                and all(isinstance(record.get(key), str) for key in ('runtime_root', 'epoch_id', 'opened_at'))):
            return record
    except (OSError, ValueError, AttributeError):
        pass
    return None


def _remove_recording(rt: Path, epoch: str) -> None:
    if Path(epoch).name != epoch or epoch in ('.', '..'):
        return
    path = rt / 'replay' / f'{epoch}.sqlite3'
    if not path.is_file() or path.is_symlink():
        return
    try:
        with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)) as db:
            metadata = dict(db.execute('SELECT key,value FROM metadata'))
        if metadata.get('schema') != SCHEMA:
            return
        path.unlink()
        for suffix in ('-journal', '-wal', '-shm'):
            path.with_name(path.name + suffix).unlink(missing_ok=True)
    except (OSError, sqlite3.Error):
        pass  # A reader may still hold the file on Windows; retry next observation.


def record_once(rt: Path, *, registry: Path | None = None) -> None:
    from .records import RecordLock, atomic_write_json
    identity = latest_run(rt)
    if identity is None:
        return
    if not (rt / 'CURRENT_EPOCH.json').is_file() and not (rt / 'replay' / f"{identity['epoch_id']}.sqlite3").exists():
        return
    with ExitStack() as stack:
        if registry is not None:
            registry.parent.mkdir(parents=True, exist_ok=True)
            stack.enter_context(RecordLock(registry))
        directory = rt / 'replay'
        directory.mkdir(parents=True, exist_ok=True)
        stack.enter_context(RecordLock(directory / 'retention'))
        # Native bootstrap may have advanced while we waited for these locks.
        # Registration, retention, and capture must all use this same identity.
        identity = latest_run(rt)
        if identity is None or identity['lifecycle'] not in ('active', 'closed'):
            return
        if registry is not None:
            previous = read_latest(registry)
            cleanup = (previous or {}).get('pending_cleanup', [])
            cleanup = list(cleanup) if isinstance(cleanup, list) else []
            if previous and (previous['runtime_root'], previous['epoch_id']) != (identity['runtime_root'], identity['epoch_id']):
                if previous['opened_at'] >= identity['opened_at']:
                    return  # An old monitor must never recreate a superseded recording.
                cleanup.append({key: previous[key] for key in ('runtime_root', 'epoch_id')})
            # Publish the live destination before deleting any old replay readers use.
            atomic_write_json(registry, {'schema': 'latest-replay/v1', **identity, 'pending_cleanup': cleanup})
            pending = []
            for item in cleanup:
                if not isinstance(item, dict) or not all(isinstance(item.get(key), str) for key in ('runtime_root', 'epoch_id')):
                    continue
                old = Path(item['runtime_root'])
                _remove_recording(old, item['epoch_id'])
                if (old / 'replay' / f"{item['epoch_id']}.sqlite3").exists():
                    pending.append(item)
            atomic_write_json(registry, {'schema': 'latest-replay/v1', **identity, 'pending_cleanup': pending})
        for path in directory.glob('*.sqlite3'):
            if path.stem != identity['epoch_id']:
                _remove_recording(rt, path.stem)
        _record_once(rt, identity)


class LatestRunFollower:
    """Follow newer epochs across the harness's configured workspaces."""
    def __init__(self, rt: Path, registry: Path | None = None):
        self.rt, self.registry = rt, registry
        self.identity = latest_run(rt)

    def poll(self) -> bool:
        candidates = [item for item in (latest_run(self.rt), read_latest(self.registry)) if item]
        if not candidates:
            return False
        newest = max(candidates, key=lambda item: item['opened_at'])
        current = self.identity
        if current and (newest['runtime_root'], newest['epoch_id']) == (current['runtime_root'], current['epoch_id']):
            return False
        if current and newest['opened_at'] < current['opened_at']:
            return False
        # Registry publication can race bootstrap; wait until native epoch exists.
        actual = latest_run(Path(newest['runtime_root']))
        if not actual or actual['epoch_id'] != newest['epoch_id']:
            return False
        self.rt, self.identity = Path(newest['runtime_root']), actual
        return True


def _record_once(rt: Path, identity: dict) -> None:
    from . import view_state
    if latest_run(rt) != identity:
        return
    epoch = identity['epoch_id']
    directory = rt / 'replay'
    if identity['lifecycle'] == 'closed' and not (directory / f'{epoch}.sqlite3').exists():
        return  # Never relabel an old unrecorded run as a complete recording.
    directory.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(directory / f'{epoch}.sqlite3', timeout=5)) as db, db:
        db.execute('CREATE TABLE IF NOT EXISTS frames (seq INTEGER PRIMARY KEY, at REAL NOT NULL, digest TEXT NOT NULL, payload BLOB NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
        db.execute('INSERT OR IGNORE INTO metadata VALUES (?, ?)', ('schema', SCHEMA))
        db.commit()
        db.execute('BEGIN IMMEDIATE')
        metadata = dict(db.execute('SELECT key,value FROM metadata'))
        if metadata.get('complete') == 'true':
            return
        state = view_state.collect_state(rt)
        if state.get('epoch_id') != epoch or (state.get('status') == 'closed' and identity['lifecycle'] != 'closed'):
            return
        raw = json.dumps(freeze(state), sort_keys=True, ensure_ascii=False).encode()
        if latest_run(rt) != identity:
            return
        digest = hashlib.sha256(raw).hexdigest()
        previous = db.execute('SELECT at, digest FROM frames ORDER BY seq DESC LIMIT 1').fetchone()
        now = max(time.time(), float(metadata.get('last_observed', 0)), previous[0] if previous else 0)
        if not previous or previous[1] != digest:
            db.execute('INSERT INTO frames(at,digest,payload) VALUES(?,?,?)', (now, digest, zlib.compress(raw)))
        db.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)', ('last_observed', str(now)))
        if state.get('status') == 'closed' and identity['lifecycle'] == 'closed':
            db.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)', ('complete', 'true'))


def record_safely(rt: Path, *, registry: Path | None = None) -> None:
    """Recording failure must not interrupt native orchestration."""
    try:
        record_once(rt, registry=registry) if registry else record_once(rt)
    except Exception as exc:
        # Retain an explicit diagnostic instead of pretending an incomplete recording is exact.
        try:
            path = rt / 'replay' / 'recording-errors.log'
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('a', encoding='utf-8') as handle:
                handle.write(f'{time.time():.3f} {type(exc).__name__}: {exc}\n')
        except OSError:
            pass


def start_recorder(rt: Path, *, registry: Path | None = None) -> tuple[threading.Event, threading.Thread]:
    stop = threading.Event()
    def run() -> None:
        while not stop.is_set():
            record_safely(rt, registry=registry)
            stop.wait(SAMPLE_SECONDS)
    thread = threading.Thread(target=run, name='harness-replay-recorder', daemon=True)
    thread.start()
    return stop, thread


def recordings(rt: Path) -> list[dict]:
    result = []
    for path in sorted((rt / 'epochs').glob('*/epoch-state.json')):
        try:
            state = json.loads(path.read_text(encoding='utf-8-sig'))
        except (OSError, ValueError):
            continue
        if not isinstance(state, dict) or not isinstance(state.get('opened_at', ''), str):
            continue
        epoch = path.parent.name
        result.append({'epoch_id': epoch, 'opened_at': state.get('opened_at', ''),
                       'recorded': (rt / 'replay' / f'{epoch}.sqlite3').is_file()})
    return sorted(result, key=lambda item: item['opened_at'])[-1:]


def validate_snapshot(state: Any, epoch: str) -> None:
    def invalid():
        raise ValueError('Replay frame has incomplete or malformed data.')
    if not isinstance(state, dict) or state.get('epoch_id') != epoch or not isinstance(state.get('lanes'), list):
        invalid()
    if not isinstance(state.get('status'), str):
        invalid()
    if not isinstance(state.get('needs_you', []), list) or any(not isinstance(item, dict) for item in state.get('needs_you', [])):
        invalid()
    lanes = state['lanes'] + ([state['root']] if state.get('root') is not None else [])
    for lane in lanes:
        if not isinstance(lane, dict) or any(not isinstance(lane.get(key), str) for key in ('lane_id', 'label', 'tone')):
            invalid()
        if lane.get('review_agent') is not None and not isinstance(lane['review_agent'], dict):
            invalid()
        if any(lane.get(key) is not None and not isinstance(lane[key], str) for key in ('role', 'lifecycle', 'run_id')):
            invalid()
        saved = lane.get('_recorded')
        if not isinstance(saved, dict) or any(not isinstance(saved.get(key), str) for key in ('prompt', 'result')):
            invalid()
        blocks = saved.get('blocks')
        if not isinstance(blocks, list):
            invalid()
        for block in blocks:
            if (not isinstance(block, dict) or set(block) != {'key', 'text', 'prose', 'heading'}
                    or any(not isinstance(block[key], str) for key in ('key', 'text', 'heading'))
                    or not isinstance(block['prose'], bool)):
                invalid()
        events = saved.get('events')
        if not isinstance(events, list) or len(events) != 3 or any(not isinstance(group, list) for group in events):
            invalid()
        if any(not isinstance(error, str) for error in events[2]):
            invalid()
        for item in events[0] + events[1]:
            if not isinstance(item, dict) or not isinstance(item.get('source'), str):
                invalid()
            if 'data' in item and not isinstance(item['data'], dict):
                invalid()
            if 'history' in item and (not isinstance(item['history'], list) or any(not isinstance(h, dict) for h in item['history'])):
                invalid()
        for key in ('steps', 'keys'):
            if not isinstance(lane.get(key, []), list) or any(not isinstance(value, str) for value in lane.get(key, [])):
                invalid()


class Playback:
    def __init__(self, rt: Path, epoch: str | None = None, speed: float = 1.5, *, clock=time.monotonic):
        if not math.isfinite(speed) or not .25 <= speed <= 8:
            raise ValueError('Replay speed must be between 0.25 and 8.')
        choices = recordings(rt)
        if not choices:
            raise ValueError('No past runs found in this runtime.')
        epoch = epoch or choices[-1]['epoch_id']
        if epoch not in {item['epoch_id'] for item in choices}:
            raise ValueError('Unknown replay epoch; use --list-replays.')
        self.epoch, self.speed, self.clock = epoch, speed, clock
        self.paused = False
        self.position = 0.0
        self.last = clock()
        self.generation = 0
        self.approximate = False
        self.warning = ''
        self.frames: list[tuple[float, int, str]] = []
        self._cached_index = -1
        self._cached_state: dict = {}
        path = rt / 'replay' / f'{epoch}.sqlite3'
        self.path = path
        if path.is_file():
            with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)) as db:
                metadata = dict(db.execute('SELECT key,value FROM metadata'))
                if metadata.get('schema') != SCHEMA:
                    raise ValueError('Unsupported replay schema.')
                rows = db.execute('SELECT at,seq,digest FROM frames ORDER BY seq').fetchall()
            if not rows:
                raise ValueError('The replay recording is empty.')
            origin = rows[0][0]
            previous_at = -math.inf
            for at, seq, digest in rows:
                if not isinstance(at, (int, float)) or not math.isfinite(at) or at < previous_at:
                    raise ValueError('Replay timestamps must be finite and ordered.')
                previous_at = at
                with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)) as db:
                    payload = db.execute('SELECT payload FROM frames WHERE seq=?', (seq,)).fetchone()[0]
                raw = zlib.decompress(payload)
                if hashlib.sha256(raw).hexdigest() != digest:
                    raise ValueError('Replay frame failed integrity validation.')
                state = json.loads(raw)
                validate_snapshot(state, epoch)
                self.frames.append((max(0.0, at - origin), seq, digest))
            if state.get('status') != 'closed':
                self.warning = 'Partial recording'
            if (rt / 'replay' / 'recording-errors.log').exists():
                self.warning = 'Recording has gaps; see recording-errors.log'
            endpoint = float(metadata.get('last_observed', rows[-1][0]))
            if not math.isfinite(endpoint) or endpoint < rows[-1][0]:
                raise ValueError('Invalid replay observation endpoint.')
            self.duration = max(self.frames[-1][0], endpoint - origin)
            self.times = [frame[0] for frame in self.frames]
        else:
            from . import view_state
            current = view_state.collect_state(rt)
            if current.get('epoch_id') != epoch:
                raise ValueError('This older epoch has no recording. Approximate replay is available only for the latest retained run.')
            self.final = freeze(current)
            if self.final.get('status') != 'closed':
                raise ValueError('This run is still active and has no replay recording yet.')
            self.approximate = True
            # Old transcripts lack per-update timestamps. Pace text, do not invent exact timing.
            self.duration = max(10.0, max((sum(max(1, len(b['text'].splitlines())) for b in lane['_recorded']['blocks']) / 12
                                         for lane in self.final.get('lanes', [])), default=10.0))
            self.warning = 'Approximate timing · events/reviews shown at end'
        self.last = clock()  # Loading and validation are not playback time.

    def close(self) -> None:
        """Release the frame index and decoded content when live work supersedes replay."""
        self.frames.clear()
        self.times = []
        self._cached_state = {}
        self.final = {}
        self.paused = True

    def tick(self) -> None:
        now = self.clock()
        if not self.paused:
            self.position = min(self.duration, self.position + max(0, now - self.last) * self.speed)
        self.last = now
        if self.position >= self.duration:
            self.paused = True

    def seek(self, position: float) -> None:
        self.tick()
        self.position = max(0.0, min(self.duration, position))
        self.generation += 1

    def control(self, key: str) -> None:
        self.tick()
        if key == ' ':
            self.paused = not self.paused
        elif key == 'r':
            self.seek(0)
            self.paused = False
        elif key in ('[', ']'):
            self.seek(self.position + (-10 if key == '[' else 10))
        elif key in ('+', '-', '='):
            self.speed = max(.25, min(8, self.speed + (-.25 if key == '-' else .25)))

    def state(self) -> dict:
        self.tick()
        if not self.approximate:
            index = max(0, bisect.bisect_right(self.times, self.position) - 1)
            if index != self._cached_index:
                _, seq, digest = self.frames[index]
                with closing(sqlite3.connect(self.path.resolve().as_uri() + '?mode=ro', uri=True)) as db:
                    row = db.execute('SELECT payload FROM frames WHERE seq=?', (seq,)).fetchone()
                if row is None:
                    raise ValueError('Replay recording was replaced.')
                raw = zlib.decompress(row[0])
                if hashlib.sha256(raw).hexdigest() != digest:
                    raise ValueError('Replay frame failed integrity validation.')
                self._cached_state = json.loads(raw)
                self._cached_index = index
            state = copy.deepcopy(self._cached_state)
        else:
            state = copy.deepcopy(self.final)
            fraction = self.position / self.duration
            if fraction < 1:
                state['status'], state['needs_you'] = 'open', []
                for lane in state.get('lanes', []):
                    lane.update(lifecycle='running', label='Replaying saved output', tone='live', root_review=None,
                                steps=['skip'] * 4 + ['now', 'todo', 'skip'])
                    saved = lane['_recorded']
                    saved['result'] = 'Results and reviews appear at the end of this approximate replay.'
                    saved['events'] = [[], [], []]
                    blocks = saved['blocks']
                    budget = int(sum(len(b['text']) for b in blocks) * fraction)
                    visible = []
                    for block in blocks:
                        if budget <= 0:
                            break
                        text = block['text']
                        block['text'] = text[:budget]
                        visible.append(block)
                        budget -= len(text)
                    saved['blocks'] = visible
                if state.get('root'):
                    state['root'].update(label='Replaying saved run', lifecycle='coordinating')
                    state['root']['_recorded']['events'] = [[], [], []]
                    state['root']['_recorded']['result'] = 'Results and reviews appear at the end of this approximate replay.'
        if state.get('root'):
            state['root']['workers'] = state.get('lanes', [])
        state['replay'] = {'position': self.position, 'duration': self.duration, 'speed': self.speed,
                           'paused': self.paused, 'generation': self.generation, 'warning': self.warning,
                           'epoch_id': self.epoch}
        return state
