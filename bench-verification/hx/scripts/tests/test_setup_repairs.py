"""Regressions for observed setup failures, using the real result validators."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1]
HARNESS = SCRIPTS.parent
sys.path[:0] = [str(SCRIPTS), str(HARNESS)]
import collect_codex_usage as collector
from orchestrator_harness import bootstrap, collector_context, controller
from orchestrator_harness.core import content_hash


def helper(name):
    path = HARNESS / "super-cache/workspace/.agent-workspace" / name
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


writer = helper("write-result.py")
budget = helper("run-budget.py")
stop = helper("result-stop-check.py")


class SetupRepairTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "root"
        self.harness = Path(temp.name) / "harness"
        self.agent = self.root / ".agent-workspace"
        self.agent.mkdir(parents=True)
        self.harness.mkdir()

    def write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def bound_worker(self):
        self.write(self.agent / "harness-hook-binding.json", {
            "schema": "harness-hook-binding/v1", "role": "worker", "lane_id": "lane",
            "run_id": "current", "result_path": str(self.root / "RESULT.json")})
        self.write(self.agent / "result-template.json", {
            "schema": "result/v1", "lane_id": "lane", "run_id": "current"})
        return {"lane_id": "lane", "run_id": "current", "result_path": str(self.root / "RESULT.json")}

    def test_generated_reports_pass_controller_and_worker_stop_check(self):
        lane = self.bound_worker()
        for outcome in ("PASS", "FAIL", "BLOCKED"):
            with self.subTest(outcome=outcome):
                record = writer.write_result(self.agent, outcome, "Evidence: café", [{"revision": "abc", "exit": 1}])
                self.assertEqual(content_hash(record), record["content_hash"])
                self.assertEqual("valid", controller._validate_result(lane)[0])
                self.assertTrue(stop.check_result(self.agent)[0])

    def test_git_hash_is_rejected_then_explicit_writer_corrects_report(self):
        lane = self.bound_worker()
        record = writer.write_result(self.agent, "FAIL", "Useful partial progress", ["check.json"])
        record["content_hash"] = "b46ea97a27347d86228ee1853e7bc2a31af8f91e"
        self.write(self.root / "RESULT.json", record)
        self.assertEqual("invalid", controller._validate_result(lane)[0])
        writer.write_result(self.agent, "FAIL", "Useful partial progress", ["check.json"])
        self.assertEqual("valid", controller._validate_result(lane)[0])

    def test_invalid_outcome_and_stale_template_preserve_existing_report(self):
        self.bound_worker()
        writer.write_result(self.agent, "FAIL", "Partial", [])
        before = (self.root / "RESULT.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "outcome"):
            writer.write_result(self.agent, "PARTIAL", "Partial", [])
        self.write(self.agent / "result-template.json", {"schema": "result/v1", "lane_id": "lane", "run_id": "old"})
        with self.assertRaisesRegex(ValueError, "run_id"):
            writer.write_result(self.agent, "PASS", "Completed", [])
        self.assertEqual(before, (self.root / "RESULT.json").read_bytes())

    def budget_record(self, seconds=7200, deadline="2026-10-11T20:02:28Z"):
        record = {"schema": "run-budget/v1", "authority": "cli-collector-watchdog",
                  "run_id": "current", "segment_started_at_utc": "2026-10-11T18:02:28Z",
                  "watchdog_deadline_utc": deadline, "watchdog_seconds": seconds}
        path = self.agent / "RUN_BUDGET.json"
        self.write(path, record)
        return path

    def test_actual_r04_launch_has_71_minutes_not_under_ten(self):
        now = datetime(2026, 10, 11, 18, 51, 8, 861542, tzinfo=timezone.utc)
        actual = budget.remaining_budget(self.budget_record(), now)
        self.assertAlmostEqual(71.319, actual["remaining_minutes"], places=3)
        self.assertFalse(actual["expired"])

    def test_three_hour_budget_and_expiry_use_same_deadline(self):
        path = self.budget_record(10800, "2026-10-11T21:02:28Z")
        early = budget.remaining_budget(path, datetime(2026, 10, 11, 18, 47, 28, tzinfo=timezone.utc))
        self.assertEqual(180, early["limit_minutes"])
        self.assertEqual(135, early["remaining_minutes"])
        expired = budget.remaining_budget(path, datetime(2026, 10, 11, 21, 3, tzinfo=timezone.utc))
        self.assertTrue(expired["expired"])
        self.assertEqual(0, expired["remaining_seconds"])

    def test_inconsistent_deadline_is_not_silently_estimated(self):
        with self.assertRaisesRegex(ValueError, "disagree"):
            budget.remaining_budget(self.budget_record(10800))

    def test_continuation_reports_original_limit_and_actual_remaining_time(self):
        path = self.budget_record(3600, "2026-10-11T19:02:28Z")
        value = json.loads(path.read_text())
        value.update(original_watchdog_seconds=10800,
                     budget_scope="entire operator-assisted run, including pauses")
        self.write(path, value)
        actual = budget.remaining_budget(path, datetime(2026, 10, 11, 18, 32, 28, tzinfo=timezone.utc))
        self.assertEqual(180, actual["limit_minutes"])
        self.assertEqual(30, actual["remaining_minutes"])
        self.assertIn("including pauses", actual["budget_scope"])

    def launch_record(self):
        launch = {"arm": "harness", "role": "root", "run_id": "current",
                  "harness_dir": str(self.harness), "workspace": str(self.root),
                  "started_at_utc": "2026-10-11T18:02:28Z", "watchdog_hours": 3,
                  "watchdog_deadline_utc": "2026-10-11T21:02:28Z"}
        path = self.root / "launch.json"
        self.write(path, launch)
        self.write(self.root / ".codex/orchestrator-harness-binding.json", {
            "schema": "harness-hook-binding/v1", "role": "root", "provider_id": "codex",
            "harness_root": str(self.harness), "liveness_path": ".agent-workspace/root-hook-liveness.jsonl"})
        return path, launch

    def test_stale_and_stop_only_hook_records_are_not_native_startup_proof(self):
        path, _ = self.launch_record()
        records = [
            {"schema": "hook-liveness/v1", "role": "root", "provider_id": "codex",
             "boundary": "post-tool-use", "at": "2026-10-11T17:59:00Z"},
            {"schema": "hook-liveness/v1", "role": "root", "provider_id": "codex",
             "boundary": "stop", "at": "2026-10-11T18:03:00Z"}]
        log = self.agent / "root-hook-liveness.jsonl"
        log.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
        with patch.dict(os.environ, {"SWE_ROOT_LAUNCH_FILE": str(path)}):
            with self.assertRaisesRegex(ValueError, "unverified"):
                collector_context.require_native_root_hooks(self.harness, self.root)
            records[-1]["boundary"] = "post-tool-use"
            log.write_text("\n".join(json.dumps(r) for r in records), encoding="utf-8")
            proof = collector_context.require_native_root_hooks(self.harness, self.root)
        self.assertEqual(1, proof["native_post_tool_use_records"])

    def test_missing_hooks_block_bootstrap_before_worktree_or_lane_creation(self):
        path, _ = self.launch_record()
        self.write(self.harness / "harness-config.json", {"root_workspace": str(self.root), "managed_coordination": "enabled"})
        self.write(self.harness / "resource-manifest.json", {"schema": "resource-manifest/v1", "resources": []})
        with (patch.dict(os.environ, {"SWE_ROOT_LAUNCH_FILE": str(path)}),
              patch("orchestrator_harness.config.find_harness_root", return_value=self.harness)):
            result = bootstrap.run_bootstrap(lane_id="worker", provider="codex", model="gpt-5.6-terra",
                                            launch_config={"reasoning_effort": "high", "service_tier": "default"},
                                            exclusive_resources=[], task_card_path=self.root / "card.json")
        self.assertFalse(result["ok"])
        self.assertEqual("BOOTSTRAP_ROOT_HOOK_UNVERIFIED", result["code"])
        self.assertFalse((self.root / ".harness-runtime").exists())

    def test_standalone_harness_use_does_not_require_collector_hook_proof(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(collector_context.require_native_root_hooks(self.harness, self.root))

    def test_budget_installation_supports_resume_without_adopting_another_run(self):
        _, launch = self.launch_record()
        source = self.harness / "super-cache/workspace/.agent-workspace/run-budget.py"
        source.parent.mkdir(parents=True)
        source.write_text("# portable helper fixture\n", encoding="utf-8")
        path = collector.install_run_budget(self.harness, self.root, launch, resuming=False)
        self.assertEqual(10800, json.loads(path.read_text())["watchdog_seconds"])
        with self.assertRaisesRegex(collector.LedgerError, "earlier launch"):
            collector.install_run_budget(self.harness, self.root, launch, resuming=False)
        resumed = {**launch, "started_at_utc": "2026-10-12T00:00:00Z", "watchdog_hours": 1,
                   "watchdog_deadline_utc": "2026-10-12T01:00:00Z"}
        collector.install_run_budget(self.harness, self.root, resumed, resuming=True)
        self.assertEqual(60, budget.remaining_budget(path, datetime(2026, 10, 12, tzinfo=timezone.utc))["remaining_minutes"])
        with self.assertRaisesRegex(collector.LedgerError, "earlier launch"):
            collector.install_run_budget(self.harness, self.root, {**resumed, "run_id": "foreign"}, resuming=True)

    def test_prompt_time_matches_two_and_three_hour_watchdogs(self):
        text = "You have <RUN_TIME_LIMIT_MINUTES> minutes, enforced by the CLI collector watchdog."
        self.assertIn("120 minutes", collector.render_run_prompt(text, 2))
        self.assertIn("180 minutes", collector.render_run_prompt(text, 3))
        self.assertEqual("You have 2 hours, enforced by the CLI collector watchdog.",
                         collector.render_run_prompt("You have 2 hours, enforced by the CLI collector watchdog.", 2))
        with self.assertRaisesRegex(collector.LedgerError, "time limit"):
            collector.render_run_prompt("You have 2 hours, enforced by the CLI collector watchdog.", 3)
        with self.assertRaisesRegex(collector.LedgerError, "run settings"):
            collector.render_run_prompt("RUN_TIME_LIMIT_MINUTES: 120\n", 3)


if __name__ == "__main__":
    unittest.main()
