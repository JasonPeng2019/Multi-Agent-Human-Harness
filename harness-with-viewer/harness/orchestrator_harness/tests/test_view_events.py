import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator_harness import view_artifacts, view_state, view_term, view_render, view_events
from orchestrator_harness.tests.test_view import ViewFixture, EPOCH, _write


class EventsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.fixture = ViewFixture(Path(self.tmp.name))
        self.state = view_state.collect_state(self.fixture.rt)
        self.lane = self.state['lanes'][0]
        self.workspace = Path(self.lane['worktree_path']) / '.agent-workspace'
        self.identity = {key: self.lane[key] for key in ('lane_id', 'run_id')}
        self.assignment = dict(self.identity, event_id='assignment-1', prompt='Please check edge cases.', state='PENDING', created_at='2026-10-30T10:00:00Z')
        self.event = dict(self.identity, event_id='envelope-1', type='LANE_STATUS_CHANGED', summary='Need guidance.', state='ACKNOWLEDGED', data={'signal_id': 'signal-1'}, history=[{'state': 'PENDING', 'at': '2026-10-30T11:00:00Z'}])
        self.notice = dict(self.identity, signal_id='signal-1', message='Which empty-input behavior should I use?')

    def inbox(self, assignments):
        _write(self.workspace / 'QUEUE.json', dict(self.identity, schema='lane-inbox/v1', assignments=assignments))

    def queue(self, events, epoch=EPOCH):
        _write(Path(self.lane['manager_queue_path']), {'schema': 'manager-queue/v1', 'epoch_id': epoch, 'events': events})

    def text(self):
        entries, _ = view_events.mailbox_entries(self.lane)
        return view_events.mailbox_text(self.lane, expanded={key for key, _, _ in entries})

    def test_direction_and_full_promoted_message_without_duplicates(self):
        self.inbox([self.assignment])
        self.queue([self.event])
        for folder in ('manager-notifications', 'processed-notifications'):
            _write(self.workspace / folder / 'notice.json', self.notice)
        text = self.text()
        inbox, outbox = text.split('### Outbox')
        self.assertIn('Please check edge cases.', inbox)
        self.assertNotIn('Need guidance.', inbox)
        self.assertIn('Agent → ROOT (1)', outbox)
        self.assertIn('Which empty-input behavior', outbox)
        self.assertIn('ACKNOWLEDGED', outbox)
        self.assertIn('envelope-1', outbox)
        self.assertIn('signal-1', outbox)

    def test_scope_excludes_other_lanes_runs_and_epochs(self):
        self.inbox([dict(self.assignment, run_id='old'), dict(self.assignment, lane_id='other')])
        self.queue([dict(self.event, run_id='old'), dict(self.event, lane_id='other')])
        _write(self.workspace / 'processed-notifications' / 'old.json', dict(self.notice, run_id='old'))
        self.assertNotIn('guidance', self.text())
        self.assertNotIn('edge cases', self.text())
        self.queue([self.event], epoch='old')
        self.assertNotIn('guidance', self.text())

    def test_pending_processed_and_harness_events_are_labeled(self):
        _write(self.workspace / 'manager-notifications' / 'new.json', self.notice)
        self.assertIn('AWAITING FORWARDING', self.text())
        (self.workspace / 'manager-notifications' / 'new.json').unlink()
        _write(self.workspace / 'processed-notifications' / 'new.json', self.notice)
        self.assertIn('FORWARDED', self.text())
        self.queue([dict(self.event, data={}, type='COMPLETION_REVIEW_REQUIRED')])
        self.assertIn('Harness status event', self.text())

    def test_empty_malformed_and_resumed_unscoped_records(self):
        self.assertIn('No events recorded', self.text())
        (self.workspace / 'QUEUE.json').write_text('{broken')
        self.assertIn('Read errors', self.text())
        self.inbox(None)
        self.queue(None)
        self.assertIn('No events recorded', self.text())
        self.lane['resumed'] = True
        _write(self.workspace / 'processed-notifications' / 'old.json', {'message': 'ambiguous old message'})
        self.assertNotIn('ambiguous old message', self.text())

    def test_closed_runtime_keeps_queue_and_view_is_read_only(self):
        self.queue([self.event])
        (self.fixture.rt / 'CURRENT_EPOCH.json').unlink()
        before = {p: p.read_bytes() for p in self.fixture.rt.rglob('*') if p.is_file()}
        lane = view_state.collect_state(self.fixture.rt)['lanes'][0]
        self.assertIn('Need guidance.', view_artifacts.panel_text(lane, 'events'))
        self.assertEqual(before, {p: p.read_bytes() for p in self.fixture.rt.rglob('*') if p.is_file()})

    def test_navigation_and_live_refresh(self):
        moment = [0.0]
        keys = iter(['enter', 'right', 'right', None, 'left', 'q'])
        def read(timeout):
            key = next(keys)
            moment[0] += 3
            if key is None:
                self.inbox([self.assignment])
            return key
        output = io.StringIO()
        with mock.patch.object(view_term._Keys, 'raw'), mock.patch.object(view_term._Keys, 'read', side_effect=read), mock.patch.object(view_term.time, 'monotonic', side_effect=lambda: moment[0]), mock.patch.object(view_term, '_terminal_size', return_value=(100, 30)):
            view_term.run_interactive(lambda: self.state, out=output, depth=0, ascii_only=True)
        self.assertIn('[Events]', output.getvalue())
        self.assertIn('Please check edge cases.', output.getvalue())
        screen = view_render.render(self.state, 80, 24, panel='events', artifact_text=self.text(), depth=0)
        self.assertIn('[Events]', screen[2])
        self.assertTrue(all(view_render.text_width(line) == 80 for line in screen))

    def test_events_start_collapsed_and_expand_entire_record(self):
        self.inbox([dict(self.assignment, prompt='Long prompt ' * 100, payload={'nested': ['complete contents']})])
        text = view_artifacts.panel_text(self.lane, 'events')
        self.assertIn('[+]', text)
        self.assertNotIn('complete contents', text)
        self.assertNotIn('assignment-1', text)
        self.assertIn('complete contents', self.text())
        self.assertIn('assignment-1', self.text())
        self.assertIn('Long prompt ' * 100, self.text())

    def test_root_mailboxes_reverse_directions_and_exclude_unsent(self):
        self.inbox([self.assignment])
        self.queue([self.event])
        _write(self.workspace / 'manager-notifications' / 'unsent.json', dict(self.notice, signal_id='not-sent', message='Not delivered'))
        root = view_state.collect_state(self.fixture.rt)['root']
        inbox, outbox, _ = view_events.mailbox_data(root)
        self.assertEqual(['Need guidance.'], [item['summary'] for item in inbox])
        self.assertEqual(['Please check edge cases.'], [item['prompt'] for item in outbox])
        self.assertEqual(self.lane['lane_id'], inbox[0]['peer'])
        text = view_artifacts.panel_text(root, 'events')
        self.assertIn('Inbox · Agent → ROOT', text)
        self.assertIn('Outbox · ROOT → Agent', text)
        self.assertNotIn('Not delivered', text)
        self.assertIn('not recorded', view_artifacts.panel_text(root, 'prompt'))
        self.assertIn('not recorded', view_artifacts.output_blocks(root)[0].text)
        self.assertIn('ROOT review results', view_artifacts.panel_text(root, 'result'))

    def test_enter_toggles_and_selection_survives_refresh(self):
        self.inbox([self.assignment])
        moment = [0.0]
        keys = iter(['enter', 'right', 'right', 'enter', None, 'enter', 'q'])
        frames = []
        original = view_render.render
        def capture(*args, **kwargs):
            if kwargs.get('panel') == 'events':
                frames.append(kwargs['artifact_text'])
            return original(*args, **kwargs)
        def read(timeout):
            key = next(keys)
            moment[0] += 3
            if key is None:
                self.inbox([dict(self.assignment, state='COMPLETE')])
            return key
        with mock.patch.object(view_term._Keys, 'raw'), mock.patch.object(view_term._Keys, 'read', side_effect=read), mock.patch.object(view_term.time, 'monotonic', side_effect=lambda: moment[0]), mock.patch.object(view_render, 'render', side_effect=capture), mock.patch.object(view_term, '_terminal_size', return_value=(100, 30)):
            view_term.run_interactive(lambda: self.state, out=io.StringIO(), depth=0, ascii_only=True)
        self.assertNotIn('assignment-1', frames[0])
        self.assertIn('assignment-1', frames[1])
        self.assertIn('COMPLETE', frames[2])
        self.assertIn('assignment-1', frames[2])
        self.assertNotIn('assignment-1', frames[3])

    def test_root_is_selectable_and_opens_same_tabs(self):
        with mock.patch.object(view_term._Keys, 'raw'), mock.patch.object(view_term._Keys, 'read', side_effect=['down'] * 4 + ['enter', 'right', 'right', 'q']), mock.patch.object(view_term, '_terminal_size', return_value=(120, 40)):
            output = io.StringIO()
            view_term.run_interactive(lambda: self.state, out=output, depth=0, ascii_only=True)
        self.assertIn('ROOT', output.getvalue())
        self.assertIn('visible in the terminal CLI', output.getvalue())
        self.assertIn('ROOT review results', output.getvalue())
        self.assertIn('Inbox - Agent > ROOT', output.getvalue())

    def test_collapsed_event_shows_lane_and_summary_before_expansion(self):
        self.queue([dict(self.event, prompt='Lower priority prompt')])
        text = view_artifacts.panel_text(self.lane, 'events')
        self.assertIn(self.lane['lane_id'], text)
        self.assertIn('Need guidance.', text)
        self.assertNotIn('Lower priority prompt', text)
        self.assertNotIn('envelope-1', text)
        root = view_state.collect_state(self.fixture.rt)['root']
        text = view_artifacts.panel_text(root, 'events')
        self.assertIn(self.lane['lane_id'], text)
        self.assertIn('Need guidance.', text)
        for panel in ('prompt', 'output'):
            self.assertIn('visible in the terminal CLI', view_artifacts.panel_text(root, panel))

    def test_explicit_sender_and_recipient_in_both_agent_and_root_views(self):
        self.inbox([self.assignment])
        self.queue([self.event])
        state = view_state.collect_state(self.fixture.rt)
        for lane in (state['lanes'][0], state['root']):
            text = view_artifacts.panel_text(lane, 'events')
            self.assertIn(f"From: ROOT → To: {self.lane['lane_id']}", text)
            self.assertIn(f"From: {self.lane['lane_id']} → To: ROOT", text)
            screen = '\n'.join(view_render.artifact_lines(text, 80, 0))
            self.assertIn(f"From: {self.lane['lane_id']} → To: ROOT", screen)
            self.assertIn('Need guidance.', screen)

    def test_long_agent_identity_is_not_truncated(self):
        agent = 'agent-with-a-very-long-lane-identifier-for-the-current-task'
        item = dict(self.event, lane_id=agent, source='Agent notification')
        text = view_events.mailbox_text(self.lane, entries=[('event', 'Outbox', item)], width=36)
        self.assertIn(f'From: {agent} → To: ROOT', text)
        rendered = ''.join(line.strip() for line in view_render.artifact_lines(text, 40, 0))
        self.assertIn(agent, rendered)
        self.assertIn('To: ROOT', rendered)
