from __future__ import annotations

import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator_harness import view_artifacts, view_render, view_state, view_term
from orchestrator_harness.view_feed import Block, Feed, prose_blocks
from orchestrator_harness.tests.test_view import ViewFixture


class RevealTests(unittest.TestCase):
    def test_new_output_reveals_one_complete_line_at_a_time(self):
        feed = Feed()
        feed.update([Block('new', 'first line\nsecond line\nthird line\n')], 0)
        self.assertEqual('', feed.text(0))
        self.assertEqual('first line\n', feed.text(.09))
        self.assertEqual('first line\nsecond line\n', feed.text(.18))
        self.assertEqual('first line\nsecond line\nthird line\n', feed.text(.26))

    def test_tool_output_joins_the_same_sequential_queue(self):
        feed = Feed()
        feed.update([Block('agent', 'Explanation\n', True), Block('tool', '$ pytest\n15 tests passed\n')], 0)
        early = feed.text(.09)
        self.assertIn('Explanation', early)
        self.assertNotIn('15 tests passed', early)
        self.assertIn('15 tests passed', feed.text(1))

    def test_large_burst_does_not_dump_and_end_explicitly_catches_up(self):
        feed = Feed()
        text = 'output line\n' * 5000
        feed.update([Block('burst', text)], 10)
        self.assertEqual(1, feed.text(10.1).count('output line'))
        self.assertLess(len(feed.text(12.5)), len(text))
        feed.finish(12.5)
        self.assertEqual(text, feed.text(12.5))

    def test_reopening_does_not_replay_received_text(self):
        blocks = [Block('a', 'one\ntwo\nthree\n', True)]
        feed = Feed()
        feed.update(blocks, 0)
        self.assertNotEqual(blocks[0].text, feed.text(0))
        feed.update(blocks, .1, immediate=True)
        self.assertEqual(blocks[0].text, feed.text(.1))
        self.assertFalse(feed.revealing)

    def test_command_completion_appends_delta_without_rewriting_history(self):
        feed = Feed()
        old = Block('command', '### Running\n$ test\n')
        feed.update([old, Block('message', 'Already reading this.')], 0, immediate=True)
        visible = feed.text(0)
        feed.update([Block('command', '### Exit 0\n$ test\n10 tests passed\n'), Block('message', 'Already reading this.')], 2)
        self.assertEqual(visible, feed.text(2))
        later = feed.text(4)
        self.assertTrue(later.startswith(visible))
        self.assertEqual(1, later.count('$ test'))
        self.assertIn('10 tests passed', later)

    def test_refresh_keeps_progress_and_does_not_duplicate_seen_records(self):
        feed = Feed()
        block = Block('a', 'line\n' * 100)
        feed.update([block], 0)
        first = feed.text(.5)
        feed.update([block], .5)
        self.assertEqual(first, feed.text(.5))
        feed.update([Block('b', 'Next message')], 1)
        feed.update([block, Block('b', 'Next message')], 1.1)
        feed.finish(1.1)
        self.assertEqual(100, feed.text(1.1).count('line\n'))

    def test_claude_and_codex_blocks_classify_tools_without_heading_heuristics(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'transcript.jsonl'
            records = [
                {'type': 'item.completed', 'item': {'id': 'command', 'type': 'command_execution', 'command': 'cat file', 'aggregated_output': '### Agent\nThis is tool output.', 'exit_code': 0}},
                {'type': 'assistant', 'message': {'id': 'claude', 'content': [
                    {'type': 'text', 'text': 'A real agent message.'},
                    {'type': 'tool_use', 'name': 'Bash', 'id': 'tool', 'input': {'command': 'pytest'}}]}},
            ]
            path.write_text('\n'.join(json.dumps(r) for r in records))
            blocks = view_artifacts._transcript_blocks(path)
            self.assertFalse(blocks[0].prose)
            self.assertTrue(blocks[1].prose)
            self.assertFalse(blocks[2].prose)
            self.assertEqual([b.key for b in blocks], [b.key for b in view_artifacts._transcript_blocks(path)])

    def test_claude_final_message_with_code_is_not_duplicated(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'transcript.jsonl'
            text = 'The result is ready.\n```python\nprint(42)\n```\nAll checks passed.'
            records = [{'type': 'assistant', 'message': {'id': 'a', 'content': [{'type': 'text', 'text': text}]}},
                       {'type': 'result', 'result': text, 'is_error': False}]
            path.write_text('\n'.join(json.dumps(r) for r in records))
            rendered = view_artifacts._transcript(path)
            self.assertEqual(1, rendered.count('All checks passed.'))
            self.assertEqual(1, rendered.count('print(42)'))


class ReadingPositionTests(unittest.TestCase):
    def test_scroll_freezes_content_and_end_loads_new_activity(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = ViewFixture(Path(tmp))
            state = view_state.collect_state(fixture.rt)
            lane = state['lanes'][0]
            path = Path(lane['artifact_paths']['transcript_path'])
            def write(text):
                path.write_text(json.dumps({'type': 'item.completed', 'item': {'id': 'command', 'type': 'command_execution', 'command': 'run', 'aggregated_output': text, 'exit_code': 0}}) + '\n')
            write('Original output\n' * 30)
            moment, calls = [0.0], [0]
            frames = []
            render = view_render.render
            def capture(*args, **kwargs):
                frames.append(kwargs.copy())
                return render(*args, **kwargs)
            def read(timeout):
                calls[0] += 1
                moment[0] += 3
                if calls[0] == 1:
                    return 'enter'
                if calls[0] == 2:
                    return 'up'
                if calls[0] == 3:
                    write('Inserted at top\n' * 20 + 'Original output\n' * 30 + 'Fresh result')
                    return None
                if calls[0] == 4:
                    return 'end'
                return 'q'
            with mock.patch.object(view_term._Keys, 'raw'), \
                 mock.patch.object(view_term._Keys, 'read', side_effect=read), \
                 mock.patch.object(view_term.time, 'monotonic', side_effect=lambda: moment[0]), \
                 mock.patch.object(view_term, '_terminal_size', return_value=(100, 24)), \
                 mock.patch.object(view_render, 'render', side_effect=capture):
                view_term.run_interactive(lambda: state, out=io.StringIO(), depth=0, ascii_only=True)
            paused = [f for f in frames if f['panel'] == 'output' and not f['follow']]
            self.assertEqual(paused[0]['artifact_text'], paused[-1]['artifact_text'])
            self.assertEqual(paused[0]['scroll'], paused[-1]['scroll'])
            self.assertTrue(paused[-1]['new_activity'])
            self.assertIn('Fresh result', frames[-1]['artifact_text'])
            self.assertFalse(frames[-1]['new_activity'])

    def test_new_activity_indicator_is_visible_at_standard_terminal_width(self):
        state = {'status': 'open', 'lanes': [{'lane_id': 'test', 'label': 'Working'}]}
        lines = view_render.render(state, 80, 24, panel='output', artifact_text='old', new_activity=True, depth=0)
        self.assertIn('New activity', lines[-1])
        self.assertIn('End latest', lines[-1])
