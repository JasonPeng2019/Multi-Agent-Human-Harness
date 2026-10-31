"""Strict read-only Claude CLI whole-tree token accounting (2.1.277+).

Final modelUsage includes built-in subagents and restores earlier session
totals on resume. The shared ledger charges cumulative deltas. Assistant
message output counts are placeholders and are never summed. Cache counts
are optional; uncached input plus output is the comparison total.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def physical_cli_starts(path: Path, *, completed: bool) -> list[int]:
    """Separate appended processes from native notification init/result turns.

    Native result indexes increase inside one CLI and reset for an appended
    process. Older receipts lack indexes and retain the one-init-per-process
    convention. A trailing init is provisional until its result arrives.
    """
    from token_ledger import LedgerError
    starts, pending = [], []
    previous_index = None
    seen_result = False
    init_pending = False
    with path.open("rb") as stream:
        for number, raw in enumerate(stream, 1):
            if not raw.strip():
                continue
            try:
                event = json.loads(raw.decode("utf-8"))
            except (UnicodeError, ValueError) as exc:
                if not completed and not raw.endswith(b"\n"):
                    break
                raise LedgerError(f"malformed Claude transcript at {path}:{number}") from exc
            if not isinstance(event, dict):
                raise LedgerError("Claude transcript record must be an object")
            if event.get("parent_tool_use_id") is not None:
                continue
            if event.get("type") == "system" and event.get("subtype") == "init":
                pending.append(number)
                init_pending = True
            if event.get("type") == "assistant":
                init_pending = False
            if event.get("type") != "result":
                continue
            if ((event.get("origin") or {}).get("kind") == "task-notification"
                    and event.get("num_turns") == 0 and not event.get("modelUsage")):
                if init_pending and pending:
                    pending.pop()
                init_pending = False
                continue
            index = event.get("result_index")
            if not seen_result:
                if pending:
                    starts.append(pending[0])
            elif pending and (index == 0 or (index is None and previous_index is None)):
                starts.append(pending[0])
            pending = []
            previous_index = index
            seen_result = True
    if pending:
        starts.append(pending[0])
    return starts


def extract_claude_usage(path: Path, *, completed: bool = True,
                         segment_index: int | None = None) -> dict[str, Any]:
    from token_ledger import LedgerError, nonnegative_int

    if not path.is_file():
        return {"status": "missing_transcript", "transcript_sha256": None}
    digest, segment_digest = hashlib.sha256(), hashlib.sha256()
    session = None
    segment = terminals = records = 0
    selected = None
    selected_line = None
    result_error = False
    result_index = None
    init_pending = False
    physical_starts = (set(physical_cli_starts(path, completed=completed))
                       if segment_index is not None else None)
    def raw_lines():
        with path.open("rb") as stream:
            yield from stream

    for number, raw in enumerate(raw_lines(), 1):
        digest.update(raw)
        if not raw.strip():
            continue
        try:
            event = json.loads(raw.decode("utf-8"))
        except (UnicodeError, ValueError) as exc:
            if not completed and not raw.endswith(b"\n"):
                break
            raise LedgerError(f"malformed Claude transcript at {path}:{number}") from exc
        if not isinstance(event, dict):
            raise LedgerError(f"Claude transcript record must be an object at {path}:{number}")
        # Nested agents may forward init/result events; only the top-level CLI
        # result supplies the inclusive whole-tree rollup.
        nested = event.get("parent_tool_use_id") is not None
        if physical_starts is not None and number in physical_starts:
            segment += 1
        if event.get("type") == "system" and event.get("subtype") == "init" and not nested:
            if physical_starts is None:
                segment += 1
            init_pending = True
        if (not nested and event.get("type") == "result"
                and (event.get("origin") or {}).get("kind") == "task-notification"
                and event.get("num_turns") == 0 and not event.get("modelUsage")):
            if init_pending and physical_starts is None:
                segment -= 1
                init_pending = False
            continue
        if event.get("type") == "assistant" and not nested:
            init_pending = False
        if segment_index is not None and segment != segment_index:
            continue
        segment_digest.update(raw)
        records += 1
        candidate = event.get("session_id")
        if not nested and isinstance(candidate, str) and candidate:
            if session is not None and candidate != session:
                raise LedgerError(f"multiple Claude session IDs in {path}")
            session = candidate
        if event.get("type") != "result" or nested:
            continue
        terminals += 1
        current_index = event.get("result_index")
        if terminals > 1:
            if (type(result_index) is not int or type(current_index) is not int
                    or current_index != result_index + 1):
                raise LedgerError(f"multiple terminal Claude results lack consecutive native result indexes: {path}")
        if type(current_index) is int:
            if current_index < 0:
                raise LedgerError("Claude native result index cannot be negative")
            result_index = current_index
        elif current_index is not None:
            raise LedgerError("invalid Claude native result index")
        result_error = event.get("is_error") is True or event.get("subtype") != "success"
        models = event.get("modelUsage")
        if not isinstance(models, dict) or not models:
            # Ordinary result.usage excludes built-in subagents. Never silently
            # substitute it or claim a whole-tree output count without a rollup.
            if not result_error:
                selected = None
                selected_line = number
            continue
        input_total = output_total = 0
        cache_values = []
        safe_models = {}
        for model, counters in models.items():
            if not isinstance(model, str) or not isinstance(counters, dict):
                raise LedgerError("invalid Claude modelUsage entry")
            inp = nonnegative_int(counters.get("inputTokens"), "inputTokens", required=True)
            out = nonnegative_int(counters.get("outputTokens"), "outputTokens", required=True)
            cached = nonnegative_int(counters.get("cacheReadInputTokens"), "cacheReadInputTokens")
            input_total += inp
            output_total += out
            cache_values.append(cached)
            safe_models[model] = {"input_tokens": inp, "output_tokens": out,
                                  "cached_input_tokens": cached}
        regressed = False
        if selected is not None:
            for model, previous in selected["model_usage"].items():
                counters = safe_models.get(model)
                if (counters is None or counters["input_tokens"] < previous["input_tokens"]
                        or counters["output_tokens"] < previous["output_tokens"]):
                    regressed = True
        if regressed:
            if result_error:
                # Keep the last known prefix when an error emits zero counters;
                # the unverified terminal status still prevents exact credit.
                continue
            raise LedgerError("Claude whole-tree cumulative counters decreased between native result records")
        selected_line = number
        selected = {
            "input_tokens": input_total, "output_tokens": output_total,
            "cached_input_tokens": sum(cache_values) if all(x is not None for x in cache_values) else None,
            "reasoning_output_tokens": None, "reported_total_tokens": None,
            "derived_input_plus_output_tokens": input_total + output_total,
            "comparison_total_tokens": input_total + output_total,
            "comparison_total_source": "claude_modelUsage_uncached_input_plus_output",
            "usage_scope": "session_cumulative_including_builtin_subagents",
            "model_usage": safe_models,
        }
    status = "ok" if selected is not None else "in_flight" if not completed else "missing_usage"
    if segment_index is not None and segment < segment_index:
        status = "in_flight" if not completed else "missing_segment"
    # Crash results can contain zeroed counters. Preserve them for diagnosis,
    # but do not call a failed terminal's possibly incomplete output exact.
    if result_error:
        status = "terminal_error_usage_unverified"
    return {
        "status": status, "thread_id": session, "selected_line": selected_line,
        "terminal_records": terminals, "json_records": records,
        "transcript_sha256": digest.hexdigest(),
        "transcript_segment_sha256": segment_digest.hexdigest(),
        **(selected or {}),
    }
