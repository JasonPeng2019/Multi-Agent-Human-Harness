"""Run-specific collector context: actual ROOT hook activity and watchdog time.

No task-completion policy, scheduling, retries, or setup is performed here.
Ordinary harness use without the collector environment remains unchanged.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from .core import read_json
from .records import atomic_write_json


def _instant(value: str) -> datetime:
    instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if instant.utcoffset() is None:
        raise ValueError("collector timestamps must include a UTC offset")
    return instant


def require_native_root_hooks(harness: Path, root: Path) -> dict | None:
    """Check real post-tool hook evidence before collector-owned worker admission."""
    name = os.environ.get("SWE_ROOT_LAUNCH_FILE")
    if not name:
        return None
    launch = read_json(Path(name))
    if launch.get("arm") != "harness" or launch.get("role") != "root":
        raise ValueError("collector launch is not a managed ROOT")
    if Path(launch.get("workspace", "")).resolve() != root.resolve():
        raise ValueError("collector launch belongs to a different ROOT workspace")
    if Path(launch.get("harness_dir", "")).resolve() != harness.resolve():
        raise ValueError("collector launch belongs to a different harness")
    provider_id = launch.get("provider_id", "codex")
    dotdir = {"codex": ".codex", "claude-code": ".claude"}.get(provider_id)
    if dotdir is None:
        raise ValueError("unsupported collector ROOT provider")
    binding = read_json(root / dotdir / "orchestrator-harness-binding.json")
    if (binding.get("role") != "root" or binding.get("provider_id") != provider_id
            or Path(binding.get("harness_root", "")).resolve() != harness.resolve()):
        raise ValueError("ROOT hook binding does not match the collector")
    relative = Path(binding.get("liveness_path", ""))
    path = (root / relative).resolve()
    if relative.is_absolute() or not path.is_relative_to(root.resolve()) or path == root.resolve():
        raise ValueError("ROOT hook liveness path is invalid")
    started = _instant(launch["started_at_utc"])
    count = 0
    if path.is_file():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            try:
                record = json.loads(line)
                fresh = _instant(record["at"]) >= started
            except (ValueError, KeyError, TypeError):
                continue
            if (fresh and record.get("schema") == "hook-liveness/v1"
                    and record.get("role") == "root" and record.get("provider_id") == provider_id
                    and record.get("boundary") == "post-tool-use"):
                count += 1
    if not count:
        raise ValueError(
            "Native ROOT PostToolUse hook execution is unverified for this launch. "
            "Preserve the failure and diagnose hook discovery; do not repeat setup, "
            "manually invoke hooks as proof, or relaunch automatically."
        )
    return {"run_id": launch["run_id"], "liveness_path": str(path),
            "native_post_tool_use_records": count}


def project_budget(worktree: Path) -> dict | None:
    name = os.environ.get("SWE_RUN_BUDGET_FILE")
    if not name:
        return None
    budget = read_json(Path(name))
    if budget.get("schema") != "run-budget/v1" or budget.get("authority") != "cli-collector-watchdog":
        raise ValueError("collector budget record is invalid")
    atomic_write_json(worktree / ".agent-workspace/RUN_BUDGET.json", budget)
    return budget


def epoch_resume_scope(rt: Path) -> dict | None:
    """Identify one operator-assisted run without changing its absolute clock."""
    name = os.environ.get("SWE_ROOT_LAUNCH_FILE")
    if not name:
        return None
    launch = read_json(Path(name))
    if launch.get("operator_assisted") is not True:
        return None
    budget_name = os.environ.get("SWE_RUN_BUDGET_FILE")
    if not budget_name:
        raise ValueError("collector epoch resume requires its original budget")
    budget = read_json(Path(budget_name))
    root = Path(launch["workspace"]).resolve()
    harness = Path(launch["harness_dir"]).resolve()
    if (launch.get("arm") != "harness" or launch.get("role") != "root"
            or budget.get("schema") != "run-budget/v1"
            or budget.get("authority") != "cli-collector-watchdog"
            or not launch.get("run_id") or budget.get("run_id") != launch["run_id"]
            or Path(budget["root_workspace"]).resolve() != root
            or Path(budget["harness_dir"]).resolve() != harness
            or rt.resolve() != root / ".harness-runtime"
            or Path(launch["harness_runtime"]).resolve() != rt.resolve()):
        raise ValueError("collector epoch resume identity does not match this runtime")
    deadline = _instant(launch["watchdog_deadline_utc"])
    from .quota_clock import validate_launch_clock
    quota = validate_launch_clock(Path(name), launch)
    original_deadline = _instant(quota["original_deadline_utc"]) if quota else deadline
    seconds = float(budget["original_watchdog_seconds"])
    if seconds <= 0 or seconds > 365 * 86400 or _instant(budget["watchdog_deadline_utc"]) != deadline:
        raise ValueError("collector epoch resume budget changed")
    return {"run_id": launch["run_id"], "root_workspace": str(root),
            "harness_dir": str(harness), "watchdog_deadline_utc": original_deadline.isoformat(),
            "original_started_at": (original_deadline - timedelta(seconds=seconds)).isoformat()}


def collector_audit_pause_ready(rt: Path, harness: Path | None = None) -> bool:
    """Prove worker quiescence for an operator audit, never task completion."""
    from . import processes
    from .leases import lease_dir

    scope = epoch_resume_scope(rt)
    if scope is None or (harness is not None and Path(scope["harness_dir"]).resolve() != harness.resolve()):
        return False
    try:
        queue = read_json(rt / "manager/QUEUE.json")
        events = queue.get("events")
        if (queue.get("schema") != "manager-queue/v1" or not isinstance(events, list)
                or any(not isinstance(event, dict) or event.get("state") not in ("COMPLETE", "BLOCKED") for event in events)):
            return False
    except (OSError, ValueError, TypeError):
        return False
    if any(lease_dir(rt).glob("*.lease")):
        return False
    for path in rt.glob("epochs/*/lanes/*/lane.json"):
        try:
            lane = read_json(path)
            if lane.get("schema") != "lane/v1" or lane.get("lifecycle") != "retired":
                return False
            status = read_json(Path(lane["controller_status_path"]))
            if (status.get("lane_id") != lane.get("lane_id")
                    or status.get("run_id") != lane.get("run_id")
                    or status.get("controller_state") != "exited"
                    or status.get("cleanup_proven") is not True):
                return False
            provider = status.get("provider_state") or {}
            if provider.get("state") != "exited":
                return False
            for identity in (lane.get("process") or {}, provider):
                pid, creation = identity.get("pid"), identity.get("creation_time")
                if (not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0
                        or not isinstance(creation, str) or not creation
                        or processes.identity_matches(pid, creation)
                        or (processes.process_alive(pid) and processes.process_identity(pid) is None)):
                    return False
            boundary = status.get("process_boundary")
            if (not isinstance(boundary, dict)
                    or not processes.process_boundary_is_gone(boundary, native_cleanup_proven=True)):
                return False
        except (OSError, ValueError, KeyError, TypeError):
            return False
    return True


def epoch_resume_deadline(rt: Path) -> datetime | None:
    """Admission uses the validated current deadline; epoch identity uses the original."""
    scope = epoch_resume_scope(rt)
    if scope is None:
        return None
    return _instant(read_json(Path(os.environ["SWE_ROOT_LAUNCH_FILE"]))["watchdog_deadline_utc"])
