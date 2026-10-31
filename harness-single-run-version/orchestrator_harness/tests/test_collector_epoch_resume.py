"""A collector continuation keeps one native epoch and one append-only replay."""
from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import unittest
from contextlib import closing
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from orchestrator_harness import collector_context, epochs, processes, root_hook_dispatch, view_replay, view_state
from orchestrator_harness.config import HarnessConfig, ResourceManifest


class CollectorEpochResumeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / 'workspace'
        self.root.mkdir()
        self.harness = self.base / 'harness'
        self.config = HarnessConfig(harness_root=self.harness, root_workspace=self.root)
        self.manifest = ResourceManifest()
        self.rt = self.config.runtime_root
        self.launch_path = self.base / 'launch.json'
        self.budget_path = self.base / 'budget.json'
        deadline = (datetime.now(timezone.utc) + timedelta(minutes=238)).isoformat()
        self.launch = dict(arm='harness', role='root', operator_assisted=True,
                           run_id='original-run', workspace=str(self.root),
                           harness_dir=str(self.harness), harness_runtime=str(self.rt),
                           watchdog_deadline_utc=deadline)
        self.budget = dict(schema='run-budget/v1', authority='cli-collector-watchdog',
                           run_id='original-run', root_workspace=str(self.root),
                           harness_dir=str(self.harness), watchdog_deadline_utc=deadline,
                           original_watchdog_seconds=14400)
        self.write_context()
        patch = mock.patch.dict(os.environ, SWE_ROOT_LAUNCH_FILE=str(self.launch_path),
                                SWE_RUN_BUDGET_FILE=str(self.budget_path))
        patch.start()
        self.addCleanup(patch.stop)

    def write_context(self):
        self.launch_path.write_text(json.dumps(self.launch))
        self.budget_path.write_text(json.dumps(self.budget))

    def open(self):
        return epochs.open_epoch(self.rt, self.config, self.manifest)

    def lane(self, epoch, lane_id, lifecycle):
        path = epochs.lane_record_path(self.rt, epoch, lane_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dict(schema='lane/v1', epoch_id=epoch, lane_id=lane_id,
                                        run_id='invocation-' + lane_id, lifecycle=lifecycle,
                                        worktree_path=str(self.base / lane_id), process={}, provider={})))

    def test_repeated_closure_resume_retains_queue_retired_lanes_and_one_view_entry(self):
        first = self.open()
        epoch = first['epoch_id']
        self.lane(epoch, 'earlier', 'retired')
        queue_path = epochs.manager_queue_path(self.rt)
        queue = json.loads(queue_path.read_text())
        queue['events'] = [{'event_id': 'receipt', 'state': 'COMPLETE', 'history': ['preserved']}]
        queue_path.write_text(json.dumps(queue))
        budget_bytes = self.budget_path.read_bytes()
        for number in (1, 2):
            epochs.close_epoch(self.rt, epoch)
            self.assertEqual('closed', view_state.list_epochs(self.rt)[0]['status'])
            reopened = self.open()
            self.assertEqual(epoch, reopened['epoch_id'])
            self.assertEqual(first['opened_at'], reopened['opened_at'])
            self.assertEqual(number, reopened['reopen_count'])
            self.assertEqual(number, len(reopened['closure_history']))
            self.assertEqual(queue, json.loads(queue_path.read_text()))
        self.lane(epoch, 'resumed', 'retired')
        entries = view_state.list_epochs(self.rt)
        self.assertEqual(1, len(entries))
        self.assertEqual(2, entries[0]['lane_count'])
        self.assertEqual({'earlier', 'resumed'}, {lane['lane_id'] for lane in view_state.collect_state(self.rt)['lanes']})
        self.assertEqual(budget_bytes, self.budget_path.read_bytes())

    def test_resumed_replay_appends_without_changing_old_frames(self):
        epoch = self.open()['epoch_id']
        self.lane(epoch, 'earlier', 'retired')
        view_replay.record_once(self.rt)
        epochs.close_epoch(self.rt, epoch)
        view_replay.record_once(self.rt)
        database = self.rt / 'replay' / (epoch + '.sqlite3')
        with closing(sqlite3.connect(database)) as db:
            original = db.execute('SELECT seq,at,digest,payload FROM frames ORDER BY seq').fetchall()
            self.assertEqual('true', dict(db.execute('SELECT key,value FROM metadata'))['complete'])
        self.open()
        self.lane(epoch, 'resumed', 'retired')
        view_replay.record_once(self.rt)
        epochs.close_epoch(self.rt, epoch)
        view_replay.record_once(self.rt)
        with closing(sqlite3.connect(database)) as db:
            frames = db.execute('SELECT seq,at,digest,payload FROM frames ORDER BY seq').fetchall()
            metadata = dict(db.execute('SELECT key,value FROM metadata'))
        self.assertEqual(original, frames[:len(original)])
        self.assertGreater(len(frames), len(original))
        self.assertEqual('true', metadata['complete'])
        self.assertEqual(1, len(json.loads(metadata['closure_history'])))
        self.assertEqual(1, len(view_replay.recordings(self.rt)))
        playback = view_replay.Playback(self.rt, epoch=epoch)
        playback.seek(playback.duration)
        self.assertEqual({'earlier', 'resumed'}, {lane['lane_id'] for lane in playback.state()['lanes']})

    def test_existing_active_epoch_can_be_bound_before_its_first_closure(self):
        with mock.patch.dict(os.environ, SWE_ROOT_LAUNCH_FILE=''):
            first = self.open()
        epochs.close_epoch(self.rt, first['epoch_id'])
        self.assertEqual(first['epoch_id'], self.open()['epoch_id'])

    def test_noncollector_runs_still_open_new_epochs(self):
        with mock.patch.dict(os.environ, SWE_ROOT_LAUNCH_FILE=''):
            first = self.open()['epoch_id']
            epochs.close_epoch(self.rt, first)
            self.assertNotEqual(first, self.open()['epoch_id'])

    def test_changed_run_deadline_config_and_queue_cannot_replace_identity(self):
        first = self.open()['epoch_id']
        epochs.close_epoch(self.rt, first)
        self.launch['run_id'] = self.budget['run_id'] = 'foreign-run'
        self.write_context()
        with self.assertRaisesRegex(epochs.EpochError, 'different run'):
            self.open()
        self.launch['run_id'] = self.budget['run_id'] = 'original-run'
        self.launch['watchdog_deadline_utc'] = self.budget['watchdog_deadline_utc'] = (
            datetime.now(timezone.utc) + timedelta(hours=6)).isoformat()
        self.write_context()
        with self.assertRaisesRegex(epochs.EpochError, 'different run'):
            self.open()
        self.launch['watchdog_deadline_utc'] = self.budget['watchdog_deadline_utc'] = json.loads(
            (self.rt / 'COLLECTOR_EPOCH.json').read_text())['scope']['watchdog_deadline_utc']
        self.write_context()
        with self.assertRaisesRegex(epochs.EpochError, 'configuration changed'):
            epochs.open_epoch(self.rt, replace(self.config, managed_coordination='disabled'), self.manifest)
        queue_path = epochs.manager_queue_path(self.rt)
        queue = json.loads(queue_path.read_text())
        queue['epoch_id'] = 'foreign-epoch'
        queue_path.write_text(json.dumps(queue))
        with self.assertRaisesRegex(epochs.EpochError, 'queue was replaced'):
            self.open()
        self.assertEqual(1, len(view_state.list_epochs(self.rt)))

    def test_foreign_workspace_or_missing_budget_is_rejected(self):
        self.budget['root_workspace'] = str(self.base / 'foreign')
        self.write_context()
        with self.assertRaisesRegex(ValueError, 'identity'):
            self.open()
        with mock.patch.dict(os.environ, SWE_RUN_BUDGET_FILE=''):
            with self.assertRaisesRegex(ValueError, 'original budget'):
                self.open()

    def test_same_epoch_with_a_replaced_queue_id_is_rejected(self):
        epoch = self.open()['epoch_id']
        epochs.close_epoch(self.rt, epoch)
        queue_path = epochs.manager_queue_path(self.rt)
        queue = json.loads(queue_path.read_text())
        queue['queue_id'] = 'replacement-queue'
        queue_path.write_text(json.dumps(queue))
        with self.assertRaisesRegex(epochs.EpochError, 'queue was replaced'):
            self.open()
        self.assertIsNone(epochs.read_current_epoch(self.rt))

    def test_initial_live_binding_can_gain_queue_pin_before_closure(self):
        epoch = self.open()['epoch_id']
        path = self.rt / 'COLLECTOR_EPOCH.json'
        binding = json.loads(path.read_text())
        original_queue = binding.pop('queue_id')
        path.write_text(json.dumps(binding))
        epochs.close_epoch(self.rt, epoch)
        self.assertEqual(original_queue, json.loads(path.read_text())['queue_id'])
        self.assertEqual(epoch, self.open()['epoch_id'])

    def test_expiry_blocks_reopening_but_still_allows_closure(self):
        epoch = self.open()['epoch_id']
        with mock.patch.object(epochs, 'utc_now', return_value=datetime.now(timezone.utc) + timedelta(days=1)):
            epochs.close_epoch(self.rt, epoch)
            with self.assertRaisesRegex(epochs.EpochError, 'deadline has expired'):
                self.open()

    def audit_lane(self):
        epoch = self.open()['epoch_id']
        self.lane(epoch, 'finished', 'retired')
        path = epochs.lane_record_path(self.rt, epoch, 'finished')
        lane = json.loads(path.read_text())
        status_path = self.base / 'finished-status.json'
        lane.update(controller_status_path=str(status_path), process=dict(pid=11, creation_time='controller-created'))
        path.write_text(json.dumps(lane))
        status = dict(lane_id=lane['lane_id'], run_id=lane['run_id'], controller_state='exited',
                      cleanup_proven=True, provider_state=dict(state='exited', pid=12, creation_time='provider-created'),
                      process_boundary=dict(kind='fixture'))
        status_path.write_text(json.dumps(status))
        return path, lane, status_path, status

    def absence_mocks(self):
        from contextlib import ExitStack
        stack = ExitStack()
        stack.enter_context(mock.patch.object(processes, 'identity_matches', return_value=False))
        stack.enter_context(mock.patch.object(processes, 'process_alive', return_value=False))
        stack.enter_context(mock.patch.object(processes, 'process_boundary_is_gone', return_value=True))
        return stack

    def test_operator_audit_pause_allows_quiescent_open_runtime_without_claiming_completion(self):
        self.audit_lane()
        with (self.absence_mocks(),
              mock.patch.object(root_hook_dispatch, 'load_config', return_value=self.config),
              mock.patch.object(root_hook_dispatch, 'read_runtime_state', return_value={'state': 'OPEN'})):
            self.assertEqual({'decision': 'ALLOW'}, root_hook_dispatch.dispatch(self.harness, 'stop', 'claude-code'))
            queue_path = epochs.manager_queue_path(self.rt)
            queue = json.loads(queue_path.read_text())
            queue['events'] = [dict(state='PENDING')]
            queue_path.write_text(json.dumps(queue))
            self.assertEqual('REJECT', root_hook_dispatch.dispatch(self.harness, 'stop', 'claude-code')['decision'])
            epochs.close_epoch(self.rt, epochs.read_current_epoch(self.rt)['epoch_id'])
            self.assertEqual('REJECT', root_hook_dispatch.dispatch(self.harness, 'stop', 'claude-code')['decision'])
            queue['events'] = []
            queue_path.write_text(json.dumps(queue))
            self.assertEqual({'decision': 'ALLOW'}, root_hook_dispatch.dispatch(self.harness, 'stop', 'claude-code'))
            self.assertFalse(collector_context.collector_audit_pause_ready(self.rt, self.base / 'foreign-harness'))

    def test_audit_pause_rejects_running_unproven_and_live_worker_states(self):
        path, lane, status_path, status = self.audit_lane()
        with self.absence_mocks():
            for lifecycle in ('prepared', 'running', 'review_pending', 'accepted'):
                path.write_text(json.dumps({**lane, 'lifecycle': lifecycle}))
                self.assertFalse(collector_context.collector_audit_pause_ready(self.rt))
            path.write_text(json.dumps(lane))
            status_path.write_text(json.dumps({**status, 'cleanup_proven': False}))
            self.assertFalse(collector_context.collector_audit_pause_ready(self.rt))
            status_path.write_text(json.dumps(status))
            with mock.patch.object(processes, 'identity_matches', return_value=True):
                self.assertFalse(collector_context.collector_audit_pause_ready(self.rt))
            with mock.patch.object(processes, 'process_boundary_is_gone', return_value=False):
                self.assertFalse(collector_context.collector_audit_pause_ready(self.rt))
            with (mock.patch.object(processes, 'process_alive', return_value=True),
                  mock.patch.object(processes, 'process_identity', return_value=None)):
                self.assertFalse(collector_context.collector_audit_pause_ready(self.rt))

    def test_audit_pause_rejects_leases_and_ordinary_noncollector_runtime(self):
        self.audit_lane()
        with self.absence_mocks():
            with mock.patch.dict(os.environ, SWE_ROOT_LAUNCH_FILE=''):
                self.assertFalse(collector_context.collector_audit_pause_ready(self.rt))
            lease = self.rt / 'resources/leases/held.lease'
            lease.parent.mkdir(parents=True)
            lease.write_text('{}')
            self.assertFalse(collector_context.collector_audit_pause_ready(self.rt))


if __name__ == '__main__':
    unittest.main()
