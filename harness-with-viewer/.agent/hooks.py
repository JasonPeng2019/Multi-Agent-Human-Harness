"""Fast Windows implementations of the portable SessionStart and PreToolUse hooks."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DELETE_COMMAND = re.compile(r"(?i)^\s*(?:&\s*)?(?:Remove-Item|rm|rmdir|rd)\b")
RECURSIVE_DELETE = re.compile(r"(?i)(?:-Recurse\b|\s-(?:[A-Za-z]*r[A-Za-z]*f?|[A-Za-z]*f[A-Za-z]*r)[A-Za-z]*\b)")
GIT_MUTATION = re.compile(
    r"""(?ix)
    ^\s*(?:&\s*)?(?:Remove-Item|rm|rmdir|rd|Move-Item|mv|move|Set-Content|Add-Content|Out-File|New-Item)\b.*(?:^|[\\/\s"'])\.git(?:[\\/\s"']|$)
    |
    (?:>|>>|2>)\s*["']?[^\r\n;|]*[\\/]?\.git(?:[\\/]|$)
    """
)
AGENT_SESSION = re.compile(
    r"(?i)\bcodex(?:\.exe)?\s+exec\b|\bclaude(?:\.exe)?\s+(?:-p|--print)\b|"
    r"\.agent[\\/](?:launch-agent\.(?:ps1|sh)|multi_agent\.py\s+(?:launch|supervise))\b"
)
BOUNDED_WRAPPER = re.compile(r"(?i)\.agent[\\/]run-bounded\.(?:ps1|sh)\b")


def emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, separators=(",", ":")))


def deny(reason: str) -> None:
    emit(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        }
    )


def read_payload() -> tuple[dict[str, Any] | None, str]:
    raw = sys.stdin.read()
    try:
        value = json.loads(raw or "{}")
    except json.JSONDecodeError:
        return None, raw
    return (value if isinstance(value, dict) else None), raw


def repository_root(payload: dict[str, Any]) -> Path:
    start = payload.get("cwd")
    if not isinstance(start, str) or not start:
        start = str(Path.cwd())
    try:
        completed = subprocess.run(
            ["git", "-C", start, "rev-parse", "--show-toplevel"],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return ROOT
    if completed.returncode == 0 and completed.stdout.strip():
        return Path(completed.stdout.strip()).resolve(strict=False)
    return ROOT


def session_start(root: Path) -> None:
    context = [
        "Portable workflow active: use repository instructions and relevant skills before acting.",
        "Route only finite non-agent commands explicitly selected in .agent/bounded-commands.txt through .agent/run-bounded.ps1.",
    ]
    if (root / ".agent" / "verify.toml").is_file():
        context.append("A local verification override exists at .agent/verify.toml.")
    handoff = root / "HANDOFF.md"
    if handoff.is_file():
        try:
            preview = "\n".join(handoff.read_text(encoding="utf-8").splitlines()[:30])[:3000]
        except OSError:
            preview = ""
        context.append(f"HANDOFF.md exists. Read it before continuing.\n{preview}")
    emit(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": "\n".join(context),
            }
        }
    )


def command_segments(command: str) -> list[str]:
    return [segment for segment in re.split(r"[;\r\n]", command) if segment.strip()]


def command_tokens(command: str) -> list[str]:
    return [token.strip("\"'").rstrip("\\/") for token in re.findall(r"""(?:"[^"]*"|'[^']*'|\S+)""", command)]


def is_dangerous_delete(command: str, root: Path) -> bool:
    protected = {
        str(root.resolve(strict=False)).rstrip("\\/").casefold(),
        Path(root.anchor).as_posix().rstrip("\\/").casefold() if root.anchor else "",
        os.path.expanduser("~").rstrip("\\/").casefold(),
    }
    for segment in command_segments(command):
        if not DELETE_COMMAND.search(segment) or not RECURSIVE_DELETE.search(segment):
            continue
        if re.search(r"(?i)(?:\$HOME|\$env:USERPROFILE|%USERPROFILE%)(?:[\\/]\*)?(?:\s|$)", segment):
            return True
        for candidate in command_tokens(segment):
            folded = candidate.casefold()
            if candidate in {"/", "~"} or re.fullmatch(r"(?i)[A-Z]:", candidate):
                return True
            if folded in protected or folded in {f"{path}\\*" for path in protected if path} or folded in {
                f"{path}/*" for path in protected if path
            }:
                return True
    return False


def is_direct_git_mutation(command: str) -> bool:
    return any(GIT_MUTATION.search(segment) is not None for segment in command_segments(command))


def is_configured_bounded_command(command: str, root: Path) -> bool:
    config = root / ".agent" / "bounded-commands.txt"
    if not config.is_file():
        return False
    try:
        fragments = config.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    lowered = command.casefold()
    return any(fragment.strip() and not fragment.lstrip().startswith("#") and fragment.strip().casefold() in lowered for fragment in fragments)


def optional_policy(raw: str, root: Path) -> str | None:
    config = root / ".agent" / "bounded-script-policy.json"
    if not config.is_file():
        return None
    try:
        value = json.loads(config.read_text(encoding="utf-8"))
        if not isinstance(value, dict) or not isinstance(value.get("enabled"), bool):
            raise ValueError("the enabled property must be a Boolean")
        if not value["enabled"]:
            return None
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return f"Optional bounded script policy configuration error: {exc}. Fix it or disable the policy."

    adapter = root / ".agent" / "bounded-script-adapter.py"
    if not adapter.is_file():
        return "Optional bounded script policy is enabled but .agent/bounded-script-adapter.py is missing. Restore it or disable the policy."
    executable = shutil.which("python") or shutil.which("py")
    if executable is None:
        return "Optional bounded script policy is enabled but Python 3 is unavailable to the hook. Install Python, restore the adapter, or disable the policy."
    arguments = [executable]
    if Path(executable).name.casefold() in {"py", "py.exe"}:
        arguments.append("-3")
    try:
        completed = subprocess.run(
            [*arguments, str(adapter), "pre-tool-use"],
            input=raw,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    except OSError as exc:
        return f"Optional bounded script policy could not run: {exc}. Fix it or disable the policy."
    output = completed.stdout.strip()
    if completed.returncode != 0:
        return f"Optional bounded script policy could not run: {output}. Fix it or disable the policy."
    if not output:
        return None
    try:
        decision = json.loads(output)
    except json.JSONDecodeError:
        return "Optional bounded script policy returned malformed output. Fix it or disable the policy."
    if isinstance(decision, dict) and decision.get("hookSpecificOutput", {}).get("permissionDecision") == "deny":
        print(output)
        return ""
    return None


def pre_tool_use(payload: dict[str, Any], raw: str, root: Path) -> None:
    tool_input = payload.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else ""
    if not isinstance(command, str) or not command:
        return
    agent_session = AGENT_SESSION.search(command) is not None
    if not agent_session:
        policy_result = optional_policy(raw, root)
        if policy_result is not None:
            if policy_result:
                deny(policy_result)
            return
    if is_dangerous_delete(command, root):
        deny("Blocked a recursive deletion aimed at a filesystem root, home directory, or repository root. Resolve and select the intended narrower target.")
    elif is_direct_git_mutation(command):
        deny("Blocked direct mutation of .git internals. Use Git commands for repository metadata operations.")
    elif agent_session and BOUNDED_WRAPPER.search(command):
        deny("Agent and subagent sessions must remain unbounded. Launch them directly; reserve .agent/run-bounded.ps1 for finite commands explicitly listed in .agent/bounded-commands.txt.")
    elif not agent_session and BOUNDED_WRAPPER.search(command) is None and is_configured_bounded_command(command, root):
        deny("This configured long-running command must run through .agent/run-bounded.ps1 with a justified runtime bound.")


def main(argv: list[str]) -> int:
    if argv != ["session-start"] and argv != ["pre-tool-use"]:
        emit({"systemMessage": "Portable workflow hook received an unknown event and took no action."})
        return 0
    payload, raw = read_payload()
    if payload is None:
        emit({"systemMessage": "Portable workflow hook received malformed JSON and took no action."})
        return 0
    root = repository_root(payload)
    if argv[0] == "session-start":
        session_start(root)
    else:
        pre_tool_use(payload, raw, root)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as exc:
        emit({"systemMessage": f"Portable workflow hook failed safely and took no action: {exc}"})
