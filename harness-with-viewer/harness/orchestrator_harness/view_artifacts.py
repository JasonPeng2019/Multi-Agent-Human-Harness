"""Bounded, read-only inspection of worker prompts, provider output and results."""
from __future__ import annotations

import json
import hashlib
import re
import shlex
from pathlib import Path
from typing import Any

from .view_feed import Block, prose_blocks

LIMIT = 512_000
_ESCAPE = re.compile(r'\x1b(?:\][^\x07]*(?:\x07|\x1b\\)|\[[0-?]*[ -/]*[@-~]|.)')


def safe_text(value: str) -> str:
    """Provider bytes are data, never terminal control sequences."""
    value = _ESCAPE.sub('', value)
    return ''.join(c if c in '\n\t' or c.isprintable() else '?' for c in value)


def read_text(path: Path, *, tail: bool = False) -> str:
    try:
        with path.open('rb') as handle:
            size = path.stat().st_size
            if tail and size > LIMIT:
                handle.seek(size - LIMIT)
                handle.readline()
            raw = handle.read(LIMIT)
        text = raw.decode('utf-8', errors='replace')
        if size > LIMIT:
            note = '[Display limited to 512 KB; full file: ' + str(path) + ']\n'
            text = note + text if tail else text + '\n' + note
        return safe_text(text)
    except OSError as exc:
        return f'[Unavailable: {path}: {exc.strerror}]'


def _pretty(value: Any) -> str:
    return value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False)


def _content(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(_content(item) for item in value)
    if isinstance(value, dict):
        if "text" in value:
            return str(value["text"])
        return "\n".join(f"{key.replace('_', ' ').capitalize()}: {_content(item)}" for key, item in value.items())
    return str(value) if value is not None else ""


def _command(value: Any) -> str:
    command = str(value)
    try:
        parts = shlex.split(command)
    except ValueError:
        return command
    if len(parts) == 3 and Path(parts[0]).name in ("sh", "bash", "zsh") and parts[1] in ("-c", "-lc"):
        return parts[2]
    return command


def _tool(name: str, data: dict[str, Any]) -> str:
    if name.lower() in ("bash", "shell", "run_shell_command"):
        return "### Command\n$ " + _command(data.get("command", data.get("cmd", "")))
    if name.lower() in ("edit", "write", "multiedit"):
        text = f"### {name} · {data.get('file_path', data.get('path', 'file'))}"
        for key, prefix in (("old_string", "- "), ("new_string", "+ "), ("content", "  ")):
            if key in data:
                text += "\n" + "\n".join(prefix + line for line in str(data[key]).splitlines())
        return text
    return f"### {name}\n" + _content(data)


def format_event(record: dict[str, Any]) -> str:
    """Present provider content, not transport metadata or event envelopes."""
    kind = record.get("type", "")
    item = record.get("item")
    if isinstance(item, dict):
        item_type = item.get("type")
        if item_type in ("agent_message", "reasoning"):
            return "### Agent\n" + str(item.get("text", ""))
        if item_type == "command_execution":
            status = item.get("status", "running")
            code = item.get("exit_code")
            ending = f"Exit {code}" if code is not None else str(status).replace('_', ' ')
            return ("### Command · " + ending + "\n$ " + _command(item.get("command", ""))
                    + "\n" + str(item.get("aggregated_output", "")))
        if item_type == "file_change":
            return "### File changes\n" + "\n".join(
                f"{change.get('kind', 'update')}  {change.get('path', '')}"
                for change in item.get("changes", []))
        if item_type in ("mcp_tool_call", "web_search", "todo_list"):
            fields = {key: value for key, value in item.items() if key not in ("id", "type")}
            return f"### {item_type.replace('_', ' ').title()}\n" + _content(fields)
        if item_type == "error":
            return "### Error\n" + str(item.get("message", ""))
        return ""
    message = record.get("message")
    if isinstance(message, dict) and isinstance(message.get("content"), list):
        parts = []
        for block in message["content"]:
            if not isinstance(block, dict):
                continue
            block_type = block.get("type")
            if block_type == "text":
                parts.append("### Agent\n" + str(block.get("text", "")))
            elif block_type == "tool_use":
                parts.append(_tool(str(block.get("name", "Tool")), block.get("input") or {}))
            elif block_type == "tool_result":
                title = "Tool error" if block.get("is_error") else "Tool output"
                parts.append(f"### {title}\n" + _content(block.get("content", "")))
            elif block_type == "thinking" and block.get("thinking"):
                parts.append("### Agent notes\n" + str(block["thinking"]))
        return "\n\n".join(parts)
    if kind == "result" and record.get("is_error"):
        return "### Error\n" + _content(record.get("result", record.get("errors", "Provider failed")))
    if kind in ("error", "turn.failed"):
        return "### Error\n" + _content(record.get("error", record.get("message", "Provider failed")))
    # Qwen stream-json messages/tools use a flatter event shape.
    if kind == "message" and record.get("role") == "assistant":
        return "### Agent\n" + _content(record.get("content", ""))
    if kind == "tool_use":
        return _tool(str(record.get("tool_name", "Tool")), record.get("parameters") or {})
    if kind == "tool_result":
        return "### Tool output\n" + _content(record.get("output", ""))
    return ""


def _transcript_blocks(path: Path) -> list[Block]:
    text = read_text(path, tail=True)
    events: list[dict[str, Any] | str] = []
    positions: dict[str, int] = {}
    final_message = ""
    notices: list[str] = []
    for line in text.splitlines():
        try:
            record = json.loads(line)
        except ValueError:
            # A live writer can end mid-record. Wait for the next refresh.
            if not line.lstrip().startswith(("{", "[")) or line.startswith(("[Display limited", "[Unavailable")):
                events.append(line)
            continue
        if not isinstance(record, dict):
            continue
        if record.get("type") == "result" and not record.get("is_error"):
            final_message = _content(record.get("result", ""))
        item = record.get("item")
        if isinstance(item, dict) and item.get("type") == "error":
            message = str(item.get("message", ""))
            if message.startswith(("Codex is ignoring", "`--dangerously-bypass-hook-trust` is enabled")):
                if message not in notices:
                    notices.append(message)
                continue
        identity = item.get("id") if isinstance(item, dict) else None
        if identity and identity in positions:
            events[positions[identity]] = record
        else:
            if identity:
                positions[identity] = len(events)
            events.append(record)
    blocks: list[Block] = []
    occurrences: dict[str, int] = {}
    for event in events:
        if isinstance(event, str):
            blocks.append(Block(f"{path}:diagnostic:{len(blocks)}", safe_text(event)))
            continue
        item = event.get("item") or {}
        message = event.get("message") or {}
        identity = (item.get("id") if isinstance(item, dict) else None) or (
            message.get("id") if isinstance(message, dict) else None) or event.get("uuid")
        if not identity:
            identity = hashlib.sha256(json.dumps(event, sort_keys=True).encode()).hexdigest()
        identity = str(identity)
        ordinal = occurrences.get(identity, 0)
        occurrences[identity] = ordinal + 1
        key = f"{path}:{identity}:{ordinal}"
        if isinstance(item, dict) and item.get("type") in ("agent_message", "reasoning"):
            blocks.extend(prose_blocks(key, safe_text(str(item.get("text", "")))))
        elif isinstance(message, dict) and isinstance(message.get("content"), list):
            for index, content in enumerate(message["content"]):
                if not isinstance(content, dict):
                    continue
                content_key = f"{key}:{index}"
                if content.get("type") in ("text", "thinking"):
                    body = content.get("text", content.get("thinking", ""))
                    title = "### Agent notes" if content.get("type") == "thinking" else "### Agent"
                    blocks.extend(prose_blocks(content_key, safe_text(str(body)), title))
                else:
                    rendered = format_event({"type": event.get("type"), "message": {"content": [content]}})
                    if rendered:
                        blocks.append(Block(content_key, safe_text(rendered)))
        elif event.get("type") == "message" and event.get("role") == "assistant":
            blocks.extend(prose_blocks(key, safe_text(_content(event.get("content", "")))))
        else:
            rendered = format_event(event)
            if rendered:
                blocks.append(Block(key, safe_text(rendered)))
    if final_message and final_message not in "".join(block.text for block in blocks):
        blocks.extend(prose_blocks(f"{path}:final", safe_text(final_message)))
    if notices:
        blocks.insert(0, Block(f"{path}:notices", safe_text("### Startup notices\n" + "\n".join(message.splitlines()[0] for message in notices))))
    return blocks or [Block(f"{path}:waiting", "Waiting for the agent to produce output…")]


def _transcript(path: Path, raw: bool = False) -> str:
    if raw:
        return read_text(path, tail=True)
    return "\n\n".join(block.render() for block in _transcript_blocks(path))


def output_blocks(lane: dict[str, Any]) -> list[Block]:
    if "_recorded" in lane:
        return [Block(**block) for block in lane["_recorded"]["blocks"]]
    if lane.get("role") == "root":
        return [Block("root-output", "ROOT’s prompt and terminal output are visible in the terminal CLI being used to run ROOT. ROOT’s terminal transcript is not recorded by this harness. Recorded communications are in Events.")]
    if not lane.get("worktree_path"):
        return [Block("preparing", "The agent has not started yet.")]
    aw = Path(lane["worktree_path"]) / ".agent-workspace"
    paths = lane.get("artifact_paths") or {}
    transcript = Path(paths.get("transcript_path") or aw / "provider-transcript.jsonl")
    stderr = Path(paths.get("stderr_path") or aw / "provider-stderr.txt")
    attempts = sorted((aw / "attempts").glob("attempt-*/provider-transcript.jsonl"),
                      key=lambda p: int(p.parent.name.split('-')[-1]) if p.parent.name.split('-')[-1].isdigit() else -1)
    files = [(transcript, stderr)] + [(p, p.parent / "provider-stderr.txt") for p in attempts]
    blocks = []
    for i, (output, errors) in enumerate(files):
        if len(files) > 1:
            blocks.append(Block(f"{output}:attempt", f"### Attempt {i + 1}"))
        if output.exists():
            blocks.extend(_transcript_blocks(output))
        else:
            blocks.append(Block(f"{output}:waiting", "Waiting for the agent to produce output…"))
        if errors.exists() and errors.stat().st_size:
            blocks.append(Block(f"{output}:stderr", "### Provider diagnostics\n" + read_text(errors, tail=True)))
    return blocks


def _final_response(aw: Path, paths: dict[str, Any]) -> str:
    """Read the actual last assistant message, not controller event markers."""
    initial = Path(paths.get("transcript_path") or aw / "provider-transcript.jsonl")
    attempts = sorted((aw / "attempts").glob("attempt-*/provider-transcript.jsonl"),
                      key=lambda p: int(p.parent.name.split('-')[-1]) if p.parent.name.split('-')[-1].isdigit() else -1)
    response = ""
    for path in [initial, *attempts]:
        if not path.is_file():
            continue
        for line in read_text(path, tail=True).splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if not isinstance(event, dict):
                continue
            item = event.get("item")
            if isinstance(item, dict) and item.get("type") == "agent_message" and item.get("text"):
                response = str(item["text"])
            message = event.get("message")
            if event.get("type") == "assistant" and isinstance(message, dict):
                text = "\n".join(str(block.get("text", "")) for block in message.get("content", [])
                                 if isinstance(block, dict) and block.get("type") == "text")
                if text:
                    response = text
            if event.get("type") == "result" and isinstance(event.get("result"), str) and event["result"]:
                response = event["result"]
    if response:
        return response
    path = aw / "last-message.txt"
    if path.is_file():
        text = read_text(path).strip()
        if text not in {"turn.completed", "turn.started", "item.completed", "result"}:
            return text
    return ""


def root_review_text(lane: dict[str, Any]) -> str:
    review = lane.get("root_review")
    if not review:
        return "### Root review\nNo verified root review has been recorded for this run yet."
    parts = ["### Root review", f"Verdict: {review['verdict']} · Decision: {review['approval']}",
             f"Reviewer: {review['reviewer']} · Reviewed: {review.get('reviewed_at', '')}",
             f"Reviewed commit: {review.get('commit', '')}",
             str(review.get("summary") or "No review summary recorded."), "### What was checked"]
    for item in review.get("evidence", []):
        if not isinstance(item, str):
            parts.append(_content(item))
            continue
        # Expand the demo's retained test report, without following arbitrary external paths.
        try:
            path = Path(item)
            if (path.is_absolute() and path.resolve().is_relative_to(Path(review['workspace']).resolve())
                    and path.suffix in ('.txt', '.log') and path.is_file()):
                parts.extend([f"Test report: {path.name}", read_text(path)])
                continue
        except (OSError, ValueError):
            pass
        parts.append(item)
    return "\n\n".join(parts)


def panel_text(lane: dict[str, Any], panel: str) -> str:
    if "_recorded" in lane and panel in ("prompt", "result"):
        return lane["_recorded"][panel]
    if lane.get("role") == "root" and panel != "events":
        if panel == "prompt":
            return "ROOT’s prompt and terminal output are visible in the terminal CLI being used to run ROOT. The conversation prompt is not recorded by this harness. Assignments sent to agents are in Events → Outbox."
        if panel == "output":
            return output_blocks(lane)[0].text
        return "### ROOT review results\n\n" + "\n\n".join(
            "### " + worker['lane_id'] + "\n\n" + root_review_text(worker)
            for worker in lane.get('workers', []))
    if not lane.get("worktree_path"):
        return "The agent has not started yet."
    if panel == "events":
        from .view_events import mailbox_text
        return mailbox_text(lane)
    worktree = Path(lane["worktree_path"])
    aw = worktree / ".agent-workspace"
    paths = lane.get("artifact_paths") or {}
    if panel == "prompt":
        initial = aw / "worker-prompt.md"
        if not initial.is_file():
            initial = aw / "prompt.md"
        files = [initial] + sorted((aw / "attempts").glob("correction-prompt-*.md"),
                                  key=lambda p: int(p.stem.split('-')[-1]) if p.stem.split('-')[-1].isdigit() else -1)
        return "\n\n".join(
            ("### Prompt sent to agent" if i == 0 else f"### Correction prompt {i}") + "\n" + read_text(path)
            for i, path in enumerate(files))
    if panel == "output":
        return "\n\n".join(block.render() for block in output_blocks(lane))
    if panel == "raw":
        transcript = Path(paths.get("transcript_path") or aw / "provider-transcript.jsonl")
        stderr = Path(paths.get("stderr_path") or aw / "provider-stderr.txt")
        attempts = sorted((aw / "attempts").glob("attempt-*/provider-transcript.jsonl"),
                          key=lambda p: int(p.parent.name.split('-')[-1]) if p.parent.name.split('-')[-1].isdigit() else -1)
        files = [(transcript, stderr)] + [(p, p.parent / "provider-stderr.txt") for p in attempts]
        sections = []
        for i, (output, errors) in enumerate(files):
            if len(files) > 1:
                sections.append(f"### Attempt {i + 1}")
            if output.exists():
                sections.append(_transcript(output, panel == "raw"))
            else:
                sections.append("Waiting for the agent to produce output…")
            if errors.exists() and errors.stat().st_size:
                sections.append("### Provider diagnostics\n" + read_text(errors, tail=True))
        return "\n\n".join(sections)
    result = Path(paths.get("result_path") or worktree / "RESULT.json")
    parts = [root_review_text(lane), "### Worker result"]
    try:
        record = json.loads(result.read_text())
    except (OSError, ValueError):
        record = None
    if isinstance(record, dict):
        parts.extend(["### " + str(record.get("outcome", "Result")), str(record.get("summary", ""))])
        if record.get("evidence"):
            parts.extend(["### Checks and evidence", "\n\n".join(_content(e) for e in record["evidence"])])
    else:
        parts.append("No final result yet. The agent's activity is available in Output.")
    response = _final_response(aw, paths)
    if response and (isinstance(record, dict) or lane.get("lifecycle") not in ("running", "prepared", "resuming")):
        parts.extend(["### Agent's final response", response])
    parts.extend(["### Review status", str(lane.get("label", "Pending"))])
    return safe_text("\n\n".join(parts))
