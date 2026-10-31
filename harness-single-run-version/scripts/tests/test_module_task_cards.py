"""Module task cards reach fresh and resumed workers without changing review roles."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HARNESS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(HARNESS))
from orchestrator_harness import bootstrap, resume
from orchestrator_harness.core import content_hash


class ModuleTaskCardTests(unittest.TestCase):
    ONBOARDING = (
        "You are a harness worker, not ROOT. Perform your assigned task directly. "
        "ROOT’s planning and orchestration instructions do not apply to you. "
        "Request coordination through the manager notification helper."
    )

    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / ".agent-workspace").mkdir()
        self.card = {"schema": "project-task-card/v1", "task": "Implement frame parsing.",
                     "task_kind": "implementation", "module_path": ".plans/frame.md"}

    def read_with_both(self, card):
        path = self.root / "card.json"
        path.write_text(json.dumps(card), encoding="utf-8")
        return [reader(path) for reader in (bootstrap._read_task_card, resume._read_task_card)]

    def render(self, card, rationale=None):
        with (patch.object(bootstrap, "_render_always_on_memory_context", return_value=[]),
              patch.object(bootstrap, "_render_worker_memory_context", return_value=[]),
              patch.object(bootstrap, "_render_memory_context", return_value=[]),
              patch.object(bootstrap, "append_current_detail")):
            return bootstrap._write_worker_prompt(
                self.root, card, managed=False, rationale=rationale).read_text(encoding="utf-8")

    def test_initial_and_resume_preserve_hashed_card_and_use_exact_prefix(self):
        self.card["content_hash"] = content_hash(self.card)
        expected = ("Make an implementation plan for the following task according to the "
                    "requirements of the module at .plans/frame.md, and execute the plan. "
                    "The task is as follows: Implement frame parsing.")
        for card, rationale in zip(self.read_with_both(self.card), (None, "Repair the failing frame check.")):
            with self.subTest(rationale=rationale):
                self.assertEqual(self.card, card)
                self.assertEqual(content_hash(card), card["content_hash"])
                prompt = self.render(card, rationale)
                self.assertTrue(prompt.startswith(self.ONBOARDING + "\n\n" + expected))
                self.assertEqual(1, prompt.count("Make an implementation plan"))
                if rationale:
                    self.assertIn("## Resume rationale\n" + rationale, prompt)
        self.assertIs(resume._write_worker_prompt, bootstrap._write_worker_prompt)

    def test_reviewers_and_validators_keep_module_context_without_implementation(self):
        for kind in ("review", "validation"):
            card = dict(self.card, task_kind=kind, module_path="PLAN.md", task="Check the integrated revision.")
            for read in self.read_with_both(card):
                prompt = self.render(read)
                self.assertEqual(self.ONBOARDING + "\n\nModule: PLAN.md\n\nCheck the integrated revision.\n", prompt)
                self.assertNotIn("execute the plan", prompt)

    def test_malformed_module_cards_rejected_by_both_readers(self):
        cards = [dict(self.card, module_path=value) for value in (None, "", "  ", 7)]
        cards += [dict(self.card, task_kind=value) for value in (None, "repair", 7)]
        for card in cards:
            path = self.root / "bad-card.json"
            path.write_text(json.dumps(card), encoding="utf-8")
            for reader, error in ((bootstrap._read_task_card, bootstrap.BootstrapError),
                                  (resume._read_task_card, ValueError)):
                with self.subTest(card=card, reader=reader.__module__):
                    with self.assertRaises(error):
                        reader(path)

    def test_legacy_task_cards_retain_assignment_after_onboarding(self):
        card = {"schema": "project-task-card/v1", "task": "  Original assignment.  "}
        for read in self.read_with_both(card):
            self.assertEqual(self.ONBOARDING + "\n\nOriginal assignment.\n", self.render(read))


if __name__ == "__main__":
    unittest.main()
