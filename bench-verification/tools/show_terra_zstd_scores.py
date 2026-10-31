"""Compare saved Terra/high Zstd scores with official run logs.

Defaults to the imported final supervised batch. Read-only and offline; never
launches models or graders. Official counters were fetched with authenticated
read-only access and checked against each canonical trial result and verifier.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys


DEFAULT_SOURCE_ROOT = Path(
    r"C:\Users\Jason\Documents\Jason\Orchestrator_Harness-Bench-Testing"
)
CORRECTED_IMAGE = (
    "sha256:cfe037596ca5fd52d050f98a75ba5b9b74fa45d909ea55002c57bab7157659fb"
)
SELECTED_RUNS = (
    (
        "zstd-skills-four-20261015/w1-r01",
        "zstd-skills-four-20261015-w1-r01",
        "zstd-evaluation-repair-20261015/evaluations/current-w1-r01/grading.json",
    ),
    (
        "zstd-skills-four-20261015/w1-r02",
        "zstd-skills-four-20261015-w1-r02",
        "zstd-evaluation-repair-20261015/evaluations/current-w1-r02/grading.json",
    ),
    (
        "zstd-w1-fixed-two-20261015/w1-r02",
        "zstd-w1-fixed-two-20261015-w1-r02",
        "zstd-w1-fixed-two-20261015/w1-r02/operator/checkpoint-grades/final/grading.json",
    ),
)
IMPORTED_FINAL = Path(__file__).resolve().parents[1] / "imported-results/terra-zstd-final"


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def fraction(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Invalid {label}: expected a number")
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"Invalid {label}: expected a finite fraction from 0 to 1")
    return float(value)


def count(metrics: dict, key: str) -> int:
    value = metrics.get(key)
    if type(value) is not int or value < 0:
        raise ValueError(f"Invalid test count: {key}")
    return value


def load_report(source_root: Path) -> dict:
    root_runs = source_root / "root_runs"
    runs = []
    for folder, expected_id, grade_file in SELECTED_RUNS:
        run = read_json(root_runs / folder / "run.json")
        grade_path = root_runs / grade_file
        grade = read_json(grade_path)
        if run.get("run_id") != expected_id or grade.get("run_id") != expected_id:
            raise ValueError(f"Run/grade identity mismatch: {folder}")
        if (
            run.get("task") != "zstd-decoder"
            or run.get("model") != "gpt-5.6-terra"
            or run.get("root_effort") != "high"
            or run.get("worker_effort") != "high"
        ):
            raise ValueError(f"Expected Terra/high Zstd run: {folder}")
        if (
            grade.get("status") != "GRADED"
            or grade.get("container_removed") is not True
            or grade.get("build_exit_code") != 0
            or grade.get("verifier_exit_code") != 0
            or grade.get("image_id") != CORRECTED_IMAGE
        ):
            raise ValueError(f"Not a completed grade from the corrected image: {grade_path}")
        metrics = grade["metrics"]
        passed = count(metrics, "total_passed")
        total = count(metrics, "total_tests")
        for group in ("public", "hidden"):
            if count(metrics, f"{group}_passed") + count(metrics, f"{group}_failed") != count(metrics, f"{group}_total"):
                raise ValueError(f"Inconsistent {group} test counts: {grade_path}")
        if (
            total != 43
            or metrics["public_total"] != 6
            or metrics["hidden_total"] != 37
            or metrics["public_passed"] + metrics["hidden_passed"] != passed
        ):
            raise ValueError(f"Inconsistent Zstd test counts: {grade_path}")
        partial = fraction(metrics["partial_score"], "local partial score")
        if not math.isclose(partial, passed / total, abs_tol=1e-12):
            raise ValueError(f"Score/test-count mismatch: {grade_path}")
        runs.append({
            "run_id": expected_id,
            "run_folder": str(root_runs / folder),
            "grade_file": str(grade_path),
            "partial_score": partial,
            "passed": passed,
            "total": total,
            "hidden_passed": metrics["hidden_passed"],
            "hidden_total": metrics["hidden_total"],
        })

    return {
        "task": "zstd-decoder",
        "model": "GPT-5.6-terra",
        "effort": "high",
        "selection_note": "Three selected local runs; not all local experiments.",
        "local_runs": runs,
        "local_average": statistics.mean(run["partial_score"] for run in runs),
        "local_best": max(run["partial_score"] for run in runs),
    }


def load_final_report() -> dict:
    manifest = read_json(IMPORTED_FINAL / "IMPORT_MANIFEST.json")
    for record in manifest["files"]:
        path = (IMPORTED_FINAL / record["destination"]).resolve()
        if not path.is_relative_to(IMPORTED_FINAL.resolve()):
            raise ValueError("Import manifest path leaves the results folder")
        if hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError(f"Imported evidence hash mismatch: {path}")
    report = read_json(IMPORTED_FINAL / "RESULTS.json")
    if report.get("schema") != "imported-terra-zstd-results/v1":
        raise ValueError("Unsupported imported results schema")
    report.pop("output_token_comparison", None)
    for run in report["local_runs"]:
        for key in ("output_tokens", "total_tokens", "token_total_is_exact", "output_vs_official_mean"):
            run.pop(key, None)
    return report


def load_official_reference() -> dict:
    # Manifest verification covers both this evidence file and the imported report.
    load_final_report()
    path = IMPORTED_FINAL / "evidence/official-terra-high-usage.json"
    evidence = read_json(path)
    rows = evidence["trials"]
    if evidence["suite"] != "v1.1" or evidence["n"] != len(rows) or len(rows) != 8:
        raise ValueError("Unexpected official suite or trial count")
    for row in rows:
        if (row["model"] != "openai/gpt-5.6-terra" or row["effort"] != "high"
                or row["agent"] != "codex"):
            raise ValueError("Official model/effort mismatch")
        fraction(row["partial_score"], "official partial score")
    return {
        "version": evidence["suite"],
        "n": len(rows),
        "average": statistics.mean(row["partial_score"] for row in rows),
        "best": max(row["partial_score"] for row in rows),
        "reference_file": str(path),
        "source": evidence["source"],
        "trials": [{key: row[key] for key in ("trial", "partial_score", "passed", "total")} for row in rows],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=DEFAULT_SOURCE_ROOT)
    parser.add_argument("--json", action="store_true", help="emit structured output")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--final-batch", dest="final_batch", action="store_true", help="load both runs from the latest supervised workflow batch (default)")
    selection.add_argument("--selected-successes", dest="final_batch", action="store_false", help="load the earlier three selected 100%% runs spanning multiple batches")
    parser.set_defaults(final_batch=True)
    parser.add_argument("--swe-only", action="store_true", help="display only official Codex/Terra high Zstd scores")
    args = parser.parse_args()
    try:
        if args.swe_only:
            report = {}
        elif args.final_batch:
            report = load_final_report()
        else:
            report = load_report(args.source_root.resolve())
        report["swe_marathon"] = load_official_reference()
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        print(f"Cannot load Terra Zstd scores: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"swe_marathon": report["swe_marathon"]} if args.swe_only else report, indent=2))
        return 0
    print("Zstd decoder | GPT-5.6-terra | HIGH effort")
    if not args.swe_only:
        print(report["selection_note"])
        for run in report["local_runs"]:
            print(f"  {run['run_id']}: {run['partial_score']:.1%} "
                  f"({run['passed']}/{run['total']}; hidden {run['hidden_passed']}/{run['hidden_total']})")
            if args.final_batch:
                print(f"    Workflow outcome: {run['workflow_outcome']}")
        print(f"{'Final-batch' if args.final_batch else 'Selected local'} average: "
              f"{report['local_average']:.2%}; best: {report['local_best']:.1%}")
    benchmark = report["swe_marathon"]
    print(f"SWE-Marathon {benchmark['version']} Terra HIGH (n={benchmark['n']}): "
          f"average {benchmark['average']:.1%}; best {benchmark['best']:.1%}")
    print("Source: official manifest + canonical result counters + verifier metrics; saved offline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
