#!/usr/bin/env python3
"""Write a result/v1 report using this worker's authoritative identities."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def read_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected an object: {path}")
    return value


def write_result(agent: Path, outcome: str, summary: str, evidence: list) -> dict:
    agent = agent.resolve()
    worker = agent.parent
    binding = read_object(agent / "harness-hook-binding.json")
    template = read_object(agent / "result-template.json")
    if binding.get("schema") != "harness-hook-binding/v1":
        raise ValueError("worker binding schema mismatch")
    if template.get("schema") != "result/v1":
        raise ValueError("result template schema mismatch")
    for key in ("lane_id", "run_id"):
        if not binding.get(key) or template.get(key) != binding[key]:
            raise ValueError(f"current result template has the wrong {key}")
    target = worker / "RESULT.json"
    expected = Path(binding.get("result_path") or target).resolve()
    if expected != target.resolve() or target.is_symlink():
        raise ValueError("result path must be this worker's RESULT.json")
    if outcome not in {"PASS", "FAIL", "BLOCKED"}:
        raise ValueError("outcome must be PASS, FAIL, or BLOCKED")
    if not isinstance(summary, str) or not summary.strip():
        raise ValueError("summary must be nonempty")
    if not isinstance(evidence, list):
        raise ValueError("evidence must be a JSON list")
    result = {
        "schema": "result/v1",
        "lane_id": binding["lane_id"],
        "run_id": binding["run_id"],
        "outcome": outcome,
        "summary": summary.strip(),
        "evidence": evidence,
        "completed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    result["content_hash"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    descriptor, temporary = tempfile.mkstemp(prefix=".RESULT-", suffix=".tmp", dir=worker)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outcome", required=True, choices=("PASS", "FAIL", "BLOCKED"))
    parser.add_argument("--summary", required=True)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--evidence", action="append", default=[])
    group.add_argument("--evidence-file", type=Path)
    args = parser.parse_args()
    try:
        evidence = (json.loads(args.evidence_file.read_text(encoding="utf-8-sig"))
                    if args.evidence_file else args.evidence)
        result = write_result(Path(__file__).resolve().parent, args.outcome, args.summary, evidence)
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(2, f"Result not written: {exc}\n")
    print(json.dumps({"result_path": str(Path(__file__).resolve().parent.parent / "RESULT.json"),
                      "outcome": result["outcome"], "content_hash": result["content_hash"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
