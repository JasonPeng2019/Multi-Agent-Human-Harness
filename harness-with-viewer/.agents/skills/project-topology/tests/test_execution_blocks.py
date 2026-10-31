"""Portable behavior checks; no hardware, network, or application processes."""

import importlib.util
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "execution_blocks",
    Path(__file__).resolve().parents[1] / "scripts/execution_blocks.py",
)
blocks = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(blocks)


def profile():
    return {
        "version": 1,
        "inputs": ["source", "runner", "target"],
        "environment": {"APP_DATA": "state", "TMP": "tmp"},
        "resources": [
            {
                "id": "authority",
                "owner": "operator",
                "consumers": ["live"],
                "kind": "attestation",
                "status": "BLOCKED",
                "evidence": "approval absent",
            }
        ],
        "checks": [
            {"id": "unit", "inputs": ["source"], "prerequisites": []},
            {"id": "rehearsal", "inputs": ["runner"], "prerequisites": ["unit"]},
            {"id": "live", "inputs": ["target"], "prerequisites": ["rehearsal"]},
        ],
    }


class ExecutionBlocksTests(unittest.TestCase):
    def test_link_detection_rejects_windows_reparse_points_without_path_is_junction(
        self,
    ):
        with patch.object(
            Path,
            "lstat",
            return_value=SimpleNamespace(st_mode=0, st_file_attributes=1024),
        ):
            self.assertTrue(blocks.is_link(Path("junction")))

    def test_cli_syntax_error_returns_one_and_help_returns_zero(self):
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(blocks.main(["ready"]), 1)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(blocks.main(["--help"]), 0)

    def test_affected_checks_include_transitive_consumers(self):
        selected = blocks.select_checks(
            profile(), ["runner"], ["unit", "rehearsal", "live"]
        )
        self.assertEqual(selected["run"], ["rehearsal", "live"])
        self.assertEqual(selected["retain"], ["unit"])

    def test_unknown_input_invalidates_all_credit(self):
        selected = blocks.select_checks(
            profile(), ["not-mapped"], ["unit", "rehearsal", "live"]
        )
        self.assertEqual(selected["run"], ["unit", "rehearsal", "live"])

    def test_uncredited_check_and_its_consumers_run(self):
        selected = blocks.select_checks(profile(), [], ["unit", "live"])
        self.assertEqual(selected["run"], ["rehearsal", "live"])

    def test_unknown_credit_is_rejected(self):
        with self.assertRaises(ValueError):
            blocks.select_checks(profile(), [], ["typo"])

    def test_cycle_missing_input_and_duplicate_id_rejected(self):
        for mutate in (
            lambda p: p["checks"][0]["prerequisites"].append("live"),
            lambda p: p["checks"][0]["inputs"].append("missing"),
            lambda p: p["checks"].append(dict(p["checks"][0])),
        ):
            p = profile()
            mutate(p)
            with self.subTest(p=p), self.assertRaises(ValueError):
                blocks.validate_profile(p)

    def test_typo_in_environment_field_rejected(self):
        p = profile()
        p["enviroment"] = p.pop("environment")
        with self.assertRaises(ValueError):
            blocks.validate_profile(p)

    def test_external_block_does_not_block_unit_checks(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(
                blocks.readiness(profile(), Path(directory), "unit")["status"], "READY"
            )
            self.assertEqual(
                blocks.readiness(profile(), Path(directory), "live")["status"],
                "BLOCKED",
            )

    def test_prerequisite_resource_block_reaches_consumer(self):
        p = profile()
        p["resources"][0]["consumers"] = ["unit"]
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(
                blocks.readiness(p, Path(directory), "live")["status"], "BLOCKED"
            )

    def test_file_readiness_checks_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pack").write_bytes(b"verified artifact")
            p = profile()
            p["resources"] = [
                {
                    "id": "pack",
                    "owner": "root",
                    "consumers": ["live"],
                    "kind": "file",
                    "path": "pack",
                    "sha256": "0" * 64,
                }
            ]
            self.assertEqual(blocks.readiness(p, root, "live")["status"], "BLOCKED")
            p["resources"][0]["sha256"] = blocks.digest(root / "pack")
            self.assertEqual(blocks.readiness(p, root, "live")["status"], "READY")

    def test_ready_attestation_requires_existing_receipt(self):
        p = profile()
        p["resources"][0].update(status="READY", evidence="missing.json")
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(
                blocks.readiness(p, Path(directory), "live")["status"], "BLOCKED"
            )

    def test_environment_cannot_escape_run_root(self):
        p = profile()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            patch = blocks.environment(p, root)
            self.assertEqual(Path(patch["APP_DATA"]), root / "state")
            self.assertFalse((root / "state").exists())
            for value in ("../escape", str(root.parent), "."):
                p["environment"]["APP_DATA"] = value
                with self.subTest(value=value), self.assertRaises(ValueError):
                    blocks.environment(p, root)

    def test_snapshot_detects_add_delete_and_same_size_edit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "edit").write_text("one")
            (root / "delete").write_text("old")
            before = blocks.snapshot([root])
            (root / "edit").write_text("two")
            (root / "delete").unlink()
            (root / "add").write_text("new")
            comparison = blocks.compare(before, blocks.snapshot([root]))
            self.assertEqual(comparison["status"], "CHANGED")
            self.assertEqual(len(comparison["changed"]), 3)

    def test_snapshot_missing_root_and_mismatched_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            absent = Path(directory) / "absent"
            before = blocks.snapshot([absent])
            absent.mkdir()
            self.assertEqual(
                blocks.compare(before, blocks.snapshot([absent]))["status"], "CHANGED"
            )
            with self.assertRaises(ValueError):
                blocks.compare(before, blocks.snapshot([Path(directory)]))

    def test_record_preserves_failure_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / "check.txt"
            evidence.write_text("check failed")
            record = blocks.make_record("smoke", "FAIL", 2.5, [str(evidence)], "exit 1")
            target = root / "record.json"
            blocks.emit(record, target)
            self.assertEqual(json.loads(target.read_text())["status"], "FAIL")
            with self.assertRaises(FileExistsError):
                blocks.emit(record, target)
            with self.assertRaises(ValueError):
                blocks.make_record("smoke", "PASS", -1, [], "invalid")

    def test_pass_record_requires_evidence(self):
        with self.assertRaises(ValueError):
            blocks.make_record("smoke", "PASS", 1, [], "claimed success")

    def test_cli_record_blocked_publishes_successfully(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "result.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(Path(blocks.__file__)),
                    "record",
                    "--claim",
                    "live",
                    "--status",
                    "BLOCKED",
                    "--elapsed-seconds",
                    "0",
                    "--note",
                    "fixture approval pending",
                    "--output",
                    str(target),
                ],
                capture_output=True,
                text=True,
            )
            self.assertTrue(target.is_file())
            self.assertEqual(json.loads(target.read_text(encoding="utf-8"))["status"], "BLOCKED")
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_cli_compare_exit_matches_footprint_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            watched = root / "watched"
            watched.mkdir()
            before = root / "before.json"
            blocks.emit(blocks.snapshot([watched]), before)
            for changed in (False, True):
                with self.subTest(changed=changed):
                    if changed:
                        (watched / "new.txt").write_text("new", encoding="utf-8")
                    after = root / f"after-{changed}.json"
                    blocks.emit(blocks.snapshot([watched]), after)
                    result = subprocess.run(
                        [sys.executable, "-B", str(Path(blocks.__file__)),
                         "compare", str(before), str(after)],
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(result.returncode, 2 if changed else 0, result.stderr)
                    self.assertEqual(
                        json.loads(result.stdout)["status"],
                        "CHANGED" if changed else "UNCHANGED",
                    )

    def test_cli_compare_returns_two_only_for_changed_footprint(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            watched = root / "watched"
            before = root / "before.json"
            after = root / "after.json"
            blocks.emit(blocks.snapshot([watched]), before)
            watched.mkdir()
            blocks.emit(blocks.snapshot([watched]), after)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(blocks.main(["compare", str(before), str(before)]), 0)
                self.assertEqual(blocks.main(["compare", str(before), str(after)]), 2)

    def test_cli_readiness_exit_is_blocked_and_validation_does_not_claim_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "profile.json"
            target.write_text(json.dumps(profile()), encoding="utf-8")
            prefix = [sys.executable, "-B", str(Path(blocks.__file__))]
            valid = subprocess.run(
                [*prefix, "validate", str(target)], capture_output=True, text=True
            )
            self.assertEqual(valid.returncode, 0, valid.stderr)
            self.assertEqual(json.loads(valid.stdout)["status"], "VALID")
            blocked = subprocess.run(
                [
                    *prefix,
                    "ready",
                    str(target),
                    "--root",
                    directory,
                    "--consumer",
                    "live",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(blocked.returncode, 2, blocked.stderr)
            self.assertEqual(json.loads(blocked.stdout)["status"], "BLOCKED")

    def test_cli_malformed_profile_fails_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "invalid.json"
            target.write_text('{"version": 1}', encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(Path(blocks.__file__)),
                    "validate",
                    str(target),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing fields", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_snapshot_compare_rejects_empty_claimed_success(self):
        with self.assertRaises(ValueError):
            blocks.compare(
                {"version": 1, "kind": "footprint", "roots": [], "entries": {}},
                {"version": 1, "kind": "footprint", "roots": [], "entries": {}},
            )


if __name__ == "__main__":
    unittest.main()
