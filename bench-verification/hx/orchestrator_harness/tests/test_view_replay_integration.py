"""Replay stays observational across the native CLI and monitor lifecycle."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator_harness import monitor, operator_launch, view_render, view_replay, view_term


class ReplayCommandTests(unittest.TestCase):
    def test_successful_native_command_captures_without_changing_its_result(self):
        result = {'ok': True, 'code': 'TEST_NATIVE_OK', 'summary': 'native success',
                  'evidence_paths': ['original'], 'next_action': 'original'}
        for error in (None, OSError('recording unavailable')):
            with self.subTest(error=error):
                output = io.StringIO()
                runtime = Path('unused-runtime')
                with (mock.patch.object(operator_launch, '_dispatch', return_value=result),
                      mock.patch.object(operator_launch, 'find_harness_root', return_value=Path('unused-harness')),
                      mock.patch.object(operator_launch, 'load_config', return_value=mock.Mock(runtime_root=runtime)),
                      mock.patch.object(view_replay, 'record_safely', side_effect=error) as capture,
                      contextlib.redirect_stdout(output)):
                    code = operator_launch.main(['--json', 'lane', 'launch', '--lane-id', 'worker'])
                self.assertEqual(0, code)
                self.assertEqual(result, json.loads(output.getvalue()))
                capture.assert_called_once_with(runtime)

    def test_failed_commands_and_read_only_commands_never_capture(self):
        for args, ok in ((['lane', 'launch', '--lane-id', 'worker'], False),
                         (['view', '--once'], True), (['scan', '--no-write'], True),
                         (['watch', '--timeout', '1'], True)):
            with self.subTest(args=args, ok=ok):
                with (mock.patch.object(operator_launch, '_dispatch', return_value={'ok': ok, 'summary': 'test'}),
                      mock.patch.object(view_replay, 'record_safely') as capture,
                      contextlib.redirect_stdout(io.StringIO())):
                    code = operator_launch.main(['--json', *args])
                self.assertEqual(0 if ok else 1, code)
                capture.assert_not_called()

    def test_cli_replay_options_reach_the_selected_epoch(self):
        with (mock.patch.object(view_term, 'run_view', return_value={'ok': True}) as view,
              mock.patch.object(view_replay, 'record_safely') as capture):
            args = operator_launch._build_parser().parse_args([
                '--json', 'view', '--runtime-root', 'saved-runtime', '--epoch', 'saved-epoch',
                '--replay', '--speed', '2', '--color',
            ])
            operator_launch._dispatch(args)
        self.assertEqual('saved-epoch', view.call_args.kwargs['epoch_id'])
        self.assertTrue(view.call_args.kwargs['replay'])
        self.assertEqual(2, view.call_args.kwargs['replay_speed'])
        self.assertTrue(view.call_args.kwargs['force_color'])
        self.assertTrue(view.call_args.kwargs['once'])
        capture.assert_not_called()

    def test_color_override_respects_explicit_disable_and_redirected_output(self):
        tty = mock.Mock()
        tty.isatty.return_value = True
        with mock.patch.dict('os.environ', {'NO_COLOR': '1', 'COLORTERM': 'truecolor'}):
            self.assertEqual(view_render.NO_COLOR, view_term.color_depth(tty))
            self.assertEqual(view_render.COLOR_TRUE, view_term.color_depth(tty, force_color=True))
            self.assertEqual(view_render.NO_COLOR, view_term.color_depth(tty, force_color=True, no_color=True))
            self.assertEqual(view_render.NO_COLOR, view_term.color_depth(io.StringIO(), force_color=True))

    def test_nonfinite_and_out_of_range_replay_speeds_fail_without_creating_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            runtime = Path(temporary) / 'absent-runtime'
            for speed in (float('nan'), float('inf'), 0, .24, 8.1):
                with self.subTest(speed=speed):
                    result = view_term.run_view(runtime_root=str(runtime), replay=True, replay_speed=speed, once=True)
                    self.assertEqual(view_term.VIEW_REPLAY_INVALID, result['code'])
            self.assertFalse(runtime.exists())


class ReplayMonitorTests(unittest.TestCase):
    def monitor_context(self, runtime, record, start, snapshot, write, run_pass=None):
        stack = contextlib.ExitStack()
        self.addCleanup(stack.close)
        for name, value in (
            ('find_harness_root', Path('unused-harness')),
            ('load_config', mock.Mock(runtime_root=runtime)),
            ('load_resource_manifest', mock.Mock()),
            ('compute_config_identity', 'identity'),
        ):
            stack.enter_context(mock.patch.object(monitor, name, return_value=value))
        stack.enter_context(mock.patch.object(monitor, 'append_activity'))
        stack.enter_context(mock.patch.object(monitor, 'RecordLock'))
        stack.enter_context(mock.patch.object(monitor, 'read_monitor_record', side_effect=record))
        stack.enter_context(mock.patch.object(monitor, 'atomic_write_json', side_effect=write))
        stack.enter_context(mock.patch.object(monitor, 'run_monitor_once', side_effect=run_pass))
        stack.enter_context(mock.patch.object(view_replay, 'start_recorder', side_effect=start))
        stack.enter_context(mock.patch.object(view_replay, 'record_safely', side_effect=snapshot))
        return stack

    def test_monitor_stops_recorder_before_final_capture_and_stopped_marker(self):
        for blocked in (False, True):
            with self.subTest(blocked=blocked):
                order = []
                stop, thread = mock.Mock(), mock.Mock()
                stop.set.side_effect = lambda: order.append('stop')
                thread.join.side_effect = lambda **kwargs: order.append('join')
                thread.is_alive.return_value = blocked
                record = {'stop_requested': True}
                context = self.monitor_context(
                    Path('unused-runtime'), lambda *_: record,
                    lambda *_: (stop, thread), lambda *_: order.append('snapshot'),
                    lambda *_: order.append('STOPPED'),
                )
                try:
                    result = monitor.main()
                finally:
                    context.close()
                self.assertEqual(1 if blocked else 0, result)
                self.assertEqual(['stop', 'join'] if blocked else ['stop', 'join', 'snapshot', 'STOPPED'], order)
                thread.join.assert_called_once_with(timeout=6)

    def test_optional_recorder_start_and_final_capture_errors_do_not_break_monitor_stop(self):
        record = {'stop_requested': True}
        written = []
        context = self.monitor_context(
            Path('unused-runtime'), lambda *_: record,
            mock.Mock(side_effect=RuntimeError('thread unavailable')),
            mock.Mock(side_effect=OSError('journal unavailable')),
            lambda path, data: written.append(dict(data)),
        )
        try:
            result = monitor.main()
        finally:
            context.close()
        self.assertEqual(0, result)
        self.assertEqual('STOPPED', written[-1]['health'])

    def test_normal_monitor_cadence_and_prompt_stop_leave_room_for_recorder_cleanup(self):
        for stop_early in (False, True):
            with self.subTest(stop_early=stop_early):
                moment, passes = [0.0], []
                stop, thread = mock.Mock(), mock.Mock()
                thread.is_alive.return_value = False

                def record(*_):
                    return {'stop_requested': moment[0] >= 1 if stop_early else len(passes) >= 2}

                def sleep(seconds):
                    moment[0] += seconds

                context = self.monitor_context(
                    Path('unused-runtime'), record, lambda *_: (stop, thread),
                    lambda *_: None, lambda *_: None,
                    lambda *_: passes.append(moment[0]),
                )
                try:
                    with (mock.patch.object(monitor.time, 'monotonic', side_effect=lambda: moment[0]),
                          mock.patch.object(monitor.time, 'sleep', side_effect=sleep)):
                        self.assertEqual(0, monitor.main())
                finally:
                    context.close()
                self.assertEqual([0, 1 if stop_early else monitor.PASS_INTERVAL_SECONDS], passes)


if __name__ == '__main__':
    unittest.main()
