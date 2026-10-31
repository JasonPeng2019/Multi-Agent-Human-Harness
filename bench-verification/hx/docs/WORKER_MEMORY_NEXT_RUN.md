# Task-configurable memory for worker lanes

The harness recalls from each ROOT-assigned worker task and delivers the
result only to that worker. Current user policy (2026-10-10): start each benchmark
run with empty, isolated memory until this harness works. Shared memory will be
a later, separate change. Preserve historical stores and do not seed prior run
experience. Verify the selected Atlas collection has zero documents and the
selected EverOS scope has no stored experience before preparation. The launcher
uses per-run defaults but does not itself prove backend emptiness.

For this run copy, launch ROOT with `tools/Invoke-WorkerMemoryRun.ps1` through
the CLI token collector. The user accepted CLI ROOT launch to collect token
usage; it supersedes the earlier native-subagent ROOT instruction. ROOT
launches all Codex planner, implementer, and reviewer/validator workers through
the harness. Every worker uses the launcher's explicit
`WorkerReasoningEffort`, including resumed lanes. It defaults to ROOT's
`ReasoningEffort`; the five-run experiment explicitly overrides it to medium
for the high-ROOT/medium-worker arm. The launcher inserts both effort settings
into the effective worker-delegation prompt. The local run prompt
is `local-config/ROOT_RUN_PROMPT.md`; append the task-specific instructions.
Inspect and finalize the ROOT-plus-worker ledger after all processes exit,
and disclose any missing usage. Keep these run-specific files in this copy;
the outer `harness-single-updated/` and `harness-single-generic/` remain frozen.

ROOT and ordinary worker profiles use gpt-5.6-terra with high reasoning and the default
service tier; the five-run experiment supplies each arm's ROOT and worker
efforts explicitly. The launcher inserts its selected
model, worker reasoning effort, and service tier into every worker's launch
instructions; verify those settings on actual and resumed invocations.

The operator's launcher defaults to a 120-minute limit (WatchdogHours = 2),
enforced externally by the CLI collector from ROOT launch. The ZSTD preset
inherits this default. The base ROOT prompt contains no deadline or time-budget
instruction. In the five-run experiment, only the designated high/high arm
adds time-limit guidance; the other four prompts omit it. Completion still requires the full
task and the prescribed implementation, validation, and cleanup evidence.

For any task, prepare a fresh ROOT workspace, run ID, and harness runtime. Set
`harness-config.json` to that workspace with managed coordination enabled. The
ROOT prompt and `AGENTS.md` must not direct ROOT to read an operator memory file.
Use a stable task ID. The default Atlas collection is `benchmark_run_<sha256>`
where the digest is of the exact UTF-8 run ID; EverOS defaults to project
`<RunId>` and namespace `<RunId>-workers`. Explicit scope overrides must remain
fresh and isolated under the current policy:

```powershell
.\tools\Invoke-WorkerMemoryRun.ps1 -RunId <fresh-run-id> `
    -Task <task-id> -Workspace <fresh-root-workspace> `
    -PromptFile <fresh-root-prompt>
```

The launcher runs native `harness setup` before starting Codex ROOT. Setup
installs and binds ROOT's hooks, opens the runtime, and starts its native
monitor. The collector refuses a fresh ROOT launch without the matching
`.agent-workspace/ROOT_PRELAUNCH_SETUP.json` receipt and unchanged hook files.
It explicitly enables hooks and trusts this invocation's project layer.
ROOT continues with that prepared runtime and must not rerun setup at startup.

Use `-PrepareOnly` with the same arguments to initialize and inspect the
harness without starting ROOT. Invoke again without that switch and with the
same run ID to launch the prepared run. An existing runtime without this exact
run's setup receipt is rejected; historical runtimes are never adopted.
An existing result directory for the run ID is also rejected before setup or
prompt writes, so a duplicate invocation cannot overwrite launch evidence.

The launcher reads Atlas and embedding credentials from `.secrets/creds/`, uses
the `memory-dev` database by default, and sets the EverOS project and namespace
from the run ID. You can override `-AtlasDatabase`, `-AtlasCollection`, `-AtlasIndex`,
`-AtlasTextKey`, `-AtlasEmbeddingKey`, and the `-Everos*` scope options, but current
preparation must use empty per-run stores. Atlas documents also use the `task`
metadata field when selecting recall within the collection.
The collection's vector index must match its embedding and text fields.

For a new ZSTD run, the compatibility preset uses the same per-run defaults:

```powershell
.\tools\Invoke-WorkerMemoryZstdRun.ps1 -RunId <fresh-run-id> `
    -Workspace <fresh-root-workspace> -PromptFile <fresh-root-prompt>
```

A new task with no stored history receives an explicit “no similar experience”
message. A backend failure is recorded separately from an empty search;
bootstrap stops if both backends are unavailable.

This experiment uses a Sol/xhigh native planner and Terra/high for ROOT and
all other workers, including resumes. The planner uses module-planning to
produce dependency-ordered packages with one objective, inputs, one
deliverable, and acceptance criteria. Each fresh module worker makes a
short local plan and implements its package. ROOT coordinates and integrates.

Run-specific guidance lives in super-cache/custom/module-planning/SKILL.md
and super-cache/custom/module-worker/AGENTS.md. Setup stages these files;
ROOT installs the planner skill and appends the implementer instructions
after bootstrap and before first launch, preserving existing AGENTS.md rules.
Follow local-config/ROOT_RUN_PROMPT.md for this arm's validation schedule.
Module completion uses its own acceptance criteria; full-task checks are final.

Repair workers diagnose and fix failures themselves, using the current
revision, failing checks, and prior attempt evidence. Do not require a
separate pre-repair reviewer. Each lane/session still gets its initial
assignment plus at most one corrective resume. Settle source custody and
confirm exact provider exit before a fresh repair lane takes ownership.
An implementer or repair session cannot serve as an independent validator.

Before validation, ROOT runs the available public build/test checks against
the exact candidate revision and preserves results, including failures.
Launch fresh independent validators in new lanes, without reusing implementer
sessions. Every validator's initial task card includes that revision, exact
commands, output or accessible evidence artifact references, per-case
pass/fail results, and known failures with expected versus actual behavior.
Rerun missing or stale checks before launch. If no public suite is provided,
supply the available task build/test evidence and state that limit. Label
failing candidates partial and identify their score blockers. Ask reviewers and
validators to report all substantiated material gaps in their assigned scope,
not just the first blocker, with source locations, specification invariants,
discriminating checks, and prioritized repair recommendations. State uncertainty. Refresh the evidence
and revalidate the final revision after any candidate change.

Each worker receives memory selected for its task card. ROOT coordinates,
integrates, and records the formal harness acceptance. Reviewer(s) have clear,
complementary specialties: for example, one reviews code and edge cases while
another writes and runs tests and builds. Prefer separate reviewers when both
jobs are substantial. Additional reviewers can cover security, performance,
or integration when that is substantial work; avoid duplicate or trivial
lanes. At least one reviewer runs task-specific builds and tests where it has
access, and each gives an evidence-based PASS/FAIL finding on the final
integrated revision. Where only ROOT can execute a host-only test command, it
relays the exact command and output for independent assessment.
ROOT cannot claim task completion on its own judgment or on failed/missing
validation. The important log records recall queries, results, selection,
and final worker prompts.

Credentials are removed from worker and controller environments.
