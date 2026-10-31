"""Portability checks against actual temporary document files."""

import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "workspace_validator", Path(__file__).resolve().parents[1] / "validate-workspace.py"
)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class PortabilityTests(unittest.TestCase):
    def scan(self, content):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "guidance.md").write_text(content, encoding="utf-8")
            with patch.object(validator, "ROOT", root), patch.object(validator, "ERRORS", []):
                validator.validate_portability()
                return list(validator.ERRORS)

    def test_resource_class_phrase_is_portable(self):
        self.assertEqual(self.scan("Apply the relevant provider/home/service quota."), [])

    def test_absolute_user_paths_are_still_rejected(self):
        paths = [
            "/".join(["", "home", "alice", "project"]),
            "/".join(["", "Users", "alice", "project"]),
            "\\".join(["C:", "Users", "alice", "project"]),
        ]
        for path in paths:
            for content in (path, "See `" + path + "`.", "file://" + path):
                with self.subTest(content=content):
                    errors = self.scan(content)
                    self.assertEqual(len(errors), 1)
                    self.assertIn("user-specific absolute path", errors[0])


class VendoredDependencyTests(unittest.TestCase):
    def test_installed_vendor_environment_is_excluded_from_hygiene_and_portability(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            vendor_env = root / "harness" / "vendor" / "example" / ".venv"
            vendor_env.mkdir(parents=True)
            (vendor_env / "machine-specific.py").write_text(
                "path = r'C:\\Users\\alice\\project'", encoding="utf-8"
            )
            app_cache = root / "app" / "__pycache__"
            app_cache.mkdir(parents=True)

            with patch.object(validator, "ROOT", root), patch.object(validator, "ERRORS", []):
                validator.validate_artifact_hygiene()
                validator.validate_portability()
                errors = list(validator.ERRORS)

        self.assertEqual(errors, ["generated artifact directory is present: app\\__pycache__"])


if __name__ == "__main__":
    unittest.main()
