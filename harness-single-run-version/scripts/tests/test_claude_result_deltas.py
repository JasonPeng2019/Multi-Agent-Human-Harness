"""Native Claude per-result accounting across interrupted CLI processes."""
import copy
import json
import unittest
from test_claude_benchmark import ClaudeBenchmarkTests
import token_ledger as ledger


class NativeDeltaTests(ClaudeBenchmarkTests):
    def delta(self, output=30, inp=100, **changes):
        event = dict(type="result", subtype="success", is_error=False,
                     session_id="session-a", result_index=0,
                     modelUsage={"root": dict(inputTokens=900, outputTokens=900)},
                     model_usage_since_last_result={"root": dict(inputTokens=inp, outputTokens=output)})
        event.update(changes)
        return event

    def transcript(self, events):
        path = self.base / "deltas.jsonl"
        path.write_text("".join(json.dumps(row) + "\n" for row in [
            dict(type="system", subtype="init", session_id="session-a"), *events]), encoding="utf-8")
        return path

    def test_native_deltas_sum_while_cumulative_counters_repeat_or_reset(self):
        events = [self.delta(output=30), self.delta(output=7, result_index=1, modelUsage={})]
        result = self.extract(self.transcript(events))
        self.assertEqual(37, result["output_tokens"])
        self.assertEqual("physical_cli_including_builtin_subagents", result["usage_scope"])

    def test_empty_delta_is_known_zero(self):
        result = self.extract(self.transcript([self.delta(model_usage_since_last_result={})]))
        self.assertEqual(("ok", 0), (result["status"], result["comparison_total_tokens"]))

    def test_zero_turn_notification_with_native_delta_is_counted(self):
        result = self.extract(self.transcript([self.delta(), self.delta(
            output=7, result_index=1, num_turns=0, origin=dict(kind="task-notification"), modelUsage={})]))
        self.assertEqual(37, result["output_tokens"])

    def test_child_delta_not_double_counted(self):
        child = self.delta(output=999, parent_tool_use_id="child")
        result = self.extract(self.transcript([child, self.delta(output=10)]))
        self.assertEqual(10, result["output_tokens"])

    def test_missing_delta_is_distinct_from_empty_map(self):
        missing = self.delta(result_index=1)
        del missing["model_usage_since_last_result"]
        with self.assertRaises(ledger.LedgerError):
            self.extract(self.transcript([self.delta(), missing]))

    def test_delta_error_preserves_known_prefix_without_exact_claim(self):
        result = self.extract(self.transcript([self.delta(), self.delta(
            output=5, result_index=1, is_error=True, subtype="error_during_execution")]))
        self.assertEqual(("terminal_error_usage_unverified", 35), (result["status"], result["output_tokens"]))

    def test_unaccounted_error_cannot_be_hidden_by_later_success(self):
        error = self.delta(result_index=1, is_error=True)
        del error["model_usage_since_last_result"]
        with self.assertRaises(ledger.LedgerError):
            self.extract(self.transcript([self.delta(), error, self.delta(result_index=2)]))

    def test_invalid_delta_and_missing_native_indexes_rejected(self):
        for change in (dict(model_usage_since_last_result=None), dict(result_index=None),
                       dict(model_usage_since_last_result={"root": dict(inputTokens=1, outputTokens=-1)})):
            with self.subTest(change=change), self.assertRaises(ledger.LedgerError):
                self.extract(self.transcript([self.delta(**change)]))

    def test_index_gaps_rejected(self):
        with self.assertRaises(ledger.LedgerError):
            self.extract(self.transcript([self.delta(), self.delta(result_index=2)]))

    def test_native_resumed_process_charges_its_own_calls_directly(self):
        original = self.base / "run"
        task = self.root(original)
        self.transcript([self.delta(output=30)]).replace(original / "claude-events.jsonl")
        continuation = original / "segments/0002"
        self.root(continuation, number=2)
        self.transcript([self.delta(output=7)]).replace(continuation / "claude-events.jsonl")
        snapshot = ledger.build_snapshot(task)
        self.assertEqual([], snapshot["errors"])
        self.assertEqual(37, snapshot["known_output_tokens"])


if __name__ == "__main__":
    unittest.main()
