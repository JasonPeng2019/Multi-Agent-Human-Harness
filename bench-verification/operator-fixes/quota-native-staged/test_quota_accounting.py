import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
sys.path.insert(1, str(Path(__file__).resolve().parents[3] / "harness-single-run-version/scripts"))
from quota_accounting import receipts, validate_row


class QuotaAccountingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.run = self.base / "out/run"
        self.run.mkdir(parents=True)
        self.workspace = self.base / "w"
        self.workspace.mkdir()
        self.launch = dict(run_id="run", workspace=str(self.workspace))
        self.write(self.run / "launch.json", self.launch)
        self.final = dict(self.launch, exit_code=1, ended_at_utc="2026-10-31T09:50:00+00:00", watchdog_expired=False, launch_error=None)
        self.write(self.run / "manifest.json", self.final)
        self.events = self.run / "claude-events.jsonl"
        self.events.write_text(json.dumps(dict(type="rate_limit_event", session_id="same-session", rate_limit_info=dict(status="rejected", resetsAt=1793443200))) + "\n" +
            json.dumps(dict(type="result", session_id="same-session", result_index=0, subtype="success", is_error=True,
                modelUsage={"claude-sonnet-5": dict(inputTokens=10, outputTokens=20, cacheReadInputTokens=0)})) + "\n")
        self.archive = self.base / "quota-stop/transcript.jsonl"
        self.archive.parent.mkdir()
        self.archive.write_bytes(self.events.read_bytes())
        self.stop = dict(schema="operator-quota-stop/v1", run_id="run", root_session_id="same-session",
            all_owned_provider_processes_absent=True, collector_sealed=True, not_task_reported_finish=True,
            segment_launch=self.ref(self.run / "launch.json"), segment_manifest=self.ref(self.run / "manifest.json"), transcript=self.ref(self.events))
        self.stop_path = self.base / "QUOTA_STOP.json"
        self.entry = dict(invocation_id="run.root", role="raw", thread_id="same-session", lane_id=None, lane_run_id=None,
            transcript_segment_sha256=hashlib.sha256(self.events.read_bytes()).hexdigest(), input_tokens=10, output_tokens=20, comparison_total_tokens=30,
            archived_transcript=self.ref(self.archive))
        self.task = dict(root_run_dir=str(self.run), run_id="run", budget_tokens=None)
        self.save()
        self.row = dict(self.entry, provider_id="claude-code", completed=True, transcript_path=str(self.events), status="terminal_error_usage_unverified")

    def write(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))

    def ref(self, path):
        return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())

    def save(self):
        self.write(self.stop_path, self.stop)
        self.write(self.run / "quota-accounting/0001.json", dict(schema="operator-quota-accounting/v1", run_id="run", stop_audit=self.ref(self.stop_path), invocations=[self.entry]))

    def check(self, row=None):
        row = row or self.row
        acknowledgement = receipts(self.task)["run.root"]
        validate_row(row, row, acknowledgement)

    def test_known_prefix_is_accepted_without_inventing_counters(self):
        self.check()

    def test_ordinary_missing_usage_is_not_excused(self):
        self.row["status"] = "missing_usage"
        with self.assertRaisesRegex(ValueError, "known whole-tree prefix"):
            self.check()

    def test_wrong_known_counter_is_rejected(self):
        self.row["output_tokens"] += 1
        with self.assertRaisesRegex(ValueError, "counters changed"):
            self.check()

    def test_changed_archived_evidence_is_rejected(self):
        self.archive.write_text("{}\n")
        with self.assertRaisesRegex(ValueError, "evidence changed"):
            self.check()

    def test_foreign_native_session_is_rejected(self):
        self.entry["thread_id"] = "foreign-session"
        self.save()
        with self.assertRaisesRegex(ValueError, "native session"):
            self.check()

    def test_incomplete_stop_proof_is_rejected(self):
        self.stop["collector_sealed"] = False
        self.save()
        with self.assertRaisesRegex(ValueError, "stopped-provider audit"):
            self.check()

    def test_expired_watchdog_cannot_be_recovered(self):
        self.final["watchdog_expired"] = True
        self.write(self.run / "manifest.json", self.final)
        self.stop["segment_manifest"] = self.ref(self.run / "manifest.json")
        self.save()
        with self.assertRaisesRegex(ValueError, "expired watchdog"):
            self.check()

    def test_partial_accounting_cannot_bypass_a_token_cap(self):
        self.task["budget_tokens"] = 100
        with self.assertRaisesRegex(ValueError, "capped run"):
            self.check()

    def test_later_worker_append_preserves_the_frozen_prefix(self):
        current = self.workspace / "provider-transcript.jsonl"
        current.write_bytes(self.archive.read_bytes() + b'{"type":"system","subtype":"init"}\n')
        self.row["transcript_path"] = str(current)
        self.check()

    def test_ignored_notification_can_extend_the_current_segment_digest(self):
        current = self.workspace / "provider-transcript.jsonl"
        current.write_bytes(self.archive.read_bytes() + b'{"type":"system","subtype":"init"}\n')
        self.row.update(transcript_path=str(current), transcript_segment_sha256="extended-segment-digest")
        self.check()

    def test_frozen_segment_digest_tampering_is_rejected(self):
        self.entry["transcript_segment_sha256"] = "foreign-digest"
        self.save()
        with self.assertRaisesRegex(ValueError, "frozen native segment"):
            self.check()


if __name__ == "__main__":
    unittest.main()
