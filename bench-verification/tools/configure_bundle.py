"""Rebind this unlaunched copy. No setup, services, memory calls, or model calls."""
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import subprocess
import sys

BASE = Path(__file__).resolve().parents[1]
SETUP = BASE / "root_runs/zstd-claude-ready-20261030"
HARNESS = BASE.parent / "harness-single-run-version"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], timeout=30).decode().strip()


def main():
    run = read(SETUP / "run.json")
    workspace = SETUP / "workspace"
    assert not (workspace / ".harness-runtime").exists()
    assert not (SETUP / "runtime/results").exists()
    assert run["benchmark_root_launches"] == run["setup_invocations"] == 0
    assert not (BASE / "CONFIGURATION.json").exists(), "One-time configuration already recorded"
    source_harness_revision = run["prepared_harness_commit"]
    copied_files = read(BASE / "COPY_MANIFEST.json")["files"]
    changes = []

    def record(path, data):
        relative = ("harness-single-run-version/" + path.relative_to(HARNESS).as_posix()
                    if path.is_relative_to(HARNESS) else path.relative_to(BASE).as_posix())
        before = copied_files.get(relative, {}).get("sha256", hashlib.sha256(path.read_bytes()).hexdigest())
        path.write_bytes(data)
        after = hashlib.sha256(data).hexdigest()
        if before != after:
            changes.append({"path": relative, "resolved_path": str(path), "before_sha256": before,
                            "after_sha256": after})

    config = HARNESS / "harness-config.json"
    value = read(config)
    value["root_workspace"] = str(workspace)
    record(config, (json.dumps(value, indent=2) + "\n").encode())
    policy = HARNESS / "local-config/public-check-policy.json"
    value = read(policy)
    value["adapter"]["path"] = str(HARNESS / "task-tools/zstd_check_adapter.py")
    record(policy, (json.dumps(value, indent=2) + "\n").encode())

    documentation = HARNESS / "docs/CLAUDE_BENCHMARK_SETUP.md"
    text = documentation.read_text(encoding="utf-8")
    if "bench-verification/root_runs/" not in text:
        text = text.replace("../root_runs/zstd-claude-ready-20261030/",
                            "../bench-verification/root_runs/zstd-claude-ready-20261030/")
        text = text.replace("root_runs/claude-adaptation-20261030/",
                            "bench-verification/root_runs/claude-adaptation-20261030/")
        text = text.replace("relative to this harness's parent\nrepository.",
                            "relative to this harness directory.")
    record(documentation, text.encode())
    version = HARNESS / "RUN_VERSION.md"
    text = version.read_text(encoding="utf-8")
    if "## Hackathon benchmark support location" not in text:
        text += ("\n## Hackathon benchmark support location\n\n"
                 "This copied harness stays at the hackathon project's top level. Its matching\n"
                 "prepared setup is `../bench-verification/root_runs/zstd-claude-ready-20261030/`.\n"
                 "Read `../bench-verification/README.md` and that setup's `run.json` for the\n"
                 "current paths, run identity, copied runtime, image archive, and pending preflight.\n"
                 "The earlier source locations above describe history in the original repository.\n"
                 "Only path configuration and these location notes changed; task/skill bodies and\n"
                 "harness implementation are retained. No benchmark or native setup ran here.\n")
    record(version, text.encode())

    audit = SETUP / "tools/verify_setup.py"
    text = audit.read_text(encoding="utf-8")
    text = text.replace('SOURCE = REPO / "root_runs/zstd-runtime-repair-20261015/workflow-1"',
                        'SOURCE = REPO / "reference/workflow-1"')
    text = text.replace('REPO / "root_runs/zstd-w1-fixed-two-20261015/tools/observe_integrations.py"',
                        'REPO / "reference/observe_integrations.py"')
    if "remote_memory_emptiness_checked=False" not in text:
        text = text.replace('isolated_memory_scope=run["memory"],',
                            'isolated_memory_scope=run["memory"], remote_memory_emptiness_checked=False,\n'
                            '                  native_health_pending=True,')
    record(audit, text.encode())

    launch = SETUP / "Launch.ps1"
    text = launch.read_text(encoding="utf-8-sig")
    marker = "$continuation=@{}"
    if marker not in text:
        marker = "$continuation = @{}"
    assert marker in text
    if "$env:HARNESS_CREDENTIAL_ROOT" not in text:
        text = text.replace(marker,
            "if ($env:HARNESS_CREDENTIAL_ROOT) { $runConfig.credential_root = $env:HARNESS_CREDENTIAL_ROOT }\n" + marker, 1)
    record(launch, text.encode())

    packages = HARNESS / ".venv/Lib/site-packages"
    for name, directory in [("_editable_impl_everos.pth", HARNESS / "vendor/everos/src"),
                             ("__editable__.memory_harness-0.1.0.pth", HARNESS / "src")]:
        record(packages / name, (str(directory) + "\n").encode())
    for name, directory in [("everos-1.3.1.dist-info", HARNESS / "vendor/everos"),
                             ("memory_harness-0.1.0.dist-info", HARNESS)]:
        path = packages / name / "direct_url.json"
        value = read(path)
        value["url"] = directory.as_uri()
        record(path, (json.dumps(value) + "\n").encode())
    cfg = HARNESS / ".venv/pyvenv.cfg"
    lines = cfg.read_text().splitlines()
    lines = [f"command = copied installed environment for {HARNESS / '.venv'}" if s.startswith("command =") else s
             for s in lines]
    record(cfg, ("\n".join(lines) + "\n").encode())
    # This is an installed-package snapshot, not a claim that every package is required.
    requirements = []
    for dist in importlib.metadata.distributions(path=[str(packages)]):
        name = dist.metadata["Name"]
        if name.lower().replace("_", "-") not in {"memory-harness", "everos", "langchain-mongodb"}:
            requirements.append(f"{name}=={dist.version}")
    (BASE / "requirements-snapshot.txt").write_text(
        "# Installed runtime dependency versions; local projects are installed separately.\n" +
        "\n".join(sorted(set(requirements), key=str.lower)) + "\n", encoding="utf-8")

    # Stage exactly the copy's path configs and location notes, retaining a clean revision.
    assert git(HARNESS, "rev-parse", "HEAD") == source_harness_revision
    allowed = {"harness-config.json", "local-config/public-check-policy.json",
               "docs/CLAUDE_BENCHMARK_SETUP.md", "RUN_VERSION.md"}
    staged = set(git(HARNESS, "diff", "--cached", "--name-only").splitlines())
    unstaged = set(git(HARNESS, "diff", "--name-only").splitlines())
    assert staged <= allowed and staged | unstaged == allowed
    git(HARNESS, "add", "-f", "--", *sorted(allowed))
    git(HARNESS, "-c", "user.name=Benchmark bundle", "-c", "user.email=benchmark-bundle@localhost",
        "commit", "-m", "Bind copied harness to hackathon benchmark workspace")
    assert not git(HARNESS, "status", "--porcelain")
    # The reference checkout must not retain a filesystem remote into the original repository.
    reference = BASE / "reference/workflow-1/workspace"
    if "origin" in git(reference, "remote").splitlines():
        git(reference, "remote", "remove", "origin")

    run_id = "zstd-hackathon-claude-20261030"
    run.update(run_id=run_id, workspace=str(workspace), harness_dir=str(HARNESS),
               python_executable=str(HARNESS / ".venv/Scripts/python.exe"),
               prompt_file=str(workspace / "ROOT_RUN_PROMPT.md"),
               launch_script=str(SETUP / "Launch.ps1"), results_dir=str(SETUP / "runtime/results"),
               source_setup=str(BASE / "reference/workflow-1"),
               evaluation_config=str(BASE / "root_runs/zstd-evaluation-repair-20261015/EVALUATION_CONFIG.json"),
               prepared_harness_commit=git(HARNESS, "rev-parse", "HEAD"),
               copied_from_harness_commit=source_harness_revision,
               status="prepared_not_launched_pending_native_preflight")
    run["memory"].update(initial_state="new_scope_not_yet_backend_verified",
        atlas_collection="benchmark_run_" + hashlib.sha256(run_id.encode()).hexdigest(),
        everos_project=run_id, everos_namespace=run_id + "-workers")
    record(SETUP / "run.json", (json.dumps(run, indent=2) + "\n").encode())
    record = {"schema": "benchmark-bundle-configuration/v1", "configured_at_utc": datetime.now(timezone.utc).isoformat(),
              "source_harness_commit": source_harness_revision,
              "prepared_harness_commit": run["prepared_harness_commit"], "run_id": run_id,
              "changes": changes, "credential_root_external": run["credential_root"],
              "credential_files_copied": False, "remote_memory_emptiness_checked": False,
              "benchmark_launches": 0, "native_setup_invocations": 0}
    write(BASE / "CONFIGURATION.json", record)
    print(json.dumps({key: record[key] for key in ["run_id", "source_harness_commit", "prepared_harness_commit"]}))


if __name__ == "__main__":
    main()
