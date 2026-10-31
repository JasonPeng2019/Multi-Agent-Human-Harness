from __future__ import annotations

import json
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import run_visualizer_demo as demo


class DemoTests(unittest.TestCase):
    def test_default_runs_directory_is_outside_harness_source(self):
        self.assertFalse(demo.RUNS_DIR.resolve().is_relative_to(demo.ROOT.resolve()))

    def test_invalid_runs_directory_is_rejected_before_any_mutation(self):
        with mock.patch.object(demo, 'guard_idle') as guard, mock.patch.object(demo, 'run') as run:
            with self.assertRaisesRegex(RuntimeError, 'outside the harness'):
                demo.demo('model', demo.ROOT / 'runtime')
            guard.assert_not_called()
            run.assert_not_called()

    def test_reset_creates_fresh_baselines_without_deleting_prior_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, _ = demo.fresh_workspace(Path(tmp))
            (first / 'keep-me.txt').write_text('prior evidence')
            (first / 'calc.py').write_text('modified')
            second, base = demo.fresh_workspace(Path(tmp))
            self.assertNotEqual(first, second)
            self.assertEqual('prior evidence', (first / 'keep-me.txt').read_text())
            self.assertEqual(demo.BASE_FILES['calc.py'], (second / 'calc.py').read_text())
            self.assertEqual(40, len(base))

    def test_independent_checks_reject_a_cheating_test_suite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, base = demo.fresh_workspace(Path(tmp))
            (root / 'calc.py').write_text('def average(values):\n    return 2\n')
            (root / 'test_calc.py').write_text('import unittest\nclass Empty(unittest.TestCase):\n    def test_pass(self):\n        pass\n')
            demo.run(['git', 'add', 'calc.py', 'test_calc.py'], cwd=root)
            demo.run(['git', 'commit', '-qm', 'Wrong fix'], cwd=root)
            with self.assertRaises(RuntimeError):
                demo.check_worker(root, 'fix-average', base)

    def test_checks_accept_a_real_fix_with_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, base = demo.fresh_workspace(Path(tmp))
            (root / 'calc.py').write_text('def average(values):\n    return sum(values) / len(values)\n')
            with (root / 'test_calc.py').open('a') as handle:
                handle.write('    def test_single(self):\n        self.assertEqual(7, average([7]))\n')
            demo.run(['git', 'add', 'calc.py', 'test_calc.py'], cwd=root)
            demo.run(['git', 'commit', '-qm', 'Real fix'], cwd=root)
            self.assertIn('assertions and diff check passed', demo.check_worker(root, 'fix-average', base))

    def test_active_runtime_is_not_reconfigured(self):
        with tempfile.TemporaryDirectory() as tmp:
            rt = Path(tmp)
            (rt / 'RUNTIME_STATE.json').write_text(json.dumps({'state': 'OPEN'}))
            with mock.patch.object(demo, 'load_config', return_value=mock.Mock(runtime_root=rt)):
                with self.assertRaisesRegex(RuntimeError, 'already open'):
                    demo.guard_idle()

    def exercise_flow(self, *, fail_checks=False):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'local-config').mkdir()
            (root / 'local-config/harness-config.json').write_text('{"original":true}')
            workspace = root / 'workspace'
            workspace.mkdir()
            calls = []
            def operator(*args):
                calls.append(args)
                return {'ok': True, 'event_id': 'event-' + args[2] if args[0] == 'watch' else None}
            checker = mock.Mock(side_effect=RuntimeError('tests failed')) if fail_checks else mock.Mock(return_value='Tests passed')
            with mock.patch.object(demo, 'ROOT', root), \
                 mock.patch.object(demo, 'guard_idle'), \
                 mock.patch.object(demo, 'run', return_value='logged in'), \
                 mock.patch.object(demo, 'fresh_workspace', return_value=(workspace, 'a' * 40)), \
                 mock.patch.object(demo, 'operator', side_effect=operator), \
                 mock.patch.object(demo, 'find_active_lane', return_value=('epoch', {'worktree_path': str(workspace)})), \
                 mock.patch.object(demo, 'check_worker', checker), \
                 mock.patch('sys.stdout', new_callable=io.StringIO):
                if fail_checks:
                    with self.assertRaisesRegex(RuntimeError, 'tests failed'):
                        demo.demo('model', root.parent / 'runs')
                else:
                    demo.demo('model', root.parent / 'runs')
            self.assertEqual('{"original":true}', (workspace / '.demo/previous-harness-config.json').read_text())
            return calls

    def test_flow_launches_both_before_waiting_and_records_checked_results(self):
        calls = self.exercise_flow()
        launches = [i for i, args in enumerate(calls) if args[:2] == ('lane', 'launch')]
        waits = [i for i, args in enumerate(calls) if args[0] == 'watch']
        self.assertEqual(2, len(launches))
        self.assertLess(max(launches), min(waits))
        reviews = [args for args in calls if args[:2] == ('lane', 'completion-review')]
        self.assertEqual(2, len(reviews))
        self.assertTrue(all('ACCEPTED' in args for args in reviews))
        self.assertEqual(('harness', 'shutdown'), calls[-1])

    def test_failed_checks_never_accept_and_only_clean_owned_lanes(self):
        calls = self.exercise_flow(fail_checks=True)
        self.assertFalse(any(args[:2] == ('lane', 'completion-review') for args in calls))
        stopped = [args[-1] for args in calls if args[:2] == ('lane', 'force-stop')]
        self.assertEqual(list(demo.TASKS), stopped)
        self.assertEqual(('harness', 'shutdown'), calls[-1])

    def test_check_only_has_no_workspace_or_agent_side_effects(self):
        with mock.patch('sys.argv', ['run_visualizer_demo.py', '--check-only']), \
             mock.patch.object(demo, 'run', return_value='tests passed') as run, \
             mock.patch.object(demo, 'demo') as live, \
             mock.patch('sys.stdout', new_callable=io.StringIO):
            self.assertEqual(0, demo.main())
        live.assert_not_called()
        self.assertEqual(1, run.call_count)
