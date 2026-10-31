import copy
from contextlib import closing
import io
import json
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

from orchestrator_harness import view_replay, view_state, view_artifacts, view_events, view_term, view_render, operator_launch
from orchestrator_harness.tests.test_view import ViewFixture, _write


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.fixture = ViewFixture(Path(self.tmp.name))
        self.rt = self.fixture.rt
        self.state = view_state.collect_state(self.rt)
        # Isolate one worker with real artifacts and record an initial pending result.
        self.state['lanes'] = self.state['lanes'][:1]
        self.state['root']['workers'] = self.state['lanes']
        self.lane = self.state['lanes'][0]
        self.aw = Path(self.lane['worktree_path']) / '.agent-workspace'
        (self.aw / 'worker-prompt.md').write_text('Original task prompt')
        self.transcript = self.aw / 'provider-transcript.jsonl'
        self.lane['artifact_paths']['transcript_path'] = str(self.transcript)
        self.write_output('first output')
        self.now = [0.0]

    def write_output(self, text):
        self.transcript.write_text(json.dumps({'type': 'item.completed', 'item': {'id': 'one', 'type': 'agent_message', 'text': text}}) + '\n')

    def record(self, at):
        if self.state.get('status') == 'closed':
            path = self.rt / 'epochs' / self.state['epoch_id'] / 'epoch-state.json'
            native = json.loads(path.read_text())
            native['lifecycle'] = 'closed'
            _write(path, native)
            (self.rt / 'CURRENT_EPOCH.json').unlink(missing_ok=True)
        with mock.patch.object(view_state, 'collect_state', return_value=self.state), mock.patch.object(view_replay.time, 'time', return_value=at):
            view_replay.record_once(self.rt)

    def playback(self, **kwargs):
        return view_replay.Playback(self.rt, clock=lambda: self.now[0], **kwargs)

    def two_frames(self):
        self.record(100)
        self.write_output('first output\nsecond output')
        self.state['status'] = 'closed'
        self.record(115)

    def test_speed_pause_seek_restart_and_speed_changes(self):
        self.two_frames()
        playback = self.playback()
        self.now[0] = 4
        self.assertEqual(6, playback.state()['replay']['position'])
        playback.control(' ')
        self.now[0] = 8
        self.assertEqual(6, playback.state()['replay']['position'])
        playback.control('+')
        self.assertEqual(1.75, playback.speed)
        playback.control(']')
        self.assertEqual(15, playback.position)
        playback.control('r')
        self.assertFalse(playback.paused)
        self.assertEqual(0, playback.position)
        playback.control('[')
        self.assertEqual(0, playback.position)
        playback = self.playback(speed=40)
        self.now[0] += .25
        self.assertEqual(10, playback.state()['replay']['position'])
        playback.control('+')
        self.assertEqual(40, playback.speed)
        playback.control('-')
        self.assertEqual(39.75, playback.speed)
        for speed in (0, -1, float('nan'), float('inf'), 40.1):
            with self.assertRaises(ValueError):
                self.playback(speed=speed)

    def test_replay_is_frozen_and_cannot_read_future_artifacts(self):
        self.record(100)
        self.write_output('future output')
        (self.aw / 'worker-prompt.md').write_text('Changed task prompt')
        self.lane['root_review'] = {'verdict': 'PASS', 'approval': 'ACCEPTED', 'reviewer': 'ROOT', 'summary': 'Future review', 'evidence': []}
        self.state['status'] = 'closed'
        self.record(115)
        playback = self.playback()
        # Reading any current file through artifact helpers would fail this test.
        with mock.patch.object(view_artifacts, 'read_text', side_effect=AssertionError('live artifact read')), mock.patch.object(Path, 'read_text', side_effect=AssertionError('live mailbox read')):
            earlier = playback.state()
            lane = earlier['lanes'][0]
            self.assertEqual('Original task prompt', view_artifacts.panel_text(lane, 'prompt').split('\n', 1)[1])
            self.assertEqual('first output', view_artifacts.output_blocks(lane)[0].text)
            self.assertNotIn('Future review', view_artifacts.panel_text(lane, 'result'))
            self.assertNotIn('Future review', view_artifacts.panel_text(earlier['root'], 'result'))
            view_events.mailbox_text(earlier['root'])
            playback.seek(15)
            later = playback.state()
            self.assertIn('Future review', view_artifacts.panel_text(later['root'], 'result'))
            playback.seek(0)
            self.assertNotIn('Future review', view_artifacts.panel_text(playback.state()['root'], 'result'))

    def test_recorded_events_retain_original_summary_and_history(self):
        identity = {key: self.lane[key] for key in ('lane_id', 'run_id')}
        inbox_path = self.aw / 'QUEUE.json'
        inbox = dict(identity, schema='lane-inbox/v1', assignments=[dict(identity, event_id='assignment', prompt='Original message', state='PENDING')])
        _write(inbox_path, inbox)
        self.record(100)
        inbox['assignments'][0].update(prompt='Updated message', state='COMPLETE')
        _write(inbox_path, inbox)
        self.record(110)
        playback = self.playback()
        text = view_events.mailbox_text(playback.state()['lanes'][0])
        self.assertIn('Original message', text)
        self.assertNotIn('Updated message', text)
        playback.seek(10)
        self.assertIn('Updated message', view_events.mailbox_text(playback.state()['lanes'][0]))

    def test_unchanged_observations_deduplicate_and_monotonic_timestamp(self):
        self.record(100)
        self.record(110)
        self.write_output('changed')
        self.record(90)
        playback = self.playback()
        self.assertEqual(2, len(playback.frames))
        self.assertEqual(sorted(playback.times), playback.times)
        self.assertIn('Partial', playback.warning)

    def test_failed_recording_is_reported_and_does_not_break_harness(self):
        with mock.patch.object(view_replay, 'record_once', side_effect=OSError('disk unavailable')):
            view_replay.record_safely(self.rt)
        self.assertIn('disk unavailable', (self.rt / 'replay' / 'recording-errors.log').read_text())

    def test_read_only_replay_and_corrupt_recording_rejected(self):
        self.two_frames()
        before = {p: p.read_bytes() for p in self.rt.rglob('*') if p.is_file()}
        playback = self.playback()
        playback.seek(15)
        playback.state()
        self.assertEqual(before, {p: p.read_bytes() for p in self.rt.rglob('*') if p.is_file()})
        database = next((self.rt / 'replay').glob('*.sqlite3'))
        with closing(sqlite3.connect(database)) as db, db:
            db.execute("UPDATE frames SET digest='invalid' WHERE seq=1")
        with self.assertRaisesRegex(ValueError, 'integrity'):
            self.playback()

    def test_approximate_legacy_replay_is_labeled_and_hides_results_until_end(self):
        state = copy.deepcopy(self.state)
        state['status'] = 'closed'
        with mock.patch.object(view_state, 'collect_state', return_value=state):
            playback = self.playback()
        earlier = playback.state()
        self.assertIn('Approximate', earlier['replay']['warning'])
        self.assertEqual([], view_artifacts.output_blocks(earlier['lanes'][0]))
        self.assertIn('at the end', view_artifacts.panel_text(earlier['lanes'][0], 'result'))
        playback.seek(playback.duration)
        self.assertEqual('closed', playback.state()['status'])
        with self.assertRaisesRegex(ValueError, 'Unknown replay epoch'):
            self.playback(epoch='../outside')

    def test_cli_flags_and_replay_error(self):
        args = operator_launch._build_parser().parse_args(['view', '--replay', '--speed', '1.5', '--epoch', 'test'])
        self.assertTrue(args.replay)
        self.assertEqual('test', args.epoch)
        result = view_term.run_view(runtime_root=str(self.rt), replay=True, epoch_id='missing', once=True)
        self.assertFalse(result['ok'])
        self.assertEqual('VIEW_REPLAY_INVALID', result['code'])
        result = view_term.run_view(runtime_root=str(self.rt), list_replays=True, once=True)
        self.assertEqual(1, len(result['recordings']))

    def test_interactive_replay_controls_seek_resets_future_output(self):
        self.two_frames()
        playback = self.playback()
        output = io.StringIO()
        frames = []
        original = view_render.render
        def render(*args, **kwargs):
            frames.append((copy.deepcopy(args[0]), kwargs.get('artifact_text')))
            return original(*args, **kwargs)
        with mock.patch.object(view_term._Keys, 'raw'), mock.patch.object(view_term._Keys, 'read', side_effect=['enter', ']', ']', 'r', ' ', 'q']), mock.patch.object(view_term, '_terminal_size', return_value=(100, 30)), mock.patch.object(view_render, 'render', side_effect=render):
            view_term.run_interactive(lambda: self.state, playback=playback, out=output, depth=0, ascii_only=True)
        self.assertIn('REPLAY 1.5x', output.getvalue())
        self.assertIn('second output', frames[3][1])
        self.assertNotIn('second output', frames[4][1])
        self.assertEqual(0, frames[4][0]['replay']['position'])

    def test_selection_stays_on_same_agent_when_new_lane_appears(self):
        # ROOT was selected while no worker existed; adding a worker must not open it instead.
        empty = copy.deepcopy(self.state)
        empty['lanes'] = []
        empty['root']['workers'] = []
        states = iter([empty, self.state, self.state, self.state])
        moment = [0]
        keys = iter(['enter', 'q'])
        def read(_):
            moment[0] += 3
            return next(keys)
        output = io.StringIO()
        with mock.patch.object(view_term._Keys, 'raw'), mock.patch.object(view_term._Keys, 'read', side_effect=read), mock.patch.object(view_term.time, 'monotonic', side_effect=lambda: moment[0]), mock.patch.object(view_term, '_terminal_size', return_value=(120, 30)):
            view_term.run_interactive(lambda: next(states), out=output, depth=0, ascii_only=True)
        self.assertIn('visible in the terminal CLI', output.getvalue())

    def test_old_closed_run_is_not_retroactively_marked_recorded(self):
        (self.rt / 'CURRENT_EPOCH.json').unlink()
        view_replay.record_once(self.rt)
        self.assertFalse((self.rt / 'replay').exists())

    def test_root_evidence_is_frozen_and_closed_recording_is_sealed(self):
        report = self.rt.parent / 'checks.txt'
        report.write_text('Original checks passed')
        self.lane['root_review'] = {'verdict': 'PASS', 'approval': 'ACCEPTED', 'reviewer': 'ROOT', 'summary': 'Reviewed', 'evidence': [str(report)], 'workspace': str(self.rt.parent)}
        self.record(100)
        self.state['status'] = 'closed'
        self.record(110)
        report.write_text('Future unrelated report')
        self.write_output('Future unrelated output')
        self.record(500)
        playback = self.playback()
        self.assertEqual(10, playback.duration)
        playback.seek(10)
        with mock.patch.object(view_artifacts, 'read_text', side_effect=AssertionError('live artifact read')):
            for lane in [*playback.state()['lanes'], playback.state()['root']]:
                text = view_artifacts.panel_text(lane, 'result')
                self.assertIn('Original checks passed', text)
                self.assertNotIn('Future unrelated report', text)

    def test_idle_observations_extend_partial_recording_duration(self):
        self.record(100)
        self.record(200)
        playback = self.playback()
        self.assertEqual(1, len(playback.frames))
        self.assertEqual(100, playback.duration)

    def test_loading_does_not_advance_playback_clock(self):
        self.two_frames()
        validate = view_replay.validate_snapshot
        def slow_validate(*args):
            self.now[0] += 20
            return validate(*args)
        with mock.patch.object(view_replay, 'validate_snapshot', side_effect=slow_validate):
            playback = self.playback()
        self.assertEqual(0, playback.state()['replay']['position'])

    def test_malformed_frames_and_nonmonotonic_timestamps_are_rejected(self):
        import hashlib
        import zlib
        self.two_frames()
        database = next((self.rt / 'replay').glob('*.sqlite3'))
        with closing(sqlite3.connect(database)) as db:
            original = db.execute('SELECT payload FROM frames WHERE seq=1').fetchone()[0]
        good = json.loads(zlib.decompress(original))
        for mutate in (
            lambda state: state['lanes'][0].update(_recorded={}),
            lambda state: state.update(needs_you=1),
            lambda state: state.update(status=[]),
            lambda state: state['lanes'][0].update(review_agent=['bad']),
            lambda state: state['lanes'][0].pop('tone'),
            lambda state: state['lanes'][0].update(steps=[{}]),
            lambda state: state['lanes'][0]['_recorded'].update(blocks=[{}]),
            lambda state: state['root']['_recorded'].update(events=[None, [], []]),
        ):
            state = copy.deepcopy(good)
            mutate(state)
            raw = json.dumps(state).encode()
            with closing(sqlite3.connect(database)) as db, db:
                db.execute('UPDATE frames SET digest=?,payload=? WHERE seq=1', (hashlib.sha256(raw).hexdigest(), zlib.compress(raw)))
            with self.assertRaisesRegex(ValueError, 'malformed'):
                self.playback()
            self.assertEqual('VIEW_REPLAY_INVALID', view_term.run_view(runtime_root=str(self.rt), replay=True, once=True)['code'])
        raw = zlib.decompress(original)
        with closing(sqlite3.connect(database)) as db, db:
            db.execute('UPDATE frames SET digest=?,payload=? WHERE seq=1', (hashlib.sha256(raw).hexdigest(), original))
            db.execute('UPDATE frames SET at=99 WHERE seq=2')
        with self.assertRaisesRegex(ValueError, 'timestamps'):
            self.playback()
        extra = self.rt / 'epochs' / 'bad' / 'epoch-state.json'
        _write(extra, ['not an object'])
        self.assertEqual(1, len(view_replay.recordings(self.rt)))

    def test_replay_page_down_reaches_last_line(self):
        (self.aw / 'worker-prompt.md').write_text('\n'.join(f'prompt-line-{i}' for i in range(80)))
        self.two_frames()
        playback = self.playback()
        playback.paused = True
        frames = []
        render = view_render.render
        def capture(*args, **kwargs):
            lines = render(*args, **kwargs)
            frames.append(lines)
            return lines
        with mock.patch.object(view_term._Keys, 'raw'), mock.patch.object(view_term._Keys, 'read', side_effect=['enter', 'left'] + ['pagedown'] * 12 + ['q']), mock.patch.object(view_term, '_terminal_size', return_value=(100, 24)), mock.patch.object(view_render, 'render', side_effect=capture):
            view_term.run_interactive(lambda: self.state, playback=playback, out=io.StringIO(), depth=0, ascii_only=True)
        self.assertIn('prompt-line-79', '\n'.join(frames[-1]))

    def test_replay_event_selection_stays_visible_beyond_viewport(self):
        identity = {key: self.lane[key] for key in ('lane_id', 'run_id')}
        _write(self.aw / 'QUEUE.json', dict(identity, schema='lane-inbox/v1', assignments=[
            dict(identity, event_id=f'event-{i}', prompt=f'Event message {i}', state='PENDING') for i in range(20)]))
        self.two_frames()
        playback = self.playback()
        playback.paused = True
        frames = []
        render = view_render.render
        def capture(*args, **kwargs):
            lines = render(*args, **kwargs)
            frames.append(lines)
            return lines
        with mock.patch.object(view_term._Keys, 'raw'), mock.patch.object(view_term._Keys, 'read', side_effect=['enter', 'right', 'right'] + ['down'] * 12 + ['q']), mock.patch.object(view_term, '_terminal_size', return_value=(100, 24)), mock.patch.object(view_render, 'render', side_effect=capture):
            view_term.run_interactive(lambda: self.state, playback=playback, out=io.StringIO(), depth=0, ascii_only=True)
        self.assertIn('> [+]', '\n'.join(frames[-1]))


    def new_epoch(self, rt, epoch='f' * 32, opened='2027-01-01T00:00:00Z'):
        _write(rt / 'CURRENT_EPOCH.json', {'schema': 'current-epoch/v1', 'epoch_id': epoch})
        _write(rt / 'epochs' / epoch / 'epoch-state.json', {'schema': 'epoch-state/v1', 'epoch_id': epoch, 'opened_at': opened, 'lane_mode': 'managed', 'lifecycle': 'active'})
        return epoch

    def test_new_epoch_retains_older_recordings_and_explicit_playback(self):
        self.two_frames()
        old_epoch = self.state['epoch_id']
        old_database = self.rt / 'replay' / f'{old_epoch}.sqlite3'
        original = old_database.read_bytes()
        newer = self.new_epoch(self.rt)
        next_state = view_state.collect_state(self.rt, epoch_id=newer)
        with mock.patch.object(view_state, 'collect_state', return_value=next_state):
            view_replay.record_once(self.rt)
        self.assertEqual(original, old_database.read_bytes())
        choices = view_replay.recordings(self.rt)
        self.assertEqual([old_epoch, newer], [item['epoch_id'] for item in choices])
        self.assertTrue(all(item['recorded'] for item in choices))
        older = self.playback(epoch=old_epoch)
        self.assertEqual(old_epoch, older.state()['epoch_id'])
        older.seek(older.duration)
        self.assertIn('second output', view_artifacts.panel_text(older.state()['lanes'][0], 'output'))
        self.assertEqual(newer, self.playback().epoch)

    def test_older_unrecorded_epoch_has_explicit_approximate_playback(self):
        old_epoch = self.state['epoch_id']
        self.new_epoch(self.rt)
        playback = self.playback(epoch=old_epoch)
        self.assertTrue(playback.approximate)
        self.assertIn('Approximate', playback.warning)
        self.assertEqual(old_epoch, playback.state()['epoch_id'])
        self.assertFalse((self.rt / 'replay').exists())

    def test_recording_is_pinned_to_native_identity_during_rollover(self):
        original_collect = view_state.collect_state
        old_epoch = self.state['epoch_id']

        def collect(rt, *, epoch_id):
            self.assertEqual(old_epoch, epoch_id)
            state = original_collect(rt, epoch_id=epoch_id)
            self.new_epoch(rt)
            return state

        with mock.patch.object(view_state, 'collect_state', side_effect=collect):
            view_replay.record_once(self.rt)
        self.assertFalse((self.rt / 'replay' / f'{old_epoch}.sqlite3').exists())

    def test_recorder_thread_captures_without_opening_viewer(self):
        captured = threading.Event()
        with mock.patch.object(view_replay, 'record_safely', side_effect=lambda rt: captured.set()):
            stop, thread = view_replay.start_recorder(self.rt)
            try:
                self.assertTrue(captured.wait(timeout=2))
            finally:
                stop.set()
                thread.join(timeout=2)
        self.assertFalse(thread.is_alive())





    def test_playback_keeps_index_only_and_loads_one_snapshot(self):
        self.two_frames()
        playback = self.playback()
        self.assertTrue(all(isinstance(frame[1], int) and isinstance(frame[2], str) for frame in playback.frames))
        self.assertFalse(any(isinstance(value, bytes) for frame in playback.frames for value in frame))
        self.assertEqual({}, playback._cached_state)
        self.assertIn('first output', view_artifacts.output_blocks(playback.state()['lanes'][0])[0].text)
        self.assertTrue(playback._cached_state)
        playback.close()
        self.assertEqual([], playback.frames)
        self.assertEqual({}, playback._cached_state)

    def test_startup_decodes_only_endpoints_of_a_large_recording(self):
        self.record(100)
        for number in range(1, 30):
            self.write_output(f'frame {number}')
            self.record(100 + number)
        self.state['status'] = 'closed'
        self.record(130)
        with mock.patch.object(view_replay.zlib, 'decompress', wraps=view_replay.zlib.decompress) as decode:
            playback = self.playback()
            self.assertEqual(31, len(playback.frames))
            self.assertEqual(2, decode.call_count)
            playback.seek(15)
            playback.state()
            self.assertEqual(3, decode.call_count)

    def test_middle_snapshot_is_validated_before_display(self):
        import hashlib
        import zlib
        self.record(100)
        self.write_output('middle')
        self.record(110)
        self.state['status'] = 'closed'
        self.record(120)
        database = next((self.rt / 'replay').glob('*.sqlite3'))
        with closing(sqlite3.connect(database)) as db:
            original = db.execute('SELECT payload FROM frames WHERE seq=2').fetchone()[0]
        for malformed in (False, True):
            raw = zlib.decompress(original)
            if malformed:
                state = json.loads(raw)
                state['lanes'][0]['_recorded'] = {}
                raw = json.dumps(state).encode()
            digest = hashlib.sha256(raw).hexdigest() if malformed else '0' * 64
            with closing(sqlite3.connect(database)) as db, db:
                db.execute('UPDATE frames SET digest=?,payload=? WHERE seq=2', (digest, zlib.compress(raw)))
            playback = self.playback()
            playback.seek(10)
            with self.assertRaisesRegex(ValueError, 'malformed' if malformed else 'integrity'):
                playback.state()
            self.assertEqual({}, playback._cached_state)

    def test_deleted_recording_during_playback_does_not_crash_tui(self):
        self.two_frames()
        playback = self.playback()
        playback.paused = True
        keys = iter(['enter', ']', ']', 'q'])
        def read(_):
            key = next(keys)
            if key == ']':
                playback.path.unlink(missing_ok=True)
            return key
        output = io.StringIO()
        with mock.patch.object(view_term._Keys, 'raw'), mock.patch.object(view_term._Keys, 'read', side_effect=read), mock.patch.object(view_term, '_terminal_size', return_value=(100, 30)):
            view_term.run_interactive(lambda: self.state, playback=playback, out=output, depth=0, ascii_only=True)
        self.assertEqual([], playback.frames)
        self.assertTrue(output.getvalue().endswith(view_term._LEAVE_SCREEN))



    def test_opening_and_closing_transitions_cannot_seal_recording_early(self):
        epoch = self.state['epoch_id']
        native_path = self.rt / 'epochs' / epoch / 'epoch-state.json'
        native = json.loads(native_path.read_text())
        native['lifecycle'] = 'opening'
        _write(native_path, native)
        view_replay.record_once(self.rt)
        self.assertFalse((self.rt / 'replay' / f'{epoch}.sqlite3').exists())
        native['lifecycle'] = 'active'
        _write(native_path, native)
        self.record(100)
        (self.rt / 'CURRENT_EPOCH.json').unlink()
        view_replay.record_once(self.rt)  # Viewer says closed; native close has not committed.
        with closing(sqlite3.connect(self.rt / 'replay' / f'{epoch}.sqlite3')) as db:
            self.assertNotEqual('true', dict(db.execute('SELECT key,value FROM metadata')).get('complete'))
        native['lifecycle'] = 'closed'
        _write(native_path, native)
        view_replay.record_once(self.rt)
        with closing(sqlite3.connect(self.rt / 'replay' / f'{epoch}.sqlite3')) as db:
            self.assertEqual('true', dict(db.execute('SELECT key,value FROM metadata'))['complete'])

    def test_pruning_before_first_playback_read_falls_back_to_live(self):
        self.two_frames()
        playback = self.playback()
        playback.path.unlink()
        output = io.StringIO()
        with mock.patch.object(view_term._Keys, 'raw'), mock.patch.object(view_term._Keys, 'read', return_value='q'), mock.patch.object(view_term, '_terminal_size', return_value=(100, 30)):
            view_term.run_interactive(lambda: self.state, playback=playback, out=output, depth=0, ascii_only=True)
        self.assertEqual([], playback.frames)
        self.assertNotIn('REPLAY', output.getvalue())

