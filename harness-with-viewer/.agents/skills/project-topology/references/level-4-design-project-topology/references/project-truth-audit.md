# Project Truth Audit

Use this read-only audit before composing a topology. Replace assumptions with the smallest set of
current facts needed to choose work, dependencies, ownership, runtime behavior, and verification.
Keep discoveries in disposable working notes and place only consumed facts in their owning plan-package artifact. Do not create
a permanent sidecar, ID, receipt, hash, or evidence artifact merely because a fact was inspected.

## 1. Audit boundary

Inspect only what is needed to decide scope, decomposition, module selection, dependencies, runtime
feasibility, verification, and cost. Prefer current authoritative state over history. Read history only
to resolve a named current ambiguity.

Do not execute the proposed workflow, run product/external tests, launch workers/controllers, create
worktrees or claims, mutate configuration, or treat product code under development as active
orchestration machinery.

Use `UNKNOWN` for an unconfirmed belief. Distinguish mandatory runtime-instance IDs from optional
content tracking:

- orchestrator/root, agent, and subagent processes and process trees: always assign process/parent IDs;
- provider invocations, sessions, or threads: always assign invocation/session/thread IDs;
- handoffs: always assign handoff IDs that correlate sender, receiver, and logical task;
- lanes, claims/locks, and Git worktrees: always assign IDs for ownership, collision prevention, and
  retirement;
- other live resources: assign an ID only when targeting or lifecycle control requires one;
- repository revisions: only when work must target, compare, preserve, integrate, or roll back a
  particular repository state;
- receipts: only when an operation must later prove or reverse its own changes;
- hashes: only when a named byte-integrity or content-comparison decision requires them;
- immutable records: only when a record or history must not change after acceptance.

Plan-local labels are optional document cross-references, not runtime identities. Ordinary features,
source documents, files, caches, configurations, facts, checks, outputs, and non-agent workspaces need
no ID, hash, receipt, or immutable record by default. A feature such as a website button does not
acquire tracking machinery merely because it is planned.

## 2. Source and authority discovery

Find direct user instructions, the product goal/spec, acceptance material, repository instructions,
the current plan, handoff/status files, role-agent mapping, runtime docs, launcher source, test
configuration, and resource/authorization policy.

For each source record only:

`Source | Authority | Path/reference | Supplies | Conflict rule`

Ask what it governs, whether it is operative/reference/historical/superseded, what higher authority
wins, and whether it describes desired or actually available behavior. Mention the canonical
role-agent mapping as an authority source, but put its literal path only in Section 0's Agent mapping
dependency row. Do not add a revision or hash column. If a specific operation later
needs a revision or hash, state that need where the operation is defined.

When operative sources conflict, record the clauses and decision owner. Do not blend them or choose
the newer-looking text without authority.

## 3. Goal and acceptance extraction

Read the goal as a behavior contract. Identify user-visible results, compatibility promises, required
failure behavior, operational outcomes, release outcomes, and exclusions. Use `OUT-*` and `REQ-*`
labels only when cross-references make the plan clearer; those labels are document references, not
runtime identities.

Split a requirement only when clauses can independently pass/fail, need different implementation
owners, use different verification, depend on different authority/resources, or are affected by
different changes. Do not split by sentence, file, function, or checklist formatting.

For each requirement identify the observable behavior, cheapest trustworthy verification, accepting
owner, authorized tolerance, external/practical validation need, and source location. If no sound
oracle exists, mark the verification gap; do not manufacture a test or evidence file.

## 4. Repository and source inspection

Inspect the repository root, relevant branch/worktree state, cleanliness, nested repositories,
ignored runtime roots, and forbidden/user-owned paths. Record a revision only when a later writer,
reviewer, integration, rollback, or cleanup action actually needs that coordinate.

For each requirement inspect the smallest source/test/document set revealing the public entrypoint,
owning implementation, shared state/protocol seam, callers, existing tests/fixtures, compatibility
surface, and cleanup owner. Paths are entrypoints, not reasons to create deliverables or tracking.

Record enforced format/lint/type/compile/test/worktree/cleanup rules and baseline failures. Discover
the effective instruction/provider configuration chain for each executor, including locations such as
`AGENTS.md`, `.codex/`, `.claude/`, or another provider directory. Determine inheritance, prompt
requirements, hooks, bounded supervisor, and the exact mechanical launcher boundary without inferring
test meaning.

## 5. Runtime and launcher inspection

Inspect actual launcher/orchestrator code and executable help when the plan relies on launches,
events, resumption, isolation, results, acknowledgement, claims, locks, watchers, or cleanup.

For each capability determine:

1. invocation owner and actual input;
2. mutable state;
3. completion/failure/timeout/cancellation/cleanup behavior;
4. whether an invocation can resume or needs a correlated handoff;
5. whether provider selection can change at dispatch; and
6. whether behavior is automatic, orchestrator-owned, target-tool supplied, or unavailable.

Classify each as `RUNTIME_ENFORCED`, `ORCHESTRATOR_ENFORCED`, `TARGET_TOOL_INVOKED`, or
`UNAVAILABLE`. Record source/command, owner, prerequisites, how it was confirmed, and fallback. Assign
IDs to every orchestrator/agent/subagent process or invocation, handoff, lane, claim/lock, and Git
worktree because lifecycle control needs exact correlation. Do not generalize that rule to content.

## 6. Verification inspection

Inventory the checks, focused selectors, result formats, writable roots, baseline failures, full-suite
commands, and external observations that the plan may actually use. For each candidate record the
claim checked, relevant inputs, expected duration/resources, isolation, result, affected-only rerun
route, and failure route. For a costly multi-check gate, also determine the smallest economical
independently runnable unit, its source/configuration/runner/environment/external inputs and
prerequisites, whether the real runner can checkpoint/resume it, and how an ordinary failure continues
to remaining runnable units. If the runner cannot expose a useful unit boundary, record that as an
`UNAVAILABLE` capability or the smallest prerequisite; never merely promise resume in the plan.

Use a check ID, registry, or dependency fingerprint only when the existing runtime needs it for
selection or reuse. A plan-local `CHECK-*` label may aid cross-reference but is not a runtime-object
ID. Persistent result paths are optional unless a later consumer, handoff, audit, or recovery
step needs them. A checkpoint contains only completed-unit outcomes, the first unresolved unit, and
the source or external attempt state necessary to decide reuse; do not add hashes or immutable
snapshots by default.

For each manifest-selected finite command, record the realistically calibrated expected upper bound,
cleanup allowance, deadline, heartbeat, bounded supervisor, bypass guard when available, unique result
path required by that supervisor, process-tree cleanup, and timeout classification. These fields exist
because supervision consumes them, not because all verification needs evidence artifacts. Record agent
and subagent sessions separately as unbounded and outside the manifest.

Preflight only fragile custom runners. Reviews, tests, and observers are distinct ways to decide facts;
file existence alone never means the product passed.

## 7. Roles, concurrency, and resources

Read the sole role-agent mapping and runtime role resolver. Keep workflow roles separate from provider
selection. Confirm unknown-role behavior and dispatch-time resolution. When an invocation changes,
preserve the logical role/task through a handoff ID; do not pretend the old and new process are the
same.

Record the slot cap and startup/context/isolation/merge/wait costs. Find genuinely independent slices
and every shared writer, mutable root, cache, result path, event log, or external resource that blocks
concurrency.

Choose the cheapest safe source mode: current checkout for one writer, an identified linked worktree
for an independent writer, a read-only view plus writable result root when needed, isolated execution
state, or no lane for a simple deterministic command. Do not freeze or hash a read-only view without a
specific consistency need.

For hardware/services/credentials/deployments/irreversible actions/scarce namespaces, record authority,
allocation owner, target/resource ID needed for safe targeting, attempt state, observation, abort/stop,
cleanup, and disposable rehearsal options.

## 8. Change and rerun inspection

### Orchestration dispatch-contract source packet

Before module instantiation, assemble the facts ROOT will need to author each direct-worker dispatch
contract. For every prospective worker task, identify the concrete problem/activation fact, desired
result, observable behavior or proof target, exact target surfaces and initial entrypoints, allowed
write scope, protected behavior and non-goals, required inputs and predecessor results, mandatory
checks, acceptance/tolerance boundary, realistic pitfalls, failure classifications, stop/escalation
conditions, handoff consumer, and first unresolved action. These are planning inputs for ROOT, not
questions to defer to the worker. When R3 justifies a lane sub-orchestrator, identify the same bounded
facts for the lane itself, the exact local decisions ROOT grants, its workers, its terminal handoff, and
the facts that must return to ROOT; the sub-orchestrator then authors concrete worker cards within that
boundary.

Also identify the stable public inputs, outputs, and allowed variation points of each prospective
M01-M10 ingredient, then identify the fewest coherent independently gated `STEP-*` compositions that
can combine configured `MI-*` occurrences without copying module process. For every candidate step,
derive its unconstrained project-specific `NORMAL` path, a distinct materially narrower
`FAST_LANE_V2_SERIES_1` scoped-repair/exit path, and a distinct materially narrower
`FAST_LANE_V2_SERIES_2` progress-bound receive/invalidate/resume path. Record separate candidate MI
occurrences for each path using `MI-NORMAL-*`, `MI-FL2-S1-*`, and `MI-FL2-S2-*`, respectively; record
the concrete normal work each fast path avoids, activation triggers and safety constraints,
the changed-input/checkpoint map, and how ROOT identifies the later current progress-bound step.
Record which changes are
module-internal, which alter a module interface, and which alter a public step boundary so later edits
can invalidate only actual consumers. For each prospective internal fan-out, record its governing
owner and one member-card fact set per actual worker: role, surface, inputs, actions, isolation, output,
handoff, and complete task meaning. Treat those members as module-private dispatches, not extra MIs or steps.

For a prospective review or audit, keep the finding set epistemically open while still identifying
the frozen input, review class, exact conceptual/product surface, governing requirements and
invariants, risk hypotheses or pitfalls to examine, exclusions, severity/materiality threshold,
required output shape, and handoff owner. Record the smallest adjacent surface a reviewer may inspect
to understand behavior, or require the reviewer to justify any such inspection. Do not encode an
expected conclusion as a review requirement.

Separate implementation discovery from task-definition discovery. Record the source seams and
adjacent dependencies a worker may inspect to learn how to implement the owning authority's
already-defined result, but do not use repository exploration as a substitute for ROOT, or its
explicitly authorized lane sub-orchestrator, naming the goal, desired behavior, things to change,
protected surfaces, proof obligation, and acceptance boundary. If those semantic facts remain
`UNKNOWN`, the prospective card is undispatchable and the unknown returns to its owning authority.

For each prospective module, scan its specialized actions for verbs such as `define`, `select`,
`choose`, `classify`, `resolve`, `decide`, `authorize`, `continue`, `resume`, or `start`. Record which
ROOT decision, explicitly delegated lane-local decision, or exact deterministic criterion supplies each
verb. Pay particular attention to test scenario/oracle meaning, review/check selection, integration
conflicts, final-assurance path selection, readiness profiles, and retry/new-attempt decisions.
Review/audit finding formation may remain open; its input, surface, invariants, watch areas, exclusions,
materiality, output, and handoff may not.

Discover the smallest semantic inputs that checks and gates consume: requirements, product behavior,
test semantics, execution procedure, external topology, authority, or another project-specific input.
For each, determine which work consumes it, what changes affect those consumers, what passing work
remains useful, and who decides an uncertain change.

Do not create identity records or hashes to implement this analysis. Usually a semantic diff and the
known dependency are enough. A task-card or prompt edit is not automatically product invalidation.
Rerun only work whose consumed meaning changed.

## 9. Gate, blocker, and continuation inspection

For each condition that can delay, deny, repeat, or restart work, record:

- `PRODUCT` or `OPERATION_BOUNDARY`;
- the one outcome, operation, or resource it may block;
- the required product criterion whose failure/indeterminacy permits a product loop;
- successors that remain ready;
- the first unresolved action, any earlier invalidated action/check, and completed unaffected work retained;
- whether stopping is cheaper while preserving outcomes; and
- the check or observation that distinguishes product failure from support failure.

Authorization, allocation, integration, deployment, promotion, readback, cleanup, retirement,
readiness, and resource safety are operation boundaries when their failure leaves accepted behavior
intact. They block only the operation or its direct consumer.

## 10. Completion packet

Finish only when the owning artifacts of the plan package can directly receive:

1. source/authority rows and contradictions;
2. outcomes, requirements, exclusions, and acceptance methods;
3. relevant repository seams and forbidden areas;
4. runtime capability classifications and owners;
5. candidate checks, costs, dependencies, and optional durable outputs;
6. roles, role resolution, concurrency cap, and isolation modes;
7. resource authority, rehearsal, live-harm, and cleanup rules;
8. required runtime-object IDs and only the revisions/receipts/hashes/records justified by operations;
9. gate classes, blocking scopes, continuation points, and ready successors; and
10. named `UNKNOWN` or contradiction items;
11. stable M-module interfaces, allowed variations, module-internal process facts, and governing/member-card needs; and
12. candidate independent step boundaries and their public inputs/outputs; and
13. for every candidate step, the three distinct entry paths, correctly prefixed per-entry MI
    candidates (`MI-NORMAL-*`, `MI-FL2-S1-*`, `MI-FL2-S2-*`), fast-lane
    activation triggers/safety constraints, saved work, repaired-output exit, progress-bound re-entry, and checkpoint
    invalidation facts.

The completion packet must also contain enough task-definition facts for ROOT to fill every material
direct-worker card without delegating the problem, goals, desired results, target/protected scope,
proof obligations, pitfalls, or acceptance boundary to the worker. If a lane sub-orchestrator is
selected, it must also contain the complete ROOT-defined lane contract so that sub-orchestrator can fill
every material worker card in its lane without delegating those decisions to a worker. For review/audit
cards, it must contain the complete bounded-investigation contract while leaving findings and conclusions
open.

Do not create module instances during the audit. Select them only after coverage, deliverables, risks,
costs, and runtime truth are visible together.
