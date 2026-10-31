"""Read-only agent mailboxes, including notifications already promoted to ROOT."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def mailbox_data(lane: dict[str, Any]) -> tuple[list[dict], list[dict], list[str]]:
    if "_recorded" in lane:
        return tuple(lane["_recorded"]["events"])
    if lane.get("role") == "root":
        inbox, outbox, errors = [], [], []
        for worker in lane.get("workers", []):
            received, sent, diagnostics = mailbox_data(worker)
            inbox.extend(dict(item, peer=worker["lane_id"]) for item in sent
                         if item.get("state") != "AWAITING FORWARDING")
            outbox.extend(dict(item, peer=worker["lane_id"]) for item in received)
            errors.extend(diagnostics)
        return inbox, outbox, errors

    diagnostics: list[str] = []

    def read(path: Path) -> dict:
        try:
            value = json.loads(path.read_text(encoding='utf-8-sig'))
            if not isinstance(value, dict):
                raise ValueError('expected a JSON object')
            return value
        except FileNotFoundError:
            return {}
        except (OSError, ValueError) as exc:
            diagnostics.append(f'Could not read {path.name}: {exc}')
            return {}

    def records(value: Any) -> list[dict]:
        return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []

    def belongs(record: dict, *, required: bool = True) -> bool:
        return all(record.get(key) == lane.get(key) or
                   (not required and key not in record)
                   for key in ('lane_id', 'run_id'))

    workspace = Path(lane['worktree_path']) / '.agent-workspace'
    inbox_record = read(workspace / 'QUEUE.json')
    inbox = []
    if inbox_record.get('schema') == 'lane-inbox/v1' and belongs(inbox_record):
        inbox = [dict(item, source='ROOT assignment') for item in records(inbox_record.get('assignments'))
                 if isinstance(item, dict) and belongs(item)]

    queue = read(Path(lane['manager_queue_path'])) if lane.get('manager_queue_path') else {}
    outbox: dict[str, dict] = {}
    if queue.get('schema') == 'manager-queue/v1' and queue.get('epoch_id') == lane.get('epoch_id'):
        for event in records(queue.get('events')):
            if not isinstance(event, dict) or not belongs(event):
                continue
            data = event.get('data') if isinstance(event.get('data'), dict) else {}
            signal = data.get('signal_id')
            key = 'signal:' + str(signal) if signal else 'event:' + str(event.get('event_id'))
            outbox[key] = dict(event, source='Agent notification' if signal else 'Harness status event')

    for folder, state in (('processed-notifications', 'FORWARDED'), ('manager-notifications', 'AWAITING FORWARDING')):
        for path in sorted((workspace / folder).glob('*.json')):
            notice = read(path)
            if not notice or not belongs(notice, required=False):
                continue
            signal = str(notice.get('signal_id') or notice.get('notice_id') or path.stem)
            key = 'signal:' + signal
            if lane.get('resumed') and 'run_id' not in notice and key not in outbox:
                continue  # Unscoped files may belong to the previous run.
            if key in outbox:
                # Keep the full original message: promotion retains only its summary.
                outbox[key]['notification'] = notice
            else:
                outbox[key] = dict(notice, signal_id=signal, state=state, source='Agent notification')

    return inbox, list(outbox.values()), diagnostics


def timestamp(item: dict) -> str:
    history = item.get('history')
    first = history[0] if isinstance(history, list) and history and isinstance(history[0], dict) else {}
    return str(item.get('created_at') or first.get('at') or item.get('ts') or '')


def mailbox_entries(lane: dict) -> tuple[list[tuple[str, str, dict]], list[str]]:
    inbox, outbox, diagnostics = mailbox_data(lane)
    entries = []
    for box, items in (('Inbox', inbox), ('Outbox', outbox)):
        for item in sorted(items, key=timestamp):
            data = item.get('data') if isinstance(item.get('data'), dict) else {}
            identity = data.get('signal_id') or item.get('signal_id') or item.get('event_id') or item.get('notice_id')
            key = json.dumps([box, item.get('peer') or lane.get('lane_id'), item.get('run_id') or lane.get('run_id'), identity])
            entries.append((key, box, item))
    return entries, diagnostics


def mailbox_text(lane: dict, *, expanded: set[str] | None = None,
                 selected: str | None = None, entries: list | None = None,
                 diagnostics: list[str] | None = None, width: int = 76) -> str:
    if entries is None:
        entries, diagnostics = mailbox_entries(lane)
    expanded = expanded or set()
    root = lane.get('role') == 'root'
    parts = []
    for box in ('Inbox', 'Outbox'):
        incoming = (box == 'Inbox') != root
        direction = 'ROOT → Agent' if incoming else 'Agent → ROOT'
        group = [(key, item) for key, section, item in entries if section == box]
        parts.append(f'### {box} · {direction} ({len(group)})')
        if not group:
            parts.append('No events recorded for this run.')
        for key, item in group:
            summary = str(item.get('summary') or item.get('prompt') or item.get('message') or item.get('type') or item['source'])
            summary = ' '.join(summary.split())
            marker = '>' if selected == key else ' '
            toggle = '-' if key in expanded else '+'
            data = item.get('data') if isinstance(item.get('data'), dict) else {}
            peer = str(item.get('lane_id') or data.get('lane_id') or item.get('peer') or lane.get('lane_id') or 'Unknown agent')
            sender, recipient = ('ROOT', peer) if incoming else (peer, 'ROOT')
            from .view_render import _truncate
            # Never truncate identities: long lane IDs wrap so both endpoints stay visible.
            parts.append(f"### {marker} [{toggle}] From: {sender} → To: {recipient}")
            origin = ' · Harness event for this agent' if item['source'] == 'Harness status event' else ''
            parts.append(f"Status: {item.get('state', 'UNKNOWN')}{origin}")
            parts.append(_truncate(summary, max(20, width)))
            if key in expanded:
                parts.append(f"{item['source']} · {timestamp(item) or 'Time not recorded'}")
                # The complete record includes original text, payload, IDs and receipts.
                parts.append('```json\n' + json.dumps(item, ensure_ascii=False, indent=2) + '\n```')
    if diagnostics:
        parts.append('### Read errors\n' + '\n'.join(diagnostics))
    return '\n\n'.join(parts)
