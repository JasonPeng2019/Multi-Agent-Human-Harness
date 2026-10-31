# Claude Code benchmark setup

The user removed this hackathon copy's run folders after transfer. There is no
current prepared trial; workspace and `Launch.ps1` paths below describe the
retained protocol and original preparation. Read `../bench-verification/README.md`
from the harness directory for current assets. Do not restore removed runs.
Fresh preparation and launch require their own authorization.

The existing memory launcher and collector now accept an explicit ROOT provider.
Codex remains the default for existing callers. The collector's historical
filename `scripts/collect_codex_usage.py` and v1 schema names are retained for
compatibility; manifests and ledger rows now identify `provider_id` explicitly.

The separately prepared workflow-1 setup is at
`../bench-verification/root_runs/zstd-claude-ready-20261030/` relative to this harness
directory. Its `run.json` selects this harness, `claude-code`,
`claude-haiku-5-5`, high effort for ROOT and workers, and the original five-hour
absolute deadline. Haiku is the inexpensive verification configuration; select
any future benchmark model/effort explicitly before that run is prepared.
No full benchmark has been launched by this adaptation.

## Preserved behavior

The task inputs and task statement are unchanged. The four supplied workflow
skills retain their exact bodies, with ROOT-only Claude skill discovery added
under `.claude/skills/`; `CLAUDE.md` supplies the existing ROOT/worker instructions.
The ROOT prompt changes provider/model, effort flag and skill invocation syntax.
It retains planning, per-module validation, final parallel independent reviewer
and test validator, partial integration, concrete repair handoffs and evidence.

Native setup precedes ROOT. Provider-bound prelaunch receipts and fresh real
PostToolUse evidence are required before worker admission. Existing dispatch,
queue, result, acceptance, attempt-limit and exact process cleanup mechanisms
remain in use. Every initial or continued ROOT process must finish a read-only
tool call before any bootstrap/launch; a prior segment's hook evidence does not
satisfy the new segment's gate. Diagnose a premature admission failure rather
than bypassing it or repeating setup. Worker memory remains enabled, initially empty and isolated by
run ID. The same lane-local client and restricted service test committed inputs
in the unchanged pinned offline container and return stdout/stderr/exit status.

Operator-assisted continuation resumes the same ROOT session, records separate
receipts, preserves the first finish, and retains the original absolute deadline
including pauses. A failed process launch is not a continuation. Every launcher
gets one attempt, with diagnosis and a fix before a separate invocation.

## Provider differences

Claude uses its existing authenticated CLI, explicit `--model` and `--effort`,
and the shipped adapter's `bypassPermissions` mode. Claude has no Codex service
tier and does not use Codex's Windows filesystem sandbox. No Codex sandbox setup,
refresh, fallback, health receipt or LOCALAPPDATA override is used for a declared
Claude ROOT. This is a provider permission difference, not equivalent OS-level
filesystem isolation. Keep operator/hidden evaluation data outside workspaces
and retain the task's prohibitions on accessing them. Public-check container
isolation and fixed-input/revision checks are unchanged.

## Output-token accounting

Claude CLI 2.1.277 or later is required; the collector verifies its version
without launching a model. Raw stream JSON, CLI identity, command, model, effort,
timestamps, original deadline and segment receipts are retained.

Each terminal `result.modelUsage` is the whole-tree rollup, including built-in
Claude subagents. Independent native harness worker processes are discovered
and counted separately. Assistant-message output counters are placeholders and
are never summed. Main-loop `result.usage` is not substituted for a missing
whole-tree rollup. Resumed session totals are charged as deltas, both for ROOT
segments and worker attempts. Nested forwarded results are not added again.

`known_output_tokens`, `aggregate_components.output_tokens`, per-row
`charged_output_tokens`, and `output_tokens_are_exact` report the result.
Missing, malformed, decreasing or interrupted output evidence never becomes a
claimed exact zero. Cached-input counts are optional and not required for an
exact output count. For Claude the comparison total is explicitly uncached input
plus output, not a claim to include all cache traffic or authoritative billing.

References: [Claude usage accounting](https://code.claude.com/docs/en/agent-sdk/cost-tracking)
and [model configuration](https://code.claude.com/docs/en/model-config).

## Entry points and evidence

Use the prepared setup's `Launch.ps1 -PrepareOnly` to inspect native preparation;
the subsequent authorized `Launch.ps1` validates and reuses that receipt without
repeating setup. The full benchmark requires separate launch authorization.
Continue only through `Launch.ps1 -ResumePromptFile <file>` after an audited,
sealed finish. Existing receipt, failure, deadline and attempt guards apply.

For direct invocation, the existing launcher accepts `-Provider claude-code`
with explicit `-Model`, `-ReasoningEffort`, `-WorkerReasoningEffort`, workspace,
prompt, run identity, credential root and results directory. The offline collector
commands `snapshot` and `finalize` read the resulting `task.json` as before;
`summarize --provider claude-code --events <file>` inspects one Claude stream.

Adaptation plan, offline tests, bounded real ROOT/worker test evidence and
limitations are recorded in the parent repository's
`bench-verification/root_runs/claude-adaptation-20261030/`.

Native lane launch returns quickly. Launching two lanes consecutively from the
harness directory leaves their workers running concurrently. When using Bash
background groups, put `cd HARNESS_DIR` inside each group; `cd h && first & second`
changes directory only for the first asynchronous list.
