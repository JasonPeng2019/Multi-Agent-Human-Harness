"""Epochs: one active epoch, launcher-owned open/reuse/close.

The public launcher owns the epoch records.  It creates a new epoch only when
none is active and otherwise reuses the active epoch while its immutable
configuration is unchanged. Collector-owned continuations reopen their bound
epoch, retaining retired lanes, queue history, and the original run deadline.
Retirement clears ``CURRENT_EPOCH.json`` before the epoch is marked closed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import HarnessConfig, ResourceManifest, compute_config_identity
from .core import iso_utc, new_id, read_json, require_schema, utc_now
from .records import RecordLock, atomic_write_json, read_record, write_record

CURRENT_EPOCH_SCHEMA = "current-epoch/v1"
EPOCH_STATE_SCHEMA = "epoch-state/v1"
ACTIVE_LANES_SCHEMA = "active-lanes/v1"
MANAGER_QUEUE_SCHEMA = "manager-queue/v1"


class EpochError(RuntimeError):
    """An epoch operation failed."""


def current_epoch_path(rt: Path) -> Path:
    return rt / "CURRENT_EPOCH.json"


def manager_queue_path(rt: Path) -> Path:
    return rt / "manager" / "QUEUE.json"


def epoch_dir(rt: Path, epoch_id: str) -> Path:
    return rt / "epochs" / epoch_id


def lane_record_dir(rt: Path, epoch_id: str, lane_id: str) -> Path:
    return epoch_dir(rt, epoch_id) / "lanes" / lane_id


def read_current_epoch(rt: Path) -> dict[str, Any] | None:
    """Return the active-epoch marker, or None when no epoch is active."""
    path = current_epoch_path(rt)
    if not path.is_file():
        return None
    try:
        return read_record(path, CURRENT_EPOCH_SCHEMA)
    except (OSError, ValueError):
        return None


def read_epoch_state(rt: Path, epoch_id: str) -> dict[str, Any]:
    return read_record(epoch_dir(rt, epoch_id) / "epoch-state.json", EPOCH_STATE_SCHEMA)


def read_active_lanes(rt: Path, epoch_id: str) -> list[dict[str, Any]]:
    path = epoch_dir(rt, epoch_id) / "active-lanes.json"
    if not path.is_file():
        return []
    try:
        record = read_record(path, ACTIVE_LANES_SCHEMA)
    except (OSError, ValueError):
        return []
    lanes = record.get("lanes")
    return lanes if isinstance(lanes, list) else []


def write_active_lanes(rt: Path, epoch_id: str, lanes: list[dict[str, Any]]) -> None:
    path = epoch_dir(rt, epoch_id) / "active-lanes.json"
    record = {
        "schema": ACTIVE_LANES_SCHEMA,
        "epoch_id": epoch_id,
        "lanes": lanes,
    }
    with RecordLock(path):
        atomic_write_json(path, record)


def _stage_manager_queue(rt: Path, epoch_id: str) -> str:
    """Atomically replace the fixed manager queue with a fresh queue_id."""
    queue_id = new_id()
    path = manager_queue_path(rt)
    record = {
        "schema": MANAGER_QUEUE_SCHEMA,
        "epoch_id": epoch_id,
        "queue_id": queue_id,
        "events": [],
    }
    with RecordLock(path):
        atomic_write_json(path, record)
    return queue_id


def open_epoch(
    rt: Path,
    config: HarnessConfig,
    manifest: ResourceManifest,
) -> dict[str, Any]:
    with RecordLock(rt / "EPOCH_LIFECYCLE.json"):
        return _open_epoch(rt, config, manifest)


def _collector_binding(rt: Path, scope: dict, state: dict | None = None) -> dict | None:
    path = rt / "COLLECTOR_EPOCH.json"
    if path.exists():
        binding = read_record(path, "collector-epoch/v1")
        if binding.get("scope") != scope:
            raise EpochError("collector epoch belongs to a different run or original deadline")
        if state is not None and binding.get("epoch_id") != state["epoch_id"]:
            raise EpochError("collector run cannot switch epoch identity")
        if state is not None and state.get("lane_mode") == "managed" and "queue_id" not in binding:
            marker = read_current_epoch(rt)
            queue = read_record(manager_queue_path(rt), MANAGER_QUEUE_SCHEMA)
            if (not marker or marker.get("epoch_id") != state["epoch_id"]
                    or queue.get("epoch_id") != state["epoch_id"]
                    or marker.get("queue_id") != queue.get("queue_id")):
                raise EpochError("collector epoch manager queue identity is unproven")
            binding["queue_id"] = queue["queue_id"]
            atomic_write_json(path, binding)
        return binding
    if state is None:
        return None
    from .collector_context import _instant
    if _instant(state["opened_at"]) < _instant(scope["original_started_at"]):
        raise EpochError("collector cannot adopt an epoch from an earlier run")
    binding = {"schema": "collector-epoch/v1", "scope": scope,
               "epoch_id": state["epoch_id"], "config_identity": state["config_identity"]}
    if state.get("lane_mode") == "managed":
        marker = read_current_epoch(rt)
        queue = read_record(manager_queue_path(rt), MANAGER_QUEUE_SCHEMA)
        if (not marker or marker.get("epoch_id") != state["epoch_id"]
                or queue.get("epoch_id") != state["epoch_id"]
                or marker.get("queue_id") != queue.get("queue_id")):
            raise EpochError("collector epoch manager queue identity is unproven")
        binding["queue_id"] = queue["queue_id"]
    atomic_write_json(path, binding)
    return binding


def _resume_recording(rt: Path, state: dict) -> None:
    if state.get("reopen_count", 0):
        from .view_replay import reopen_recording
        reopen_recording(rt, state["epoch_id"], state["reopen_count"])


def _open_epoch(rt: Path, config: HarnessConfig, manifest: ResourceManifest) -> dict[str, Any]:
    """Return the active epoch, opening a new one when none is active.

    Reuses the active epoch while its immutable configuration is unchanged;
    a config-identity mismatch is an epoch-breaking change and forces a new
    epoch (the caller must retire the old one first).
    """
    identity = compute_config_identity(config, manifest)
    from .collector_context import epoch_resume_scope, epoch_resume_deadline, _instant
    scope = epoch_resume_scope(rt)
    if scope is not None:
        if (Path(scope["root_workspace"]).resolve() != config.root_workspace.resolve()
                or Path(scope["harness_dir"]).resolve() != config.harness_root.resolve()):
            raise EpochError("collector configuration does not match its epoch")
        if utc_now() >= epoch_resume_deadline(rt):
            raise EpochError("the original collector deadline has expired")
    marker = read_current_epoch(rt)
    if marker is not None:
        epoch_id = str(marker["epoch_id"])
        state = read_epoch_state(rt, epoch_id)
        if state.get("config_identity") != identity:
            raise EpochError(
                "active epoch configuration changed; retire the runtime before "
                "changing root_workspace, profile, or the resource manifest"
            )
        if state.get("lifecycle") != "active":
            raise EpochError(f"active epoch {epoch_id} is not active")
        if scope is not None:
            _collector_binding(rt, scope, state)
        _resume_recording(rt, state)
        return state

    binding = _collector_binding(rt, scope) if scope is not None else None
    if binding is not None:
        epoch_id = binding["epoch_id"]
        state = read_epoch_state(rt, epoch_id)
        if state.get("config_identity") != identity or binding.get("config_identity") != identity:
            raise EpochError("closed collector epoch configuration changed")
        if state.get("lifecycle") != "closed":
            raise EpochError("collector epoch is not safely closed")
        marker = {"schema": CURRENT_EPOCH_SCHEMA, "epoch_id": epoch_id,
                  "lane_mode": state["lane_mode"], "opened_at": state["opened_at"]}
        if state["lane_mode"] == "managed":
            queue = read_record(manager_queue_path(rt), MANAGER_QUEUE_SCHEMA)
            if (queue.get("epoch_id") != epoch_id or not queue.get("queue_id")
                    or queue.get("queue_id") != binding.get("queue_id")):
                raise EpochError("closed epoch manager queue was replaced")
            marker["queue_id"] = queue["queue_id"]
        state.setdefault("closure_history", []).append({"closed_at": state.get("closed_at"), "reopened_at": iso_utc()})
        state.pop("closed_at", None)
        state["reopen_count"] = int(state.get("reopen_count", 0)) + 1
        state["lifecycle"] = "active"
        with RecordLock(epoch_dir(rt, epoch_id) / "epoch-state.json"):
            atomic_write_json(epoch_dir(rt, epoch_id) / "epoch-state.json", state)
        with RecordLock(current_epoch_path(rt)):
            atomic_write_json(current_epoch_path(rt), marker)
        _resume_recording(rt, state)
        return state

    epoch_id = new_id()
    lane_mode = config.profile
    queue_id: str | None = None
    if lane_mode == "managed":
        queue_id = _stage_manager_queue(rt, epoch_id)
    directory = epoch_dir(rt, epoch_id)
    directory.mkdir(parents=True, exist_ok=True)
    state = {
        "schema": EPOCH_STATE_SCHEMA,
        "epoch_id": epoch_id,
        "config_identity": identity,
        "lane_mode": lane_mode,
        "lifecycle": "opening",
        "lane_dir": str(directory / "lanes"),
        "ownership": "launcher",
        "opened_at": iso_utc(),
    }
    with RecordLock(directory / "epoch-state.json"):
        atomic_write_json(directory / "epoch-state.json", state)
    marker = {
        "schema": CURRENT_EPOCH_SCHEMA,
        "epoch_id": epoch_id,
        "lane_mode": lane_mode,
        "opened_at": iso_utc(),
    }
    if queue_id is not None:
        marker["queue_id"] = queue_id
    with RecordLock(current_epoch_path(rt)):
        atomic_write_json(current_epoch_path(rt), marker)
    state["lifecycle"] = "active"
    with RecordLock(directory / "epoch-state.json"):
        atomic_write_json(directory / "epoch-state.json", state)
    write_active_lanes(rt, epoch_id, [])
    if scope is not None:
        _collector_binding(rt, scope, state)
    return state


def close_epoch(rt: Path, epoch_id: str) -> None:
    with RecordLock(rt / "EPOCH_LIFECYCLE.json"):
        _close_epoch(rt, epoch_id)


def _close_epoch(rt: Path, epoch_id: str) -> None:
    """Retire one epoch: clear the marker first, then mark the epoch closed."""
    marker_path = current_epoch_path(rt)
    from .collector_context import epoch_resume_scope
    scope = epoch_resume_scope(rt)
    if scope is not None:
        _collector_binding(rt, scope, read_epoch_state(rt, epoch_id))
    with RecordLock(marker_path):
        try:
            marker_path.unlink()
        except FileNotFoundError:
            pass
    state_path = epoch_dir(rt, epoch_id) / "epoch-state.json"
    with RecordLock(state_path):
        try:
            state = read_json(state_path)
        except (OSError, ValueError):
            state = {}
        state["lifecycle"] = "closed"
        state["closed_at"] = iso_utc()
        atomic_write_json(state_path, state)


def lane_record_path(rt: Path, epoch_id: str, lane_id: str) -> Path:
    return lane_record_dir(rt, epoch_id, lane_id) / "lane.json"
