#!/usr/bin/env python3
"""Run the complete memory-backed harness demo from one Python command.

Usage:
    python3 run_memory_harness_demo.py

The script starts the harness (which opens the configured visualizer), begins
at Recall, creates a fresh lane and Git branch, injects the demo EverOS and
Atlas memories, launches a worker, waits for its result, launches a separate
review agent, records that agent's verdict, retires the lane, and shuts the
harness down. Every
invocation force-stops and retires any earlier ``fix-average-memory-*`` demo
lane first, so even paused or partially completed work is reset.

The script pauses at Recall until the operator types ``LAUNCH``. No provider
process starts before that signal.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Sequence

from orchestrator_harness.core import iso_utc
from orchestrator_harness.records import atomic_write_json


HARNESS_ROOT = Path(__file__).resolve().parent
SHARED_WORKSPACE = HARNESS_ROOT.parents[2]
DEFAULT_TASK_CARD = (
    SHARED_WORKSPACE / "test" / ".harness-tasks" / "fix-average.json"
)
OPERATOR_MODULE = "orchestrator_harness.operator_launch"
MEMORY_DEMO_MODULE = "orchestrator_harness.tests.memory_demo"
DEMO_PROGRESS_SCHEMA = "harness-demo-progress/v1"
REVIEW_AGENT_SCHEMA = "harness-review-agent/v1"
REVIEW_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "review_outcome": {"type": "string", "enum": ["PASS", "FAIL", "BLOCKED"]},
        "summary": {"type": "string", "minLength": 1, "maxLength": 1200},
        "evidence": {
            "type": "array",
            "maxItems": 10,
            "items": {"type": "string", "minLength": 1, "maxLength": 500},
        },
    },
    "required": ["review_outcome", "summary", "evidence"],
    "additionalProperties": False,
}


class RunFailed(RuntimeError):
    """A command or harness contract failed."""


def _show_command(argv: Sequence[str]) -> None:
    rendered = " ".join(json.dumps(part) if " " in part else part for part in argv)
    print(f"\n$ {rendered}", flush=True)


def _run(
    argv: Sequence[str],
    *,
    cwd: Path = HARNESS_ROOT,
    timeout: float | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    _show_command(argv)
    completed = subprocess.run(
        list(argv),
        cwd=cwd,
        text=True,
        input=input_text,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    if completed.stdout:
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
    if completed.stderr:
        print(
            completed.stderr,
            end="" if completed.stderr.endswith("\n") else "\n",
            file=sys.stderr,
        )
    return completed


def _runtime_root() -> Path:
    config = json.loads((HARNESS_ROOT / "harness-config.json").read_text(encoding="utf-8"))
    workspace = config.get("root_workspace")
    if not isinstance(workspace, str) or not workspace:
        raise RunFailed("harness-config.json has no root_workspace")
    return Path(workspace) / ".harness-runtime"


def _runtime_state_name() -> str | None:
    path = _runtime_root() / "RUNTIME_STATE.json"
    if not path.is_file():
        return None
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    state = record.get("state")
    return state if isinstance(state, str) else None


def _ensure_runtime_open() -> None:
    """Finish an interrupted shutdown, run setup, and verify its postcondition."""

    if _runtime_state_name() == "SHUTTING_DOWN":
        # An interrupted shutdown may still own a prepared or partially run
        # demo lane. Retire only this script's lanes before asking shutdown to
        # prove the runtime clean; unrelated lanes remain protected.
        _reset_prior_demo_lanes()
        _operator(
            "harness",
            "shutdown",
            label="finish interrupted harness shutdown",
            timeout=180,
        )
    _operator("harness", "setup", label="harness setup", timeout=60)
    state = _runtime_state_name()
    if state != "OPEN":
        raise RunFailed(
            "harness setup did not leave the runtime OPEN "
            f"(RUNTIME_STATE.json reports {state!r})"
        )


def _write_demo_progress(
    *, lane_id: str, task: str, phase: str, state: str
) -> Path:
    path = _runtime_root() / "DEMO_PROGRESS.json"
    atomic_write_json(
        path,
        {
            "schema": DEMO_PROGRESS_SCHEMA,
            "lane_id": lane_id,
            "task": task,
            "provider": "claude-code",
            "model": "sonnet",
            "phase": phase,
            "state": state,
            "started_at": iso_utc(),
            "updated_at": iso_utc(),
        },
    )
    return path


def _clear_demo_progress() -> None:
    (_runtime_root() / "DEMO_PROGRESS.json").unlink(missing_ok=True)


def _json_result(
    argv: Sequence[str],
    *,
    label: str,
    timeout: float | None = None,
    allowed_failure_codes: frozenset[str] = frozenset(),
) -> dict[str, Any]:
    completed = _run(argv, timeout=timeout)
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RunFailed(f"{label} returned non-JSON output") from exc
    if result.get("code") in allowed_failure_codes:
        return result
    if completed.returncode != 0 or result.get("ok") is not True:
        code = result.get("code", f"exit {completed.returncode}")
        summary = result.get("summary", "unknown failure")
        raise RunFailed(f"{label} failed: {code}: {summary}")
    return result


def _operator(
    *arguments: str,
    label: str,
    timeout: float | None = None,
    allowed_failure_codes: frozenset[str] = frozenset(),
) -> dict[str, Any]:
    return _json_result(
        [sys.executable, "-m", OPERATOR_MODULE, "--json", *arguments],
        label=label,
        timeout=timeout,
        allowed_failure_codes=allowed_failure_codes,
    )


def _reset_prior_demo_lanes() -> bool:
    """Discard every prior demo lane so this invocation starts from zero."""

    scan = _operator(
        "scan",
        "--no-write",
        label="initial lane scan",
        allowed_failure_codes=frozenset({"SCAN_NO_ACTIVE_EPOCH"}),
    )
    if scan.get("code") == "SCAN_NO_ACTIVE_EPOCH":
        return False
    lanes = scan.get("snapshot", {}).get("lanes", [])
    if not lanes:
        return False

    non_demo = [
        lane for lane in lanes
        if not str(lane.get("lane_id", "")).startswith("fix-average-memory-")
    ]
    if non_demo:
        names = ", ".join(str(lane.get("lane_id", "unknown")) for lane in non_demo)
        raise RunFailed(
            "the active epoch contains non-demo lanes that were preserved: " f"{names}"
        )

    for summary in lanes:
        lane_id = str(summary["lane_id"])
        _operator(
            "lane",
            "force-stop",
            "--lane-id",
            lane_id,
            label=f"reset prior demo lane {lane_id}",
            timeout=60,
        )
    return True


def _find_evidence(result: dict[str, Any], filename: str) -> Path:
    for value in result.get("evidence_paths", []):
        path = Path(value)
        if path.name == filename:
            return path
    raise RunFailed(f"harness result did not publish {filename}")


def _diagnose(lane_id: str | None) -> None:
    print("\nThe run stopped before acceptance. Durable evidence was preserved.", file=sys.stderr)
    _run(
        [sys.executable, "-m", OPERATOR_MODULE, "--json", "scan", "--no-write"],
        timeout=30,
    )
    if lane_id:
        print(
            "To stop only this lane, run:\n"
            f"  {sys.executable} -m {OPERATOR_MODULE} lane force-stop --lane-id {lane_id}",
            file=sys.stderr,
        )


def _await_launch_signal(lane_id: str) -> None:
    print(
        "\nThe fresh run is reset and waiting at Recall; no agent is running yet.\n"
        f"Lane: {lane_id}\n"
        "After LAUNCH, the visualizer will advance through Recall, Vet, Plan, "
        "Pack, Work, agent Review, and Learn.",
        flush=True,
    )
    while True:
        try:
            signal = input("\nType LAUNCH and press Return to start the agent: ").strip()
        except EOFError as exc:
            raise RunFailed(
                "launch signal requires an interactive terminal; the prepared lane was preserved"
            ) from exc
        if signal.upper() == "LAUNCH":
            return
        print("Agent remains paused. Type exactly LAUNCH when you are ready.", flush=True)


def _write_review_agent_status(
    worktree: Path,
    *,
    state: str,
    verdict: dict[str, Any] | None = None,
    error: str | None = None,
) -> Path:
    path = worktree / ".agent-workspace" / "review-agent.json"
    record: dict[str, Any] = {
        "schema": REVIEW_AGENT_SCHEMA,
        "state": state,
        "provider": "claude-code",
        "model": "sonnet",
        "updated_at": iso_utc(),
    }
    if verdict is not None:
        record["verdict"] = verdict
    if error is not None:
        record["error"] = error
    atomic_write_json(path, record)
    return path


def _review_prompt(worktree: Path) -> str:
    return f"""You are the independent completion-review agent for a coding lane.

Review the implementation in this Git worktree: {worktree}

Independently inspect `.agent-workspace/task-card.json`, `RESULT.json`, the Git
diff and commit, and all relevant source and tests. Run the appropriate tests
yourself. Do not edit, create, delete, commit, or reformat any file.

Return PASS only when the requested change is correct, minimal, committed, the
tests pass, and RESULT.json accurately reports the work. Return FAIL for an
incorrect or inadequately tested result, and BLOCKED only when review cannot be
completed. Your structured response must contain the factual outcome, a concise
summary, and concrete evidence such as commands and results.
"""


def _extract_review_verdict(output: str) -> dict[str, Any]:
    try:
        outer = json.loads(output)
    except json.JSONDecodeError as exc:
        raise RunFailed("review agent returned non-JSON output") from exc
    candidate: Any = outer.get("structured_output") if isinstance(outer, dict) else None
    if candidate is None and isinstance(outer, dict):
        candidate = outer.get("result")
    if isinstance(candidate, str):
        try:
            candidate = json.loads(candidate)
        except json.JSONDecodeError as exc:
            raise RunFailed("review agent did not return its structured verdict") from exc
    if not isinstance(candidate, dict):
        raise RunFailed("review agent response has no structured verdict")
    outcome = candidate.get("review_outcome")
    summary = candidate.get("summary")
    evidence = candidate.get("evidence")
    if outcome not in {"PASS", "FAIL", "BLOCKED"}:
        raise RunFailed(f"review agent returned an invalid outcome: {outcome!r}")
    if not isinstance(summary, str) or not summary.strip():
        raise RunFailed("review agent returned an empty summary")
    if not isinstance(evidence, list) or not all(
        isinstance(item, str) and item.strip() for item in evidence
    ):
        raise RunFailed("review agent returned invalid evidence")
    return {
        "review_outcome": outcome,
        "summary": summary.strip(),
        "evidence": [item.strip() for item in evidence[:10]],
    }


def _run_review_agent(worktree: Path) -> dict[str, Any]:
    _write_review_agent_status(worktree, state="running")
    argv = [
        "claude",
        "--print",
        "--output-format",
        "json",
        "--json-schema",
        json.dumps(REVIEW_OUTPUT_SCHEMA, separators=(",", ":")),
        "--model",
        "sonnet",
        "--effort",
        "low",
        "--permission-mode",
        "bypassPermissions",
        "--allowedTools",
        "Read,Grep,Glob,Bash",
        "--no-session-persistence",
        "--disable-slash-commands",
    ]
    completed = _run(
        argv,
        cwd=worktree,
        timeout=300,
        input_text=_review_prompt(worktree),
    )
    if completed.returncode != 0:
        error = f"Claude reviewer exited {completed.returncode}"
        _write_review_agent_status(worktree, state="failed", error=error)
        raise RunFailed(error)
    try:
        verdict = _extract_review_verdict(completed.stdout)
    except RunFailed as exc:
        _write_review_agent_status(worktree, state="failed", error=str(exc))
        raise
    _write_review_agent_status(worktree, state="complete", verdict=verdict)
    return verdict


def run_demo(*, task_card_path: Path, watch_timeout: str) -> None:
    if shutil.which("claude") is None:
        raise RunFailed("Claude Code is not installed or is not on PATH")
    if not task_card_path.is_file():
        raise RunFailed(f"task card does not exist: {task_card_path}")

    auth = _run(["claude", "auth", "status"], timeout=30)
    if auth.returncode != 0:
        raise RunFailed("Claude Code is not logged in; run `claude auth login`")

    _ensure_runtime_open()
    if _reset_prior_demo_lanes():
        _operator("harness", "shutdown", label="close prior epoch", timeout=60)
        _ensure_runtime_open()

    stamp = datetime.now().strftime("%Y%m%d%H%M%S")
    lane_id = f"fix-average-memory-{stamp}-{uuid.uuid4().hex[:6]}"
    branch = f"lane/{lane_id}"

    try:
        with tempfile.TemporaryDirectory(prefix="memory-harness-demo-") as temporary:
            plain_card = json.loads(task_card_path.read_text(encoding="utf-8"))
            plain_card["branch"] = branch
            generated_card = Path(temporary) / f"{lane_id}.json"
            generated_card.write_text(
                json.dumps(plain_card, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            task_value = plain_card.get("task", "Memory-backed demo")
            task_text = (
                task_value
                if isinstance(task_value, str)
                else json.dumps(task_value, sort_keys=True)
            )
            progress_path = _write_demo_progress(
                lane_id=lane_id,
                task=task_text,
                phase="Recall",
                state="waiting",
            )
            _await_launch_signal(lane_id)
            _write_demo_progress(
                lane_id=lane_id,
                task=task_text,
                phase="Recall",
                state="running",
            )

            bootstrap = _json_result(
                [
                    sys.executable,
                    "-m",
                    MEMORY_DEMO_MODULE,
                    "--lane-id",
                    lane_id,
                    "--task-card",
                    str(generated_card),
                    "--provider",
                    "claude-code",
                    "--model",
                    "sonnet",
                    "--effort",
                    "low",
                    "--progress-file",
                    str(progress_path),
                ],
                label="memory-backed lane bootstrap",
                timeout=120,
            )
            evidence = [Path(value) for value in bootstrap.get("evidence_paths", [])]
            worktree = next((path for path in evidence if path.name == lane_id), None)
            if worktree is None or not worktree.is_dir():
                raise RunFailed("bootstrap did not report the created lane worktree")
            _clear_demo_progress()

            _operator(
                "lane",
                "launch",
                "--lane-id",
                lane_id,
                label="lane launch",
                timeout=60,
            )

            watched = _operator(
                "watch",
                "--until-review-for",
                lane_id,
                "--timeout",
                watch_timeout,
                label="completion wait",
                timeout=660,
            )
            event_id = watched.get("event_id")
            if not isinstance(event_id, str) or not event_id:
                raise RunFailed(
                    "the lane became actionable without a manager completion event; "
                    f"inspect the visualizer ({watched.get('summary', 'no summary')})"
                )

            _operator(
                "manager",
                "acknowledge",
                "--event-id",
                event_id,
                label="manager acknowledgement",
                timeout=30,
            )
            verdict = _run_review_agent(worktree)
            approval = (
                "ACCEPTED" if verdict["review_outcome"] == "PASS" else "REJECTED"
            )
            review_arguments = [
                "lane",
                "completion-review",
                "--event-id",
                event_id,
                "--review-outcome",
                str(verdict["review_outcome"]),
                "--approval",
                approval,
                "--review-summary",
                f"Independent Claude reviewer: {verdict['summary']}",
            ]
            for item in verdict["evidence"]:
                review_arguments.extend(("--evidence", item))
            review = _operator(
                *review_arguments,
                label="record independent agent review",
                timeout=60,
            )
            if approval != "ACCEPTED":
                raise RunFailed(
                    "the independent review agent rejected the worker result: "
                    f"{verdict['summary']}"
                )
            acceptance = _find_evidence(review, "ORCHESTRATOR_ACCEPTANCE.json")
            _operator(
                "lane",
                "retire",
                "--acceptance-ref",
                str(acceptance),
                label="lane retirement",
                timeout=60,
            )
            _operator("harness", "shutdown", label="harness shutdown", timeout=60)
    except Exception:
        _diagnose(lane_id)
        raise

    print(
        f"\nSUCCESS: {lane_id} used EverOS + Atlas memory, passed independent "
        "agent review, was accepted, retired, and the harness shut down cleanly."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--task-card",
        type=Path,
        default=DEFAULT_TASK_CARD,
        help=f"plain task card to enrich with memory (default: {DEFAULT_TASK_CARD})",
    )
    parser.add_argument(
        "--watch-timeout",
        default="10m",
        help="native harness wait duration (default: 10m)",
    )
    args = parser.parse_args()
    try:
        run_demo(
            task_card_path=args.task_card.expanduser().resolve(),
            watch_timeout=args.watch_timeout,
        )
    except KeyboardInterrupt:
        print("\nInterrupted; durable harness state was preserved.", file=sys.stderr)
        return 130
    except (RunFailed, subprocess.TimeoutExpired, OSError, ValueError) as exc:
        print(f"\nFAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
