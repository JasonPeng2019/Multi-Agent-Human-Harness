"""Reusable, stdlib-only planning/execution helpers. Never launches or deletes anything."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import stat
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def strings(value, label, nonempty=False):
    require(isinstance(value, list), f"{label}: expected list")
    require(
        all(isinstance(x, str) and x.strip() for x in value),
        f"{label}: expected strings",
    )
    require(len(value) == len(set(value)), f"{label}: duplicate entries")
    require(not nonempty or value, f"{label}: empty")
    return value


def fields(value, required, optional=()):
    require(isinstance(value, dict), "expected object")
    require(
        set(required) <= value.keys(), f"missing fields: {set(required) - value.keys()}"
    )
    require(value.keys() <= set(required) | set(optional), "unexpected fields")


def validate_profile(p):
    fields(p, ("version", "inputs", "checks", "resources", "environment"))
    require(
        type(p["version"]) is int and p["version"] == 1, "unsupported profile version"
    )
    inputs = strings(p["inputs"], "inputs", True)
    require(isinstance(p["environment"], dict), "environment: expected object")
    for name, path in p["environment"].items():
        require(
            isinstance(name, str) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name),
            "invalid environment name",
        )
        require(isinstance(path, str) and path.strip(), "empty environment path")
    require(
        isinstance(p["checks"], list) and p["checks"], "checks: empty or not a list"
    )
    checks = {}
    for row in p["checks"]:
        fields(row, ("id", "inputs", "prerequisites"))
        strings([row["id"]], "check id", True)
        require(row["id"] not in checks, "duplicate check id")
        require(
            set(strings(row["inputs"], "check inputs", True)) <= set(inputs),
            "unknown input",
        )
        strings(row["prerequisites"], "prerequisites")
        checks[row["id"]] = row
    ordered = []
    pending = list(checks)
    while pending:
        ready = [
            key for key in pending if set(checks[key]["prerequisites"]) <= set(ordered)
        ]
        require(ready, "cyclic or unknown check prerequisite")
        ordered.extend(ready)
        pending = [key for key in pending if key not in ready]
    require(isinstance(p["resources"], list), "resources: expected list")
    seen = set()
    for row in p["resources"]:
        require(isinstance(row, dict), "resource: expected object")
        common = ("id", "owner", "consumers", "kind")
        if row.get("kind") == "file":
            fields(row, (*common, "path"), ("sha256",))
            require(
                isinstance(row["path"], str) and row["path"].strip(),
                "empty resource path",
            )
            if "sha256" in row:
                require(
                    isinstance(row["sha256"], str)
                    and re.fullmatch(r"[a-fA-F0-9]{64}", row["sha256"]),
                    "invalid sha256",
                )
        else:
            fields(row, (*common, "status", "evidence"))
            require(row["kind"] == "attestation", "unknown resource kind")
            require(
                row["status"] in ("READY", "PENDING", "BLOCKED"),
                "invalid readiness status",
            )
            require(
                isinstance(row["evidence"], str) and row["evidence"].strip(),
                "missing evidence/reason",
            )
        strings([row["id"]], "resource id", True)
        strings([row["owner"]], "owner", True)
        require(row["id"] not in seen, "duplicate resource id")
        seen.add(row["id"])
        require(
            set(strings(row["consumers"], "consumers", True)) <= checks.keys(),
            "unknown consumer",
        )
    return ordered


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def readiness(p, project_root, consumer=None):
    ordered = validate_profile(p)
    checks = {row["id"]: row for row in p["checks"]}
    require(consumer is None or consumer in checks, "unknown consumer")
    relevant = set(ordered) if consumer is None else {consumer}
    for key in reversed(ordered):
        if key in relevant:
            relevant.update(checks[key]["prerequisites"])
    results = []
    for row in p["resources"]:
        if not relevant.intersection(row["consumers"]):
            continue
        status = row.get("status", "READY")
        reason = row.get("evidence", row.get("path"))
        if row["kind"] == "file" or status == "READY":
            path = Path(project_root) / (
                row["path"] if row["kind"] == "file" else row["evidence"]
            )
            if not path.is_file():
                status, reason = (
                    "BLOCKED",
                    "required file/attestation receipt is missing",
                )
            elif "sha256" in row and digest(path) != row["sha256"].lower():
                status, reason = "BLOCKED", "artifact digest differs"
        results.append(
            {
                "id": row["id"],
                "owner": row["owner"],
                "status": status,
                "consumers": row["consumers"],
                "basis": reason,
                "kind": row["kind"],
            }
        )
    return {
        "version": 1,
        "kind": "readiness",
        "consumer": consumer,
        "status": "READY"
        if all(row["status"] == "READY" for row in results)
        else "BLOCKED",
        "resources": results,
        "limit": "Attestations require human/orchestrator semantic acceptance.",
    }


def environment(p, run_root):
    validate_profile(p)
    root = Path(run_root).resolve(strict=True)
    require(root.is_dir(), "run root must be an existing owned directory")
    patch = {}
    for name, value in p["environment"].items():
        relative = Path(value)
        require(
            not relative.is_absolute()
            and not relative.drive
            and ".." not in relative.parts,
            f"{name}: expected a path below the run root",
        )
        resolved = (root / relative).resolve()
        require(
            resolved != root and resolved.is_relative_to(root),
            f"{name}: path escapes or equals root",
        )
        patch[name] = str(resolved)
    return patch


def is_link(path):
    # Path.is_junction is unavailable on Python 3.11. Reject all Windows reparse
    # points conservatively, including junctions, rather than silently following.
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return stat.S_ISLNK(info.st_mode) or bool(
        getattr(info, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
    )


def snapshot(paths):
    require(bool(paths), "at least one explicit watched path is required")
    roots = []
    entries = {}
    for raw in paths:
        path = Path(raw).absolute()
        for part in (path, *path.parents):
            require(
                not is_link(part),
                f"snapshot scope includes a link: {part}",
            )
        path = path.resolve()
        name = str(path)
        require(name not in roots, "duplicate snapshot root")
        roots.append(name)

        def visit(item):
            require(
                not is_link(item),
                f"snapshot cannot follow link: {item}",
            )
            if item.is_file():
                entries[str(item)] = "file:" + digest(item)
            elif item.is_dir():
                entries[str(item)] = "directory"
                for child in sorted(item.iterdir()):
                    visit(child)
            elif not item.exists():
                entries[str(item)] = "missing"
            else:
                raise ValueError(f"unsupported file type: {item}")

        visit(path)
    return {
        "version": 1,
        "kind": "footprint",
        "roots": sorted(roots),
        "entries": entries,
    }


def compare(before, after):
    for value in (before, after):
        fields(value, ("version", "kind", "roots", "entries"))
        require(
            value["version"] == 1 and value["kind"] == "footprint", "invalid snapshot"
        )
        strings(value["roots"], "snapshot roots", True)
        require(
            isinstance(value["entries"], dict) and value["entries"],
            "empty snapshot entries",
        )
        require(
            all(
                isinstance(k, str) and isinstance(v, str)
                for k, v in value["entries"].items()
            ),
            "invalid snapshot entries",
        )
        require(
            set(value["roots"]) <= value["entries"].keys(), "missing root observations"
        )
    require(
        before["roots"] == after["roots"], "cannot compare different watched scopes"
    )
    left, right = before["entries"], after["entries"]
    changed = sorted(
        key for key in left.keys() | right.keys() if left.get(key) != right.get(key)
    )
    return {
        "version": 1,
        "kind": "comparison",
        "status": "CHANGED" if changed else "UNCHANGED",
        "changed": changed,
        "limit": "Only the named watched paths were compared; not an OS sandbox.",
    }


def select_checks(p, changed, credited):
    ordered = validate_profile(p)
    strings(changed, "changed inputs")
    strings(credited, "credited checks")
    require(set(credited) <= set(ordered), "unknown credited check")
    unknown = sorted(set(changed) - set(p["inputs"]))
    checks = {row["id"]: row for row in p["checks"]}
    run = set(ordered) - set(credited)
    for key in ordered:
        row = checks[key]
        if (
            unknown
            or set(row["inputs"]).intersection(changed)
            or set(row["prerequisites"]).intersection(run)
        ):
            run.add(key)
    return {
        "version": 1,
        "kind": "selection",
        "run": [key for key in ordered if key in run],
        "retain": [key for key in ordered if key not in run],
        "unknown_inputs": unknown,
        "limit": "Credit and input mapping are owner-supplied, not inferred from source or hardware.",
    }


def make_record(claim, status, elapsed_seconds, evidence, note):
    require(isinstance(claim, str) and claim.strip(), "empty claim")
    require(
        status in ("PASS", "FAIL", "BLOCKED", "INDETERMINATE"), "invalid result status"
    )
    require(
        isinstance(elapsed_seconds, (int, float))
        and not isinstance(elapsed_seconds, bool)
        and math.isfinite(elapsed_seconds)
        and elapsed_seconds >= 0,
        "invalid elapsed seconds",
    )
    strings(evidence, "evidence")
    require(status not in ("PASS", "FAIL") or evidence, "PASS/FAIL requires evidence")
    require(all(Path(path).is_file() for path in evidence), "missing evidence file")
    require(isinstance(note, str) and note.strip(), "result needs basis/limitation")
    return {
        "version": 1,
        "kind": "result",
        "claim": claim,
        "status": status,
        "elapsed_seconds": elapsed_seconds,
        "evidence": [str(Path(path).resolve()) for path in evidence],
        "note": note,
        "limit": "Recorded observation; semantic acceptance belongs to the decision owner.",
    }


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def emit(value, path=None):
    text = json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n"
    if path is None:
        print(text, end="")
    else:
        with Path(path).open("x", encoding="utf-8") as stream:
            stream.write(text)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("validate", "ready", "env", "select"):
        command = sub.add_parser(name)
        command.add_argument("profile", type=Path)
        if name == "ready":
            command.add_argument("--root", type=Path, required=True)
            command.add_argument("--consumer")
        if name == "env":
            command.add_argument("--run-root", type=Path, required=True)
        if name == "select":
            command.add_argument("--changed", action="append", default=[])
            command.add_argument("--credited", action="append", default=[])
    command = sub.add_parser("snapshot")
    command.add_argument("--path", action="append", type=Path, required=True)
    command.add_argument("--output", type=Path, required=True)
    command = sub.add_parser("compare")
    command.add_argument("before", type=Path)
    command.add_argument("after", type=Path)
    command = sub.add_parser("record")
    command.add_argument("--claim", required=True)
    command.add_argument(
        "--status", required=True, choices=("PASS", "FAIL", "BLOCKED", "INDETERMINATE")
    )
    command.add_argument("--elapsed-seconds", type=float, required=True)
    command.add_argument("--evidence", action="append", default=[])
    command.add_argument("--note", required=True)
    command.add_argument("--output", type=Path, required=True)
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 0 if exc.code == 0 else 1
    try:
        p = read(args.profile) if hasattr(args, "profile") else None
        action = args.action
        if action == "validate":
            result = {
                "version": 1,
                "kind": "validation",
                "status": "VALID",
                "checks": validate_profile(p),
            }
        elif action == "ready":
            result = readiness(p, args.root, args.consumer)
        elif action == "env":
            result = {
                "version": 1,
                "kind": "environment",
                "environment": environment(p, args.run_root),
                "limit": "Create these directories and apply to every child; verify effective paths in the application.",
            }
        elif action == "select":
            result = select_checks(p, args.changed, args.credited)
        elif action == "snapshot":
            result = snapshot(args.path)
        elif action == "compare":
            result = compare(read(args.before), read(args.after))
        else:
            result = make_record(
                args.claim, args.status, args.elapsed_seconds, args.evidence, args.note
            )
        emit(result, getattr(args, "output", None))
        if (action == "ready" and result.get("status") == "BLOCKED") or (
            action == "compare" and result.get("status") == "CHANGED"
        ):
            return 2
        return 0
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        print(f"execution blocks: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
