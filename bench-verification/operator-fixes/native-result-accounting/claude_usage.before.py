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
        if event.get("type") == "system" and event.get("subtype") == "init" and not nested:
            segment += 1
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
        if terminals > 1:
            raise LedgerError(f"multiple terminal Claude results in one provider segment: {path}")
        selected_line = number
        result_error = event.get("is_error") is True or event.get("subtype") != "success"
        models = event.get("modelUsage")
        if not isinstance(models, dict) or not models:
            # Ordinary result.usage excludes built-in subagents. Never silently
            # substitute it or claim a whole-tree output count without a rollup.
            selected = None
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
