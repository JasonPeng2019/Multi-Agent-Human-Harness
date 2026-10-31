#!/usr/bin/env python3
"""One-command real-agent demo. Every run starts from a fresh buggy calculator."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tomllib

from orchestrator_harness.config import load_config
from orchestrator_harness.lanes import find_active_lane
from orchestrator_harness.records import RecordLock, atomic_write_json

ROOT = Path(__file__).resolve().parent
RUNS_DIR = ROOT.parent / "runtime" / "visualizer-demos"
TESTS = [f"orchestrator_harness.tests.{name}" for name in
         ("test_view", "test_view_artifacts", "test_view_feed", "test_view_review", "test_view_events", "test_view_replay", "test_visualizer_demo")]
BASE_FILES = {
    "calc.py": 'def average(values):\n    return sum(values) / (len(values) + 1)\n',
    "test_calc.py": 'import unittest\nfrom calc import average\n\nclass CalcTests(unittest.TestCase):\n    def test_average(self):\n        self.assertEqual(2, average([1, 2, 3]))\n',
    ".gitignore": '.harness-runtime/\n.harness-tasks/\n.demo/\n.codex/\n.claude/\n__pycache__/\n',
}
TASKS = {
    "fix-average": "Fix average() and add tests for single, negative and fractional inputs.",
    "add-median": "Add median(values): handle odd/even, unsorted, duplicate and negative values without modifying input; raise ValueError for an empty list. Add tests for all these cases. Also fix the inherited average divisor bug.",
}
AVERAGE_CHECK = '''from calc import average
for values, expected in [([1,2,3],2), ([7],7), ([-3,-1],-2), ([.5,1.5],1)]:
    assert average(values) == expected, (values, expected)
'''
MEDIAN_CHECK = '''from calc import median
for values, expected in [([3,1,2],2), ([4,1,3,2],2.5), ([2,2,1],2), ([2,2,1,1],1.5), ([-5,-1,-3],-3), ([7],7)]:
    original = values.copy()
    assert median(values) == expected, (values, expected)
    assert values == original, "median mutated input"
try:
    median([])
except ValueError:
    pass
else:
    raise AssertionError("empty input must raise ValueError")
'''


def run(argv: list[str], *, cwd: Path = ROOT, timeout: int = 120, stdout_only: bool = False) -> str:
    result = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"{argv[0]} failed ({result.returncode}):\n{result.stdout}\n{result.stderr}")
    return result.stdout if stdout_only else result.stdout + result.stderr


def operator(*args: str) -> dict:
    result = json.loads(run([sys.executable, "-m", "orchestrator_harness.operator_launch", "--json", *args], timeout=660, stdout_only=True))
    if not result.get("ok"):
        raise RuntimeError(f"{result.get('code')}: {result.get('summary')}")
    print(result.get("summary", ""), flush=True)
    return result


def guard_idle() -> None:
    config = load_config(ROOT)
    state = config.runtime_root / "RUNTIME_STATE.json"
    if state.exists() and json.loads(state.read_text()).get("state") != "CLOSED":
        raise RuntimeError("A harness runtime is already open. Finish it or run `python3 -m orchestrator_harness.operator_launch harness shutdown` from this script's directory before rerunning.")


def fresh_workspace(parent: Path) -> tuple[Path, str]:
    parent.mkdir(parents=True, exist_ok=True)
    workspace = Path(tempfile.mkdtemp(prefix="run-", dir=parent))
    for name, text in BASE_FILES.items():
        (workspace / name).write_text(text)
    run(["git", "init", "-q"], cwd=workspace)
    run(["git", "config", "user.name", "Harness Demo"], cwd=workspace)
    run(["git", "config", "user.email", "harness-demo@example.invalid"], cwd=workspace)
    run(["git", "config", "commit.gpgsign", "false"], cwd=workspace)
    run(["git", "add", *BASE_FILES], cwd=workspace)
    run(["git", "commit", "-qm", "Disposable calculator baseline"], cwd=workspace)
    return workspace, run(["git", "rev-parse", "HEAD"], cwd=workspace).strip()


def check_worker(worktree: Path, lane: str, base: str) -> str:
    changed = set(run(["git", "diff", "--name-only", base, "HEAD"], cwd=worktree).splitlines())
    if changed != {"calc.py", "test_calc.py"}:
        raise RuntimeError(f"Unexpected committed files for {lane}: {sorted(changed)}")
    output = run([sys.executable, "-m", "unittest", "-v"], cwd=worktree)
    check = AVERAGE_CHECK + (MEDIAN_CHECK if lane == "add-median" else "")
    output += run([sys.executable, "-c", check], cwd=worktree)
    run(["git", "diff", "--check", base, "HEAD"], cwd=worktree)
    return output + "\nIndependent demo assertions and diff check passed.\n"


def demo(model: str, parent: Path) -> None:
    if parent.resolve().is_relative_to(ROOT.resolve()):
        raise RuntimeError("--runs-dir must be outside the harness source directory.")
    guard_idle()
    run(["codex", "login", "status"])
    workspace, base = fresh_workspace(parent)
    rt, local = workspace / ".harness-runtime", ROOT / "local-config"
    evidence = workspace / ".demo"
    evidence.mkdir()
    local.mkdir(exist_ok=True)
    for name in ("harness-config.json", "resource-manifest.json"):
        source = local / name
        if source.exists():
            (evidence / ("previous-" + name)).write_bytes(source.read_bytes())
    atomic_write_json(local / "harness-config.json", {"root_workspace": str(workspace), "managed_coordination": "enabled", "visualizer": "auto"})
    atomic_write_json(local / "resource-manifest.json", {"schema": "resource-manifest/v1", "resources": []})
    print(f"\nFresh coding workspace: {workspace}\nLive Codex agents use your account.\n", flush=True)
    owned: list[str] = []
    try:
        operator("harness", "setup")
        for lane, task in TASKS.items():
            card = workspace / ".harness-tasks" / f"{lane}.json"
            atomic_write_json(card, {"schema": "project-task-card/v1", "task": task + " Run the complete unittest suite, commit implementation and tests, then write RESULT.json as instructed.",
                "acceptance_criteria": [task, "All tests pass; implementation and tests are committed."],
                "deliverables": ["calc.py", "test_calc.py", "RESULT.json"],
                "reason_for_acceptance_and_deliverables": "Executable checks demonstrate the requested calculator behavior.",
                "branch": f"lane/{lane}", "base_commit": base})
            owned.append(lane)
            operator("lane", "bootstrap", "--lane-id", lane, "--provider", "codex", "--model", model,
                     "--provider-option", "reasoning_effort=medium", "--provider-option", "service_tier=default", "--task-card", str(card))
        operator("scan", "--no-write")
        for lane in owned:
            operator("lane", "launch", "--lane-id", lane)
        print("\nWatch Terminal: Enter opens an agent; arrows switch sections; End follows output.\n", flush=True)
        for lane in owned:
            event = operator("watch", "--until-review-for", lane, "--timeout", "10m")
            if not event.get("event_id"):
                raise RuntimeError(f"{lane} stopped without a review event; inspect its Output panel.")
            _, record = find_active_lane(rt, lane)
            report = check_worker(Path(record["worktree_path"]), lane, base)
            report_path = evidence / f"{lane}-checks.txt"
            report_path.write_text(report)
            print(f"\n{lane}:\n{report}", flush=True)
            operator("manager", "acknowledge", "--event-id", event["event_id"])
            operator("lane", "completion-review", "--event-id", event["event_id"], "--review-outcome", "PASS", "--approval", "ACCEPTED",
                     "--review-summary", "Automated demo review: unittest suite, independent behavioral assertions, committed file scope and diff check passed. This is a fixed demo check, not a separate AI code review.",
                     "--evidence", str(report_path))
        operator("harness", "shutdown")  # Keeps worktrees/logs available in the viewer.
    except BaseException:
        print("\nDemo stopped. Preserving logs and cleaning up only this run's agents.", flush=True)
        for lane in owned:
            try:
                operator("lane", "force-stop", "--lane-id", lane)
            except Exception as exc:
                print(f"Cleanup for {lane}: {exc}", file=sys.stderr)
        try:
            operator("harness", "shutdown")
        except Exception as exc:
            print(f"Shutdown needs attention: {exc}", file=sys.stderr)
        raise
    print(f"\nDONE: both agents passed demo checks. Logs: {rt}\nRerun this script for a fresh reset.\nReopen the viewer: {sys.executable} -m orchestrator_harness.operator_launch view --runtime-root {str(rt)!r}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="run local tests only; no agents or workspace changes")
    parser.add_argument("--model", help="Codex model; defaults to your configured model")
    parser.add_argument("--runs-dir", type=Path, default=RUNS_DIR)
    args = parser.parse_args()
    try:
        print(run([sys.executable, "-m", "unittest", *TESTS]), flush=True)
        if not args.check_only:
            config = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "config.toml"
            model = args.model or (tomllib.loads(config.read_text()).get("model") if config.exists() else None)
            if not model:
                raise RuntimeError("Pass --model with a model available to your Codex account.")
            with RecordLock(ROOT / "local-config" / "visualizer-demo"):
                demo(model, args.runs_dir.expanduser().resolve())
        return 0
    except (Exception, KeyboardInterrupt) as exc:
        print(f"\nStopped: {exc or 'interrupted'}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
