from __future__ import annotations

import unittest
from unittest.mock import call, patch

import run_memory_harness_demo as demo


class DemoRuntimeRecoveryTests(unittest.TestCase):
    def test_interrupted_shutdown_is_finished_before_setup(self) -> None:
        with (
            patch.object(
                demo,
                "_runtime_state_name",
                side_effect=["SHUTTING_DOWN", "OPEN"],
            ),
            patch.object(demo, "_reset_prior_demo_lanes") as reset_lanes,
            patch.object(demo, "_operator") as operator,
        ):
            demo._ensure_runtime_open()

        reset_lanes.assert_called_once_with()
        self.assertEqual(
            [
                call(
                    "harness",
                    "shutdown",
                    label="finish interrupted harness shutdown",
                    timeout=180,
                ),
                call("harness", "setup", label="harness setup", timeout=60),
            ],
            operator.call_args_list,
        )

    def test_setup_postcondition_must_be_open(self) -> None:
        with (
            patch.object(
                demo,
                "_runtime_state_name",
                side_effect=["CLOSED", "SHUTTING_DOWN"],
            ),
            patch.object(demo, "_operator"),
        ):
            with self.assertRaisesRegex(demo.RunFailed, "did not leave the runtime OPEN"):
                demo._ensure_runtime_open()


if __name__ == "__main__":
    unittest.main()
