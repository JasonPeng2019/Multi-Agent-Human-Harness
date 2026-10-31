#!/usr/bin/env python3
"""Provider-neutral delegated-agent launcher.

The launcher deliberately knows nothing about a particular AI provider. A repository
declares an argument-vector command for each locally installed CLI and selects the
role to give that command. It writes a durable task card, runs the CLI without a
shell, keeps agent sessions unbounded, and records the terminal result.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from string import Formatter
from typing import Any, Iterator


SCHEMA = "portable-multi-agent/v2"
ROLE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
ALLOWED_TOKENS = frozenset({"prompt_file", "role", "task_id", "workspace", "delegation_dir"})


class MultiAgentError(RuntimeError):
    """Raised for an invalid delegation request or launcher state."""


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MultiAgentError(f"cannot read JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise MultiAgentError(f"{path} must contain a JSON object")
    return value


def require_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise MultiAgentError(f"{label} must be a non-empty string")
    return value


def require_positive_int(value: object, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise MultiAgentError(f"{label} must be a positive integer")
    return value


def resolve_config(value: str | None, start: Path) -> Path:
    if value:
        configured = Path(value)
        return (start / configured).resolve() if not configured.is_absolute() else configured.resolve()
    for candidate_root in (start, *start.parents):
        candidate = candidate_root / ".agent" / "multi-agent.json"
        if candidate.is_file():
            return candidate
    raise MultiAgentError("cannot find .agent/multi-agent.json; use --config to select one")


def validate_config(config_path: Path) -> dict[str, Any]:
    config = read_json(config_path)
    if config.get("schema") != SCHEMA:
        raise MultiAgentError(f"{config_path} must use schema {SCHEMA}")
    defaults = config.get("defaults")
    if not isinstance(defaults, dict):
        raise MultiAgentError("defaults must be an object")
    for field in ("heartbeat_interval_seconds", "max_parallel_agents"):
        require_positive_int(defaults.get(field), f"defaults.{field}")
    runtime_directory = require_string(defaults.get("runtime_directory"), "defaults.runtime_directory")
    runtime_path = Path(runtime_directory)
    if runtime_path.is_absolute() or ".." in runtime_path.parts:
        raise MultiAgentError("defaults.runtime_directory must be a relative path inside the workspace")
    agents = config.get("agents")
    if not isinstance(agents, dict) or not agents:
        raise MultiAgentError("agents must be a non-empty object")
    for name, agent in agents.items():
        if not isinstance(name, str) or not ROLE_NAME.fullmatch(name):
            raise MultiAgentError(f"invalid agent name: {name!r}")
        if not isinstance(agent, dict):
            raise MultiAgentError(f"agents.{name} must be an object")
        if not isinstance(agent.get("enabled"), bool):
            raise MultiAgentError(f"agents.{name}.enabled must be true or false")
        command = agent.get("command")
        if not isinstance(command, list) or not command or not all(isinstance(item, str) and item for item in command):
            raise MultiAgentError(f"agents.{name}.command must be a non-empty array of non-empty strings")
        validate_tokens(command, f"agents.{name}.command")
        if not any("{prompt_file}" in item for item in command):
            raise MultiAgentError(f"agents.{name}.command must include {{prompt_file}} so the worker receives its task card")
        roles = agent.get("roles")
        if not isinstance(roles, list) or not roles or not all(
            isinstance(role, str) and ROLE_NAME.fullmatch(role) for role in roles
        ):
            raise MultiAgentError(f"agents.{name}.roles must be a non-empty array of role names")
        environment = agent.get("environment")
        if not isinstance(environment, dict) or not all(
            isinstance(key, str)
            and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key)
            and isinstance(item, str)
            for key, item in environment.items()
        ):
            raise MultiAgentError(f"agents.{name}.environment must map environment names to strings")
    return config


def validate_tokens(values: list[str], label: str) -> None:
    for value in values:
        for _, field_name, format_spec, conversion in Formatter().parse(value):
            if field_name is None:
                continue
            if format_spec or conversion or field_name not in ALLOWED_TOKENS:
                raise MultiAgentError(f"{label} has an unsupported placeholder in {value!r}")


def parse_role(path: Path) -> tuple[dict[str, str], str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise MultiAgentError(f"cannot read role definition {path}: {exc}") from exc
    if not text.startswith("---\n"):
        raise MultiAgentError(f"role definition {path} must start with YAML-style metadata")
    try:
        metadata_text, body = text[4:].split("\n---\n", 1)
    except ValueError as exc:
        raise MultiAgentError(f"role definition {path} has no closing metadata separator") from exc
    metadata: dict[str, str] = {}
    for line in metadata_text.splitlines():
        key, separator, value = line.partition(":")
        if not separator or not key.strip() or not value.strip():
            raise MultiAgentError(f"role definition {path} has malformed metadata")
        metadata[key.strip()] = value.strip()
    if metadata.get("write_access") not in {"true", "false"}:
        raise MultiAgentError(f"role definition {path} must set write_access to true or false")
    if not metadata.get("default_scope"):
        raise MultiAgentError(f"role definition {path} must set default_scope")
    return metadata, body.strip()


def workspace_for(config_path: Path) -> Path:
    if config_path.parent.name != ".agent":
        raise MultiAgentError("multi-agent config must live directly inside .agent")
    return config_path.parent.parent.resolve()


def runtime_root(config: dict[str, Any], workspace: Path) -> Path:
    return workspace / str(config["defaults"]["runtime_directory"])


def delegation_id(task: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", task).strip("-").lower()[:48] or "delegation"
    return f"{slug}-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{uuid.uuid4().hex[:8]}"


def inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def expand_vector(command: list[str], mapping: dict[str, str]) -> list[str]:
    try:
        return [item.format(**mapping) for item in command]
    except (KeyError, ValueError) as exc:
        raise MultiAgentError(f"cannot expand agent command: {exc}") from exc


def resolve_bash(command: list[str]) -> list[str]:
    """Resolve a literal leading "bash" to a real Git for Windows bash.

    subprocess.Popen on Windows delegates to CreateProcess, which always
    checks system directories such as System32 before consulting PATH. When
    WSL is installed, that means a bare "bash" resolves to the WSL launcher
    shim at C:\\Windows\\System32\\bash.exe no matter how PATH is ordered.
    That shim cannot interpret a Windows-style path, so any command entry
    piping a repository path through bash would silently break. Substitute a
    located Git Bash when one exists; otherwise leave the command unchanged
    and let the normal launch-failure path report the real error.
    """
    if os.name != "nt" or not command or command[0] != "bash":
        return command
    roots = [os.environ.get("ProgramFiles"), os.environ.get("ProgramW6432"), os.environ.get("LocalAppData")]
    for root in roots:
        if not root:
            continue
        for suffix in ("Git/bin/bash.exe", "Programs/Git/bin/bash.exe"):
            candidate = Path(root) / suffix
            if candidate.is_file():
                return [str(candidate), *command[1:]]
    return command


def active_delegation_count(root: Path) -> int:
    count = 0
    for status_path in root.glob("*/status.json"):
        try:
            state = read_json(status_path).get("state")
        except MultiAgentError:
            continue
        if state in {"QUEUED", "LAUNCHING", "RUNNING"}:
            count += 1
    return count


@contextmanager
def launch_lock(root: Path) -> Iterator[None]:
    lock = root / ".launch-lock"
    deadline = time.monotonic() + 5
    while True:
        try:
            lock.mkdir(parents=True)
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise MultiAgentError("another delegation launch is still preparing; try again")
            time.sleep(0.05)
    try:
        yield
    finally:
        try:
            lock.rmdir()
        except OSError:
            pass


def status_path(delegation_dir: Path) -> Path:
    return delegation_dir / "status.json"


def update_status(delegation_dir: Path, new_state: str, **extra: Any) -> dict[str, Any]:
    path = status_path(delegation_dir)
    value = read_json(path) if path.exists() else {"schema": "portable-delegation-status/v1"}
    value.update(extra)
    value["state"] = new_state
    value["updated_at"] = utc_now()
    write_json(path, value)
    return value


def build_prompt(
    *,
    role: str,
    role_body: str,
    task_id: str,
    task: str,
    scope: str,
    owner: str,
    write_access: bool,
    workspace: Path,
    working_directory: Path,
    acceptance_check: str,
) -> str:
    authority = "You may edit only the assigned write boundary." if write_access else "Read-only: do not edit files."
    return f"""# Delegated agent task

Role: {role}
Delegation ID: {task_id}
Workspace: {workspace}
Working directory: {working_directory}
Authority: {authority}
Owner: {owner or 'primary agent'}
Scope: {scope}
Acceptance check: {acceptance_check or 'Report the evidence needed to assess completion.'}

## Objective

{task}

## Role guidance

{role_body}

## Return contract

Return a concise summary containing: completed outcome or findings; changed files
(or "none"); commands/checks run and their results; assumptions; integration
notes; and unresolved risks. Do not commit, push, merge, or alter another
delegation's area unless this task explicitly authorizes it.
"""


def prepare_delegation(args: argparse.Namespace) -> tuple[dict[str, Any], Path, dict[str, Any], dict[str, str], str]:
    start = Path.cwd().resolve()
    config_path = resolve_config(args.config, start)
    config = validate_config(config_path)
    workspace = workspace_for(config_path)
    agent_name = args.agent
    agents = config["agents"]
    if agent_name not in agents:
        raise MultiAgentError(f"unknown agent {agent_name!r}; use the configured command entry")
    agent = agents[agent_name]
    if not agent["enabled"]:
        raise MultiAgentError(f"agent {agent_name!r} is disabled; review its command entry before enabling it")
    if agent["command"][0].startswith("REPLACE_WITH_"):
        raise MultiAgentError(f"agent {agent_name!r} still has a placeholder executable")
    role_name = args.role
    if role_name not in agent["roles"]:
        raise MultiAgentError(f"agent {agent_name!r} is not configured for role {role_name!r}")
    role_path = workspace / ".agent" / "roles" / f"{role_name}.md"
    metadata, role_body = parse_role(role_path)
    working_directory = Path(args.working_directory).resolve()
    if not working_directory.is_dir():
        raise MultiAgentError(f"working directory does not exist: {working_directory}")
    write_access = metadata["write_access"] == "true"
    if write_access and inside(working_directory, workspace) and not args.allow_shared_workspace:
        raise MultiAgentError(
            "a writing role needs an isolated working directory outside the main workspace; pass a worktree or explicitly use --allow-shared-workspace"
        )
    heartbeat = args.heartbeat_interval_seconds or int(config["defaults"]["heartbeat_interval_seconds"])
    require_positive_int(heartbeat, "heartbeat interval")
    if heartbeat > 60:
        raise MultiAgentError("heartbeat interval must not exceed 60 seconds")
    task_id = args.id or delegation_id(args.task)
    if not ROLE_NAME.fullmatch(task_id):
        raise MultiAgentError("delegation ID may contain only letters, numbers, dot, underscore, and hyphen")
    scope = args.scope or metadata["default_scope"]
    root = runtime_root(config, workspace)
    delegation_dir = root / task_id
    if delegation_dir.exists():
        raise MultiAgentError(f"delegation ID already exists: {task_id}")
    prompt_path = delegation_dir / "prompt.md"
    prompt = build_prompt(
        role=role_name,
        role_body=role_body,
        task_id=task_id,
        task=args.task,
        scope=scope,
        owner=args.owner,
        write_access=write_access,
        workspace=workspace,
        working_directory=working_directory,
        acceptance_check=args.acceptance_check,
    )
    mapping = {
        # Forward slashes here (not str(), which is backslash-separated on
        # Windows): these values are substituted into an external command's
        # argv. A worker invoked through bash (Git Bash on Windows, required
        # for Claude Code's own hook execution, or a POSIX host) reparses its
        # argv and treats a backslash as an escape character, silently
        # corrupting a Windows-style path. Forward-slash Windows paths remain
        # fully valid for every consumer used here (pathlib, PowerShell,
        # native executables), so this is unconditionally safe.
        "prompt_file": prompt_path.as_posix(),
        "role": role_name,
        "task_id": task_id,
        "workspace": workspace.as_posix(),
        "delegation_dir": delegation_dir.as_posix(),
    }
    command = resolve_bash(expand_vector(agent["command"], mapping))
    record = {
        "schema": "portable-delegation/v1",
        "id": task_id,
        "created_at": utc_now(),
        "agent": agent_name,
        "role": role_name,
        "task": args.task,
        "scope": scope,
        "owner": args.owner or None,
        "acceptance_check": args.acceptance_check or None,
        "write_access": write_access,
        "workspace": str(workspace),
        "working_directory": str(working_directory),
        "command": command,
        "environment": agent["environment"],
        "execution_mode": "unbounded",
        "heartbeat_interval_seconds": heartbeat,
        "prompt_path": str(prompt_path),
        "stdout_path": str(delegation_dir / "worker.stdout.log"),
        "stderr_path": str(delegation_dir / "worker.stderr.log"),
        "result_path": str(delegation_dir / "result.json"),
    }
    return config, workspace, record, mapping, prompt


def launch(args: argparse.Namespace) -> int:
    config, workspace, record, _mapping, prompt = prepare_delegation(args)
    delegation_dir = Path(str(record["prompt_path"])).parent
    if args.dry_run:
        print(json.dumps({"state": "PREVIEW", "delegation": record, "prompt": prompt}, indent=2))
        return 0
    root = runtime_root(config, workspace)
    with launch_lock(root):
        if active_delegation_count(root) >= int(config["defaults"]["max_parallel_agents"]):
            raise MultiAgentError("configured max_parallel_agents is already active")
        delegation_dir.mkdir(parents=True)
        Path(str(record["prompt_path"])).write_text(prompt, encoding="utf-8")
        write_json(delegation_dir / "delegation.json", record)
        update_status(delegation_dir, "QUEUED", id=record["id"], agent=record["agent"], role=record["role"])
    if args.background:
        supervisor_stdout = (delegation_dir / "supervisor.stdout.log").open("w", encoding="utf-8")
        supervisor_stderr = (delegation_dir / "supervisor.stderr.log").open("w", encoding="utf-8")
        popen_args: dict[str, Any] = {
            "cwd": str(delegation_dir),
            "stdout": supervisor_stdout,
            "stderr": supervisor_stderr,
        }
        if os.name == "nt":
            popen_args["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        else:
            popen_args["start_new_session"] = True
        process = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "supervise", "--record", str(delegation_dir / "delegation.json")],
            **popen_args,
        )
        supervisor_stdout.close()
        supervisor_stderr.close()
        print(f"QUEUED id={record['id']} supervisor_pid={process.pid} directory={delegation_dir}")
        return 0
    return supervise_record(delegation_dir / "delegation.json")


def supervise_record(record_path: Path) -> int:
    record = read_json(record_path)
    if record.get("schema") != "portable-delegation/v1":
        raise MultiAgentError(f"{record_path} is not a portable delegation record")
    delegation_dir = record_path.parent.resolve()
    update_status(delegation_dir, "LAUNCHING", supervisor_pid=os.getpid())
    command = record.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(item, str) and item for item in command):
        raise MultiAgentError("delegation record has an invalid command vector")
    working_directory = Path(require_string(record.get("working_directory"), "working_directory"))
    if not working_directory.is_dir():
        raise MultiAgentError(f"working directory no longer exists: {working_directory}")
    for field in ("stdout_path", "stderr_path", "result_path"):
        if not inside(Path(require_string(record.get(field), field)), delegation_dir):
            raise MultiAgentError(f"delegation {field} must remain inside its delegation directory")
    environment = record.get("environment")
    if not isinstance(environment, dict) or not all(isinstance(key, str) and isinstance(value, str) for key, value in environment.items()):
        raise MultiAgentError("delegation environment is invalid")
    if record.get("execution_mode") != "unbounded":
        raise MultiAgentError("delegation record must use unbounded execution_mode")
    heartbeat = require_positive_int(record.get("heartbeat_interval_seconds"), "heartbeat_interval_seconds")
    stdout_path = Path(str(record["stdout_path"]))
    stderr_path = Path(str(record["stderr_path"]))
    started_at = utc_now()
    started = time.monotonic()
    child_env = os.environ.copy()
    child_env.update(environment)
    popen_args: dict[str, Any] = {
        "cwd": str(working_directory),
        "stdout": stdout_path.open("w", encoding="utf-8"),
        "stderr": stderr_path.open("w", encoding="utf-8"),
        "env": child_env,
    }
    if os.name == "nt":
        popen_args["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        popen_args["start_new_session"] = True
    try:
        process = subprocess.Popen(command, **popen_args)
    except OSError as exc:
        popen_args["stdout"].close()
        popen_args["stderr"].close()
        result = {
            "schema": "portable-delegation-result/v1",
            "state": "LAUNCH_FAILED",
            "error": str(exc),
            "started_at": started_at,
            "finished_at": utc_now(),
            "exit_code": 127,
        }
        write_json(Path(str(record["result_path"])), result)
        update_status(delegation_dir, "LAUNCH_FAILED", **result)
        print(f"LAUNCH_FAILED id={record['id']} error={exc}", file=sys.stderr)
        return 127
    update_status(delegation_dir, "RUNNING", worker_pid=process.pid, started_at=started_at)
    while process.poll() is None:
        elapsed = round(time.monotonic() - started, 3)
        print(f"RUNNING id={record['id']} pid={process.pid} elapsed_seconds={elapsed}", flush=True)
        try:
            process.wait(timeout=heartbeat)
        except subprocess.TimeoutExpired:
            pass
    exit_code = process.returncode if process.returncode is not None else 1
    state = "PASSED" if exit_code == 0 else "FAILED"
    popen_args["stdout"].close()
    popen_args["stderr"].close()
    finished_at = utc_now()
    result = {
        "schema": "portable-delegation-result/v1",
        "id": record["id"],
        "state": state,
        "exit_code": exit_code,
        "execution_mode": "unbounded",
        "started_at": started_at,
        "finished_at": finished_at,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "worker_pid": process.pid,
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
    }
    write_json(Path(str(record["result_path"])), result)
    update_status(delegation_dir, state, **result)
    print(f"{state} id={record['id']} exit_code={exit_code} result={record['result_path']}")
    return exit_code


def command_status(args: argparse.Namespace) -> int:
    config_path = resolve_config(args.config, Path.cwd().resolve())
    config = validate_config(config_path)
    root = runtime_root(config, workspace_for(config_path))
    if args.id:
        path = root / args.id / "status.json"
        if not path.is_file():
            raise MultiAgentError(f"unknown delegation ID: {args.id}")
        print(json.dumps(read_json(path), indent=2, sort_keys=True))
        return 0
    records = []
    if root.exists():
        for path in sorted(root.glob("*/status.json")):
            value = read_json(path)
            records.append({"id": path.parent.name, "state": value.get("state"), "role": value.get("role"), "agent": value.get("agent")})
    print(json.dumps(records, indent=2))
    return 0


def command_validate(args: argparse.Namespace) -> int:
    path = resolve_config(args.config, Path.cwd().resolve())
    config = validate_config(path)
    workspace = workspace_for(path)
    for role in sorted({role for agent in config["agents"].values() for role in agent["roles"]}):
        parse_role(workspace / ".agent" / "roles" / f"{role}.md")
    print(f"VALID config={path} agents={len(config['agents'])}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch provider-neutral delegated CLI agents.")
    parser.add_argument("--config", help="Path to .agent/multi-agent.json (default: find upward from cwd)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate", help="Validate command entries and role templates.")
    launch_parser = commands.add_parser("launch", help="Create a delegation task card and run its configured CLI.")
    launch_parser.add_argument("--agent", required=True)
    launch_parser.add_argument("--role", required=True)
    launch_parser.add_argument("--task", required=True)
    launch_parser.add_argument("--id")
    launch_parser.add_argument("--working-directory", default=str(Path.cwd()))
    launch_parser.add_argument("--scope", default="")
    launch_parser.add_argument("--owner", default="")
    launch_parser.add_argument("--acceptance-check", default="")
    launch_parser.add_argument("--heartbeat-interval-seconds", type=int, default=0)
    launch_parser.add_argument("--background", action="store_true")
    launch_parser.add_argument("--dry-run", action="store_true")
    launch_parser.add_argument("--allow-shared-workspace", action="store_true")
    status_parser = commands.add_parser("status", help="Show one delegation status or all known delegations.")
    status_parser.add_argument("--id")
    supervise_parser = commands.add_parser("supervise", help=argparse.SUPPRESS)
    supervise_parser.add_argument("--record", required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "validate":
            return command_validate(args)
        if args.command == "launch":
            return launch(args)
        if args.command == "status":
            return command_status(args)
        return supervise_record(Path(args.record).resolve())
    except MultiAgentError as exc:
        parser.exit(2, f"multi-agent: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
