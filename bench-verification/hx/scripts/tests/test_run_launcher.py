"""Exercise the real PowerShell launcher with synthetic preparation/collector CLIs.

No model, database, sandbox setup, or native harness service is started.
"""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import json

SOURCE = Path(__file__).resolve().parents[2]


@unittest.skipUnless(os.name == "nt" and shutil.which("powershell.exe"), "Windows PowerShell test")
class RunLauncherExitTests(unittest.TestCase):
    def test_resume_preserves_collector_exit_code_with_routine_stderr(self):
        for expected in (0, 23):
            with self.subTest(exit_code=expected), tempfile.TemporaryDirectory() as temporary:
                base = Path(temporary)
                harness, workspace = base / "h", base / "w"
                for path in (harness / "tools", harness / "scripts", workspace, base / "creds"):
                    path.mkdir(parents=True)
                shutil.copyfile(SOURCE / "tools/Invoke-WorkerMemoryRun.ps1", harness / "tools/Invoke-WorkerMemoryRun.ps1")
                (harness / "harness-config.json").write_text(json.dumps({
                    "root_workspace": str(workspace), "managed_coordination": "enabled"}))
                for name in ("check_windows_sandbox.py", "prepare_root_launch.py"):
                    (harness / "scripts" / name).write_text("raise SystemExit(0)\n")
                (harness / "scripts/collect_codex_usage.py").write_text(
                    "import sys\nassert sys.argv[1] == 'resume'\n"
                    "print('artifacts: synthetic launcher probe', file=sys.stderr)\n"
                    f"raise SystemExit({expected})\n")
                (base / "creds/MongoDB.txt").write_text("mongodb://unused.invalid/\n")
                (base / "creds/DeepInfra.txt").write_text("synthetic-unused-key\n")
                prompt = base / "prompt.md"
                prompt.write_text("Continue the synthetic test.\n")
                def quote(value):
                    return "'" + str(value).replace("'", "''") + "'"
                params = {
                    "RunId": "synthetic-continuation", "Task": "launcher-test", "Workspace": workspace,
                    "PromptFile": prompt, "PythonExecutable": sys.executable,
                    "CredentialRoot": base / "creds", "ResultsDir": base / "results",
                    "ResumeTaskFile": base / "task.json",
                }
                command = "$ErrorActionPreference = 'Stop'; & " + quote(harness / "tools/Invoke-WorkerMemoryRun.ps1") + " "
                command += " ".join(f"-{key} {quote(value)}" for key, value in params.items())
                command += " *> " + quote(base / "launcher.log") + "; exit $LASTEXITCODE"
                child = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
                                       capture_output=True, text=True, timeout=30)
                self.assertEqual(expected, child.returncode, child.stderr)
                raw = (base / "launcher.log").read_bytes()
                log = raw.decode("utf-16" if raw.startswith(b"\xff\xfe") else "utf-8-sig")
                self.assertIn("artifacts: synthetic launcher probe", log)


if __name__ == "__main__":
    unittest.main()
