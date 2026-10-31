"""One-shot, operator-only continuation of a timed-out BioFabric verifier.

Keeps the official verifier and its assertions/counting formula unchanged. A
documented cargo shim replays only *completed* suite transcripts, then executes
the remaining suites. No benchmark model is launched or resumed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

import grade_run as official

VERIFIER_SHA = "151ad3d8afb777b4ecf70e4bc0febf39db69b95368890ceeeffa01b8e38371b8"
COMPLETED = ["cli-unit", "cli_tests", "core-unit", "analysis_tests"]
EXPECTED_COUNTS = [(0, 0, 0), (14, 37, 0), (15, 0, 0), (63, 0, 0)]
SUMMARY = re.compile(r"^test result: (?:ok|FAILED)\. (\d+) passed; (\d+) failed; (\d+) ignored;", re.M)
RUNNING = re.compile(r"^\s*Running (.+)$", re.M)


def completed_prefix(raw: bytes):
    text = raw.decode("utf-8")
    starts = list(RUNNING.finditer(text))
    expected = ["unittests src/main.rs", "tests/cli_tests.rs", "unittests src/lib.rs", "tests/analysis_tests.rs", "tests/hidden_tests.rs"]
    if len(starts) != len(expected) or any(not m[1].startswith(e + " ") for m, e in zip(starts, expected)):
        raise ValueError("Checkpoint target sequence is not the expected original verifier prefix")
    counts = []
    for i in range(4):
        matches = SUMMARY.findall(text[starts[i].start():starts[i + 1].start()])
        if len(matches) != 1:
            raise ValueError("Cannot reuse an unfinished or duplicate target")
        counts.append(tuple(map(int, matches[0])))
    if counts != EXPECTED_COUNTS or SUMMARY.search(text[starts[4].start():]):
        raise ValueError("Checkpoint counts differ or the unfinished suite has a summary")
    return text[:starts[4].start()].encode(), [dict(target=t, passed=c[0], failed=c[1], ignored=c[2]) for t, c in zip(COMPLETED, counts)]


# Uploaded only to the isolated grading container, never to a model workspace.
SHIM = r'''#!/usr/bin/env python3
import json, os, subprocess, sys
from pathlib import Path

if sys.argv[1:] != ['test','--workspace','--no-fail-fast','--','--test-threads=4']:
    raise SystemExit('Unexpected cargo command; refusing continuation')
real = os.environ['OPERATOR_REAL_CARGO']
root = Path('/logs/verifier')
metadata = subprocess.check_output([real,'metadata','--no-deps','--format-version','1'],cwd='/app')
(root/'cargo-metadata.json').write_bytes(metadata)
packages = json.loads(metadata)['packages']
inventory = sorted((p['name'],t['name'],tuple(t['kind'])) for p in packages for t in p['targets'])
expected = sorted([
 ('biofabric','biofabric',('bin',)), ('biofabric','cli_tests',('test',)),
 ('biofabric-core','biofabric_core',('lib',)),
 ('biofabric-core','analysis_tests',('test',)), ('biofabric-core','hidden_tests',('test',)),
 ('biofabric-core','parity_tests',('test',)), ('biofabric-core','pipeline_stub',('test',))])
if inventory != expected:
    raise SystemExit('Official target inventory differs; refusing to omit any target')
sys.stdout.buffer.write(Path('/tmp/operator-completed-prefix.log').read_bytes())
sys.stdout.flush()
receipts = []
overall = 101  # The reused, completed CLI suite has 37 failures.
for target in ['hidden_tests','parity_tests','pipeline_stub','doc']:
    args = [real,'test','-p','biofabric-core']
    args += ['--doc'] if target == 'doc' else ['--test',target]
    args += ['--','--test-threads=4']
    log = root / (target+'.log')
    with log.open('wb') as saved:
        p = subprocess.Popen(args,cwd='/app',stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        for line in iter(p.stdout.readline,b''):
            saved.write(line); saved.flush()
            sys.stdout.buffer.write(line); sys.stdout.flush()
        code = p.wait()
    receipts.append({'target':target,'argv':args,'exit_code':code,'log':str(log)})
    (root/'continuation-targets.json').write_text(json.dumps(receipts,indent=2)+'\n')
    if code not in (0,101):
        raise SystemExit('Cargo infrastructure failure; stopped after '+target)
raise SystemExit(overall)
'''


def grade(folder: Path):
    folder = folder.resolve(strict=True)
    run = official.read(folder / "run.json")
    if run["task"] != "biofabric-rust-rewrite" or folder.name != "b1":
        raise ValueError("Latest authorization covers only BioFabric b1")
    official.stopped(run, folder)
    workspace = Path(run["workspace"])
    if official.git(workspace, "status", "--porcelain").strip():
        raise ValueError("Candidate must remain clean and committed")
    out = folder / "hidden-evaluation"
    old = official.read(out / "grading.json")
    if old["status"] != "FAILED" or old["failure_type"] != "TimeoutExpired" or old["cleanup_proven"] is not True:
        raise ValueError("Expected a cleaned-up verifier timeout")
    revision = official.git(workspace, "rev-parse", "HEAD").decode().strip()
    if revision != old["candidate_revision"]:
        raise ValueError("Candidate revision changed")
    archive = official.git(workspace, "archive", "--format=tar", revision, "--", "crates", "Cargo.toml", "Cargo.lock")
    if archive != (out / "candidate.tar").read_bytes():
        raise ValueError("Candidate archive differs from the timed-out attempt")
    raw_checkpoint = (out / "operator-progress-checkpoint.log").read_bytes()
    prefix, reused = completed_prefix(raw_checkpoint)
    task_root = official.BENCH / "biofabric"
    verifier = task_root / "operator-only/tests/test.sh"
    if official.sha(verifier) != VERIFIER_SHA or old["verifier_sha256"] != VERIFIER_SHA:
        raise ValueError("Official verifier changed")
    assets = official.read(task_root / "ASSETS.json")
    if official.command(["docker", "image", "inspect", assets["image"], "--format", "{{.Id}}"]).stdout.decode().strip() != old["image_id"]:
        raise ValueError("Pinned image changed")
    # Preserve the failed attempt in full; never overwrite original evidence.
    previous = folder / "hidden-evaluation-attempt-0001-timeout"
    if previous.exists():
        raise ValueError("Previous attempt archive already exists; diagnose before another invocation")
    out.rename(previous)
    out.mkdir()
    (out / "candidate.tar").write_bytes(archive)
    (out / "reused-completed-prefix.log").write_bytes(prefix)
    (out / "operator-cargo-shim.py").write_text(SHIM, encoding="utf-8", newline="\n")
    result = dict(schema="benchmark-grade/v1", status="RUNNING", run_id=run["run_id"], task=run["task"], oracle=False,
        feedback_to_live_roots=False, image_id=old["image_id"], engine_sha256=official.sha(Path(__file__)),
        verifier_sha256=VERIFIER_SHA, candidate_revision=revision, candidate_sha256=hashlib.sha256(archive).hexdigest(),
        started_at_utc=datetime.now(timezone.utc).isoformat(), cleanup_proven=False,
        official_comparable=False, scoring_variant="continued-official-tests-extended-time/v1",
        scoring_note="Official tests and score formula; completed suites reused, grading timeout extended by user authorization.",
        original_attempt=str(previous), original_grading_sha256=official.sha(previous / "grading.json"),
        original_checkpoint_sha256=hashlib.sha256(raw_checkpoint).hexdigest(), reused_targets=reused,
        grading_timeout_seconds=7200, cpu_cores=4)
    cid = None
    official.write(out / "grading.json", result)
    try:
        cid = official.command(["docker", "create", "--pull", "never", "--name", "continued-b1-" + uuid.uuid4().hex[:16],
            "--label", "benchmark.operator-eval=b1-continuation", "--network", "none", "--cpus", "4", "--memory", "16g",
            "--pids-limit", "1024", assets["image"], "bash", "-lc", "sleep 18000"]).stdout.decode().strip()
        if not re.fullmatch("[0-9a-f]{64}", cid):
            raise ValueError("Invalid owned container ID")
        result["container"] = cid
        official.write(out / "grading.json", result)
        official.command(["docker", "start", cid])
        official.command(["docker", "exec", cid, "rm", "-rf", "/app/crates", "/app/target"])
        official.command(["docker", "exec", "-i", cid, "tar", "xf", "-", "-C", "/app"], data=archive)
        official.upload(cid, "/tmp/operator-verifier.sh", verifier.read_bytes())
        official.upload(cid, "/tmp/operator-completed-prefix.log", prefix)
        official.upload(cid, "/tmp/operator-cargo-bin/cargo", SHIM.encode())
        official.command(["docker", "exec", cid, "chmod", "+x", "/tmp/operator-cargo-bin/cargo"])
        command = ["docker", "exec", "-e", "CARGO_INCREMENTAL=0", cid, "bash", "-lc",
            'export OPERATOR_REAL_CARGO="$(command -v cargo)"; export PATH="/tmp/operator-cargo-bin:$PATH"; bash /tmp/operator-verifier.sh']
        # File-backed output is durable during execution, including on timeout.
        with (out / "verifier.stdout.log").open("wb") as stdout, (out / "verifier.stderr.log").open("wb") as stderr:
            execution = subprocess.run(command, stdout=stdout, stderr=stderr, timeout=7200)
        for name in ["metrics.json", "reward.txt", "test_output.log", "cargo-metadata.json", "continuation-targets.json", "hidden_tests.log", "parity_tests.log", "pipeline_stub.log", "doc.log"]:
            data = official.command(["docker", "exec", cid, "cat", "/logs/verifier/" + name]).stdout
            (out / name).write_bytes(data)
        metrics = official.read(out / "metrics.json")
        receipts = official.read(out / "continuation-targets.json")
        if [r["target"] for r in receipts] != ["hidden_tests", "parity_tests", "pipeline_stub", "doc"]:
            raise ValueError("Missing remaining target receipt")
        for receipt in receipts:
            summaries = SUMMARY.findall((out / (receipt["target"] + ".log")).read_text(encoding="utf-8"))
            if len(summaries) != 1 or receipt["exit_code"] not in (0, 101):
                raise ValueError("Remaining target did not finish normally")
        combined = SUMMARY.findall((out / "test_output.log").read_text(encoding="utf-8"))
        totals = [sum(int(row[i]) for row in combined) for i in range(3)]
        if len(combined) != 8 or totals != [metrics[k] for k in ("passed", "failed", "ignored")]:
            raise ValueError("Official combined scoring totals differ")
        if execution.returncode or metrics.get("phase") != "complete" or metrics["partial_score"] != totals[0] / sum(totals[:2]):
            raise ValueError("No valid completed official test score")
        if (out / "reward.txt").read_text().strip() != "0" or metrics["reward"] != 0:
            raise ValueError("Reused failed CLI suite must produce binary reward zero")
        result.update(status="GRADED", partial_score=metrics["partial_score"], binary_reward=0, metrics=metrics)
    except BaseException as exc:
        result.update(status="FAILED", failure_type=type(exc).__name__, failure_reason=str(exc)[:800])
        raise
    finally:
        if cid:
            result["cleanup_proven"] = official.command(["docker", "rm", "-f", cid], check=False).returncode == 0
        result["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        official.write(out / "grading.json", result)
    if not result["cleanup_proven"]:
        raise ValueError("Owned grading container cleanup unproven")
    print(json.dumps({"grading_file": str(out / "grading.json"), "partial_score": result["partial_score"], "binary_reward": 0}), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("run_folder", type=Path)
    grade(p.parse_args().run_folder)
