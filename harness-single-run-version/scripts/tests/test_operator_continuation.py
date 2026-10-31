from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import collect_codex_usage as collector
import prepare_root_launch as preparation


class OperatorContinuationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "root"
        self.harness = self.base / "harness"
        self.run = self.base / "results/fixture"
        for path in (self.root, self.harness, self.run):
            path.mkdir(parents=True)
        self.runtime = self.root / ".harness-runtime"
        self.deadline = (datetime.now(timezone.utc) + timedelta(minutes=40)).isoformat()
        self.launch = dict(run_id="fixture", task="fixture", arm="harness", budget_tokens=None,
                           harness_runtime=str(self.runtime), workspace=str(self.root),
                           harness_dir=str(self.harness), model="gpt-5.6-terra", reasoning_effort="high",
                           service_tier="default", sandbox="danger-full-access", watchdog_hours=1,
                           watchdog_deadline_utc=self.deadline, trust_project_hooks=True)
        self.task = dict(schema="codex-token-task/v1", run_id="fixture", task="fixture", arm="harness",
                         budget_tokens=None, root_run_dir=str(self.run), harness_runtime=str(self.runtime),
                         interruption_policy="planned_resume", operator_assisted=True,
                         watchdog_deadline_utc=self.deadline)
        self.write(self.run / "launch.json", self.launch)
        self.write(self.run / "manifest.json", dict(self.launch, elapsed_seconds=60, exit_code=0, launch_error=None))
        self.write(self.run / "task.json", self.task)
        self.write(self.runtime / "RUNTIME_STATE.json", {"state": "CLOSED"})
        self.args = argparse.Namespace(resume_task_file=str(self.run / "task.json"), continue_open_runtime=True)
        for name, value in (("build_snapshot", dict(errors=[], in_flight_invocations=0)),
                            ("extract_usage", dict(status="ok", thread_id="same-root"))):
            mock = patch.object(collector, name, return_value=value)
            mock.start()
            self.addCleanup(mock.stop)

    def write(self, path, record):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record), encoding="utf-8")

    def test_gap_consumes_original_wall_clock_budget(self):
        segment, number, session, limit = collector.prepare_resume(self.args)
        self.assertEqual((number, session, limit), (2, "same-root", 1))
        self.assertTrue(39 / 60 < self.args.watchdog_hours <= 40 / 60)
        self.assertEqual(self.deadline, self.args.absolute_deadline_utc)
        self.assertEqual(segment, self.run / "segments/0002")

    def test_legacy_planned_pause_keeps_active_time_policy(self):
        self.task.pop("operator_assisted")
        self.write(self.run / "task.json", self.task)
        collector.prepare_resume(self.args)
        self.assertAlmostEqual(59 / 60, self.args.watchdog_hours)
        self.assertFalse(self.args.operator_assisted)

    def test_expired_original_deadline_refuses_resume(self):
        self.task["watchdog_deadline_utc"] = self.launch["watchdog_deadline_utc"] = (
            datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()
        self.write(self.run / "task.json", self.task)
        self.write(self.run / "launch.json", self.launch)
        with self.assertRaisesRegex(collector.LedgerError, "exhausted"):
            collector.prepare_resume(self.args)
        self.assertFalse((self.run / "segments").exists())

    def test_changed_deadline_refuses_resume(self):
        self.task["watchdog_deadline_utc"] = (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat()
        self.write(self.run / "task.json", self.task)
        with self.assertRaisesRegex(collector.LedgerError, "differs"):
            collector.prepare_resume(self.args)

    def test_failed_launch_is_not_a_normal_continuation(self):
        self.write(self.run / "manifest.json", dict(self.launch, elapsed_seconds=60, exit_code=2, launch_error="failed"))
        with self.assertRaisesRegex(collector.LedgerError, "launch failed"):
            collector.prepare_resume(self.args)

    def test_undeclared_run_cannot_be_retroactively_resumed(self):
        self.task.pop("interruption_policy")
        self.write(self.run / "task.json", self.task)
        with self.assertRaisesRegex(collector.LedgerError, "not declared"):
            collector.prepare_resume(self.args)

    def test_running_worker_blocks_continuation(self):
        self.write(self.runtime / "RUNTIME_STATE.json", {"state": "OPEN"})
        self.write(self.runtime / "epochs/e/lanes/w/lane.json", {"lifecycle": "running"})
        with self.assertRaisesRegex(collector.LedgerError, "quiescent"):
            collector.prepare_resume(self.args)

    def install_receipt(self):
        self.write(self.harness / "harness-config.json", dict(root_workspace=str(self.root), managed_coordination="enabled"))
        self.write(self.root / ".codex/hooks.json", {"hooks": {
            event: [{"hooks": [{"command": "python " + filename}]}]
            for event, filename in (("PostToolUse", "orchestrator_harness_post_tool_use.py"),
                                    ("Stop", "orchestrator_harness_stop.py"))}})
        self.write(self.root / ".codex/orchestrator-harness-binding.json", dict(
            schema="harness-hook-binding/v1", role="root", provider_id="codex",
            harness_root=str(self.harness), runtime_root=str(self.runtime)))
        for relative in preparation.HOOK_FILES[2:]:
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# fixture\n", encoding="utf-8")
        receipt = dict(schema=preparation.SCHEMA, status="PASS", run_id="fixture",
                       harness_dir=str(self.harness), workspace=str(self.root), prepared_at_utc="initial",
                       hook_sha256=preparation.check_installed(self.harness, self.root, allow_closed=True),
                       harness_config_sha256=preparation.digest(self.harness / "harness-config.json"))
        original = self.root / preparation.RECEIPT
        self.write(original, receipt)
        self.launch["root_prelaunch"] = dict(receipt_path=str(original), receipt_sha256=preparation.digest(original))
        self.write(self.run / "launch.json", self.launch)
        return original

    def test_closed_reopen_is_once_and_preserves_initial_receipt(self):
        from orchestrator_harness import public_checks
        original = self.install_receipt()
        before = original.read_bytes()
        def reopen(command, **kwargs):
            self.assertEqual(["harness", "setup"], command[-2:])
            self.assertNotIn("--overwrite", command)
            self.write(self.runtime / "RUNTIME_STATE.json", {"state": "OPEN"})
            return SimpleNamespace(returncode=0, stdout='{"ok": true}', stderr="")
        with (patch.object(preparation, "require_ready", return_value=None),
              patch.object(preparation.subprocess, "run", side_effect=reopen) as setup,
              patch.object(preparation.subprocess, "check_output", return_value="candidate\n"),
              patch.object(public_checks, "policy", return_value=None),
              patch.object(public_checks, "start_service", return_value=None)):
            result = preparation.prepare_continuation(self.harness, self.root, "fixture", self.run / "task.json")
            again = preparation.prepare_continuation(self.harness, self.root, "fixture", self.run / "task.json")
        self.assertEqual(1, setup.call_count)
        self.assertEqual(result, again)
        self.assertEqual(before, original.read_bytes())
        self.assertTrue((self.run / "first-reported-finish.json").is_file())

    def test_failed_reopen_is_preserved_and_not_retried(self):
        from orchestrator_harness import public_checks
        self.install_receipt()
        with (patch.object(preparation, "require_ready", return_value=None),
              patch.object(preparation.subprocess, "run", return_value=SimpleNamespace(returncode=1, stdout='{"ok":false}', stderr="failure")) as setup,
              patch.object(preparation.subprocess, "check_output", return_value="candidate\n"),
              patch.object(public_checks, "policy", return_value=None)):
            with self.assertRaisesRegex(ValueError, "reopen failed"):
                preparation.prepare_continuation(self.harness, self.root, "fixture", self.run / "task.json")
            with self.assertRaises(FileExistsError):
                preparation.prepare_continuation(self.harness, self.root, "fixture", self.run / "task.json")
        self.assertEqual(1, setup.call_count)
        self.assertTrue((self.root / ".agent-workspace/root-continuations/0002/native-reopen.json").exists())


if __name__ == "__main__":
    unittest.main()
