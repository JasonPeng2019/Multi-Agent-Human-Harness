"""Read-only state for the terminal viewer (``operator_launch view``).

The viewer is a human-facing diagnostic.  This module only reads durable
runtime records: it never takes a record lock, writes a file, acknowledges an
event, or changes a lease.  Every lane is summarized as seven steps

    Recall -> Vet -> Plan -> Pack -> Work -> Review -> Learn

where the first four come from the optional memory handoff and the last three
from the ordinary harness lifecycle.  A lane without a memory handoff shows
the memory steps as skipped instead of pretending they ran.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import load_config
from .core import content_hash
from . import terminal_evidence
from .epochs import (
    epoch_dir,
    manager_queue_path,
    read_current_epoch,
)
from .monitor import (
    _discover_orphaned_leases,
    _lease_files,
    _read_acceptance_chain,
    derive_lane_status,
    read_controller_status,
)
from .setup import read_monitor_record

VIEW_STATE_SCHEMA = "harness-view-state/v1"
REVIEW_AGENT_SCHEMA = "harness-review-agent/v1"

STEPS = ("Recall", "Vet", "Plan", "Pack", "Work", "Review", "Learn")
RECALL, VET, PLAN, PACK, WORK, REVIEW, LEARN = range(len(STEPS))

# Step codes: what a single step cell shows.
DONE, NOW, WAIT, FAIL, TODO, SKIP = "done", "now", "wait", "fail", "todo", "skip"

# Tones colour the lane's status label.
TONE_LIVE, TONE_MEMORY, TONE_PLAN, TONE_ATTENTION, TONE_GOOD, TONE_BAD, TONE_IDLE = (
    "live", "memory", "plan", "attention", "good", "bad", "idle",
)

MONITOR_STALE_SECONDS = 180.0
_TAIL_BYTES = 64_000
_MAX_JSONL_LINES = 10_000

_PLAN_BRANCH_LABELS = {
    "selected_memory": "plan built on memory",
    "direct_fill": "reused plan",
    "apc_proposal": "adapted plan",
    "shortlist": "template shortlist",
}

_SOURCE_LABELS = {
    "everos-generated-skills": "EverOS skill",
    "atlas-shared-procedures": "Atlas procedure",
    "local-reviewed-experience": "past case",
    "local-template-registry": "template",
}

_PROBLEM_LABELS = {
    "controller_exited": "Worker stopped unexpectedly",
    "provider_exited_no_result": "Worker ended without a report",
    "status_transcript_contradiction": "Worker status is inconsistent",
    "cleanup_unproven": "Cleanup not yet proven",
    "orphaned_lease": "Holding a key after stopping",
}

_PROBLEM_HINTS = {
    "controller_exited": "resume-lane or lane force-stop",
    "provider_exited_no_result": "resume-lane --lane-id {lane}",
    "status_transcript_contradiction": "health reconcile",
    "cleanup_unproven": "lane force-stop --lane-id {lane}",
    "orphaned_lease": "lease force-release --resource-id {resource}",
}


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _age_seconds(value: Any, now: datetime) -> float | None:
    parsed = _parse_time(value)
    if parsed is None:
        return None
    return max(0.0, (now - parsed).total_seconds())


def _read_json_quiet(path: Path) -> dict[str, Any] | None:
    try:
        with path.open("r", encoding="utf-8-sig") as handle:
            value = json.load(handle)
    except (OSError, ValueError):
        return None
    return value if isinstance(value, dict) else None


def _jsonl_records(path: Path, *, tail_only: bool) -> list[dict[str, Any]]:
    """Read JSONL objects; ``tail_only`` reads a bounded tail of large files."""
    try:
        size = path.stat().st_size
        with path.open("rb") as handle:
            if tail_only and size > _TAIL_BYTES:
                handle.seek(size - _TAIL_BYTES)
                handle.readline()  # drop the partial first line
            raw = handle.read()
    except OSError:
        return []
    records: list[dict[str, Any]] = []
    for line in raw.decode("utf-8", errors="replace").splitlines()[-_MAX_JSONL_LINES:]:
        line = line.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except ValueError:
            continue
        if isinstance(value, dict) and "schema" not in value:
            records.append(value)
    return records


def _task_title(worktree: Path) -> str:
    card = _read_json_quiet(worktree / ".agent-workspace" / "task-card.json")
    task = (card or {}).get("task")
    if isinstance(task, dict):
        task = task.get("title") or task.get("summary") or task.get("objective")
    if not isinstance(task, str) or not task.strip():
        return ""
    return " ".join(task.strip().splitlines()[0].split())


def _memory_summary(lane: dict[str, Any], worktree: Path) -> dict[str, Any] | None:
    """Summarize the lane's optional memory handoff, or None for a plain lane."""
    agent_workspace = worktree / ".agent-workspace"
    envelope = _read_json_quiet(agent_workspace / "memory-dispatch.json")
    card = _read_json_quiet(agent_workspace / "task-card.json") or {}
    handoff = card.get("memory_handoff") if isinstance(card.get("memory_handoff"), dict) else None
    plan_state = lane.get("memory_plan_state")
    if plan_state is None and handoff is not None:
        plan_state = handoff.get("plan_state")
    if envelope is None and plan_state is None:
        return None

    summary: dict[str, Any] = {
        "plan_state": plan_state,
        "strategy": None,
        "delivered": None,
        "omitted": None,
        "sources": [],
        "plan_branch": None,
    }
    plan = (handoff or {}).get("plan")
    if isinstance(plan, dict):
        source = plan.get("source")
        if isinstance(source, dict) and isinstance(source.get("branch"), str):
            summary["plan_branch"] = source["branch"]
        elif isinstance(source, dict) and source.get("kind") == "selected_memory":
            summary["plan_branch"] = "selected_memory"
        elif str(plan.get("plan_id", "")).startswith("fresh:"):
            summary["plan_branch"] = "fresh"
    if envelope is not None:
        summary["strategy"] = envelope.get("strategy")
        trace = envelope.get("delivery_trace")
        if isinstance(trace, dict):
            delivered = trace.get("context_delivered")
            omitted = trace.get("omitted")
            summary["delivered"] = len(delivered) if isinstance(delivered, list) else None
            summary["omitted"] = len(omitted) if isinstance(omitted, list) else None
        else:
            delivery = envelope.get("delivery") if isinstance(envelope.get("delivery"), dict) else {}
            optional = delivery.get("optional")
            omitted = delivery.get("omitted")
            summary["delivered"] = len(optional) if isinstance(optional, list) else None
            summary["omitted"] = len(omitted) if isinstance(omitted, list) else None
        origins = sorted({
            str(item.get("origin"))
            for item in envelope.get("optional_content", [])
            if isinstance(item, dict) and item.get("origin")
        })
        summary["sources"] = origins
        if summary["plan_branch"] is None and str(envelope.get("plan_id", "")).startswith("fresh:"):
            summary["plan_branch"] = "fresh"
    return summary


def _memory_detail(memory: dict[str, Any] | None) -> str:
    if memory is None:
        return ""
    parts: list[str] = []
    if memory.get("delivered") is not None:
        names = [_SOURCE_LABELS.get(source, source) for source in memory.get("sources") or []]
        suffix = f" ({' + '.join(names)})" if names else ""
        parts.append(f"{memory['delivered']} memories{suffix}")
    branch = memory.get("plan_branch")
    if branch:
        parts.append(_PLAN_BRANCH_LABELS.get(branch, "fresh plan" if branch == "fresh" else branch))
    return " · ".join(parts)


def _held_keys(lane: dict[str, Any], leases: list[dict[str, Any]]) -> list[str]:
    return sorted(
        str(lease.get("resource_id"))
        for lease in leases
        if lease.get("lane_id") == lane.get("lane_id")
        and lease.get("run_id") == lane.get("run_id")
        and lease.get("resource_id")
    )


def _root_review(rt: Path, epoch_id: str, lane: dict[str, Any], acceptance: dict[str, Any] | None) -> dict[str, Any] | None:
    folder = terminal_evidence.publication_dir(rt, epoch_id, lane)
    path = folder / "COMPLETION_REVIEW.json"
    review = _read_json_quiet(path)
    if review is None:
        path = epoch_dir(rt, epoch_id) / "lanes" / str(lane["lane_id"]) / "retirement-archive" / "COMPLETION_REVIEW.json"
        review = _read_json_quiet(path)
    if not review or review.get("schema") != "completion-review/v1":
        return None
    if (review.get("lane_id") != lane.get("lane_id") or review.get("run_id") != lane.get("run_id")
            or review.get("content_hash") != content_hash(review)):
        return None
    decision = acceptance
    if decision is None:
        candidate = _read_json_quiet(path.parent / "ORCHESTRATOR_ACCEPTANCE.json")
        if candidate:
            from .review import validate_acceptance_chain
            if validate_acceptance_chain(review, candidate, lane_id=lane['lane_id'], run_id=lane['run_id']):
                decision = candidate
    return {"verdict": review.get("review_outcome"), "summary": review.get("review_summary"),
            "evidence": review.get("evidence", []), "reviewed_at": review.get("reviewed_at"),
            "commit": review.get("commit"), "reviewer": (decision or {}).get("accepted_by", "ROOT"),
            "approval": (decision or {}).get("approval", "Pending"), "path": str(path),
            "workspace": str(rt.parent)}


def _derive_lane(
    rt: Path,
    epoch_id: str,
    lane: dict[str, Any],
    *,
    leases: list[dict[str, Any]],
    orphaned: list[dict[str, Any]],
    now: datetime,
) -> dict[str, Any]:
    lane_id = str(lane.get("lane_id", "?"))
    worktree = Path(str(lane.get("worktree_path", "")))
    status = read_controller_status(lane) if lane.get("controller_status_path") else None
    try:
        actionable = derive_lane_status(
            rt, epoch_id, lane, status, lease_records=leases, orphaned_leases=orphaned
        )
    except Exception:
        actionable = None
    try:
        acceptance = _read_acceptance_chain(rt, epoch_id, lane_id, lane)
    except Exception:
        acceptance = None
    approval = (acceptance or {}).get("approval")
    if approval is None and isinstance(lane.get("acceptance_advancement"), dict):
        # Retirement archives the review pair; the lane keeps the decision.
        approval = lane["acceptance_advancement"].get("approval")
    outcome_recorded = (
        epoch_dir(rt, epoch_id) / "lanes" / lane_id / "NATIVE_OUTCOME_RECORDED.json"
    ).is_file()
    lifecycle = str(lane.get("lifecycle") or "unknown")
    recorded = (status or {}).get("recorded_status")
    memory = _memory_summary(lane, worktree)
    review_agent = _read_json_quiet(
        worktree / ".agent-workspace" / "review-agent.json"
    )
    if (review_agent or {}).get("schema") != REVIEW_AGENT_SCHEMA:
        review_agent = None

    events_path = lane.get("controller_events_path")
    events = _jsonl_records(Path(events_path), tail_only=False) if events_path else []
    attempts_path = lane.get("attempts_path")
    attempts = len(_jsonl_records(Path(attempts_path), tail_only=True)) if attempts_path else 0
    started = next((e.get("ts") for e in events if e.get("event_type") == "controller_started"), None)
    last_event = events[-1].get("event_type") if events else None

    steps = [TODO] * len(STEPS)
    label, tone, current = "Preparing", TONE_IDLE, WORK

    # Memory steps.
    if memory is None:
        for index in (RECALL, VET, PLAN, PACK):
            steps[index] = SKIP
    elif memory.get("plan_state") in ("absent", "candidate_review"):
        steps[RECALL] = steps[VET] = DONE
        steps[PLAN] = WAIT
        current = PLAN
        label, tone = "Plan awaiting orchestrator review", TONE_ATTENTION
    else:
        for index in (RECALL, VET, PLAN, PACK):
            steps[index] = DONE

    pending_plan = memory is not None and memory.get("plan_state") in ("absent", "candidate_review")
    if not pending_plan:
        accepted = approval == "ACCEPTED" or lifecycle == "accepted"
        rejected = approval == "REJECTED"
        stopped = lifecycle in ("retired", "abandoned") and not accepted
        reviewable = lifecycle == "review_pending" or recorded == "review_pending" or actionable == "review_pending"
        if accepted:
            steps[WORK] = steps[REVIEW] = steps[LEARN] = DONE
            label = "Accepted"
            if outcome_recorded:
                label += " · outcome saved"
            if lifecycle == "retired":
                label += " · retired"
            current, tone = LEARN, TONE_GOOD
        elif stopped:
            steps[WORK] = FAIL
            current, label, tone = WORK, "Stopped without acceptance", TONE_IDLE
        elif rejected:
            steps[WORK] = DONE
            steps[REVIEW] = FAIL
            current, label, tone = REVIEW, "Rejected, can resume", TONE_BAD
        elif actionable in _PROBLEM_LABELS:
            steps[WORK] = FAIL
            current, label, tone = WORK, _PROBLEM_LABELS[actionable], TONE_BAD
        elif actionable == "result_invalid" or lifecycle == "result_invalid":
            steps[WORK] = DONE
            steps[REVIEW] = FAIL
            current, label, tone = REVIEW, "Report invalid", TONE_BAD
        elif reviewable:
            steps[WORK] = DONE
            steps[REVIEW] = NOW
            current = REVIEW
            if (review_agent or {}).get("state") == "running":
                label, tone = "Agent reviewing", TONE_LIVE
            elif (review_agent or {}).get("state") == "complete":
                verdict = review_agent.get("verdict") or {}
                label = f"Agent review complete: {verdict.get('review_outcome', 'UNKNOWN')}"
                tone = TONE_LIVE
            elif (review_agent or {}).get("state") == "failed":
                label, tone = "Review agent failed", TONE_BAD
            else:
                label, tone = "Awaiting orchestrator review", TONE_ATTENTION
        elif lifecycle == "running" or lane.get("launch_pending") is True:
            steps[WORK] = NOW
            current = WORK
            if recorded == "correction_pending" or attempts > 1:
                label, tone = "Fixing its report", TONE_LIVE
            else:
                label, tone = "Working", TONE_LIVE
        elif lifecycle == "resuming":
            steps[WORK] = WAIT
            current, label, tone = WORK, "Resuming", TONE_LIVE
        elif lifecycle == "prepared":
            steps[WORK] = WAIT
            current = WORK
            if last_event == "lease_busy":
                label, tone = "Waiting for a key", TONE_MEMORY
            else:
                label, tone = "Ready to launch", TONE_IDLE

    keys = _held_keys(lane, leases)
    orphan_ids = [o.get("resource_id") for o in orphaned if o.get("lane_id") == lane_id]
    provider = lane.get("provider") if isinstance(lane.get("provider"), dict) else {}
    return {
        "lane_id": lane_id,
        "worktree_path": str(worktree),
        "root_review": _root_review(rt, epoch_id, lane, acceptance),
        "epoch_id": epoch_id,
        "manager_queue_path": str(manager_queue_path(rt)),
        "artifact_paths": {key: lane.get(key) for key in ("transcript_path", "stderr_path", "result_path", "attempts_path")},
        "run_id": lane.get("run_id"),
        "task": _task_title(worktree),
        "provider": provider.get("id"),
        "model": provider.get("model"),
        "lifecycle": lifecycle,
        "actionable": actionable,
        "steps": steps,
        "current": current,
        "label": label,
        "tone": tone,
        "attempts": attempts,
        "resumed": bool(lane.get("resume_from_run_id")),
        "keys": keys,
        "orphaned_keys": [str(item) for item in orphan_ids if item],
        "memory": memory,
        "detail": _memory_detail(memory),
        "elapsed_seconds": _age_seconds(started, now),
        "review_agent": review_agent,
    }


def _needs_you(lanes: list[dict[str, Any]], queue: dict[str, Any] | None, now: datetime) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    automated_reviews = {
        lane["lane_id"]
        for lane in lanes
        if (lane.get("review_agent") or {}).get("state") in {"running", "complete"}
    }
    for event in (queue or {}).get("events", []):
        if not isinstance(event, dict) or event.get("state") not in ("PENDING", "ACKNOWLEDGED"):
            continue
        if (
            event.get("lane_id") in automated_reviews
            and event.get("type") == "COMPLETION_REVIEW_REQUIRED"
        ):
            continue
        history = event.get("history") or []
        since = history[0].get("at") if history and isinstance(history[0], dict) else None
        items.append({
            "lane_id": event.get("lane_id"),
            "text": str(event.get("summary") or event.get("type") or "manager event"),
            "state": event.get("state"),
            "age_seconds": _age_seconds(since, now),
            "hint": ("orchestrator: inspect result and record completion-review"
                     if event.get("type") == "COMPLETION_REVIEW_REQUIRED" else
                     f"orchestrator: manager acknowledge --event-id {event.get('event_id')}"
                     if event.get("state") == "PENDING" else "orchestrator: handle event, then manager close"),
        })
    listed = {item["lane_id"] for item in items}
    for lane in lanes:
        if lane["lane_id"] in listed:
            continue
        if lane["tone"] in (TONE_ATTENTION, TONE_BAD) and lane["lifecycle"] not in ("retired",):
            hint = _PROBLEM_HINTS.get(str(lane["actionable"]), "")
            if lane["label"] == "Awaiting orchestrator review":
                hint = "orchestrator must inspect the result and record completion-review"
            elif lane["label"].startswith("Plan awaiting"):
                hint = "orchestrator must review the plan before execution"
            resource = (lane["orphaned_keys"] or [""])[0]
            items.append({
                "lane_id": lane["lane_id"],
                "text": lane["label"],
                "state": None,
                "age_seconds": None,
                "hint": hint.format(lane=lane["lane_id"], resource=resource),
            })
    return items


def _valid_epoch_id(epoch_id: Any) -> bool:
    return isinstance(epoch_id, str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', epoch_id) is not None


def list_epochs(rt: Path) -> list[dict[str, Any]]:
    """List durable epochs, newest first, without consulting the active-lane index."""
    root = rt / "epochs"
    if not root.is_dir():
        return []
    marker = read_current_epoch(rt) or {}
    epochs = []
    for folder in root.iterdir():
        if not folder.is_dir() or not _valid_epoch_id(folder.name):
            continue
        state = _read_json_quiet(folder / "epoch-state.json")
        if (state is None or state.get('schema') != 'epoch-state/v1'
                or state.get('epoch_id') != folder.name):
            continue
        epochs.append({
            'epoch_id': folder.name, 'opened_at': state.get('opened_at'),
            'closed_at': state.get('closed_at'), 'mode': state.get('lane_mode'),
            'status': 'open' if marker.get('epoch_id') == folder.name and state.get('lifecycle') == 'active' else 'closed',
            'lane_count': len(_epoch_lane_records(rt, folder.name)),
        })
    epochs.sort(key=lambda item: (_parse_time(item['opened_at']) or datetime.min.replace(tzinfo=timezone.utc), item['epoch_id']), reverse=True)
    return epochs


def _epoch_lane_records(rt: Path, epoch_id: str) -> list[dict[str, Any]]:
    # Retirement removes entries from active-lanes.json, but retains lane.json.
    lanes_dir = epoch_dir(rt, epoch_id) / "lanes"
    records = []
    if lanes_dir.is_dir():
        for folder in sorted(lanes_dir.iterdir()):
            record = _read_json_quiet(folder / "lane.json")
            if (record is not None and record.get('schema') == 'lane/v1'
                    and record.get("lane_id") == folder.name
                    and isinstance(record.get('run_id'), str) and record['run_id']
                    and isinstance(record.get('worktree_path'), str) and record['worktree_path']):
                records.append(record)
    return records


def collect_state(rt: Path, *, epoch_id: str | None = None, now: datetime | None = None) -> dict[str, Any]:
    """Build the viewer state from the runtime root ``rt`` without writing."""
    now = now or datetime.now(timezone.utc)
    base: dict[str, Any] = {
        "schema": VIEW_STATE_SCHEMA,
        "collected_at": now.isoformat(),
        "status": "no_runtime",
        "epoch_id": None,
        "mode": None,
        "opened_at": None,
        "run_seconds": None,
        "monitor": {"state": "missing", "age_seconds": None},
        "lanes": [],
        "needs_you": [],
        "keys_held": 0,
    }
    if epoch_id is not None and not _valid_epoch_id(epoch_id):
        raise ValueError('epoch must be a stored epoch ID, not a path')
    if not rt.is_dir() and epoch_id is None:
        return base

    marker = read_current_epoch(rt)
    if epoch_id is None:
        choices = list_epochs(rt)
        if not choices:
            base["status"] = "idle"
            return base
        current = (marker or {}).get('epoch_id')
        epoch_id = next((item['epoch_id'] for item in choices if item['epoch_id'] == current), choices[0]['epoch_id'])
    state = _read_json_quiet(epoch_dir(rt, epoch_id) / 'epoch-state.json')
    if (not state or state.get('schema') != 'epoch-state/v1' or state.get('epoch_id') != epoch_id):
        raise ValueError(f'epoch not found or invalid: {epoch_id}')
    active = (marker or {}).get('epoch_id') == epoch_id and state.get('lifecycle') == 'active'

    base["epoch_id"] = epoch_id
    base["mode"] = state.get("lane_mode")
    base["opened_at"] = state.get("opened_at")
    base["status"] = "open" if active and state.get("lifecycle") == "active" else "closed"
    if base["status"] == "closed":
        opened = _parse_time(state.get("opened_at"))
        closed = _parse_time(state.get("closed_at"))
        if opened and closed:
            base["run_seconds"] = max(0.0, (closed - opened).total_seconds())
    else:
        base["run_seconds"] = _age_seconds(state.get("opened_at"), now)

    monitor = read_monitor_record(rt) if active else None
    if monitor is not None:
        age = _age_seconds(monitor.get("last_heartbeat_at"), now)
        healthy = age is not None and age <= MONITOR_STALE_SECONDS
        base["monitor"] = {"state": "healthy" if healthy else "stale", "age_seconds": age}

    leases = _lease_files(rt) if active else []
    try:
        orphaned = _discover_orphaned_leases(rt, epoch_id) if active else []
    except Exception:
        orphaned = []
    lanes = [
        _derive_lane(rt, epoch_id, lane, leases=leases, orphaned=orphaned, now=now)
        for lane in _epoch_lane_records(rt, epoch_id)
    ]
    lanes.sort(key=lambda item: item["lane_id"])
    base["lanes"] = lanes
    base["root"] = {
        "lane_id": "ROOT", "role": "root", "run_id": epoch_id, "epoch_id": epoch_id,
        "worktree_path": str(rt.parent), "workers": lanes,
        "task": "Coordinate agents, handle events and review results",
        "label": "Runtime open" if base["status"] == "open" else "Epoch closed",
        "lifecycle": "coordinating" if base["status"] == "open" else "retired",
        "tone": "idle", "steps": [SKIP] * len(STEPS), "keys": [],
        "provider": "Root orchestrator", "model": None,
    }
    base["keys_held"] = sum(len(lane["keys"]) for lane in lanes)

    queue = None
    if base["mode"] == "managed" and active:
        queue = _read_json_quiet(manager_queue_path(rt))
        if (queue or {}).get('epoch_id') != epoch_id:
            queue = None
    base["needs_you"] = _needs_you(lanes, queue, now)
    return base


def collect_from_harness(harness_root: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    """Load the stored configuration and collect state for its runtime root."""
    from .config import find_harness_root

    root = Path(harness_root) if harness_root is not None else find_harness_root()
    config = load_config(root)
    return collect_state(config.runtime_root)
