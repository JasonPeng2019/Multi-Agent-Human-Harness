from __future__ import annotations
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator_harness import view_artifacts, view_render, view_state, view_term
from orchestrator_harness.tests.test_view import ViewFixture, _tree_fingerprint


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.fixture = ViewFixture(Path(self.tmp.name))
        self.state = view_state.collect_state(self.fixture.rt)
        self.lane = self.state['lanes'][0]
        self.aw = Path(self.lane['worktree_path']) / '.agent-workspace'

    def test_prompt_and_correction_are_inspectable_without_writes(self):
        (self.aw / 'worker-prompt.md').write_text('Original task\nAcceptance: pass tests')
        (self.aw / 'attempts').mkdir()
        (self.aw / 'attempts/correction-prompt-2.md').write_text('Fix result schema')
        before = _tree_fingerprint(Path(self.tmp.name))
        text = view_artifacts.panel_text(self.lane, 'prompt')
        self.assertIn('Original task', text)
        self.assertIn('Fix result schema', text)
        self.assertEqual(before, _tree_fingerprint(Path(self.tmp.name)))

    def test_live_output_tool_results_stderr_and_partial_json(self):
        path = self.aw / 'provider-transcript.jsonl'
        path.write_text(json.dumps({'type': 'user', 'message': {'content': [
            {'type': 'tool_result', 'tool_use_id': 't1', 'content': '3 tests passed'}]}}) + '\n')
        (self.aw / 'provider-stderr.txt').write_text('warning from CLI')
        text = view_artifacts.panel_text(self.lane, 'output')
        self.assertIn('Tool output', text)
        self.assertNotIn('t1', text)
        self.assertIn('3 tests passed', text)
        self.assertIn('warning from CLI', text)
        with path.open('a') as f:
            f.write('{"partial":')
        self.assertNotIn('{"partial":', view_artifacts.panel_text(self.lane, 'output'))
        self.assertIn('tool_result', view_artifacts.panel_text(self.lane, 'raw'))

    def test_latest_attempt_missing_files_and_escape_safety(self):
        self.assertIn('Waiting for the agent', view_artifacts.panel_text(self.lane, 'output'))
        attempt = self.aw / 'attempts/attempt-2'
        attempt.mkdir(parents=True)
        (attempt / 'provider-transcript.jsonl').write_text('latest\x1b[2J\x1b]0;bad\x07\rtext')
        text = view_artifacts.panel_text(self.lane, 'output')
        self.assertIn('Attempt 2', text)
        self.assertIn('latest', text)
        self.assertNotIn('\x1b', text)
        self.assertNotIn('\r', text)

    def test_output_limit_and_result(self):
        with mock.patch.object(view_artifacts, 'LIMIT', 32):
            (self.aw / 'worker-prompt.md').write_text('x' * 100)
            self.assertIn('Display limited', view_artifacts.panel_text(self.lane, 'prompt'))
        Path(self.lane['artifact_paths']['result_path']).write_text(json.dumps({'summary': 'Fixed bug'}))
        self.assertIn('Fixed bug', view_artifacts.panel_text(self.lane, 'result'))

    def test_scroll_follow_and_terminal_dimensions(self):
        text = '\n'.join(f'line-{i:03}' for i in range(200))
        options = dict(panel='output', artifact_text=text, depth=0)
        top = view_render.render(self.state, 90, 20, **options)
        bottom = view_render.render(self.state, 90, 20, follow=True, **options)
        middle = view_render.render(self.state, 90, 20, scroll=50, **options)
        self.assertIn('line-000', '\n'.join(top))
        self.assertIn('line-199', '\n'.join(bottom))
        self.assertIn('line-050', '\n'.join(middle))
        self.assertEqual(20, len(bottom))
        self.assertTrue(all(view_render.text_width(line) == 90 for line in bottom))

    def test_runtime_override_does_not_load_or_modify_configuration(self):
        with mock.patch('orchestrator_harness.config.load_config', side_effect=AssertionError('config accessed')):
            result = view_term.run_view(runtime_root=str(self.fixture.rt), once=True, out=io.StringIO())
        self.assertTrue(result['ok'])
        self.assertEqual(4, len(result['state']['lanes']))

    def test_interactive_navigation_exits_and_never_reviews(self):
        with mock.patch.object(view_term._Keys, 'raw') as raw, \
             mock.patch.object(view_term._Keys, 'read', side_effect=['enter', 'left', 'down', 'right', 'up', 'right', 'escape', 'q']), \
             mock.patch.object(view_term, '_terminal_size', return_value=(120, 30)):
            output = io.StringIO()
            view_term.run_interactive(lambda: self.state, out=output, depth=0, ascii_only=True)
        self.assertIn('Prompt sent to agent', output.getvalue())
        self.assertIn('No final result yet', output.getvalue())
        self.assertTrue(output.getvalue().endswith(view_term._LEAVE_SCREEN))


class ProviderFormattingTests(unittest.TestCase):
    def test_codex_commands_collapse_started_and_completed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'events.jsonl'
            records = [
                {'type': 'thread.started', 'thread_id': 'secret-internal-id'},
                {'type': 'item.started', 'item': {'id': 'item1', 'type': 'command_execution', 'command': 'python3 -m unittest', 'status': 'in_progress'}},
                {'type': 'item.completed', 'item': {'id': 'item1', 'type': 'command_execution', 'command': 'python3 -m unittest', 'aggregated_output': 'Ran 5 tests\nOK', 'exit_code': 0}},
                {'type': 'item.completed', 'item': {'id': 'item2', 'type': 'agent_message', 'text': 'Tests passed. Here is the fix.'}},
            ]
            p.write_text('\n'.join(json.dumps(r) for r in records))
            result = view_artifacts._transcript(p)
            self.assertEqual(1, result.count('$ python3 -m unittest'))
            self.assertIn('Exit 0', result)
            self.assertIn('Ran 5 tests\nOK', result)
            self.assertIn('Tests passed. Here is the fix.', result)
            self.assertNotIn('aggregated_output', result)
            self.assertNotIn('secret-internal-id', result)

    def test_claude_messages_tools_and_edits_are_readable(self):
        record = {'type': 'assistant', 'message': {'content': [
            {'type': 'text', 'text': 'I will fix the divisor.'},
            {'type': 'tool_use', 'id': 'abc', 'name': 'Bash', 'input': {'command': 'python3 -m unittest'}},
            {'type': 'tool_use', 'id': 'def', 'name': 'Edit', 'input': {'file_path': 'calc.py', 'old_string': 'len(values) + 1', 'new_string': 'len(values)'}},
        ]}}
        text = view_artifacts.format_event(record)
        self.assertIn('I will fix the divisor.', text)
        self.assertIn('$ python3 -m unittest', text)
        self.assertIn('- len(values) + 1', text)
        self.assertIn('+ len(values)', text)
        self.assertNotIn('tool_use', text)
        self.assertNotIn('abc', text)

    def test_final_result_has_summary_and_evidence_without_envelope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'RESULT.json').write_text(json.dumps({'schema': 'result/v1', 'content_hash': 'hash', 'run_id': 'id', 'outcome': 'PASS', 'summary': 'Fixed average.', 'evidence': [{'command': 'unittest', 'result': '5 passed'}]}))
            text = view_artifacts.panel_text({'worktree_path': str(root), 'label': 'Accepted'}, 'result')
            self.assertIn('PASS', text)
            self.assertIn('Fixed average.', text)
            self.assertIn('Command: unittest', text)
            self.assertNotIn('content_hash', text)
            self.assertNotIn('run_id', text)

    def test_wide_text_is_wrapped_without_losing_content(self):
        original = '界' * 100
        lines = view_render.artifact_lines(original, 40, 0)
        self.assertEqual(original, ''.join(line.strip() for line in lines))
        self.assertTrue(all(view_render.text_width(line) == 40 for line in lines))

    def test_agent_heading_and_tabs_stay_visible_when_scrolled(self):
        state = {'status': 'open', 'lanes': [{'lane_id': 'agent-one', 'label': 'Working', 'provider': 'codex', 'model': 'test'}]}
        text = '\n'.join(f'line {i}' for i in range(100))
        lines = view_render.render(state, 100, 20, panel='output', artifact_text=text, follow=True, depth=0)
        self.assertIn('agent-one', lines[0])
        for label in ('Prompt', 'Output', 'Result'):
            self.assertIn(label, lines[2])
        self.assertIn('line 99', '\n'.join(lines))
        self.assertIn('Esc all agents', lines[-1])

    def test_startup_notices_do_not_displace_latest_agent_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'transcript.jsonl'
            notice = {'type': 'item.completed', 'item': {'type': 'error', 'message': 'Codex is ignoring 1 unrecognized configuration setting.'}}
            message = {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'I will fix this.'}}
            path.write_text('\n'.join(json.dumps(r) for r in (notice, notice, message)))
            text = view_artifacts._transcript(path)
            self.assertEqual(1, text.count('Codex is ignoring'))
            self.assertLess(text.index('Startup notices'), text.index('I will fix this.'))

    def test_failed_provider_keeps_actual_error_visible(self):
        record = {'type': 'result', 'is_error': True, 'result': 'OAuth session expired'}
        self.assertIn('OAuth session expired', view_artifacts.format_event(record))

    def test_prompt_text_is_retained_verbatim(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / '.agent-workspace').mkdir()
            original = '# Task\n\nUse `average()` exactly.\n  Preserve spaces.\n'
            (root / '.agent-workspace/worker-prompt.md').write_text(original)
            self.assertIn(original, view_artifacts.panel_text({'worktree_path': str(root)}, 'prompt'))


class LiveRefreshTests(unittest.TestCase):
    def test_open_output_refreshes_without_reopening_agent(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = ViewFixture(Path(tmp))
            state = view_state.collect_state(fixture.rt)
            lane = state['lanes'][0]
            transcript = Path(lane['artifact_paths']['transcript_path'])
            def event(text):
                return json.dumps({'type':'item.completed', 'item':{'id':text, 'type':'agent_message', 'text':text}}) + '\n'
            transcript.write_text(event('First live message'))
            moment = [0.0]
            calls = [0]
            def next_key(timeout):
                calls[0] += 1
                moment[0] += 3
                if calls[0] == 1:
                    return 'enter'
                if calls[0] == 2:
                    with transcript.open('a') as handle:
                        handle.write(event('Second live message'))
                    return None
                return None if calls[0] == 3 else 'q'
            output = io.StringIO()
            with mock.patch.object(view_term._Keys, 'raw'), \
                 mock.patch.object(view_term._Keys, 'read', side_effect=next_key), \
                 mock.patch.object(view_term.time, 'monotonic', side_effect=lambda: moment[0]), \
                 mock.patch.object(view_term, '_terminal_size', return_value=(100, 24)):
                view_term.run_interactive(lambda: state, out=output, depth=0, ascii_only=True)
            self.assertIn('First live message', output.getvalue())
            self.assertIn('Second live message', output.getvalue())


class FinalResponseTests(unittest.TestCase):
    def test_final_response_uses_transcript_instead_of_controller_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            aw = root / '.agent-workspace'
            aw.mkdir()
            (aw / 'last-message.txt').write_text('turn.completed')
            (aw / 'provider-transcript.jsonl').write_text(json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'Implemented percentile. All 15 tests passed.'}}) + '\n')
            text = view_artifacts.panel_text({'worktree_path': str(root), 'lifecycle': 'review_pending'}, 'result')
            self.assertIn('Implemented percentile. All 15 tests passed.', text)
            self.assertNotIn('turn.completed', text)

    def test_latest_correction_response_takes_precedence(self):
        with tempfile.TemporaryDirectory() as tmp:
            aw = Path(tmp)
            def event(text):
                return json.dumps({'type':'item.completed','item':{'type':'agent_message','text':text}})
            (aw / 'provider-transcript.jsonl').write_text(event('First attempt'))
            correction = aw / 'attempts/attempt-2'
            correction.mkdir(parents=True)
            (correction / 'provider-transcript.jsonl').write_text(event('Corrected report; validation passed.'))
            self.assertEqual('Corrected report; validation passed.', view_artifacts._final_response(aw, {}))
