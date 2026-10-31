# Worker continuity and recovery

Use this reference when designing worker lanes, including direct use of the formal Tier 4 compiler.
The plan must preserve useful context while preventing retries that repeat a demonstrated failure.
Inspect the selected runtime's resume, result-validation, identity, and cleanup contracts before
assigning capabilities. Use its native controls; do not invent a recovery service or wrapper.

## Prevent recurring launch and handoff failures

When actual launches repeatedly fail for the same permission or configuration reason, plan one
repair at the authoritative configuration owner and prove it with the exact headless tool action.
Authentication and a text-only response do not prove that an observer can start, publish readiness,
and clean up. Use a disposable probe with those actions before another expensive attempt. Scope
permissions to the authorized operations; do not silently select another model or globally bypass
permissions. Keep the configuration fix reusable by later launches instead of copying workarounds.
Check read scope too: a reviewer in an isolated worktree needs explicit access to its named source
directories through the provider's native directory-scope controls. A writable report directory
alone does not establish permission to read the review target. Preserve this scope in resume calls.

When malformed handoffs recur, first reuse or provide a small native result-emission helper that
derives envelope identities from the current ROOT-owned invocation and verified repository state.
The worker supplies substantive outcomes, checks and findings. The helper validates against the
runtime's real schema before atomic publication and after readback; it never fabricates findings,
converts FAIL/BLOCKED to PASS, commits work, or accepts a result. Keep detailed handoffs separate
where their contract differs from the terminal envelope, and use their existing validator if one
exists. Supply exact helper/input/output paths in each affected card and require local correction
of precise preflight errors before the worker finishes. Account for this correction in the same
bounded recovery budget. Do not duplicate the schema in each lane's finalizer.

If the runtime mistakes missing output for success, repair that behavior at its owner when
authorized; a policy reminder alone is insufficient enforcement. Make the prerequisite repair
explicit when the selected runtime is protected. Do not add a wrapper that hides the bad result.

These changes preserve the project's assigned workers and required reviews. Removing mechanical
worker assignments is a separate optional optimization, not a prerequisite for reliable handoffs.

## Choose the continuation

The owning orchestrator makes each recovery decision. A terminal handoff ends a task card, not
necessarily the provider thread: a separately authorized correction card can reuse that thread.
Represent recovery in existing cards and handoffs. Do not create a new review, worktree, lane, or
module merely to fix a report's shape. Preserve the assigned role and independent-review boundary.

| Observed condition | Planned action |
| --- | --- |
| Result satisfies the runtime contract | Proceed to semantic acceptance. A valid FAIL or BLOCKED result is a substantive outcome to classify, not malformed output to retry until PASS. |
| Missing or malformed required result, with safe native resume available | Resume the same thread with the exact validation errors, expected result contract, retained work, and only the unresolved result/handoff correction. Do not repeat discovery or product checks whose inputs remain unchanged. |
| Resume unsupported, thread/worktree unavailable, allocation changed by the user, or unexpected source/external-state drift | Reconcile current state and use a fresh same-role lane with the accepted inputs and first unresolved action. Do not repeatedly attempt unavailable resume. |
| Both same-thread result-correction attempts fail | Retain the failure and useful work, stop only verified owned processes, confirm cleanup before releasing claims, then start a fresh same-role lane on the unresolved action. A repeated error or lack of progress after the first attempt does not trigger this route. |
| A fresh recovery lane also stalls | Reassess the cause and split the unresolved work into smaller concrete outcomes. If a shared prerequisite is broken, diagnose that prerequisite once; do not launch identical replacements against it. Continue independent work. |

Every replacement assignment carries the useful discovery and names what changed to address the
observed failure: a repaired prerequisite, a narrower concrete seam, or an authorized allocation
change. A smaller heading or reworded copy of the same failed task is not a recovery strategy.

Before resuming, verify the native thread/session, repository/worktree, assigned role, selected
provider/model/configuration, output paths, and any consumed external state. Preserve correlation
IDs according to the runtime's actual resume contract; do not invent new identities or blindly
reuse IDs the runtime requires to change. Authorized work by the lane is retained progress, not
unexpected repository drift. A changed input invalidates only the checks or decisions consuming it.

For a frozen controller that exposes `result_validation.state`, require `VALID` before treating its
terminal contract as satisfied; exit zero alone is insufficient. `INVALID` or `MISSING` requires
correction or an honest unresolved classification. Existing product evidence may still support
independent decisions, but never label the malformed launch successful. A worker must not alter
observed outcomes or expected behavior to manufacture a valid PASS, and ROOT must not impersonate
an independent reviewer to fill missing findings.

## Bound retries by progress

Default to two narrow same-thread correction attempts after the initial missing or malformed
terminal result, stopping early when the result becomes valid. The second attempt does not require
progress from the first: models can repeat a mistake on the first correction. A repeated validator
error or lack of progress after that first attempt must not trigger a fresh lane. Unsafe continuity,
unavailable resume, or changed user allocation still requires the reconciliation route above.
Count both correction attempts against the unresolved action; a fresh lane must not silently reset
that history. Local emitter preflight fixes within an attempt do not consume the second resume.
Allow one fresh
recovery lane before splitting or diagnosing the prerequisite, rather than an endless replacement
cycle.

Progress means a resolved validation error, new relevant evidence, a completed assigned action, or
a changed artifact that moves toward the contract. Transcript growth, cosmetic result rewrites,
repeated discovery, and repeated identical commands are not progress. Persistent malformed output
or nonprogress routes terminal-result recovery to a fresh lane only after both correction attempts
fail. Track progress to focus the second correction and subsequent handoff, not to withhold that
second attempt.

If transcript nonprogress needs a time window, calibrate it to observed task/provider behavior and
record the basis. Outside terminal-result recovery, repeated discovery twice or five minutes of repetitive activity
without a relevant change can justify intervention in a lane already exhibiting that failure.
Silence, a slow useful computation, and elapsed time alone do not establish thrashing. This is an
orchestrator progress decision, not an agent-session deadline or permission to use a bounded runner.

Missing/malformed results and thrashing alone never authorize a provider/model fallback. Re-resolve
the current role selection before dispatch and apply only the project's separate fallback policy.
Preserve native compaction; context compaction is not a new task, a failure, or a reason to replay
accepted work. Resume an experiment only within its existing authorization and verified state.

## Keep the recovery handoff small

Record only what the next decision consumes: current thread/lane correlation, relevant source and
resource identities, completed work and reusable checks, exact failure or validator errors,
correction count and progress/stall evidence, cleanup state, and the first unresolved action.
Use existing result/handoff paths and available validation or result-emission helpers. Do not add
an evidence database, new hashes, repeated broad reviews, or a full restart merely for reporting.

For formal Tier 4 output, P02 owns continuity, attempt budgets, progress/stall criteria and fresh
lane routing; P09 owns report-only correction and direct-consumer impact. Cards cite those policies.
Keep the fixed package schemas, required independent reviews, and FAST_LANE_V2 paths intact.

## Semantic validation cases

Before declaring the recovery plan ready, walk through these cases against the selected runtime:

- An implementation is complete but RESULT lacks one required field: request only the result
  correction in the same usable thread; preserve implementation and check evidence.
- A schema-valid result reports a real failed test: classify the defect through the repair route;
  never repeat report correction until its outcome reads PASS.
- The first correction returns the identical validator error: give the second correction in the
  same usable thread with the precise error and focused instructions, preserving partial work.
- Both corrections return malformed output: use the fresh-lane route with the retained work and
  attempt history; avoid resetting the retry budget in successive fresh lanes.
- Resume is unavailable or another actor changed consumed state: reconcile, carry unaffected
  credit forward, and dispatch the first unresolved action with verified inputs.
- A live matrix scenario deliberately tests malformed product results: retain the observed
  malformed result as test evidence. Recovery of the outer worker's report must not rewrite the
  scenario outcome, erase a deviation, or bypass the plan's live-attempt authorization.
- A headless worker authenticates but its required shell action is denied: repair scoped launch
  permissions and prove that action, output and cleanup in a disposable probe before live reuse.
- A worker adds extra envelope fields or copies a stale invocation ID: the native emitter must
  reject misplaced facts or derive the correct current identity, never silently manufacture results.
