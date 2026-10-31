#!/usr/bin/env python3
"""Read the collector's active watchdog deadline; never estimate or change it."""
from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path


def remaining_budget(path: Path, now: datetime | None = None) -> dict:
    record = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(record, dict) or record.get("schema") != "run-budget/v1":
        raise ValueError("collector budget record is missing or invalid")
    if record.get("authority") != "cli-collector-watchdog":
        raise ValueError("budget record has no collector authority")
    seconds = record.get("watchdog_seconds")
    if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or seconds <= 0:
        raise ValueError("watchdog_seconds must be positive and finite")
    start = datetime.fromisoformat(record["segment_started_at_utc"].replace("Z", "+00:00"))
    deadline = datetime.fromisoformat(record["watchdog_deadline_utc"].replace("Z", "+00:00"))
    if start.utcoffset() is None or deadline.utcoffset() is None:
        raise ValueError("budget times must have UTC offsets")
    if abs((deadline - start).total_seconds() - seconds) > 0.001:
        raise ValueError("deadline and watchdog duration disagree")
    original_seconds = record.get("original_watchdog_seconds", seconds)
    if (isinstance(original_seconds, bool) or not isinstance(original_seconds, (int, float))
            or not math.isfinite(original_seconds) or original_seconds < seconds):
        raise ValueError("original watchdog duration must cover this segment")
    now = now or datetime.now(timezone.utc)
    remaining = max(0.0, (deadline - now).total_seconds())
    return {
        "run_id": record["run_id"],
        "budget_scope": record.get("budget_scope", "current active collector segment"),
        "checked_at_utc": now.isoformat().replace("+00:00", "Z"),
        "watchdog_deadline_utc": record["watchdog_deadline_utc"],
        "limit_minutes": original_seconds / 60,
        "remaining_seconds": round(remaining, 3),
        "remaining_minutes": round(remaining / 60, 3),
        "expired": remaining == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--budget-file", type=Path,
                        default=Path(__file__).resolve().parent / "RUN_BUDGET.json")
    args = parser.parse_args()
    try:
        print(json.dumps(remaining_budget(args.budget_file)))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f"Cannot determine remaining time: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
