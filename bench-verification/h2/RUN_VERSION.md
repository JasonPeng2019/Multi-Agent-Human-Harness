# Benchmark harness copy

Created 2026-10-30 from the maintained workflow-1 benchmark harness:

- Source: `../root_runs/zstd-runtime-repair-20261015/workflow-1/harness/`
- Source commit: `022f14f64e3e4482e74b0d7b5919b361d7657994`
- Source Git tree: `d919fa4cd0c46b5742b42624697ed3aad531a5dc`
- Verification: all 1,517 tracked source files match the source's working files
  byte for byte. No harness code was changed during copying.
- Aggregate SHA-256: `263d103470003ce86fef6bf97f10c3866c984838b5fa2d52fbb2dc52917ad0bf`
  (sorted UTF-8 paths, each followed by NUL, its file's hex SHA-256, and LF).

The initial copy retained the source branch/history and its
`core.autocrlf=false` policy. It has no configured remote. This document is the
only addition at creation. Ignored credentials, runtime output,
caches and local worktrees were excluded.

The copy includes the benchmark's runtime repairs, memory implementation,
worker guidance, Zstd adapter, prompts and policies. It also retains the
benchmark's workflow-specific behavior; it has not been generalized to match
`harness-single-updated` or `harness-single-generic`.

## Setup context

At initial creation, configuration paths and memory identifiers were preserved
from the source and referred to the original workflow-1 setup. Its original
matching ROOT workspace and supplied skills remain at:

`../root_runs/zstd-runtime-repair-20261015/workflow-1/workspace/`

Read the original setup's `README.md`, `CARRY_FORWARD_AUDIT.md`,
`CONTINUATION.md`, `GUIDANCE_CHANGES.json` and `evidence/VERIFICATION.json`
before preparing another run. Preparation must bind fresh paths/run
identity, isolated memory, fresh bounded health evidence and native prelaunch
setup. Do not launch directly using the inherited paths or reuse old receipts.
Whole-task completion still requires operator audit and any authorized
continuations; this copy adds no deterministic task-completion gate.

No model, benchmark, sandbox setup or harness service was launched to make or
verify the initial copy. Both reusable top-level harnesses and the original
benchmark sources were preserved.

## Subsequent authorized Claude adaptation

The user subsequently requested a full Claude Code setup adaptation and bounded
real CLI tests. This working copy now includes that adaptation; the initial
byte-for-byte digest above describes its creation baseline. See
`docs/CLAUDE_BENCHMARK_SETUP.md` and the parent repository's
`root_runs/claude-adaptation-20261030/` for the changes and verification.
Its configuration selects the separately prepared Claude workflow-1 workspace
under `root_runs/zstd-claude-ready-20261030/`. Original repaired sources remain
in place. The prepared full benchmark is not launched by the bounded tests.

## Hackathon benchmark support location

This copied harness stays at the hackathon project's top level. Benchmark support
is under `../bench-verification/`. The user subsequently removed the run folders,
so no prepared workspace remains. The last configured ROOT workspace is a removed
path; bind a fresh workspace only when preparation is requested. Do not restore
historical runs. Read `../bench-verification/README.md` for retained source inputs,
reference workflow skills, Python dependencies, and the pinned image archive.
The earlier source locations above describe history in the original repository.
Only path configuration and location notes changed; harness implementation is
retained. No benchmark or native setup ran here.

## Authorized viewer merge

The terminal viewer was ported from `../harness-with-viewer/harness/` into
`orchestrator_harness/view_*.py`, with a new manual `operator_launch view` route.
It selects one epoch, includes retired lanes throughout a multi-step run, keeps
the selected epoch and lane stable during refresh, and handles Windows CRLF
Claude transcripts. See `docs/TERMINAL_VIEWER.md` for usage and retained-history
limits. The original viewer source is unchanged.

This merge leaves the calibrated launch/setup/controller, Claude provider hooks
and adapters, configuration, and benchmark usage collector unchanged. Viewer
and Claude regression checks use temporary fixtures; no native setup, model or
benchmark was launched, and deleted run folders were not restored.

## Viewer replay update

The updated viewer's replay controls, frozen artifact playback, replay banner,
scroll sizing and explicit color override were incorporated. Replay recording
runs in the native monitor and after successful mutating launcher commands,
using per-epoch SQLite sidecars. Capture failure leaves native command outcomes
unchanged, and recorder cleanup precedes the monitor's STOPPED marker. Normal
monitor pass cadence is retained; idle stop checks allow recorder cleanup within
the existing shutdown wait window.

The benchmark port retains all epoch recordings and keeps the selected epoch
fixed. It does not adopt the source viewer's newest-only pruning or automatic
workspace switching. The calibrated Claude launch/setup/controller, provider
hooks/adapters, configuration and benchmark accounting code remain unchanged.
Verification uses offline fixtures, with no native setup or benchmark launch.
