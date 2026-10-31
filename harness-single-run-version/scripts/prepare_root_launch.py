"""Initialize and bind the run's native harness before Codex ROOT starts."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from orchestrator_harness.windows_sandbox_preflight import require_ready

SCHEMA = "root-prelaunch-setup/v1"
RECEIPT = ".agent-workspace/ROOT_PRELAUNCH_SETUP.json"
HOOK_FILES = (
    ".codex/hooks.json",
    ".codex/orchestrator-harness-binding.json",
    ".codex/hooks/orchestrator_harness_post_tool_use.py",
    ".codex/hooks/orchestrator_harness_stop.py",
)


def hook_files(provider_id: str) -> tuple[str, ...]:
    if provider_id == "codex":
        return HOOK_FILES
    if provider_id == "claude-code":
        return (".claude/settings.json", ".claude/orchestrator-harness-binding.json",
                ".claude/hooks/orchestrator_harness_post_tool_use.py",
                ".claude/hooks/orchestrator_harness_stop.py")
    raise ValueError(f"unsupported ROOT provider: {provider_id}")


def sandbox_health(harness: Path, workspace: Path, provider_id: str) -> dict | None:
    hook_files(provider_id)  # Validate before any setup or service mutation.
    return require_ready(harness, workspace=workspace) if provider_id == "codex" else None


def read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_installed(harness: Path, workspace: Path, *, allow_closed: bool = False,
                    provider_id: str = "codex") -> dict[str, str]:
    config = read(harness / "harness-config.json")
    if (Path(config.get("root_workspace", "")).resolve() != workspace
            or config.get("managed_coordination") != "enabled"):
        raise ValueError("harness configuration does not select this managed ROOT workspace")
    runtime = workspace / ".harness-runtime"
    allowed = {"OPEN", "CLOSED"} if allow_closed else {"OPEN"}
    if read(runtime / "RUNTIME_STATE.json").get("state") not in allowed:
        raise ValueError("ROOT's prepared harness runtime is not OPEN")
    files = hook_files(provider_id)
    binding = read(workspace / files[1])
    for field, expected in {"schema": "harness-hook-binding/v1", "role": "root", "provider_id": provider_id}.items():
        if binding.get(field) != expected:
            raise ValueError(f"ROOT hook binding has the wrong {field}")
    for field, expected in (("harness_root", harness), ("runtime_root", runtime)):
        if Path(binding.get(field, "")).resolve() != expected:
            raise ValueError(f"ROOT hook binding has the wrong {field}")
    hooks = read(workspace / files[0]).get("hooks", {})
    for event, filename in (("PostToolUse", "orchestrator_harness_post_tool_use.py"), ("Stop", "orchestrator_harness_stop.py")):
        commands = [hook.get("command", "") for group in hooks.get(event, []) for hook in group.get("hooks", [])]
        if not any(filename in command for command in commands):
            raise ValueError(f"ROOT's native {event} hook is missing")
    return {relative: digest(workspace / relative) for relative in files}


def validate_prepared_root(harness: Path, workspace: Path, run_id: str, *, resuming: bool = False,
                           receipt_path: Path | None = None, provider_id: str = "codex") -> dict[str, Any]:
    harness, workspace = harness.resolve(), workspace.resolve()
    receipt_path = receipt_path or workspace / RECEIPT
    if not receipt_path.is_file():
        raise ValueError("ROOT setup must finish before CLI launch; pre-launch setup receipt is missing")
    receipt = read(receipt_path)
    if receipt.get("provider_id", "codex") != provider_id:
        raise ValueError("prelaunch receipt belongs to a different ROOT provider")
    expected = {"schema": SCHEMA, "run_id": run_id, "harness_dir": str(harness), "workspace": str(workspace)}
    if any(receipt.get(key) != value for key, value in expected.items()):
        raise ValueError("pre-launch setup receipt belongs to a different ROOT run")
    if receipt.get("status") != "PASS":
        raise ValueError("pre-launch harness setup did not pass")
    if receipt.get("hook_sha256") != check_installed(harness, workspace, allow_closed=resuming, provider_id=provider_id):
        raise ValueError("ROOT hook files changed after pre-launch setup")
    if receipt.get("harness_config_sha256") != digest(harness / "harness-config.json"):
        raise ValueError("harness configuration changed after pre-launch setup")
    health = sandbox_health(harness, workspace, provider_id)
    if receipt.get("windows_sandbox_health") != health:
        raise ValueError("Windows sandbox health changed after pre-launch setup")
    sys.path.insert(0, str(harness))
    from orchestrator_harness.public_checks import policy, validate_service
    if policy(harness) is not None:
        closed = resuming and read(workspace / ".harness-runtime/RUNTIME_STATE.json").get("state") == "CLOSED"
        service = validate_service(workspace, harness, runtime_closed=closed)
        expected_service = receipt.get("public_check_service")
        if closed and isinstance(expected_service, dict):
            expected_service = {**expected_service, "status": "STOPPED"}
        if expected_service != service:
            if not (workspace / ".agent-workspace/OPERATOR_PUBLIC_SERVICE_REPAIR.json").is_file():
                raise ValueError("public check service changed after pre-launch setup")
            from public_service_repair import validate_repair
            validate_repair(workspace, harness, receipt_path, receipt, service, closed=closed)
    return {"receipt_path": str(receipt_path), "receipt_sha256": digest(receipt_path), "prepared_at_utc": receipt["prepared_at_utc"]}


def prepare(harness: Path, workspace: Path, run_id: str, *, provider_id: str = "codex") -> dict[str, Any]:
    harness, workspace = harness.resolve(), workspace.resolve()
    health = sandbox_health(harness, workspace, provider_id)
    runtime = workspace / ".harness-runtime"
    if runtime.exists():
        # Only this exact run's successful preparation may be reused. Never
        # adopt an existing runtime or repeat setup in a live run.
        return validate_prepared_root(harness, workspace, run_id, provider_id=provider_id)
    config = read(harness / "harness-config.json")
    if Path(config.get("root_workspace", "")).resolve() != workspace:
        raise ValueError("harness configuration does not select this ROOT workspace")
    command = [sys.executable, "-B", "-m", "orchestrator_harness.operator_launch", "--json", "harness", "setup"]
    completed = subprocess.run(command, cwd=harness, capture_output=True, text=True, encoding="utf-8", timeout=120)
    try:
        result = json.loads(completed.stdout)
    except ValueError as exc:
        raise ValueError("native harness setup did not return a structured result") from exc
    if completed.returncode or not isinstance(result, dict) or result.get("ok") is not True:
        raise ValueError(f"native harness setup failed: {result}")
    hashes = check_installed(harness, workspace, provider_id=provider_id)
    sys.path.insert(0, str(harness))
    from orchestrator_harness.public_checks import start_service
    service = start_service(harness, workspace)
    receipt = {
        "schema": SCHEMA, "status": "PASS", "run_id": run_id,
        "provider_id": provider_id,
        "harness_dir": str(harness), "workspace": str(workspace),
        "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
        "setup_command": command, "setup_result": result,
        "hook_sha256": hashes,
        "harness_config_sha256": digest(harness / "harness-config.json"),
    }
    if health is not None:
        receipt["windows_sandbox_health"] = health
    if service is not None:
        receipt["public_check_service"] = service
    receipt_path = workspace / RECEIPT
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    with receipt_path.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    return validate_prepared_root(harness, workspace, run_id, provider_id=provider_id)


def prepare_continuation(harness: Path, workspace: Path, run_id: str, task_file: Path,
                         *, provider_id: str = "codex") -> dict[str, Any]:
    """Record one operator-approved continuation, reopening only a clean CLOSED runtime.

    This uses native harness setup, never Windows sandbox setup. Initial and
    earlier receipts stay immutable. A failed attempt cannot be silently repeated.
    """
    from types import SimpleNamespace
    from collect_codex_usage import prepare_resume

    harness, workspace = harness.resolve(), workspace.resolve()
    args = SimpleNamespace(resume_task_file=str(task_file.resolve()), continue_open_runtime=True)
    segment, number, session, _ = prepare_resume(args)
    if getattr(args, "provider_id", "codex") != provider_id:
        raise ValueError("continuation belongs to another ROOT provider")
    if not args.operator_assisted:
        raise ValueError("operator-assisted continuation must be declared at the initial launch")
    if (Path(args.harness_dir).resolve() != harness or Path(args.cwd).resolve() != workspace
            or args.run_id != run_id):
        raise ValueError("continuation does not belong to this run/workspace/harness")
    previous_dir = segment.parent.parent if number == 2 else segment.parent / f"{number - 1:04d}"
    previous = read(previous_dir / "launch.json")
    previous_ref = previous["root_prelaunch"]
    previous_receipt = Path(previous_ref["receipt_path"])
    if digest(previous_receipt) != previous_ref["receipt_sha256"]:
        raise ValueError("previous prelaunch receipt changed")
    target = Path(args.continuation_receipt)
    if target.is_file():
        return validate_prepared_root(harness, workspace, run_id, receipt_path=target, provider_id=provider_id)
    validate_prepared_root(harness, workspace, run_id, resuming=True, receipt_path=previous_receipt, provider_id=provider_id)
    attempt = target.parent / "attempt.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    runtime = workspace / ".harness-runtime"
    state = read(runtime / "RUNTIME_STATE.json")["state"]
    archive = {}
    for relative in ("RUNTIME_STATE.json", "monitor/MONITOR.json",
                     "manager/QUEUE.json", "operator-only/public-check-service/service.json"):
        source = runtime / relative
        if source.is_file():
            archive[relative] = read(source)
    checkpoint = {
        "schema": "operator-continuation-preparation/v1", "run_id": run_id,
        "segment_number": number, "root_session_id": session,
        "continuation_reason": "quota_recovery" if getattr(args, "quota_resume", False) else "workflow_audit",
        "previous_receipt": previous_ref, "runtime_before": state,
        "watchdog_deadline_utc": args.absolute_deadline_utc,
        "runtime_records_before": archive,
        "root_revision": subprocess.check_output(
            ["git", "-C", str(workspace), "rev-parse", "HEAD"], text=True).strip(),
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    with attempt.open("x", encoding="utf-8") as stream:
        json.dump(checkpoint, stream, indent=2)
        stream.write("\n")
    first = Path(task_file).resolve().parent / "first-reported-finish.json"
    if not first.exists() and not getattr(args, "quota_resume", False):
        with first.open("x", encoding="utf-8") as stream:
            json.dump(checkpoint, stream, indent=2)
            stream.write("\n")
    result = None
    if state == "CLOSED":
        command = [sys.executable, "-B", "-m", "orchestrator_harness.operator_launch",
                   "--json", "harness", "setup"]
        completed = subprocess.run(command, cwd=harness, capture_output=True, text=True,
                                   encoding="utf-8", timeout=120)
        result = {"command": command, "exit_code": completed.returncode,
                  "stdout": completed.stdout, "stderr": completed.stderr}
        (target.parent / "native-reopen.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        if completed.returncode or json.loads(completed.stdout).get("ok") is not True:
            raise ValueError("native continuation reopen failed; preserve and diagnose before another launch")
    from orchestrator_harness.public_checks import start_service
    service = start_service(harness, workspace, restart_stopped=state == "CLOSED")
    receipt = {
        **read(previous_receipt), "prepared_at_utc": datetime.now(timezone.utc).isoformat(),
        "hook_sha256": check_installed(harness, workspace, provider_id=provider_id),
        "harness_config_sha256": digest(harness / "harness-config.json"),
        "continuation": {"segment_number": number, "root_session_id": session,
                         "previous_receipt": previous_ref, "checkpoint_path": str(attempt),
                         "native_reopen": state == "CLOSED"},
    }
    if service is not None:
        receipt["public_check_service"] = service
    with target.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")
    return validate_prepared_root(harness, workspace, run_id, receipt_path=target, provider_id=provider_id)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harness-dir", required=True, type=Path)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--resume-task-file", type=Path)
    parser.add_argument("--provider", choices=("codex", "claude-code"), default="codex")
    args = parser.parse_args()
    try:
        result = (prepare_continuation(args.harness_dir, args.workspace, args.run_id, args.resume_task_file, provider_id=args.provider)
                  if args.resume_task_file else prepare(args.harness_dir, args.workspace, args.run_id, provider_id=args.provider))
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        print(f"ROOT pre-launch setup failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
