"""Claude accounting and provider-bound prelaunch regressions; no live launches."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HARNESS = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(HARNESS), str(HARNESS / "scripts")]
import collect_codex_usage as collector
import prepare_root_launch as preparation
import token_ledger as ledger
from orchestrator_harness import collector_context


class ClaudeBenchmarkTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)

    def write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def events(self, path, session="session-a", output=30, inp=100, **changes):
        final = {"type": "result", "subtype": "success", "is_error": False,
                 "session_id": session, "usage": {"output_tokens": 2},
                 "modelUsage": {"claude-haiku-5-5": {"inputTokens": inp, "outputTokens": output}}}
        final.update(changes)
        records = [{"type": "system", "subtype": "init", "session_id": session},
                   {"type": "assistant", "message": {"usage": {"output_tokens": 9999}}}, final]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(row) + "\n" for row in records), encoding="utf-8")
        return records

    def extract(self, path, **options):
        return ledger.extract_usage(path, provider_id="claude-code", **options)

    def root(self, directory, *, output=30, session="session-a", number=1):
        workspace = self.base / "workspace"
        original = self.base / "run"
        command = ["claude", "--print", "--model", "claude-haiku-5-5", "--effort", "high"]
        launch = dict(schema=ledger.RUN_SCHEMA, run_id="fixture", task="fixture", arm="raw",
                      provider_id="claude-code", model="claude-haiku-5-5", reasoning_effort="high",
                      service_tier=None, sandbox="claude-bypassPermissions", workspace=str(workspace),
                      started_at_utc=f"2026-10-30T12:0{number}:00+00:00", command=command, budget_tokens=None)
        if number > 1:
            launch.update(segment_number=number, resume_session_id=session)
            command += ["--resume", session]
        self.write(directory / "launch.json", launch)
        self.write(directory / "manifest.json", {**launch, "exit_code": 0, "elapsed_seconds": 10,
                                                "ended_at_utc": f"2026-10-30T12:0{number}:10+00:00"})
        self.events(directory / "claude-events.jsonl", session=session, output=output, inp=100 * number)
        task = dict(schema=ledger.TASK_SCHEMA, run_id="fixture", task="fixture", arm="raw",
                    root_run_dir=str(original), budget_tokens=None, interruption_policy="planned_resume")
        self.write(original / "task.json", task)
        return original / "task.json"

    def test_whole_tree_rollup_includes_nested_models_and_ignores_assistant_placeholders(self):
        path = self.base / "events"
        self.events(path, modelUsage={"root": {"inputTokens": 100, "outputTokens": 30},
                                     "child": {"inputTokens": 20, "outputTokens": 17}})
        result = self.extract(path)
        self.assertEqual(("ok", 47, 167), (result["status"], result["output_tokens"], result["comparison_total_tokens"]))
        self.assertIsNone(result["cached_input_tokens"])

    def test_main_loop_usage_cannot_substitute_for_missing_whole_tree_rollup(self):
        path = self.base / "events"
        self.events(path, modelUsage={})
        self.assertEqual("missing_usage", self.extract(path)["status"])

    def test_missing_negative_and_boolean_output_counters_are_rejected(self):
        for out in (None, -1, True):
            path = self.base / "events"
            self.events(path, modelUsage={"root": {"inputTokens": 100, "outputTokens": out}})
            with self.subTest(out=out), self.assertRaises(ledger.LedgerError):
                self.extract(path)

    def test_crash_zero_counters_are_not_exact(self):
        path = self.base / "events"
        self.events(path, output=0, inp=0, is_error=True, subtype="error_during_execution")
        self.assertEqual("terminal_error_usage_unverified", self.extract(path)["status"])

    def test_nested_results_are_not_double_counted(self):
        path = self.base / "events"
        records = self.events(path)
        child = copy.deepcopy(records[-1])
        child.update(session_id="child", parent_tool_use_id="tool-child")
        records.insert(1, child)
        path.write_text("".join(json.dumps(row) + "\n" for row in records), encoding="utf-8")
        self.assertEqual(30, self.extract(path)["output_tokens"])

    def test_indexed_native_notification_results_use_last_cumulative_rollup_once(self):
        path = self.base / "events"
        records = self.events(path, result_index=0)
        for index, output in ((1, 30), (2, 47)):
            final = copy.deepcopy(records[-1])
            final.update(result_index=index, origin={"kind": "task-notification"})
            final["modelUsage"]["claude-haiku-5-5"]["outputTokens"] = output
            records.append(final)
        path.write_text("".join(json.dumps(row) + "\n" for row in records))
        result = self.extract(path)
        self.assertEqual(47, result["output_tokens"])
        self.assertEqual(3, result["terminal_records"])

    def test_native_result_counter_regression_is_rejected(self):
        path = self.base / "events"
        records = self.events(path, result_index=0)
        final = copy.deepcopy(records[-1]);final["result_index"] = 1
        final["modelUsage"]["claude-haiku-5-5"]["outputTokens"] = 2
        records.append(final);path.write_text("".join(json.dumps(row) + "\n" for row in records))
        with self.assertRaisesRegex(ledger.LedgerError, "cumulative counters decreased"):
            self.extract(path)

    def test_error_does_not_erase_a_known_cumulative_prefix_or_make_it_exact(self):
        for counters in ({}, {"claude-haiku-5-5":{"inputTokens":0,"outputTokens":0}}):
            path=self.base/"events";records=self.events(path,result_index=0)
            records.append(dict(type="result",subtype="error_during_execution",is_error=True,
                                session_id="session-a",result_index=1,modelUsage=counters))
            path.write_text("".join(json.dumps(row)+"\n" for row in records))
            with self.subTest(counters=counters):
                result=self.extract(path)
                self.assertEqual("terminal_error_usage_unverified",result["status"])
                self.assertEqual(30,result["output_tokens"])
                self.assertEqual(3,result["selected_line"])

    def test_resumed_cli_may_continue_its_native_result_index(self):
        path = self.base / "events"
        self.events(path, result_index=7)
        self.assertEqual(30,self.extract(path)["output_tokens"])
        self.assertEqual(30,self.extract(path,segment_index=1)["output_tokens"])

    def test_worker_notification_turn_is_not_a_second_physical_resume(self):
        path=self.base/"events";records=self.events(path,result_index=0)
        notification=copy.deepcopy(records[-1]);notification.update(result_index=1,origin={"kind":"task-notification"})
        notification["modelUsage"]["claude-haiku-5-5"]["outputTokens"]=47
        records += [copy.deepcopy(records[0]),notification]
        other=self.base/"second";records += self.events(other,output=80,result_index=0)
        path.write_text("".join(json.dumps(row)+"\n" for row in records))
        self.assertEqual(47,self.extract(path,segment_index=1)["output_tokens"])
        self.assertEqual(80,self.extract(path,segment_index=2)["output_tokens"])

    def test_pending_physical_resume_does_not_reuse_old_notification_usage(self):
        path=self.base/"events";records=self.events(path,result_index=0)
        notification=copy.deepcopy(records[-1]);notification["result_index"]=1
        records += [copy.deepcopy(records[0]),notification,copy.deepcopy(records[0])]
        path.write_text("".join(json.dumps(row)+"\n" for row in records))
        self.assertEqual("in_flight",self.extract(path,segment_index=2,completed=False)["status"])
        self.assertNotIn("output_tokens",self.extract(path,segment_index=2,completed=False))

    def test_duplicate_or_skipped_native_result_indexes_are_rejected(self):
        for index in (0, 2, True):
            path = self.base / "events";records = self.events(path, result_index=0)
            final = copy.deepcopy(records[-1]);final["result_index"] = index
            records.append(final);path.write_text("".join(json.dumps(row) + "\n" for row in records))
            with self.subTest(index=index), self.assertRaises(ledger.LedgerError):self.extract(path)

    def test_zero_turn_notification_drain_does_not_create_worker_attempt(self):
        path = self.base / "events";records = self.events(path, result_index=0)
        drain = [copy.deepcopy(records[0]),dict(type="result", subtype="success", is_error=False,
                 session_id="session-a", origin={"kind":"task-notification"},num_turns=0,modelUsage={})]
        path.write_text("".join(json.dumps(row) + "\n" for row in drain + records))
        self.assertEqual(30,self.extract(path,segment_index=1)["output_tokens"])

    def test_appended_worker_resume_segments_are_selected_individually(self):
        path, other = self.base / "events", self.base / "other"
        self.events(path, output=30)
        self.events(other, output=50)
        path.write_bytes(path.read_bytes() + other.read_bytes())
        self.assertEqual(30, self.extract(path, segment_index=1)["output_tokens"])
        self.assertEqual(50, self.extract(path, segment_index=2)["output_tokens"])

    def test_missing_terminal_and_malformed_tail_cannot_finalize(self):
        path = self.base / "events"
        path.write_text('{"type":"system","subtype":"init","session_id":"s"}\n{', encoding="utf-8")
        self.assertEqual("in_flight", self.extract(path, completed=False)["status"])
        with self.assertRaises(ledger.LedgerError):
            self.extract(path)

    def test_same_session_resume_counts_only_new_output(self):
        task = self.root(self.base / "run", output=30)
        self.root(self.base / "run/segments/0002", output=50, number=2)
        snapshot = ledger.build_snapshot(task)
        self.assertEqual([], snapshot["errors"])
        self.assertEqual(50, snapshot["known_output_tokens"])
        self.assertEqual([30, 20], [row["charged_output_tokens"] for row in snapshot["rows"]])
        self.assertTrue(snapshot["output_tokens_are_exact"])
        archive = ledger.finalize(task, self.base / "archive")
        self.assertEqual(50, archive["known_output_tokens"])

    def test_resumed_output_regression_is_not_exact_even_when_input_increases(self):
        task = self.root(self.base / "run", output=30)
        self.root(self.base / "run/segments/0002", output=20, number=2)
        snapshot = ledger.build_snapshot(task)
        self.assertTrue(any("output_tokens decreased" in error for error in snapshot["errors"]))
        self.assertFalse(snapshot["output_tokens_are_exact"])

    def test_changed_resume_session_is_rejected(self):
        task = self.root(self.base / "run")
        self.root(self.base / "run/segments/0002", session="different", number=2)
        with self.assertRaisesRegex(ledger.LedgerError, "session differs"):
            ledger.build_snapshot(task)

    def test_native_claude_worker_discovery_and_resumed_output_join_root_total(self):
        task_path = self.root(self.base / "run", output=30)
        runtime = self.base / "workspace/.harness-runtime"
        for name in ("task.json", "launch.json", "manifest.json"):
            path = task_path.parent / name
            record = json.loads(path.read_text())
            record.update(arm="harness", harness_runtime=str(runtime))
            self.write(path, record)
        agent = runtime / "worktrees/epoch/worker/.agent-workspace"
        provider = dict(id="claude-code", model="claude-haiku-5-5", launch_config={"effort": "high"})
        transcript = agent / "provider-transcript.jsonl"
        self.write(agent / "invocation.json", dict(schema="controller-invocation/v1", lane_id="worker",
                   run_id="worker-run", provider=provider, paths={"transcript": str(transcript)}))
        events, attempts = [], [{"schema": "controller-attempts/v1"}]
        for number in (1, 2):
            events.append(dict(event_type="provider_started", run_id="worker-run",
                               ts=f"2026-10-30T12:01:0{number}+00:00"))
            argv = ["claude", "--model", "claude-haiku-5-5", "--effort", "high"]
            if number == 2:
                argv += ["--resume", "session-worker"]
            attempts.append(dict(attempt=number, argv=argv, provider=provider, transcript_path=str(transcript),
                                 at=f"2026-10-30T12:01:0{number + 2}+00:00", exit_code=0))
        for path, records in ((agent / "controller.events.jsonl", events),
                              (agent / "controller.attempts.jsonl", attempts)):
            path.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
        other = self.base / "attempt-two"
        self.events(transcript, session="session-worker", output=7, inp=10)
        self.events(other, session="session-worker", output=11, inp=20)
        transcript.write_bytes(transcript.read_bytes() + other.read_bytes())
        snapshot = ledger.build_snapshot(task_path)
        self.assertEqual([], snapshot["errors"])
        self.assertEqual(41, snapshot["known_output_tokens"])
        workers = [r for r in snapshot["rows"] if r["role"] == "worker"]
        self.assertEqual([7, 4], [r["charged_output_tokens"] for r in workers])
        self.assertTrue(snapshot["output_tokens_are_exact"])

    def test_claude_launch_preferences_require_explicit_model_effort_without_tier(self):
        argv = ["claude", "--print", "--model", "claude-haiku-5-5", "--effort", "high"]
        self.assertEqual(dict(model="claude-haiku-5-5", reasoning_effort="high", service_tier=None),
                         ledger.launch_preferences(argv, "claude-code"))
        with self.assertRaises(ledger.LedgerError):
            ledger.launch_preferences(argv[:-2], "claude-code")

    def test_claude_preparation_never_runs_codex_sandbox_health(self):
        with patch.object(preparation, "require_ready", side_effect=AssertionError("sandbox must not run")):
            self.assertIsNone(preparation.sandbox_health(self.base, self.base, "claude-code"))
        with self.assertRaisesRegex(ValueError, "unsupported"):
            preparation.sandbox_health(self.base, self.base, "unknown")

    def test_claude_hook_gate_requires_real_fresh_matching_provider_evidence(self):
        root, harness = self.base / "root", self.base / "harness"
        launch = self.base / "launch.json"
        self.write(launch, dict(arm="harness", role="root", provider_id="claude-code", run_id="test",
                               workspace=str(root), harness_dir=str(harness), started_at_utc="2026-10-30T12:00:00Z"))
        self.write(root / ".claude/orchestrator-harness-binding.json",
                   dict(role="root", provider_id="claude-code", harness_root=str(harness),
                        liveness_path=".agent-workspace/hooks.jsonl"))
        live = root / ".agent-workspace/hooks.jsonl"
        record = dict(schema="hook-liveness/v1", role="root", provider_id="claude-code",
                      boundary="post-tool-use", at="2026-10-30T12:01:00Z")
        with patch.dict("os.environ", {"SWE_ROOT_LAUNCH_FILE": str(launch)}):
            with self.assertRaisesRegex(ValueError, "unverified"):
                collector_context.require_native_root_hooks(harness, root)
            self.write(live, {**record, "provider_id": "codex"})
            with self.assertRaisesRegex(ValueError, "unverified"):
                collector_context.require_native_root_hooks(harness, root)
            self.write(live, record)
            self.assertEqual(1, collector_context.require_native_root_hooks(harness, root)["native_post_tool_use_records"])


if __name__ == "__main__":
    unittest.main()
