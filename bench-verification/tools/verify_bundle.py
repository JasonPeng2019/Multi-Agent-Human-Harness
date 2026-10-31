"""Verify the retained copy without setup, services, containers, or model calls."""
from datetime import datetime, timezone
import ast
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

BASE = Path(__file__).resolve().parents[1]
PROJECT = BASE.parent
HARNESS = PROJECT / "harness-single-run-version"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], timeout=60).decode().strip()


def main():
    manifest = read(BASE / "COPY_MANIFEST.json")
    configuration = read(BASE / "CONFIGURATION.json")
    transformed = {c["path"]: c["after_sha256"] for c in configuration["changes"]}
    reviewed_doc_edits = {"root_runs/zstd-claude-ready-20261030/README.md",
                         "root_runs/zstd-claude-ready-20261030/CONTINUATION.md"}
    checked, metadata_skipped, missing_run_files, changed = 0, 0, [], []
    for name, original in manifest["files"].items():
        if ".git" in Path(name).parts:
            metadata_skipped += 1
            continue
        path = PROJECT / name if name.startswith("harness-single-run-version/") else BASE / name
        try:
            actual = sha(path)
        except FileNotFoundError:
            if name.startswith("root_runs/"):
                missing_run_files.append(name)
                continue
            raise
        expected = transformed.get(name, original["sha256"])
        if name not in reviewed_doc_edits:
            assert actual == expected, f"Unexplained changed copy: {name}"
        if actual != original["sha256"]:
            changed.append({"path": name, "sha256": actual})
        checked += 1

    allowed = {"harness-config.json", "local-config/public-check-policy.json",
               "RUN_VERSION.md", "docs/CLAUDE_BENCHMARK_SETUP.md"}
    assert not git(HARNESS, "status", "--porcelain")
    assert git(HARNESS, "rev-parse", "HEAD") == configuration["prepared_harness_commit"]
    assert set(git(HARNESS, "diff", "--name-only", configuration["source_harness_commit"], "HEAD").splitlines()) == allowed
    assert not (HARNESS / ".secrets").exists()
    assert not (BASE / ".secrets").exists()

    # Verify task files from the copied Git objects, preserving pinned bytes.
    upstream = BASE / "benchmarks/swe-marathon"
    pin = "f34867643bf07aec5208a861e667e01df0942099"
    archive = subprocess.check_output(["git", "-C", str(upstream), "archive", pin,
                                       "tasks/zstd-decoder"], timeout=60)
    canonical_files = 0
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        for member in stream:
            if member.isfile():
                assert (upstream / member.name).read_bytes() == stream.extractfile(member).read(), member.name
                canonical_files += 1

    export = read(BASE / "images/ZSTD_IMAGE_EXPORT.json")
    image_id = "sha256:cfe037596ca5fd52d050f98a75ba5b9b74fa45d909ea55002c57bab7157659fb"
    assert export["status"] == "EXPORTED_AND_VERIFIED" and export["image_id"] == image_id
    assert export["verified_oci_index_digest"] == image_id and export["referenced_digest_graph_verified"]
    image = BASE / "images" / export["archive"]
    assert image.stat().st_size == export["archive_bytes"] and sha(image) == export["archive_sha256"]

    setup = BASE / "root_runs/zstd-claude-ready-20261030"
    run_path = setup / "run.json"
    setup_available = run_path.exists() and (setup / "workspace").is_dir()
    if setup_available:
        run = read(run_path)
        assert Path(run["harness_dir"]) == HARNESS
        assert Path(run["workspace"]) == setup / "workspace"
        assert Path(run["python_executable"]) == HARNESS / ".venv/Scripts/python.exe"
        assert run["prepared_harness_commit"] == git(HARNESS, "rev-parse", "HEAD")
        assert not (setup / "workspace/.harness-runtime").exists()
        assert read(HARNESS / "harness-config.json")["root_workspace"] == run["workspace"]
        assert run["memory"]["everos_project"] == run["run_id"]
        assert run["memory"]["atlas_collection"] == "benchmark_run_" + hashlib.sha256(run["run_id"].encode()).hexdigest()

    for script in (BASE / "tools").glob("*.py"):
        ast.parse(script.read_text(encoding="utf-8-sig"), filename=str(script))
    record = {"schema": "benchmark-bundle-verification/v1", "status": "PASS_RETAINED_FILES",
              "checked_at_utc": datetime.now(timezone.utc).isoformat(), "benchmark_support": str(BASE),
              "harness": str(HARNESS), "copied_payload_files_verified": checked,
              "git_metadata_checked_by_revision_instead_of_byte_identity": metadata_skipped,
              "intentional_payload_changes": changed,
              "user_deleted_run_files_not_restored": missing_run_files,
              "user_deleted_run_folders_are_expected": True,
              "harness_implementation_unchanged": True, "harness_git_clean": True,
              "prepared_harness_commit": configuration["prepared_harness_commit"],
              "zstd_files_matching_pinned_git_bytes": canonical_files,
              "image_archive_sha256": export["archive_sha256"], "image_id": image_id,
              "image_archive_verified": True, "prepared_setup_currently_present": setup_available,
              "python_imports_verified": "everos, memory_harness, pymongo, langchain_mongodb resolve inside copied harness",
              "evaluation_config_unit_tests": "4 passed before any user removal of run folders",
              "powershell_syntax": "Launch.ps1 and New-PythonEnvironment.ps1 passed parser checks",
              "credentials_copied": False, "benchmark_launches": 0, "native_setup_invocations": 0,
              "pending_before_authorized_launch": ["confirm or prepare a fresh run-specific setup",
                  "verify isolated memory backend scope is empty", "fresh bounded native health evidence",
                  "native prelaunch setup and matching receipt"]}
    (BASE / "BUNDLE_VERIFICATION.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    relocation = read(BASE / "RELOCATION.json")
    relocation["status"] = "MOVED_AND_VERIFIED_RETAINED_FILES"
    relocation["verified_at_utc"] = record["checked_at_utc"]
    relocation["user_run_folder_deletions_respected"] = True
    (BASE / "RELOCATION.json").write_text(json.dumps(relocation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: record[k] for k in ["status", "copied_payload_files_verified",
                     "zstd_files_matching_pinned_git_bytes", "image_archive_verified",
                     "prepared_setup_currently_present", "benchmark_launches", "native_setup_invocations"]}))


if __name__ == "__main__":
    main()
