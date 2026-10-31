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
from datetime import datetime, timezone
from contextlib import closing
from pathlib import Path
from typing import Any

SCHEMA = 'harness-replay/v1'
SAMPLE_SECONDS = 1.0
MAX_REPLAY_SPEED = 40


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
    from .view_state import _parse_time, _valid_epoch_id
    try:
        marker = read_current_epoch(rt)
        if marker:
            epoch = marker.get('epoch_id')
            if not _valid_epoch_id(epoch):
                return None
            state = json.loads((rt / 'epochs' / epoch / 'epoch-state.json').read_text(encoding='utf-8-sig'))
        else:
            # Identity checks run several times per sample. Do not enumerate every
            # historical lane just to find the latest epoch.
            choices = []
            for path in (rt / 'epochs').glob('*/epoch-state.json'):
                if not _valid_epoch_id(path.parent.name):
                    continue
                try:
                    candidate = json.loads(path.read_text(encoding='utf-8-sig'))
                except (OSError, ValueError):
                    continue
                if (isinstance(candidate, dict) and candidate.get('schema') == 'epoch-state/v1'
                        and candidate.get('epoch_id') == path.parent.name
                        and isinstance(candidate.get('opened_at'), str)):
                    choices.append((path.parent.name, candidate))
            if not choices:
                return None
            epoch, state = max(choices, key=lambda item: (
                _parse_time(item[1]['opened_at']) or datetime.min.replace(tzinfo=timezone.utc), item[0],
            ))
        if (not isinstance(state, dict) or state.get('schema') != 'epoch-state/v1'
                or state.get('epoch_id') != epoch or not isinstance(state.get('opened_at'), str)):
            return None
        return {'runtime_root': str(rt.resolve()), 'epoch_id': epoch, 'opened_at': state['opened_at'], 'lifecycle': state.get('lifecycle')}
    except (OSError, ValueError, KeyError, TypeError):
        return None


def record_once(rt: Path) -> None:
    """Record the native current/latest epoch without pruning earlier recordings."""
    identity = latest_run(rt)
    if identity is None or identity['lifecycle'] not in ('active', 'closed'):
        return
    if not (rt / 'CURRENT_EPOCH.json').is_file() and not (rt / 'replay' / f"{identity['epoch_id']}.sqlite3").exists():
        return
    _record_once(rt, identity)


def reopen_recording(rt: Path, epoch: str, generation: int) -> None:
    """Append a resumed interval to the same journal; never rewrite its frames."""
    identity = latest_run(rt)
    if not identity or identity['epoch_id'] != epoch or identity['lifecycle'] != 'active':
        raise ValueError('Only the active native epoch can resume its recording.')
    path = rt / 'replay' / f'{epoch}.sqlite3'
    if not path.exists():
        return
    if path.is_symlink():
        raise ValueError('Replay recording must be a regular file.')
    with closing(sqlite3.connect(path, timeout=5)) as db, db:
        db.execute('BEGIN IMMEDIATE')
        metadata = dict(db.execute('SELECT key,value FROM metadata'))
        if metadata.get('schema') != SCHEMA:
            raise ValueError('Unsupported replay schema.')
        if int(metadata.get('reopen_count', '0')) >= generation:
            return
        seals = json.loads(metadata.get('closure_history', '[]'))
        if metadata.get('complete') == 'true':
            seals.append({'last_observed': metadata.get('last_observed'), 'reopen_count': generation})
        for key, value in (('closure_history', json.dumps(seals)),
                           ('complete', 'false'), ('reopen_count', str(generation))):
            db.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)', (key, value))


def _record_once(rt: Path, identity: dict) -> None:
    from . import view_state
    if latest_run(rt) != identity:
        return
    epoch = identity['epoch_id']
    directory = rt / 'replay'
    if identity['lifecycle'] == 'closed' and not (directory / f'{epoch}.sqlite3').exists():
        return  # Never relabel an old unrecorded run as a complete recording.
    path = directory / f'{epoch}.sqlite3'
    if path.is_symlink():
        raise ValueError('Replay recording must be a regular file.')
    if path.is_file():
        with closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True, timeout=5)) as db:
            metadata = dict(db.execute('SELECT key,value FROM metadata'))
        if metadata.get('schema') != SCHEMA:
            raise ValueError('Unsupported replay schema.')
        if metadata.get('complete') == 'true':
            return
    # Do not lock the database while inspecting worktrees and formatting artifacts.
    state = view_state.collect_state(rt, epoch_id=epoch)
    if state.get('epoch_id') != epoch or (state.get('status') == 'closed' and identity['lifecycle'] != 'closed'):
        return
    raw = json.dumps(freeze(state), sort_keys=True, ensure_ascii=False).encode()
    if latest_run(rt) != identity:
        return
    digest = hashlib.sha256(raw).hexdigest()
    payload = zlib.compress(raw)
    directory.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path, timeout=5)) as db, db:
        db.execute('CREATE TABLE IF NOT EXISTS frames (seq INTEGER PRIMARY KEY, at REAL NOT NULL, digest TEXT NOT NULL, payload BLOB NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)')
        db.execute('INSERT OR IGNORE INTO metadata VALUES (?, ?)', ('schema', SCHEMA))
        db.commit()
        db.execute('BEGIN IMMEDIATE')
        metadata = dict(db.execute('SELECT key,value FROM metadata'))
        if metadata.get('schema') != SCHEMA:
            raise ValueError('Unsupported replay schema.')
        if metadata.get('complete') == 'true':
            return
        if latest_run(rt) != identity:
            return
        previous = db.execute('SELECT at, digest FROM frames ORDER BY seq DESC LIMIT 1').fetchone()
        now = max(time.time(), float(metadata.get('last_observed', 0)), previous[0] if previous else 0)
        if not previous or previous[1] != digest:
            db.execute('INSERT INTO frames(at,digest,payload) VALUES(?,?,?)', (now, digest, payload))
        db.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)', ('last_observed', str(now)))
        if state.get('status') == 'closed' and identity['lifecycle'] == 'closed':
            db.execute('INSERT OR REPLACE INTO metadata VALUES (?, ?)', ('complete', 'true'))


def record_safely(rt: Path) -> None:
    """Recording failure must not interrupt native orchestration."""
    try:
        record_once(rt)
    except Exception as exc:
        # Retain an explicit diagnostic instead of pretending an incomplete recording is exact.
        try:
            path = rt / 'replay' / 'recording-errors.log'
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('a', encoding='utf-8') as handle:
                handle.write(f'{time.time():.3f} {type(exc).__name__}: {exc}\n')
        except OSError:
            pass


def start_recorder(rt: Path) -> tuple[threading.Event, threading.Thread]:
    stop = threading.Event()
    def run() -> None:
        while not stop.is_set():
            record_safely(rt)
            stop.wait(SAMPLE_SECONDS)
    thread = threading.Thread(target=run, name='harness-replay-recorder', daemon=True)
    thread.start()
    return stop, thread


def recordings(rt: Path) -> list[dict]:
    from .view_state import list_epochs
    return [{'epoch_id': item['epoch_id'], 'opened_at': item['opened_at'], 'status': item['status'],
             'recorded': (rt / 'replay' / f"{item['epoch_id']}.sqlite3").is_file()}
            for item in reversed(list_epochs(rt))]


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
        if not math.isfinite(speed) or not .25 <= speed <= MAX_REPLAY_SPEED:
            raise ValueError('Replay speed must be between 0.25 and 40.')
        choices = recordings(rt)
        if not choices:
            raise ValueError('No past runs found in this runtime.')
        if epoch is None:
            identity = latest_run(rt)
            epoch = identity['epoch_id'] if identity else choices[-1]['epoch_id']
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
                if (not isinstance(digest, str) or len(digest) != 64
                        or any(character not in '0123456789abcdef' for character in digest)):
                    raise ValueError('Replay frame failed integrity validation.')
                self.frames.append((max(0.0, at - origin), seq, digest))
            # Indexing is cheap even for long runs. Decode the endpoints now and
            # validate every other snapshot immediately before displaying it.
            # Eagerly decoding every cumulative transcript delays the first frame.
            state = self._read_frame(0)
            if len(self.frames) > 1:
                state = self._read_frame(-1)
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
            current = view_state.collect_state(rt, epoch_id=epoch)
            self.final = freeze(current)
            if self.final.get('status') != 'closed':
                raise ValueError('This run is still active and has no replay recording yet.')
            self.approximate = True
            # Old transcripts lack per-update timestamps. Pace text, do not invent exact timing.
            self.duration = max(10.0, max((sum(max(1, len(b['text'].splitlines())) for b in lane['_recorded']['blocks']) / 12
                                         for lane in self.final.get('lanes', [])), default=10.0))
            self.warning = 'Approximate timing · events/reviews shown at end'
        self.last = clock()  # Loading and validation are not playback time.

    def _read_frame(self, index: int) -> dict:
        _, seq, digest = self.frames[index]
        with closing(sqlite3.connect(self.path.resolve().as_uri() + '?mode=ro', uri=True)) as db:
            row = db.execute('SELECT payload FROM frames WHERE seq=?', (seq,)).fetchone()
        if row is None:
            raise ValueError('Replay recording was replaced.')
        raw = zlib.decompress(row[0])
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError('Replay frame failed integrity validation.')
        state = json.loads(raw)
        validate_snapshot(state, self.epoch)
        return state

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
            self.speed = max(.25, min(MAX_REPLAY_SPEED, self.speed + (-.25 if key == '-' else .25)))

    def state(self) -> dict:
        self.tick()
        if not self.approximate:
            index = max(0, bisect.bisect_right(self.times, self.position) - 1)
            if index != self._cached_index:
                self._cached_state = self._read_frame(index)
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
