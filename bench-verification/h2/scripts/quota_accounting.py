"""Validate immutable quota interruptions; never invent or repair token counters."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def bound(reference):
    path = Path(reference["path"]).resolve(strict=True)
    if hashlib.sha256(path.read_bytes()).hexdigest() != reference["sha256"]:
        raise ValueError("Quota accounting evidence changed")
    return path


def rejected_session(path, session):
    events = [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    top = [event for event in events if not event.get("parent_tool_use_id")]
    sessions = {event["session_id"] for event in top if event.get("session_id")}
    if sessions != {session}:
        raise ValueError("Quota accounting changed native session")
    rejected = [event for event in top if event.get("type") == "rate_limit_event"
                and event.get("rate_limit_info", {}).get("status") == "rejected"]
    if not rejected:
        raise ValueError("Quota accounting lacks native rejection")
    return rejected[-1]["rate_limit_info"]["resetsAt"]


def receipts(task):
    run = Path(task["root_run_dir"]).resolve(strict=True)
    result = {}
    for number, path in enumerate(sorted((run / "quota-accounting").glob("*.json")), 1):
        if path.name != f"{number:04d}.json":
            raise ValueError("Quota accounting receipts must be consecutive")
        record = read(path)
        if (record.get("schema") != "operator-quota-accounting/v1"
                or record.get("run_id") != task["run_id"] or task.get("budget_tokens") is not None):
            raise ValueError("Quota accounting belongs to another or capped run")
        stop_path = bound(record["stop_audit"])
        if not stop_path.is_relative_to(run.parent.parent):
            raise ValueError("Quota stop audit is outside this trial")
        stop = read(stop_path)
        if (stop.get("schema") != "operator-quota-stop/v1" or stop.get("run_id") != task["run_id"]
                or stop.get("all_owned_provider_processes_absent") is not True
                or stop.get("collector_sealed") is not True or stop.get("not_task_reported_finish") is not True):
            raise ValueError("Quota accounting lacks a sealed stopped-provider audit")
        launch_path = bound(stop["segment_launch"])
        manifest_path = bound(stop["segment_manifest"])
        transcript_path = bound(stop["transcript"])
        if (not launch_path.parent.is_relative_to(run) or manifest_path.parent != launch_path.parent
                or transcript_path.parent != launch_path.parent):
            raise ValueError("Quota accounting segment belongs to another run")
        launch, final = read(launch_path), read(manifest_path)
        if (launch.get("run_id") != task["run_id"] or final.get("run_id") != task["run_id"]
                or final.get("watchdog_expired") or final.get("launch_error") or not final.get("ended_at_utc")
                or any(final.get(key) != value for key, value in launch.items())):
            raise ValueError("Quota accounting cannot excuse a failed launch or expired watchdog")
        reset = rejected_session(transcript_path, stop["root_session_id"])
        entries = record.get("invocations")
        if not isinstance(entries, list) or not entries:
            raise ValueError("Quota accounting requires exact invocation evidence")
        for entry in entries:
            invocation = entry["invocation_id"]
            if invocation in result:
                raise ValueError("Duplicate quota accounting invocation")
            archived = bound(entry["archived_transcript"])
            if not archived.is_relative_to(run.parent.parent) or archived.is_relative_to(Path(launch["workspace"]).resolve()):
                raise ValueError("Quota accounting archive must be operator evidence outside the model workspace")
            if rejected_session(archived, entry["thread_id"]) != reset:
                raise ValueError("Quota accounting worker rejected a different quota window")
            if entry["role"] == "worker":
                proofs = [proof for proof in stop.get("worker_stop_evidence", []) if proof["lane_id"] == entry["lane_id"]]
                if len(proofs) != 1:
                    raise ValueError("Quota accounting worker lacks unique cleanup proof")
                lane = read(bound(proofs[0]["lane"]))
                status = read(bound(proofs[0]["controller_status"]))
                if (lane.get("run_id") != entry["lane_run_id"] or status.get("run_id") != entry["lane_run_id"]
                        or status.get("controller_state") != "exited" or status.get("cleanup_proven") is not True
                        or status.get("provider_state", {}).get("state") != "exited"
                        or status.get("provider_state", {}).get("provider_session_id") != entry["thread_id"]):
                    raise ValueError("Quota accounting worker cleanup identity differs")
            elif entry["role"] not in ("root", "raw") or entry["thread_id"] != stop["root_session_id"]:
                raise ValueError("Quota accounting ROOT identity differs")
            result[invocation] = {**entry, "receipt_path": str(path), "archive_path": str(archived)}
    return result


def validate_row(row, evidence, receipt):
    if (row.get("provider_id") != "claude-code" or row.get("completed") is not True
            or evidence.get("status") != "terminal_error_usage_unverified"
            or type(evidence.get("comparison_total_tokens")) is not int):
        raise ValueError("Quota receipt only acknowledges a stopped error terminal with a known whole-tree prefix")
    for field in ("invocation_id", "role", "thread_id", "lane_id", "lane_run_id"):
        if row.get(field) != receipt.get(field):
            raise ValueError("Quota accounting invocation identity or transcript segment changed")
    prefix = Path(receipt["archive_path"]).read_bytes()
    with Path(row["transcript_path"]).open("rb") as stream:
        if stream.read(len(prefix)) != prefix:
            raise ValueError("Quota accounting transcript prefix changed")
    # An ignored zero-turn notification may extend the old segment's raw digest
    # before the next physical CLI init. Bind the frozen original segment and
    # its native counters independently, while allowing that harmless append.
    from token_ledger import extract_usage
    frozen = extract_usage(Path(receipt["archive_path"]), completed=True,
        segment_index=receipt.get("transcript_segment_index"), provider_id="claude-code")
    if (frozen.get("status") != "terminal_error_usage_unverified"
            or frozen.get("thread_id") != receipt["thread_id"]
            or frozen.get("transcript_segment_sha256") != receipt["transcript_segment_sha256"]):
        raise ValueError("Quota accounting frozen native segment changed")
    for field in ("input_tokens", "output_tokens", "comparison_total_tokens"):
        if evidence.get(field) != receipt.get(field) or frozen.get(field) != receipt.get(field):
            raise ValueError("Quota accounting known counters changed")
