"""Exercise staged native epoch changes without touching the live packages."""
import hashlib
import importlib.util
import json
import os
import sys
import unittest
import argparse
import tempfile
from unittest import mock
from datetime import datetime, timedelta, timezone
from pathlib import Path

STAGED = Path(__file__).resolve().parent
LIVE = STAGED.parents[2] / "harness-single-run-version"
sys.path.insert(0, str(LIVE))


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


import orchestrator_harness
for name in ("quota_clock", "collector_context", "epochs"):
    value = module("orchestrator_harness." + name, STAGED / "orchestrator_harness" / (name + ".py"))
    setattr(orchestrator_harness, name, value)

original = module("original_epoch_tests", LIVE / "orchestrator_harness/tests/test_collector_epoch_resume.py")
clock = orchestrator_harness.quota_clock
context = orchestrator_harness.collector_context
sys.path.insert(0, str(LIVE / "scripts"))
collector = module("staged_collector", STAGED / "scripts/collect_codex_usage.py")
preparation = module("staged_preparation", STAGED / "scripts/prepare_root_launch.py")


class QuotaEpochTests(original.CollectorEpochResumeTests):
    def install_pause(self):
        self.launch["watchdog_deadline_utc"] = self.budget["watchdog_deadline_utc"] = (
            datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
        self.write_context()
        epoch = self.open()["epoch_id"]
        binding = (self.rt / "COLLECTOR_EPOCH.json").read_bytes()
        orchestrator_harness.epochs.close_epoch(self.rt, epoch)
        self.run_dir = self.base / "out/original-run"
        self.run_dir.mkdir(parents=True)
        deadline = datetime.fromisoformat(self.launch["watchdog_deadline_utc"])
        first = dict(self.launch, started_at_utc=(deadline - timedelta(hours=4)).isoformat(),
            task="test-task", budget_tokens=None, watchdog_hours=4, provider_id="claude-code",
            model="claude-sonnet-5", reasoning_effort="low", service_tier=None,
            sandbox="claude-bypassPermissions")
        reset = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(minutes=1)
        stopped = reset - timedelta(minutes=10)

        def write(path, value):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value), encoding="utf-8")

        def ref(path):
            return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())

        write(self.run_dir / "launch.json", first)
        write(self.run_dir / "manifest.json", dict(run_id=first["run_id"], ended_at_utc=stopped.isoformat(),
            watchdog_expired=False, elapsed_seconds=6000, exit_code=getattr(self, "quota_exit_code", 0)))
        events = self.run_dir / "claude-events.jsonl"
        events.write_text(json.dumps(dict(type="rate_limit_event", session_id="same-session",
            rate_limit_info=dict(status="rejected", resetsAt=reset.timestamp()))) + "\n")
        stop = self.base / "QUOTA_STOP.json"
        write(stop, dict(schema="operator-quota-stop/v1", run_id=first["run_id"], root_session_id="same-session",
            all_owned_provider_processes_absent=True, collector_sealed=True, stopped_at_utc=stopped.isoformat(),
            segment_launch=ref(self.run_dir / "launch.json"), segment_manifest=ref(self.run_dir / "manifest.json"), transcript=ref(events)))
        write(self.run_dir / "quota-pauses/0001.json", dict(schema="operator-quota-pause/v1", run_id=first["run_id"],
            root_session_id="same-session", original_deadline_utc=first["watchdog_deadline_utc"], stop_audit=ref(stop),
            paused_at_utc=stopped.isoformat(), clock_resumed_at_utc=reset.isoformat()))
        verified = clock.effective_deadline(self.run_dir)
        self.launch.update(quota_clock=verified, watchdog_deadline_utc=verified["effective_deadline_utc"], resume_session_id="same-session")
        self.budget["watchdog_deadline_utc"] = verified["effective_deadline_utc"]
        self.launch_path = self.run_dir / "segments/0002/launch.json"
        self.launch_path.parent.mkdir(parents=True)
        os.environ["SWE_ROOT_LAUNCH_FILE"] = str(self.launch_path)
        self.write_context()
        return epoch, binding

    def test_verified_quota_pause_keeps_original_epoch_and_binding(self):
        epoch, binding = self.install_pause()
        self.assertEqual(epoch, self.open()["epoch_id"])
        self.assertEqual(binding, (self.rt / "COLLECTOR_EPOCH.json").read_bytes())
        self.assertEqual(600, self.launch["quota_clock"]["paused_seconds"])
        self.assertEqual(datetime.fromisoformat(self.launch["watchdog_deadline_utc"]), context.epoch_resume_deadline(self.rt))

    def test_extended_clock_cannot_change_root_session(self):
        self.install_pause()
        self.launch["resume_session_id"] = "foreign-session"
        self.write_context()
        with self.assertRaisesRegex(ValueError, "session"):
            self.open()

    def test_unreceipted_extension_is_rejected(self):
        self.install_pause()
        self.launch["quota_clock"]["paused_seconds"] += 1
        self.write_context()
        with self.assertRaisesRegex(ValueError, "evidence"):
            self.open()

    def test_tampered_stop_proof_is_rejected(self):
        self.install_pause()
        (self.base / "QUOTA_STOP.json").write_text("{}")
        with self.assertRaisesRegex(ValueError, "evidence changed"):
            self.open()

    def check_collector_clock(self, raw=False):
        self.install_pause()
        # prepare_resume runs before the future continuation directory exists.
        self.launch_path.parent.rename(self.base / "simulated-future-segment")
        (self.rt / "RUNTIME_STATE.json").write_text(json.dumps(dict(state="CLOSED")))
        first = json.loads((self.run_dir / "launch.json").read_text())
        task = dict(first, root_run_dir=str(self.run_dir), interruption_policy="planned_resume")
        if raw:
            # The native raw arm normally uses active-only accounting. A verified
            # quota receipt must instead charge operator delay after reset.
            task.update(arm="raw", operator_assisted=False)
            first.update(arm="raw", operator_assisted=False)
        args = argparse.Namespace(resume_task_file=str(self.run_dir / "task.json"), continue_open_runtime=False)
        read = collector.read_object
        def read_record(path):
            return first if Path(path) == self.run_dir / "launch.json" else read(path)
        with mock.patch.object(collector, "load_task", return_value=task), \
             mock.patch.object(collector, "read_object", side_effect=read_record), \
             mock.patch.object(collector, "build_snapshot", return_value=dict(errors=[], in_flight_invocations=0)), \
             mock.patch.object(collector, "extract_usage", return_value=dict(
                 status="terminal_error_usage_unverified" if getattr(self, "quota_exit_code", 0) else "ok",
                 thread_id="same-session", comparison_total_tokens=30)):
            result = collector.prepare_resume(args)
        self.assertEqual("same-session", result[2])
        self.assertEqual(4, result[3])
        self.assertEqual(self.launch["quota_clock"]["effective_deadline_utc"], args.absolute_deadline_utc)
        self.assertAlmostEqual(2 + 10 / 60, args.watchdog_hours, delta=0.002)

    def test_native_harness_collector_uses_only_verified_pause(self):
        self.check_collector_clock()

    def test_native_raw_collector_charges_delay_after_reset(self):
        self.check_collector_clock(raw=True)

    def test_verified_native_quota_exit_is_resumable(self):
        self.quota_exit_code = 1
        self.check_collector_clock()

    def test_quota_receipt_does_not_excuse_an_unrelated_failed_segment(self):
        self.install_pause()
        first = json.loads((self.run_dir / "launch.json").read_text())
        task = dict(first, root_run_dir=str(self.run_dir), interruption_policy="planned_resume")
        (self.rt / "RUNTIME_STATE.json").write_text(json.dumps(dict(state="CLOSED")))
        (self.launch_path.parent / "manifest.json").write_text(json.dumps(dict(run_id=first["run_id"], exit_code=1, elapsed_seconds=1)))
        args = argparse.Namespace(resume_task_file=str(self.run_dir / "task.json"), continue_open_runtime=False)
        with mock.patch.object(collector, "load_task", return_value=task), \
             mock.patch.object(collector, "build_snapshot", return_value=dict(errors=[], in_flight_invocations=0)):
            with self.assertRaisesRegex(collector.LedgerError, "diagnose"):
                collector.prepare_resume(args)

    def quota_lane(self):
        epoch = self.open()["epoch_id"]
        self.lane(epoch, "quota-worker", "result_invalid")
        lane_path = orchestrator_harness.epochs.lane_record_path(self.rt, epoch, "quota-worker")
        lane = json.loads(lane_path.read_text())
        status = dict(run_id=lane["run_id"], recorded_status="provider_exited_no_result",
            controller_state="exited", cleanup_proven=True,
            provider_state=dict(state="exited", pid=432, creation_time="provider-creation"),
            process_boundary=dict(kind="native-boundary"))
        status_path = self.base / "controller-status.json"
        status_path.write_text(json.dumps(status))
        lane.update(controller_status_path=str(status_path), process=dict(pid=431, creation_time="controller-creation"))
        lane_path.write_text(json.dumps(lane))
        return status_path, status

    def test_invalid_worker_cannot_pass_ordinary_review_quiescence(self):
        self.quota_lane()
        self.assertFalse(collector.quiescent_open_runtime(self.rt))

    def test_quota_worker_requires_exact_absence_and_boundary_cleanup(self):
        self.quota_lane()
        with mock.patch.multiple(orchestrator_harness.processes, identity_matches=mock.Mock(return_value=False),
                process_alive=mock.Mock(return_value=False), process_boundary_is_gone=mock.Mock(return_value=True)):
            self.assertTrue(collector.quiescent_open_runtime(self.rt, quota_recovery=True))

    def test_live_quota_provider_cannot_be_resumed(self):
        self.quota_lane()
        with mock.patch.object(orchestrator_harness.processes, "identity_matches", return_value=True):
            self.assertFalse(collector.quiescent_open_runtime(self.rt, quota_recovery=True))

    def test_unknown_quota_boundary_cannot_be_resumed(self):
        self.quota_lane()
        with mock.patch.multiple(orchestrator_harness.processes, identity_matches=mock.Mock(return_value=False),
                process_alive=mock.Mock(return_value=False), process_boundary_is_gone=mock.Mock(return_value=False)):
            self.assertFalse(collector.quiescent_open_runtime(self.rt, quota_recovery=True))

    def test_accepted_worker_needs_cleanup_proof_but_no_retirement(self):
        status_path, status = self.quota_lane()
        status["recorded_status"] = "review_pending"
        status_path.write_text(json.dumps(status))
        lane_path = next(self.rt.glob("epochs/*/lanes/quota-worker/lane.json"))
        lane = json.loads(lane_path.read_text())
        lane["lifecycle"] = "accepted"
        lane_path.write_text(json.dumps(lane))
        self.assertFalse(collector.quiescent_open_runtime(self.rt))
        with mock.patch.multiple(orchestrator_harness.processes, identity_matches=mock.Mock(return_value=False),
                process_alive=mock.Mock(return_value=False), process_boundary_is_gone=mock.Mock(return_value=True)):
            self.assertTrue(collector.quiescent_open_runtime(self.rt, quota_recovery=True))


class PreparationRecordsTests(unittest.TestCase):
    def check_finish_record(self, quota, historical_quota=False):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            workspace = base / "w"
            runtime = workspace / ".harness-runtime"
            runtime.mkdir(parents=True)
            (runtime / "RUNTIME_STATE.json").write_text(json.dumps(dict(state="OPEN")))
            harness = base / "harness"
            run = base / "out/run"
            run.mkdir(parents=True)
            prior = base / "initial-prelaunch.json"
            prior.write_text(json.dumps(dict(schema="test-receipt")))
            ref = dict(receipt_path=str(prior), receipt_sha256=hashlib.sha256(prior.read_bytes()).hexdigest())
            (run / "launch.json").write_text(json.dumps(dict(root_prelaunch=ref)))
            target = workspace / ".agent-workspace/root-continuations/0002/prelaunch.json"
            def ready(args):
                args.provider_id = "claude-code"
                args.operator_assisted = True
                args.harness_dir = str(harness)
                args.cwd = str(workspace)
                args.run_id = "run"
                args.continuation_receipt = str(target)
                args.absolute_deadline_utc = "2026-10-31T14:00:00+00:00"
                args.quota_resume = quota
                if quota or historical_quota:
                    args.quota_clock = dict(paused_seconds=600)
                return run / "segments/0002", 2, "same-session", 4
            with mock.patch.dict(sys.modules, collect_codex_usage=collector), \
                 mock.patch.object(collector, "prepare_resume", side_effect=ready), \
                 mock.patch.object(preparation, "validate_prepared_root", return_value=dict(status="PASS")), \
                 mock.patch.object(preparation, "check_installed", return_value={}), \
                 mock.patch.object(preparation.subprocess, "check_output", return_value="candidate-sha"), \
                 mock.patch("orchestrator_harness.public_checks.start_service", return_value=None):
                # The fixture needs a stable native config hash, but starts no service.
                harness.mkdir()
                (harness / "harness-config.json").write_text("{}")
                preparation.prepare_continuation(harness, workspace, "run", run / "task.json", provider_id="claude-code")
            self.assertEqual(not quota, (run / "first-reported-finish.json").exists())
            attempt = json.loads((target.parent / "attempt.json").read_text())
            self.assertEqual("quota_recovery" if quota else "workflow_audit", attempt["continuation_reason"])

    def test_quota_preparation_does_not_claim_task_finish(self):
        self.check_finish_record(True)

    def test_workflow_preparation_preserves_first_finish_record(self):
        self.check_finish_record(False)

    def test_first_finish_after_prior_quota_recovery_is_still_preserved(self):
        self.check_finish_record(False, historical_quota=True)


if __name__ == "__main__":
    unittest.main()
