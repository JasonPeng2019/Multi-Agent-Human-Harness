"""Regressions for duplicate dispatch and terminal Job cleanup in the last batch."""
from __future__ import annotations

import json
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack, contextmanager
from pathlib import Path
from threading import Barrier
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from orchestrator_harness import launch, processes, shutdown
from orchestrator_harness.config import HarnessConfig


class SingleDispatchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.runtime = self.root / 'runtime'
        self.worktree = self.root / 'worktree'
        (self.worktree / '.agent-workspace').mkdir(parents=True)
        binding = self.root / 'orchestrator_harness/provider_adapters/codex/launcher_binding.py'
        binding.parent.mkdir(parents=True)
        binding.write_text('# fixture\n', encoding='utf-8')
        self.lane = dict(schema='lane/v1', lane_id='lane', run_id='run-1', lifecycle='prepared',
                         process={}, worktree_path=str(self.worktree),
                         controller_status_path=str(self.worktree / '.agent-workspace/controller.status.json'),
                         controller_events_path=str(self.worktree / '.agent-workspace/controller.events.jsonl'))
        self.preferences = dict(reasoning_effort='high', service_tier='default')
        self.child = MagicMock(pid=41)
        self.child.poll.return_value = 0

    @contextmanager
    def fixture(self, spawn_error=None):
        with ExitStack() as stack:
            replacements = {
                'find_harness_root': lambda: self.root,
                'load_config': lambda _: SimpleNamespace(runtime_root=self.runtime),
                'read_runtime_state': lambda _: {'state': 'OPEN'},
                'find_active_lane': lambda *_: ('epoch', dict(self.lane)),
                'read_record': lambda *_: dict(schema='controller-invocation/v1', lane_id='lane',
                    run_id=self.lane['run_id'], provider=dict(id='codex', model='fixture-model', launch_config=self.preferences)),
                '_validate_provider_launch_config': lambda *a, **kw: self.preferences,
                'update_lane': lambda *args: args[-1](dict(self.lane)),
                'read_lane': lambda *_: dict(self.lane),
                '_read_controller_status': lambda _: dict(controller_state='exited', cleanup_proven=True,
                    provider_state={'state': 'exited', 'exit_code': 0}, recorded_status='review_pending'),
            }
            for name, value in replacements.items():
                stack.enter_context(patch.object(launch, name, side_effect=value))
            stack.enter_context(patch.object(processes, 'process_identity', return_value={'pid': 41, 'creation_time': 'owned'}))
            spawn = stack.enter_context(patch.object(launch, '_spawn_controller_logged', return_value=self.child,
                                                     side_effect=spawn_error))
            yield spawn

    def test_repeated_command_does_not_start_second_controller(self):
        with self.fixture() as spawn:
            first = launch.run_launch('lane')
            repeated = launch.run_launch('lane')
        self.assertTrue(first['ok'], first)
        self.assertEqual(launch.LAUNCH_ALREADY_DISPATCHED, repeated['code'])
        self.assertEqual(1, spawn.call_count)

    def test_concurrent_commands_have_exactly_one_dispatch(self):
        ready = Barrier(2)
        def invoke():
            ready.wait(timeout=5)
            return launch.run_launch('lane')
        with self.fixture() as spawn, ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: invoke(), range(2)))
        self.assertEqual(1, sum(result['ok'] for result in results), results)
        self.assertEqual(1, spawn.call_count)
        self.assertEqual(1, sum(result['code'] == launch.LAUNCH_ALREADY_DISPATCHED for result in results))

    def test_failed_spawn_keeps_claim_and_cannot_silently_retry(self):
        with self.fixture(spawn_error=OSError('recorded spawn failure')) as spawn:
            first = launch.run_launch('lane')
            second = launch.run_launch('lane')
        self.assertFalse(first['ok'])
        self.assertEqual(launch.LAUNCH_ALREADY_DISPATCHED, second['code'])
        self.assertEqual(1, spawn.call_count)
        claim = next(self.runtime.glob('epochs/*/lanes/*/dispatches/*.json'))
        self.assertEqual('run-1', json.loads(claim.read_text())['run_id'])

    def test_separately_prepared_new_run_can_launch(self):
        with self.fixture() as spawn:
            self.assertTrue(launch.run_launch('lane')['ok'])
            self.lane['run_id'] = 'run-2'
            self.assertTrue(launch.run_launch('lane')['ok'])
        self.assertEqual(2, spawn.call_count)
        self.assertEqual(2, len(list(self.runtime.glob('epochs/*/lanes/*/dispatches/*.json'))))

    def test_existing_running_lane_without_new_claim_cannot_be_relaunched(self):
        self.lane.update(lifecycle='running', process={'pid': 41, 'creation_time': 'owned'})
        with self.fixture() as spawn:
            result = launch.run_launch('lane')
        self.assertEqual(launch.LAUNCH_ALREADY_DISPATCHED, result['code'])
        spawn.assert_not_called()

    def test_prepared_resume_with_running_label_can_launch_once(self):
        # resume-lane records the new run as running before dispatch; an empty
        # controller identity and a fresh claim distinguish it from a live run.
        self.lane['lifecycle'] = 'running'
        with self.fixture() as spawn:
            first = launch.run_launch('lane')
            second = launch.run_launch('lane')
        self.assertTrue(first['ok'], first)
        self.assertEqual(launch.LAUNCH_ALREADY_DISPATCHED, second['code'])
        self.assertEqual(1, spawn.call_count)

    def test_proven_pre_provider_failure_preserves_separate_launch(self):
        events = Path(self.lane['controller_events_path'])
        events.write_text('{"event_type":"lease_busy"}\n', encoding='utf-8')
        status = dict(controller_state='exited', cleanup_proven=True,
                      provider_state={'state': 'not_started'}, recorded_status='lease_busy')
        with (
            self.fixture() as spawn,
            patch.object(launch, '_read_controller_status', return_value=status),
            patch.object(launch, '_reap_controller_and_prove_exit', return_value=True),
        ):
            first = launch.run_launch('lane')
            second = launch.run_launch('lane')
        self.assertEqual(launch.LAUNCH_LEASE_BUSY, first['code'], first)
        self.assertEqual(launch.LAUNCH_LEASE_BUSY, second['code'], second)
        self.assertEqual(2, spawn.call_count)
        history = list(self.runtime.glob('epochs/*/lanes/*/dispatches/*.no-provider.json'))
        self.assertEqual(2, len(history))


class ProvenJobCleanupTests(unittest.TestCase):
    def setUp(self):
        self.boundary = dict(kind='windows-job', root={'pid': 41, 'creation_time': 'old-root'},
                             process_group_id=None, session_id=None,
                             processes=[{'pid': 42, 'creation_time': 'old-child'}])

    @contextmanager
    def identities(self, live):
        with (
            patch.object(processes, 'process_alive', side_effect=lambda pid: pid in live),
            patch.object(processes, 'process_identity', side_effect=lambda pid: (
                {'pid': pid, 'creation_time': live[pid]} if live.get(pid) else None)),
            patch.object(processes, 'process_snapshot', side_effect=AssertionError('terminal Job must not rescan descendants')),
        ):
            yield

    def test_cleaned_job_with_reused_root_and_child_is_gone(self):
        with self.identities({41: 'unrelated-root', 42: 'unrelated-child'}):
            self.assertTrue(processes.process_boundary_is_gone(self.boundary, native_cleanup_proven=True))

    def test_surviving_exact_child_still_blocks_cleanup(self):
        with self.identities({42: 'old-child'}):
            self.assertFalse(processes.process_boundary_is_gone(self.boundary, native_cleanup_proven=True))

    def test_inaccessible_live_identity_still_blocks_cleanup(self):
        with self.identities({42: None}):
            self.assertFalse(processes.process_boundary_is_gone(self.boundary, native_cleanup_proven=True))

    def test_malformed_identity_still_blocks_cleanup(self):
        self.boundary['processes'].append({'pid': 43})
        with self.identities({}):
            self.assertFalse(processes.process_boundary_is_gone(self.boundary, native_cleanup_proven=True))

    def test_unproven_job_keeps_full_boundary_check(self):
        with patch.object(processes.ProcessBoundary, 'observe', return_value=False) as observe:
            self.assertFalse(processes.process_boundary_is_gone(self.boundary))
        observe.assert_called_once()

    def test_force_stop_of_cleaned_lane_never_targets_reused_processes(self):
        lane = {'process': {'pid': 43, 'creation_time': 'old-controller'}}
        status = dict(cleanup_proven=True, process_boundary=self.boundary,
                      provider_state={'pid': 41, 'creation_time': 'old-root'})
        with (
            self.identities({41: 'unrelated-root', 42: 'unrelated-child', 43: 'unrelated-controller'}),
            patch.object(launch, '_read_controller_status', return_value=status),
            patch.object(processes, 'terminate_process') as terminate,
            patch.object(processes, 'cleanup_recorded_process_boundary') as cleanup,
        ):
            self.assertTrue(launch._terminate_lane_processes(lane))
        terminate.assert_not_called()
        cleanup.assert_not_called()

    def test_shutdown_reaches_closed_after_terminal_job_cleanup(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            workspace = root / 'workspace'
            workspace.mkdir()
            config = HarnessConfig(root, workspace, 'enabled')
            lane = dict(lifecycle='accepted', lane_id='lane', run_id='run',
                        process={'pid': 43, 'creation_time': 'old-controller'})
            status = dict(cleanup_proven=True, process_boundary=self.boundary,
                          provider_state={'pid': 41, 'creation_time': 'old-root'})
            with ExitStack() as stack:
                stack.enter_context(self.identities({41: 'reused', 42: 'reused', 43: 'reused'}))
                replacements = {
                    'find_harness_root': lambda: root, 'load_config': lambda _: config,
                    'read_runtime_state': lambda _: {'state': 'OPEN'},
                    'read_current_epoch': lambda _: {'epoch_id': 'epoch'},
                    'read_manager_queue': lambda _: {'events': []},
                    'read_epoch_state': lambda *_: {'lifecycle': 'active'},
                    'read_active_lanes': lambda *_: [{'lane_id': 'lane'}],
                    'read_lane': lambda *_: lane, '_read_controller_status': lambda _: status,
                }
                for name, value in replacements.items():
                    stack.enter_context(patch.object(shutdown, name, side_effect=value))
                for name in ['release_leases', '_retire_lane', 'close_epoch', '_stop_monitor', '_prune_worktrees']:
                    stack.enter_context(patch.object(shutdown, name))
                stack.enter_context(patch('orchestrator_harness.public_checks.stop_service'))
                result = shutdown.run_shutdown()
            self.assertEqual('SHUTDOWN_OK', result['code'], result)
            self.assertEqual('CLOSED', json.loads((config.runtime_root / 'RUNTIME_STATE.json').read_text())['state'])


if __name__ == '__main__':
    unittest.main()
