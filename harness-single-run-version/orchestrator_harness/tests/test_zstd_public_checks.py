"""Benchmark policy regressions for the reviewed v2 worker feedback route."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from orchestrator_harness import public_checks as service
from orchestrator_harness.records import atomic_write_json
from orchestrator_harness.tests import test_public_checks as general

SOURCE = Path(__file__).resolve().parents[2]


class ZstdPublicCheckPolicyTests(unittest.TestCase):
    def setUp(self):
        # Reuse the general route fixture without inheriting/repeating its tests.
        self.fixture = general.PublicCheckTests(methodName="runTest")
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.policy = json.loads((SOURCE / service.POLICY).read_text(encoding="utf-8"))
        root = self.fixture.root
        (root / "test_artifacts").mkdir()
        (root / "test_artifacts/visible.zst").write_bytes(b"public fixture")
        for name in ("rfc8878.txt", "test.sh", "timer.sh", "src/Makefile", "src/harness.c"):
            (root / name).write_text("fixed task fixture\n", encoding="utf-8")
        (root / "src/zstd_decompress.c").write_text("editable decoder\n", encoding="utf-8")
        self.fixture.git(root, "add", ".")
        self.fixture.git(root, "commit", "-qm", "ZSTD policy fixture")
        revision = self.fixture.git(root, "rev-parse", "HEAD")
        self.fixture.git(self.fixture.lane, "merge", "--ff-only", revision)
        self.fixture.revision = revision
        self.fixture.config["policy"] = self.policy
        self.fixture.config["fixed_inputs"] = service._file_digests(root, revision, self.policy["fixed_paths"])
        self.fixture.route.update({"input_paths": self.policy["input_paths"] + self.policy["optional_input_paths"],
                                   "allow_focused": self.policy["allow_focused"]})
        atomic_write_json(self.fixture.agent / "public-check-route.json", self.fixture.route)

    def commit(self, name, text):
        (self.fixture.lane / name).write_text(text, encoding="utf-8")
        self.fixture.git(self.fixture.lane, "add", name)
        self.fixture.git(self.fixture.lane, "commit", "-qm", "policy test change")

    def test_active_policy_matches_pinned_external_zstd_configuration(self):
        expected = json.loads((SOURCE / "task-tools/public-check-policy.v2.json").read_text(encoding="utf-8"))
        self.assertEqual(expected, self.policy)
        self.assertEqual("public-check-policy/v2", self.policy["schema"])
        adapter = Path(self.policy["adapter"]["path"])
        self.assertEqual((SOURCE / "task-tools/zstd_check_adapter.py").resolve(), adapter.resolve())
        self.assertEqual(hashlib.sha256(adapter.read_bytes()).hexdigest(), self.policy["adapter"]["sha256"])
        self.assertEqual(["make", "-C", "/app/src"], self.policy["commands"]["build"])
        self.assertEqual({"test_artifacts", "rfc8878.txt", "test.sh", "timer.sh", "src/Makefile"},
                         set(self.policy["fixed_paths"]))

    def test_committed_cli_change_is_checked_at_its_exact_revision(self):
        self.commit("src/harness.c", "allowed CLI repair\n")
        execute = Mock(return_value={"exit_code": 0, "stdout": "build passed\n",
                                     "stderr": "", "cleanup_proven": True})
        request = self.fixture.submit("build")
        result = self.fixture.serve(request, execute)
        feedback, code = general.client.wait(self.fixture.agent, request.parent.name, 0)
        self.assertEqual("PASS", result["status"])
        self.assertEqual(0, code)
        self.assertEqual(self.fixture.git(self.fixture.lane, "rev-parse", "HEAD"), feedback["revision"])
        execute.assert_called_once()

    def test_fixed_zstd_makefile_is_rejected_before_backend_execution(self):
        self.commit("src/Makefile", "replacement build\n")
        execute = Mock()
        result = self.fixture.serve(self.fixture.submit("build"), execute)
        self.assertEqual("ERROR", result["status"])
        self.assertIn("fixed public check inputs changed", result["error"])
        execute.assert_not_called()

    def test_fixed_public_artifact_is_rejected_before_backend_execution(self):
        self.commit("test_artifacts/visible.zst", "replacement artifact\n")
        execute = Mock()
        result = self.fixture.serve(self.fixture.submit(), execute)
        self.assertEqual("ERROR", result["status"])
        self.assertIn("fixed public check inputs changed", result["error"])
        execute.assert_not_called()

    def test_decoder_repair_gets_completed_failure_feedback_including_raw_75(self):
        self.commit("src/zstd_decompress.c", "committed decoder repair\n")
        request = self.fixture.submit()
        execute = Mock(return_value={"exit_code": 75, "stdout": "PASS visible\nFAIL edge\n",
                                     "stderr": "compiler diagnostic\n", "cleanup_proven": True})
        result = self.fixture.serve(request, execute)
        feedback, code = general.client.wait(self.fixture.agent, request.parent.name, 0)
        self.assertEqual("FAIL", result["status"])
        self.assertEqual(75, feedback["exit_code"])
        self.assertEqual(2, code)
        self.assertEqual(self.fixture.git(self.fixture.lane, "rev-parse", "HEAD"), feedback["revision"])
        self.assertEqual("compiler diagnostic\n", feedback["stderr"])
        self.assertEqual("PASS visible\nFAIL edge\n", feedback["stdout"])
        execute.assert_called_once()

    def test_uncommitted_decoder_is_not_submitted(self):
        (self.fixture.lane / "src/zstd_decompress.c").write_text("uncommitted decoder", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "commit the configured"):
            self.fixture.submit()

    def test_snapshot_includes_committed_scratch_and_excludes_other_files(self):
        (self.fixture.lane / "scratch").mkdir()
        self.commit("scratch/focused.c", "focused task check\n")
        self.commit("private.txt", "unselected synthetic data\n")
        revision = self.fixture.git(self.fixture.lane, "rev-parse", "HEAD")
        with tempfile.TemporaryDirectory() as temporary:
            snapshot = Path(temporary)
            service.snapshot(self.fixture.lane, revision, snapshot, self.policy)
            self.assertTrue((snapshot / "src/zstd_decompress.c").is_file())
            self.assertTrue((snapshot / "scratch/focused.c").is_file())
            self.assertTrue((snapshot / "test_artifacts/visible.zst").is_file())
            self.assertFalse((snapshot / "private.txt").exists())
            self.assertFalse((snapshot / ".agent-workspace").exists())
            self.assertFalse((snapshot / "tests").exists())


if __name__ == "__main__":
    unittest.main()
