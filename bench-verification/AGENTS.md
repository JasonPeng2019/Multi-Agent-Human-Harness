# Coding-agent instructions

Read `CODING_AGENT_ENTRYPOINT.md`, `CURRENT_HARNESS.md`,
`CODING_AGENT_HANDOFF.md`, and `README.md` before selecting a setup.

During this transfer, the user said deletion of `root_runs` is expected. Preserve
those deletions; do not restore removed run folders to satisfy the initial copy
manifest. Check that a run-specific setup still exists before using it. Fresh
preparation requires a separate request.

This bundle was copied for future Zstd / SWE-Marathon runs. Copy/preparation is
not authorization to launch or resume a model benchmark or perform native setup.
No prepared trial remains after the user's deletion. Prepare a fresh run only
when requested, and launch only after explicit authorization. Every new trial
needs its own clean workspace, run ID, memory scope, matching harness paths,
fresh health evidence, and native prelaunch receipt.

Every launcher invocation gets one attempt. Preserve failures and diagnose/fix
them before a separate invocation. Do not retry setup automatically, switch
sandbox implementations, or bypass health gates. Only stop processes whose exact
PID, creation identity, and ownership by this work have been verified.

Keep hidden evaluation material and reference solutions outside agent workspaces,
prompts, and memory. Use the corrected immutable image and calibration recorded
in `root_runs/zstd-evaluation-repair-20261015/EVALUATION_CONFIG.json`.
The old `lf-20260925` image has corrupted expected outputs and is unsuitable for
new score comparisons. Preserve source bytes from pinned Git, not a checkout's
newline-normalized text.

Audit actual skill-defined workflow completion after each reported finish.
Preserve the first finish, use the same ROOT session for authorized continuations,
retain its original deadline and attempt limits, and account for every segment
and worker. Do not provide hidden grading feedback to live agents.

`reference/` and copied historical health records supply provenance only. They
are not current launch receipts. The memory scope is fresh but its remote
emptiness has not been rechecked during copying. EverOS capture/recall wiring and
removing the Atlas startup dependency remain deferred implementation work.

Update `CURRENT_HARNESS.md`, entry point, and handoff together if maintained
copies move or are replaced. Preserve original repository sources. In particular,
the sibling original repository's `harness-single-updated/` and
`harness-single-generic/` remain frozen and outside this task's write scope.
