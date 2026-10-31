"""Regression checks for safe reuse of a timed-out verifier transcript."""
import unittest
from pathlib import Path

from continue_biofabric_grade import COMPLETED, EXPECTED_COUNTS, SHIM, completed_prefix


def checkpoint():
    rows = []
    targets = ["unittests src/main.rs", "tests/cli_tests.rs", "unittests src/lib.rs", "tests/analysis_tests.rs"]
    for target, (passed, failed, ignored) in zip(targets, EXPECTED_COUNTS):
        rows += [f"     Running {target} (target/debug/deps/example)",
                 f"test result: {'FAILED' if failed else 'ok'}. {passed} passed; {failed} failed; {ignored} ignored; 0 measured; 0 filtered out; finished in 0.1s"]
    rows += ["     Running tests/hidden_tests.rs (target/debug/deps/hidden)", "running 20 tests", "test unfinished has been running for over 60 seconds"]
    return ("\n".join(rows) + "\n").encode()


class CheckpointTests(unittest.TestCase):
    def test_only_completed_targets_reused(self):
        prefix, receipts = completed_prefix(checkpoint())
        self.assertNotIn(b"hidden_tests.rs", prefix)
        self.assertEqual([r['target'] for r in receipts], COMPLETED)
        self.assertEqual(sum(r['passed'] for r in receipts), 92)
        self.assertEqual(sum(r['failed'] for r in receipts), 37)

    def test_unfinished_preceding_target_rejected(self):
        with self.assertRaises(ValueError):
            completed_prefix(checkpoint().replace(b"test result: ok. 63 passed; 0 failed; 0 ignored;", b"interrupted"))

    def test_duplicate_summary_rejected(self):
        with self.assertRaises(ValueError):
            completed_prefix(checkpoint().replace(b"running 20 tests", b"test result: ok. 20 passed; 0 failed; 0 ignored;"))

    def test_changed_counts_rejected(self):
        with self.assertRaises(ValueError):
            completed_prefix(checkpoint().replace(b"14 passed; 37 failed;", b"51 passed; 0 failed;"))

    def test_changed_target_inventory_rejected(self):
        with self.assertRaises(ValueError):
            completed_prefix(checkpoint().replace(b"tests/analysis_tests.rs", b"tests/other.rs"))

    def test_shim_compiles(self):
        compile(SHIM, "operator-cargo-shim", "exec")


if __name__ == '__main__':
    unittest.main()
