# Modular Execution-Package Templates

These are the exact artifact skeletons for `design-project-topology`. They define one modular plan and
workflow package, not a default workflow. Module decisions and graph edges must be derived from the
   project. Global rules, the three-entry step composition, M-module behavior, agent allocation, and validation each have one
authoritative file.

## Contents

1. Authoring rules
2. Reference conventions
3. Composition-root skeleton
4. Global-rules skeleton
5. Independent step-file schema
6. M01-M10 module-file and instance schema
7. Validation file and structural definitions

## 1. Authoring rules

These skeletons specify the expanded runtime package and legacy format. For new
formal plans use [normalized authoring](normalized-authoring.md) and the executable
source compiler. Populate each decision at its source owner; generate reciprocal
indexes and fully expanded cards instead of hand-maintaining them in these tables.
Steps own local instances, library definitions own shared recipes/defaults, and
review records retain actual independent judgments. Do not add source/state files
inside the exact generated package envelope. An old instruction to "fill" a table
means bind its source inputs and compile the table, not create a second authority.

The [plan-conformance review](../../plan-conformance-review.md) and test-scope audit
use four distinct independent reviewer groups with unanimous final approval. Use
the expanded Audit field / Value rows and group-approval table in
[test-scope audit](../../test-scope-audit.md), including outcome/non-goals,
scope/authority, topology/simplicity, verification/budgets, execution authorization
boundary and final Plan review verdict. Keep their authoritative facts in existing
plan-workflow.md scope/authority, cost and external-operation fields. Section 16
records review evidence and dispositions, not a new runtime permission source.

For every selected acceptance activity or equivalent family, bind
[Acceptance design](../../acceptance-design.md) in existing claim/oracle, Inputs,
Local instructions, cost and invalidation fields. Explain environment necessity,
repetition/combination rationale and the simpler adequate design or justified
retention. Use the [review assignment](../../../assets/plan-review-assignment.md)
for concrete independent review duties. In Section 16's existing per-STEP table,
populate Necessity assessment, Multiplicity assessment and Proportionality assessment
with actual group judgments/references covering all three entry paths. Do not add
these as fields to fixed module or task-card tables.

For every substantial post-step matrix, use
[Matrix execution](../../matrix-execution.md) and the
[matrix binding template](../../../assets/matrix-execution-binding.md).
Map its prompts into the owning module/card's existing Inputs, Outputs, Isolation
and lifecycle, Critical-path effect and Local instructions fields, referencing
shared bindings once. Do not append fields to fixed tables or require a new package
file. The same obligation applies to normal and repair-entry matrices. Record the
review of scheduling, terminal exits, collection, cause-group repair, affected reruns
and coordinate/total budgets in the existing Section 16 scope-audit tables.

Apply [Test-scope audit](../../test-scope-audit.md) before finalizing the package.
Under validation.md Section 16, include its exact metadata, group-approval and
per-STEP evidence-audit table schemas, populated from four actual independent
reviews, writer dispositions and ROOT acceptance. These three mandatory audit tables
extend the validation schema; existing artifact headings, V01-V30 rows, module
recipes and fixed STEP paths remain intact. No N/A sentinel is permitted in any
of these tables. The deterministic validator rejects missing or unaccepted audit records;
semantic sufficiency and reviewer authenticity still require direct inspection.

For applicable execution risks, use [execution efficiency](../../execution-efficiency.md)
to specialize the existing owner fields, policies and module actions. Record
semantic validation separately from structural PASS and leave unavailable runtime
enforcement explicit. Do not add new required artifacts or duplicate policy prose
in every card.

1. Create the exact package from `artifact-architecture.md`: `plan-workflow.md`, `global-rules.md`,
   `validation.md`, one `steps/<STEP-ID>.md` per gated step, and exactly `modules/M01.md` through
   `modules/M10.md`. Keep the
   sole canonical role-agent mapping in its JSON file. Do not copy this reference's introduction.
2. Preserve each artifact's exact headings, table headers, policy order, step field and entry-flow order, M-module
   field order, module-instance heading order, task-card field order, and structural-check IDs. Every
   declared schema table header occurs exactly once in its owning section/card; a second valid-looking
   table is a contradictory shadow, not an override.
3. Replace every `{{UPPER_SNAKE_TOKEN}}` with project-specific content. Delete every line beginning
   `TEMPLATE NOTE:`. The validator rejects remaining tokens or notes.
4. Repeat table rows, step files, and module-instance blocks only for real project items. Use the reference labels below only
   where cross-references make the plan clearer. Do not create labels, records, or tracking machinery
   merely because the template permits them.
5. `N/A` sentinel rows are permitted only in these genuinely optional tables: Section 8 parallel
   groups; Section 10 claim/lock, check, source-allocation, and retirement
   manifests; Section 12 external/readiness decisions; Section 13 integration/release decisions; and
   Section 14 final tolerances/out-of-scope items. Use exactly one explained sentinel row when such a category has no
   items. No other required table may use an `N/A` sentinel, regardless of justification.
   Selected executable fields also reject bare equivalents such as `none`, `disabled`, `skipped`,
   `omitted`, `ineligible`, `unavailable`, `not needed`, `not required`, or `no action`; state a
   concrete controlling fact and route instead of using a synonym to hollow out the field.
6. A table row must contain one decision. Put cross-cutting behavior only in `global-rules.md`, put
   each M01-M10 ingredient's flow/rules and executable instance cards only in its `modules/Mxx.md`, and
   put each gated composition and its three distinct entry paths only in its `steps/STEP-*.md`. Reference stable IDs elsewhere instead of copying prose.
7. The generated Markdown package must contain no concrete provider, model, reasoning-effort, or service-tier
   selection. Those values live only in the separate canonical role-agent mapping.
8. Classify every gate as `PRODUCT` or `OPERATION_BOUNDARY` by what failure disproves, not by whether
   the step is required. A product gate decides observable behavior, contract, capability, or
   correctness and may loop only for a failed or genuinely undecidable required product criterion. A
   required allocation, integration-coordinate mutation, deployment, promotion, readback, cleanup, or
   retirement is still an operation boundary when its failure leaves accepted behavior intact. An
   operation boundary may hold only its exact operation/resource and must leave every independent
   successor default-forward.
9. In each gate row, make those bounds mechanically visible. A `PRODUCT` continuation cell must say
   `only` and name the `required product` criterion that `failed` or is `undecidable`; its blocking scope
   must say `only`. An `OPERATION_BOUNDARY` scope must say `only` and `never product`, its continuation
   cell must say `No product loop`, and its failure target must not name M02/material/product repair.
   Every default-forward cell must name the successor/terminal action that still advances.
10. Keep logical-task continuity separate from persistence of a concrete provider invocation. P02 and
    every executable card must keep the functional role, bounded card, accepted state, complete
    accepted results, and first unresolved action continuous within one unaccepted task. They must prefer
    reuse of the active invocation only when it remains available and the current mapping and user
    direction still select it. They must instead require a recorded structured handoff when the user
    changes subagent/provider/allocation or the invocation cannot resume. Neither case by itself
    invalidates product credit, restarts completed work, or requires a product loop.

11. P02/P04/P09 must adopt the repository's discovered bounded-command manifest for only its selected
    finite commands. Plans must name behavior and discovered sources, not mandate `.codex`, `.claude`,
    or another provider's filenames. Each covered finite-command card must carry a realistically
    calibrated expected upper bound, bounded cleanup allowance, computed maximum lifetime and basis,
    heartbeat no greater than 60 seconds, terminal result path, exact cleanup expectation, and timeout
    support-classification route. Agent/subagent sessions and agent-launch wrappers are explicitly
    unbounded and never appear in that manifest. When an available provider hook can inspect commands,
    it must reject only selected direct finite commands that bypass the launcher.
12. Assign an ID to every orchestrator/root, agent, or subagent process/process tree; provider
    invocation/session/thread; handoff; lane; claim/lock; and Git worktree. These are runtime instances
    whose exact lifecycle must be correlated. This mandatory rule does not make identity a general plan
    property. Plan-local labels are optional cross-references, and ordinary features, files, sources,
    caches, configurations, facts, checks, results, and non-agent workspaces need no ID merely because
    they exist. Add a revision, hash, receipt, immutable record, or evidence file only when a named
    operation or decision requires it. Hashes are reserved for byte-integrity or content comparison;
    immutability is reserved for records or history that must not change after acceptance.
13. Treat every executable card as a complete dispatch contract authored by its owning orchestration
    authority. In the direct topology that authority is ROOT. In the optional two-orchestrator-tier topology, ROOT
    first defines the lane boundary and its authorized lane sub-orchestrator authors every worker card
    in that lane. The card must state the problem/activation fact, desired result, exact behaviors or
    proof targets, target and protected surfaces, required and forbidden changes, authoritative inputs,
    checks, acceptance/tolerances, realistic pitfalls, outputs, failure/stop routes, and next handoff.
    The worker chooses mechanics only inside those bounds and returns any material omission or
    contradiction to its owner. A review or audit card leaves findings open but still fixes the frozen
    input, class, investigation surface, governing invariants, watch areas, exclusions, materiality
    threshold, output, and handoff.
14. Interpret every worker-facing `define`, `select`, `choose`, `classify`, `resolve`, `decide`,
    `authorize`, `continue`, `resume`, `start`, or equivalent action as execution of an owning
    authority's decision or exact deterministic rule. It must not transfer task semantics. An
    undeclared behavior, test meaning, oracle, conflict, retry/new attempt, acceptance choice, scope
    expansion, or next edge returns to the owning authority and, when it crosses a lane boundary, to
    ROOT. Review/audit may determine findings independently only within its concrete assigned
    investigation boundary.

15. For every expensive multi-check gate, accumulated safeguard, or stateful practical/hardware
    attempt, P04/P11/P12 must name independently runnable check units,
    conservative source/configuration/runner/environment/external-state inputs, checkpoint owner,
    PASS reuse condition, first-unresolved checkpoint field, earliest-required-unit execution rule,
    and ordinary-failure continuation rule. The required execution set contains failed, unresolved,
    change-affected, and uncertain units; it begins with its earliest member and never replays an
    unaffected PASS. A checkpoint records only facts a later selector needs; a revision or external
    attempt state is used only when needed to decide reuse. Put
    `CHECKPOINTED_VERIFICATION_V1` in Section 0; it is the required formal-plan
    protocol selector, not an identity or evidence artifact. P07 names its compatible-finding batch
    and the condition for resuming assurance.
16. Every `STEP-*` must first copy the canonical FAST_LANE_V2 usage block below exactly once and
    unchanged beneath its entry-flow heading, then define exactly three distinct entry paths in this order: `NORMAL`,
    `FAST_LANE_V2_SERIES_1`, and `FAST_LANE_V2_SERIES_2`. `NORMAL` may contain any justified number
    and combination of M01-M10 instances, all named `MI-NORMAL-*`. Series 1 is the materially narrower
    local repair-and-exit path using only `MI-FL2-S1-*` instances for one compatible
    set of scoped edits owned by that step; it must name the complete feasible finding pool,
    correction objective, motivating test, changed-source compile smoke, independent frozen-tip
    review, separate integration, repaired public output, and later current progress-bound step.
    Series 2 is the materially narrower progress-bound re-entry path using only `MI-FL2-S2-*`
    instances; it must receive and join accepted
    Series 1 exits, calculate the changed-input/invalidation map, preserve unaffected PASS credit, run
    only failed/unresolved/change-affected/uncertain/uncredited units from the earliest required unit,
    and continue the normal successors. Give each entry a disjoint set of configured IDs with its
    required prefix. The
    exact count and M01-M10 combination are project-specific; do not force the illustrative
    repair/smoke/review/integrate or receive/invalidate/check/continue functions into one universal
    module sequence. A fast-lane path must name its saved work and may not invoke or rename the normal
    broad campaign. Both series must always have complete configured paths. Trigger state changes
    runtime execution timing only and has zero effect on required plan content; it never permits
    disabling, omission, relabeling, reasoning away, normal-route substitution, or `N/A`.
17. A selected M04/M07 checking campaign or M09 practical attempt must finish every feasible check
    after ordinary failures, then return one complete pool. P07 must batch compatible material
    findings before another assurance run.

## 2. Reference conventions

Use these labels when the plan needs unambiguous cross-references. They are document references, not
claims of runtime identity or requirements to create persistent records. The numeric width is formatting,
not a count limit.

| Family | Meaning | Example |
|---|---|---|
| `SRC-*` | Authority/source | `SRC-001` |
| `OUT-*` | Acceptance outcome | `OUT-001` |
| `BOUND-*` | Exclusion/authorization boundary | `BOUND-001` |
| `REQ-*` | Atomic requirement | `REQ-001` |
| `DEL-*` | Coherent deliverable | `DEL-001` |
| `STEP-*` | Independently gated workflow step | `STEP-001` |
| `MI-NORMAL-*` / `MI-FL2-S1-*` / `MI-FL2-S2-*` | Selected module instance owned by exactly one STEP entry | `MI-NORMAL-IMPLEMENT` |
| `CARD-*` | Governing or member task-card contract | `CARD-001` |
| `EDGE-*` | Typed graph edge | `EDGE-001` |
| `PG-*` | Parallel work group | `PG-001` |
| `JOIN-*` | Join | `JOIN-001` |
| `GATE-*` | Decision/gate boundary | `GATE-001` |
| `LOOP-*` | Same-task repair return | `LOOP-001` |
| `LANE-*` | Executable lane | `LANE-001` |
| `LOCK-*` | Claim/lock | `LOCK-001` |
| `CHECK-*` | Named check when cross-reference is useful | `CHECK-001` |
| `HANDOFF-*` | Runtime handoff; always identified | `HANDOFF-001` |
| `RESULT-*` | Durable result reference only when a consumer needs one | `RESULT-001` |
| `ALLOC-*` | Source allocation | `ALLOC-001` |
| `RETIRE-*` | Retirement action | `RETIRE-001` |
| `EXT-*` | External/practical decision | `EXT-001` |
| `REL-*` | Integration/release decision | `REL-001` |
| `EXC-*` | Predeclared exception | `EXC-001` |
| `LEDGER-*` | Tolerance/unresolved/out-of-scope item | `LEDGER-001` |

## 3. Composition-root skeleton

Copy this skeleton into `plan-workflow.md`. It intentionally omits global-policy prose, step bodies,
M-module bodies, rule mapping, and validation rows. It imports those authoritative
artifacts from Section 0.

# {{PROJECT_NAME}} - Modular Execution Plan

## 0. Plan contract and status

| Field | Value |
|---|---|
| Plan ID | {{PLAN_ID}} |
| Plan version | {{PLAN_VERSION}} |
| Status | VALIDATED |
| Decision owner | {{DECISION_OWNER_ROLE}} |
| Orchestration topology | {{ROOT_DIRECT_WORKERS_OR_ROOT_WITH_LANE_SUB_ORCHESTRATORS}} |
| Verification protocol | CHECKPOINTED_VERIFICATION_V1 |
| Operative document boundary | {{OPERATIVE_AND_SUPERSEDED_BOUNDARY}} |
| Change procedure | {{CHANGE_AND_AFFECTED_WORK_PROCEDURE}} |
| Definition of valid | {{SEMANTIC_AND_STRUCTURAL_VALIDITY_DEFINITION}} |

TEMPLATE NOTE: `VALIDATED` is the only final passing status. A work in progress blocked by a missing
fact remains `INCOMPLETE`, may not claim `PLAN_STRUCTURE=VALID`, and cannot pass the final validator.

### Package dependencies and edit boundaries

| Dependency | Authoritative path | Owns | Referenced by | Compatible edit boundary |
|---|---|---|---|---|
| Global rules | global-rules.md | P01-P15 and EXC-* behavior | STEP-* and M-module citations | Edit here only while policy IDs and public contracts remain compatible |
| Gated steps | steps/ | One independent STEP-* composition, public boundary, and NORMAL/FAST_LANE_V2_SERIES_1/FAST_LANE_V2_SERIES_2 entry contract per file | Section 6 and Section 8 | Internal composition edits stay local while the step interface remains compatible |
| M-module library | modules/M01.md through modules/M10.md | Module selection, interfaces, rules/process, variations, MI-* instances, and cards | STEP-* compositions | Internal module-flow edits stay in one M file while its public contract remains compatible |
| Agent mapping | {{CANONICAL_MAPPING_PATH}} | Concrete role-to-agent launch selection | Runtime role resolver | Change one role allocation without Markdown or launcher edits |
| Validation | validation.md | Rule application and V01-V30 results | Delivery report | Observes behavior; defines none |

Step-file, module-file, and module-catalog order are not execution order. Only typed step edges and
the composition inside each step define runtime order.

## 1. Inputs, authority, and directive hierarchy

| Source | Authority | Path/reference | Supplies | Conflict rule |
|---|---|---|---|---|
| SRC-001 | {{AUTHORITY_CLASS}} | {{SOURCE_PATH_OR_REFERENCE}} | {{FACTS_SUPPLIED}} | {{CONFLICT_RULE}} |

TEMPLATE NOTE: Add one `SRC-*` row per operative/reference source. The Agent mapping dependency row in
Section 0 is the sole literal mapping-path occurrence; refer here to its role-agent authority without
repeating that path.

| Layer | Authority | May define | Must not override |
|---|---|---|---|
| 1 | Direct user instructions and goal/spec | Required outcome and authority | No lower source; direct instruction controls conflicts |
| 2 | Composition root | Project coverage and inter-step graph | Layer 1 |
| 3 | Global rules | Cross-cutting workflow behavior | Layers 1-2 |
| 4 | STEP-* file | One gated composition through stable MI-* interfaces | Layers 1-3 |
| 5 | M01-M10 module file | One ingredient's rules/process and configured instances | Layers 1-4 |
| 6 | Local governing/member task card | Authorized instance or worker inputs/actions | Layers 1-5 |
| 7 | Handoff/status | Current facts and next authorized edge | Layers 1-6 |
| 8 | Runtime results | Materialized facts needed by a consumer | Any policy layer |
| 9 | Role-agent mapping | Concrete launch selection only | Task semantics or graph order |

The plan's ROOT/orchestrator decision owner must author every direct-worker contract completely before
dispatch. When the optional two-orchestrator-tier topology is selected, ROOT must instead author the bounded lane
contract before dispatching its direct lane sub-orchestrator; that sub-orchestrator authors every worker
contract in its lane. Workers execute and report within the stated problem, objective, desired behavior,
target/protected scope, proof, pitfall, acceptance, and failure boundaries; they do not invent missing
task meaning or authorize their own follow-up edge. Review/audit workers may discover new findings, but
only inside a concretely assigned investigation boundary and without a prescribed conclusion.

Worker implementation discovery is limited to learning how to realize the already-defined result
inside the named source seams. Card insufficiency never authorizes discovery of what the task should
mean. Any specialized recipe verb that appears to choose behavior, tests, conflicts, assurance paths,
retries, attempts, acceptance, or routing must name ROOT's prior decision, an explicitly delegated
lane-local decision, or a deterministic criterion; otherwise the card is not dispatchable.

## 2. Goal, exclusions, and acceptance outcomes

Goal: {{FAITHFUL_GOAL_TEXT}}

| Outcome ID | Required behavior | Acceptance method | Decision owner | Status |
|---|---|---|---|---|
| OUT-001 | {{OBSERVABLE_REQUIRED_BEHAVIOR}} | {{DECISIVE_CHECK_OR_REVIEW}} | {{OWNER_ROLE}} | COVERED |

| Boundary ID | Type | Included/excluded/authorization condition | Reason | Owner |
|---|---|---|---|---|
| BOUND-001 | {{IN_SCOPE_OR_OUT_OF_SCOPE_OR_AUTHORIZATION}} | {{EXACT_CONDITION}} | {{SOURCE_BACKED_REASON}} | {{OWNER_ROLE}} |

## 3. Requirement coverage map

| Requirement ID | Source | Deliverable ID | Implementation owner | Verification | Acceptance owner | Status |
|---|---|---|---|---|---|---|
| REQ-001 | {{SOURCE_AND_LOCATION}} | DEL-001 | {{ROLE}} | {{CHECK_REVIEW_OR_EXTERNAL_VALIDATION}} | {{ROLE}} | COVERED |

## 4. Runtime and repository truth

| Capability/action | State | Source of truth | Invocation owner | Preconditions | How confirmed | Fallback |
|---|---|---|---|---|---|---|
| {{CAPABILITY_OR_ACTION}} | {{RUNTIME_ENFORCED_OR_ORCHESTRATOR_ENFORCED_OR_TARGET_TOOL_INVOKED_OR_UNAVAILABLE}} | {{SOURCE_PATH_OR_COMMAND}} | {{ROLE}} | {{PRECONDITIONS}} | {{CONCRETE_OBSERVATION}} | {{HONEST_FALLBACK}} |

TEMPLATE NOTE: `UNAVAILABLE` is an honest capability state, not a waiver. Any such row requires M01 to
be `SELECTED`, and its fallback must name the exact configured M01 `MI-*` recovery instance.

## 5. Deliverable, dependency, risk, and cost model

| Deliverable ID | Behavioral output | Requirement IDs | Dependencies | Shared seams | Release unit |
|---|---|---|---|---|---|
| DEL-001 | {{INDEPENDENTLY_USEFUL_OUTPUT}} | {{REQ_IDS}} | {{DEL_IDS_OR_NONE}} | {{SHARED_INVARIANTS_AND_INTERFACES}} | {{RELEASE_UNIT}} |

| Deliverable ID | Realistic failure | Impact | Coupling | Expected range | Expensive operations | Cheapest adequate topology | Why |
|---|---|---|---|---|---|---|---|
| DEL-001 | {{LATE_EXPENSIVE_FAILURE}} | {{PRODUCT_IMPACT}} | {{COUPLING}} | {{DURATION_RANGE}} | {{EXPENSIVE_ACTIONS_OR_NONE}} | {{MINIMAL_MODULE_COMPOSITION}} | {{PROJECT_SPECIFIC_REASON}} |

## 6. Step and M-module library index

| Step ID | Step file | Public input | Public output | Gate/decision ID | Acceptance owner |
|---|---|---|---|---|---|
| STEP-001 | steps/STEP-001.md | {{STABLE_STEP_INPUT}} | {{STABLE_STEP_OUTPUT}} | {{GATE_OR_DECISION_ID}} | {{OWNER_ROLE}} |

| Module type | Authoritative module file |
|---|---|
| M01 | modules/M01.md |
| M02 | modules/M02.md |
| M03 | modules/M03.md |
| M04 | modules/M04.md |
| M05 | modules/M05.md |
| M06 | modules/M06.md |
| M07 | modules/M07.md |
| M08 | modules/M08.md |
| M09 | modules/M09.md |
| M10 | modules/M10.md |

TEMPLATE NOTE: Repeat the step row for each real gated step. The ten module index rows are fixed.
Selection decisions, reasons, configured instances, rules, and process live only in the indexed M files.

## 7. Roles and role-agent mapping boundary

| Workflow role | Authority class | Reports to | Directs | Responsibilities | Pool capacity | Context class | Write authority | Resources | Activation | Lifetime |
|---|---|---|---|---|---|---|---|---|---|---|
| {{ROLE_KEY}} | {{ROOT_LANE_SUB_ORCHESTRATOR_OR_WORKER}} | {{PARENT_ROLE_OR_NA}} | {{COMMA_SEPARATED_DIRECT_CHILD_ROLE_KEYS_OR_NA}} | {{RESPONSIBILITIES}} | {{MAX_CONCURRENT_INVOCATIONS_AND_REASON}} | {{BOUNDED_CONTEXT_CLASS}} | {{WRITE_AUTHORITY}} | {{RESOURCE_SCOPE}} | {{ACTIVATION_CONDITION}} | {{LOGICAL_TASK_LIFETIME_AND_INVOCATION_HANDOFF_RULE}} |

TEMPLATE NOTE: Declare exactly one `ROOT` authority row. The normal topology is
`ROOT_DIRECT_WORKERS`: every other role is `WORKER`, reports to ROOT, and directs `N/A`. When the stated
R3 payoff justifies it, select `ROOT_WITH_LANE_SUB_ORCHESTRATORS`: each
`LANE_SUB_ORCHESTRATOR` reports directly to ROOT, directs at least one `WORKER`, and states its exact
R3 payoff, lane outcome, inputs, protected scope, mutable resources, directed workers, permitted local
decisions, terminal handoff, and return conditions in its role row. A worker may report to
ROOT or one direct lane sub-orchestrator and directs `N/A`. Every `Directs` cell is a comma-separated
list of direct child role keys and must agree reciprocally with `Reports to`. These structured edges are
the mechanically validated authority boundary; no role may create a third orchestration tier.

When a lane sub-orchestrator is an acceptance owner, its structured role contract must explicitly name
every exact `REQ-*` ID it is authorized to accept. Lane-local acceptance cannot be inferred from a role
title, broad scope prose, or mere membership in the authority graph.

`Pool capacity` is the role's maximum permitted concurrent invocation count, not a module's active
member count. An M module may change its internal fan-out locally while remaining within this ceiling;
exceeding the ceiling changes the role/resource contract and therefore also requires a Section 7 edit.

| Resolution rule | Unknown-role behavior | Mapping-update behavior |
|---|---|---|
| {{RUNTIME_RESOLUTION_RULE}} | {{FAIL_CLOSED_BEHAVIOR}} | {{NO_WORKFLOW_EDIT_REQUIRED_BEHAVIOR}} |

## 8. Composed execution graph and critical path

| Edge ID | From step/output | To step/input | Condition | Serial/parallel | Join ID | Failure branch |
|---|---|---|---|---|---|---|
| EDGE-001 | {{STEP_ID_AND_OUTPUT}} | {{STEP_ID_AND_INPUT}} | {{EXACT_CONDITION}} | {{SERIAL_OR_PARALLEL}} | {{JOIN_ID_OR_NA}} | {{DECLARED_STEP_FAILURE_ROUTE}} |

| Parallel group | Shared input | Member step IDs | Writable-root isolation | Launch rule | Join ID | Serial exception |
|---|---|---|---|---|---|---|
| PG-001 | {{SHARED_INPUT}} | {{STEP_IDS}} | {{DISJOINT_ROOTS_OR_LOCK}} | {{LAUNCH_ALL_BEFORE_WAIT}} | {{JOIN_ID}} | {{EXCEPTION_ID_OR_NA}} |

| Path ID | Ordered step/edge IDs | Expected range | Overlap | Expensive operations | Why critical |
|---|---|---|---|---|---|
| {{PATH_ID}} | {{ORDERED_IDS}} | {{DURATION_RANGE}} | {{PARALLEL_OVERLAP}} | {{COUNT_AND_ACTIONS}} | {{DEPENDENCY_REASON}} |

| Gate/loop ID | Owning step | Step file | Gate class | Public outcome/operation | Default-forward edge | Failure/return reference |
|---|---|---|---|---|---|---|
| GATE-001 | STEP-001 | steps/STEP-001.md | {{PRODUCT_OR_OPERATION_BOUNDARY}} | {{ONE_PUBLIC_GATE_QUESTION}} | {{SATISFIED_SUCCESSOR_EDGE}} | {{STEP_LOCAL_FAILURE_OR_RETURN_REFERENCE}} |

## 4. Global-rules skeleton

Copy the following H1, Section 9 heading, P01-P15 blocks, and exception table into
`global-rules.md`. Do not copy them into `plan-workflow.md`, step files, or module files.

# {{PROJECT_NAME}} - Global Workflow Rules

## 9. Global workflow policies and exceptions

TEMPLATE NOTE: Preserve these P01-P15 headings in order. Put one or more rows under each table. Cite
selected module IDs; use N/A only in the Module IDs or optional result/record cell when the policy
genuinely has no such consumer or record. Owner, trigger, required action, and exit are mandatory and
never accept N/A. Every cited MI must exist.

### P01 Ownership and decisions

TEMPLATE NOTE: Include a ROOT/orchestrator row making global and lane-boundary definition
non-delegable. For direct workers, ROOT must concretely name the problem/activation fact, desired
result, exact behavior/proof targets, target and protected boundaries, required/forbidden changes,
pitfalls, acceptance/tolerances, and handoff/next-edge decision. If a lane sub-orchestrator is
selected, ROOT must state that lane's bounded authority and the sub-orchestrator must provide the same
concrete contract to every worker it directs. For review/audit, the owning authority must bound the
investigation without prescribing its findings.

| Owner | Trigger | Required action | Exit | Result/record if needed | Module IDs |
|---|---|---|---|---|---|
| {{OWNER}} | {{TRIGGER}} | {{MANDATORY_ACTION}} | {{EXIT_CONDITION}} | {{OPTIONAL_PATH_RECORD_OR_NA}} | {{MI_IDS_OR_NA}} |

### P02 Context and thread lifetime

TEMPLATE NOTE: State that an insufficient card permits only a bounded insufficiency report and
terminal handoff, not worker reconstruction of missing goals, desired behavior, change/protected
scope, test meaning, oracle, acceptance, or routing. Require a separate owning-authority decision/card
for any nontrivial conflict, changed proof meaning, new attempt, or follow-up edge; route any
cross-lane or global issue to ROOT.

TEMPLATE NOTE: Apply [Worker continuity and recovery](../../worker-continuity-and-recovery.md).
State the runtime's terminal validity check, verified identities for same-thread report correction,
two same-thread correction attempts after the initial missing/malformed result, measurable
progress/stall criteria, and fresh/split same-role handoff when continuity is unavailable/unsafe or
both attempts fail. The second attempt must not require first-attempt progress; an identical first
validator error does not justify a fresh lane. Retain accepted work, native compaction, mapping and
review independence. A correction requires a new owning-authority card, not necessarily a new
thread; missing output is enough to initiate correction without fabricating a terminal handoff.
Keep result failure distinct from fallback eligibility and avoid a universal agent-session timeout.
For repeated configuration failures, require a scoped configuration repair and a disposable probe
of the real required tool action, output and cleanup. Replacement cards must explain the changed
assignment or prerequisite while carrying retained discovery forward.

| Owner | Trigger | Required action | Exit | Result/record if needed | Module IDs |
|---|---|---|---|---|---|
| {{OWNER}} | {{TRIGGER}} | {{MANDATORY_ACTION}} | {{EXIT_CONDITION}} | {{OPTIONAL_PATH_RECORD_OR_NA}} | {{MI_IDS_OR_NA}} |

### P03 Failure-case selection

| Owner | Trigger | Required action | Exit | Result/record if needed | Module IDs |
|---|---|---|---|---|---|
| {{OWNER}} | {{TRIGGER}} | {{MANDATORY_ACTION}} | {{EXIT_CONDITION}} | {{OPTIONAL_PATH_RECORD_OR_NA}} | {{MI_IDS_OR_NA}} |

### P04 Check selection and green credit

TEMPLATE NOTE: State the unit/input map, checkpoint and resume owner, PASS reuse rule, the failed/
unresolved/affected/uncertain execution set beginning at its earliest unit, and continuation after
ordinary failure. Because every STEP defines both FAST_LANE_V2 series, also define Series 1's complete
pool prerequisite, distinct narrow repair path, compile-plus-motivating-test smoke, review/integration
exit, and reusable smoke credit, plus Series 2's progress-bound receipt/join, invalidation map,
earliest-required remaining checks, saved work, and normal continuation.

| Owner | Trigger | Required action | Exit | Result/record if needed | Module IDs |
|---|---|---|---|---|---|
| {{OWNER}} | {{TRIGGER}} | {{MANDATORY_ACTION}} | {{EXIT_CONDITION}} | {{OPTIONAL_PATH_RECORD_OR_NA}} | {{MI_IDS_OR_NA}} |

### P05 Review classes and invalidation

| Owner | Trigger | Required action | Exit | Result/record if needed | Module IDs |
|---|---|---|---|---|---|
| {{OWNER}} | {{TRIGGER}} | {{MANDATORY_ACTION}} | {{EXIT_CONDITION}} | {{OPTIONAL_PATH_RECORD_OR_NA}} | {{MI_IDS_OR_NA}} |

### P06 Parallel checks and results

| Owner | Trigger | Required action | Exit | Result/record if needed | Module IDs |
|---|---|---|---|---|---|
| {{OWNER}} | {{TRIGGER}} | {{MANDATORY_ACTION}} | {{EXIT_CONDITION}} | {{OPTIONAL_PATH_RECORD_OR_NA}} | {{MI_IDS_OR_NA}} |

### P07 Finding pooling and material repair

TEMPLATE NOTE: Require every feasible selected result before classification. State how compatible
material findings are batched into one writer tranche and when differing owners/source contexts/criteria
split the pool. Do not rerun assurance until each admitted compatible tranche has an accepted integrated
coordinate. State how every accepted Series 1 exit for the repair set joins once at the current
progress-bound step before Series 2 resumes checkpointed verification.

| Owner | Trigger | Required action | Exit | Result/record if needed | Module IDs |
|---|---|---|---|---|---|
| {{OWNER}} | {{TRIGGER}} | {{MANDATORY_ACTION}} | {{EXIT_CONDITION}} | {{OPTIONAL_PATH_RECORD_OR_NA}} | {{MI_IDS_OR_NA}} |

### P08 Test-only correction

| Owner | Trigger | Required action | Exit | Result/record if needed | Module IDs |
|---|---|---|---|---|---|
| {{OWNER}} | {{TRIGGER}} | {{MANDATORY_ACTION}} | {{EXIT_CONDITION}} | {{OPTIONAL_PATH_RECORD_OR_NA}} | {{MI_IDS_OR_NA}} |

### P09 Administrative recovery

TEMPLATE NOTE: Cite P02 for worker-result recovery. Correct only required report facts using retained
evidence; do not repeat unaffected product checks or rewrite observed FAIL/BLOCKED outcomes to PASS.
Missing or malformed reports hold only their direct consumers and never count as successful launches.
When repeated envelope errors justify it, require a shared native emitter with invocation-derived
identity, worker-authored facts, preflight, atomic publication and validated readback. Keep the
existing domain handoff and its validation separate; schema validity never proves its findings.

| Owner | Trigger | Required action | Exit | Result/record if needed | Module IDs |
|---|---|---|---|---|---|
| {{OWNER}} | {{TRIGGER}} | {{MANDATORY_ACTION}} | {{EXIT_CONDITION}} | {{OPTIONAL_PATH_RECORD_OR_NA}} | {{MI_IDS_OR_NA}} |

### P10 Semantic acceptance

| Owner | Trigger | Required action | Exit | Result/record if needed | Module IDs |
|---|---|---|---|---|---|
| {{OWNER}} | {{TRIGGER}} | {{MANDATORY_ACTION}} | {{EXIT_CONDITION}} | {{OPTIONAL_PATH_RECORD_OR_NA}} | {{MI_IDS_OR_NA}} |

### P11 Full-safeguard scope

TEMPLATE NOTE: For each selected accumulated safeguard, name its check units, conservative input map,
checkpoint owner, first-unresolved checkpoint field, earliest-required failed/unresolved/affected/
uncertain execution route, and terminal complete-pool behavior.

| Owner | Trigger | Required action | Exit | Result/record if needed | Module IDs |
|---|---|---|---|---|---|
| {{OWNER}} | {{TRIGGER}} | {{MANDATORY_ACTION}} | {{EXIT_CONDITION}} | {{OPTIONAL_PATH_RECORD_OR_NA}} | {{MI_IDS_OR_NA}} |

### P12 External authorization and rehearsal

TEMPLATE NOTE: For stateful M09 work, state each practical unit's consumed target/resource state,
PASS reuse condition, checkpoint/resume owner, and the safe close-and-ROOT-reauthorization route when
that state no longer holds.

| Owner | Trigger | Required action | Exit | Result/record if needed | Module IDs |
|---|---|---|---|---|---|
| {{OWNER}} | {{TRIGGER}} | {{MANDATORY_ACTION}} | {{EXIT_CONDITION}} | {{OPTIONAL_PATH_RECORD_OR_NA}} | {{MI_IDS_OR_NA}} |

### P13 Gate/loop sizing, health, and topology reassessment

| Owner | Trigger | Required action | Exit | Result/record if needed | Module IDs |
|---|---|---|---|---|---|
| {{OWNER}} | {{TRIGGER}} | {{MANDATORY_ACTION}} | {{EXIT_CONDITION}} | {{OPTIONAL_PATH_RECORD_OR_NA}} | {{MI_IDS_OR_NA}} |

### P14 Exception classes

| Owner | Trigger | Required action | Exit | Result/record if needed | Module IDs |
|---|---|---|---|---|---|
| {{OWNER}} | {{TRIGGER}} | {{MANDATORY_EXCEPTION_HANDLING_ACTION}} | {{EXIT_CONDITION}} | {{OPTIONAL_PATH_RECORD_OR_NA}} | {{MI_IDS_OR_NA}} |

| Exception ID | Affected policy | Exact trigger | Decision owner | Allowed alternate action | Required confirmation | Preserved results | Invalidated results | Scope | Expiry |
|---|---|---|---|---|---|---|---|---|---|
| EXC-001 | {{POLICY_ID}} | {{EXACT_TRIGGER}} | {{OWNER}} | {{BOUNDED_ACTION}} | {{REQUIRED_CONFIRMATION}} | {{PRESERVED}} | {{INVALIDATED}} | {{SCOPE}} | {{EXPIRY}} |

TEMPLATE NOTE: Emit an `EXC-*` row only for a real bounded alternate route. When none exists, replace
the example with one explained no-exception sentinel row that explicitly says no exception class is declared and that an
unknown route requires plan amendment. Every field of an actual `EXC-*` row is required and rejects
`N/A` regardless of explanation; only the sole no-exception sentinel row may use it.

### P15 Stop and live-harm containment

| Owner | Trigger | Required action | Exit | Result/record if needed | Module IDs |
|---|---|---|---|---|---|
| {{OWNER}} | {{EXACT_LIVE_HARM_TRIGGER}} | {{CONTAIN_PRESERVE_AND_CLASSIFY}} | {{SAFE_BOUNDARY}} | {{OPTIONAL_PATH_RECORD_OR_NA}} | {{MI_IDS_OR_NA}} |

TEMPLATE NOTE: Resume `plan-workflow.md` with Section 10 below. `global-rules.md` ends after P15.

## 10. Lane, resource, result, and handoff manifest

| Lane ID | Module instance | Role | Activation | Mutable root | Consumer | Completion condition | Failure route |
|---|---|---|---|---|---|---|---|
| LANE-001 | {{MI_ID}} | {{ROLE}} | {{ACTIVATION}} | {{ROOT_OR_READ_ONLY}} | {{CONSUMER}} | {{COMPLETION}} | {{FAILURE_ROUTE}} |

TEMPLATE NOTE: Every member task card represents a real worker dispatch and must name one concrete
`LANE-*` ID. Emit a reciprocal lane row for each; this table never uses an `N/A` sentinel.

| Claim/lock ID | Resource | Owner | Activation | Mutable root | Consumer | Completion condition | Failure route |
|---|---|---|---|---|---|---|---|
| LOCK-001 | {{RESOURCE}} | {{OWNER}} | {{ACTIVATION}} | {{ROOT_OR_NA}} | {{CONSUMER}} | {{RELEASE_CONDITION}} | {{FAILURE_ROUTE}} |

| Check | Proves | Dependencies | Result owner | Reuse condition | Rerun route | Result path if needed | Failure route |
|---|---|---|---|---|---|---|---|
| CHECK-001 | {{ACCEPTANCE_CLAIM}} | {{DEPENDENCIES}} | {{OWNER}} | {{WHEN_PRIOR_PASS_REMAINS_USEFUL}} | {{AFFECTED_ONLY_ROUTE}} | {{OPTIONAL_PATH_OR_NA}} | {{FAILURE_ROUTE}} |

| Result/handoff ID | Producer | Consumer | Path if durable | Correlation needed | Publication rule | Completion condition | Failure route |
|---|---|---|---|---|---|---|---|
| HANDOFF-001 | {{PRODUCER}} | {{CONSUMER}} | {{OPTIONAL_PATH_OR_NA}} | {{PROCESS_THREAD_HANDOFF_CORRELATION}} | {{PUBLICATION_RULE}} | {{COMPLETION}} | {{FAILURE_ROUTE}} |

TEMPLATE NOTE: Use one row with a mandatory `HANDOFF-*` ID for every handoff. Use a `RESULT-*`
reference only when a durable result has a named consumer; an ordinary output needs no result ID.
Every member card names its terminal `HANDOFF-*`, so this table never uses an `N/A` sentinel.

| Source allocation ID | Mode | Source/worktree | Writer | Mutable root | Consumer | Completion condition | Failure route |
|---|---|---|---|---|---|---|---|
| ALLOC-001 | {{WORKTREE_VIEW_OR_CURRENT_WRITER}} | {{SOURCE_OR_WORKTREE_ID_WHEN_REQUIRED}} | {{ROLE_OR_NONE}} | {{ROOT}} | {{CONSUMER}} | {{COMPLETION}} | {{FAILURE_ROUTE}} |

| Retirement ID | Target | Owner | Activation | What must be retained | Completion condition | Recovery visibility | Failure route |
|---|---|---|---|---|---|---|---|
| RETIRE-001 | {{LANE_ROOT_OR_RESOURCE}} | {{OWNER}} | {{ACTIVATION}} | {{REQUIRED_RESULTS_OR_CHANGES_OR_NONE}} | {{SAFE_TERMINAL_STATE}} | {{ARCHIVE_OR_RECOVERY_PATH}} | {{FAILURE_ROUTE}} |

TEMPLATE NOTE: Do not emit Section 11 in `plan-workflow.md`. Step bodies live only in `steps/`; all
M01-M10 rules and selected `MI-*` bodies live only in their matching `modules/Mxx.md`. Section 6 is
the sole step/module import index. Resume `plan-workflow.md` with Section 12.

## 12. External and practical validation

| Decision ID | Module type | Decision | Authority/resource | Synthetic proof | Real proof | Owner | Failure route |
|---|---|---|---|---|---|---|---|
| EXT-001 | {{M08_OR_M09}} | {{SELECTED_OR_OMITTED_COLON_FREE_FORM_JUSTIFICATION}} | {{AUTHORITY_AND_RESOURCE_OR_NA}} | {{READINESS_CLAIM_OR_NA}} | {{REAL_ACCEPTANCE_RESULT_OR_NA}} | {{OWNER}} | {{FAILURE_ROUTE}} |

TEMPLATE NOTE: A concrete optional-profile row uses exactly `SELECTED` or
`OMITTED: <free-form project justification>` in its Decision cell. This is a project decision, not an
eligibility gate. A selected M08 or M09 has at least one `SELECTED` row; omission-only rows may describe
only additional optional profiles. For a selected M08 row, Authority/resource and Synthetic proof are
concrete. For a selected M09 row, Authority/resource and Real proof are concrete. When no
external/practical profile is relevant because neither module is selected, use the one explained table sentinel.

## 13. Integration, safeguard, promotion, rollback, and retirement

| Decision ID | Module type | Decision | Accepted input | Action/order | Checks | Promotion/rollback/retirement | Owner |
|---|---|---|---|---|---|---|---|
| REL-001 | {{M06_OR_M07}} | {{SELECTED_OR_OMITTED_COLON_FREE_FORM_JUSTIFICATION}} | {{ACCEPTED_MI_OUTPUT_OR_NA}} | {{ORDERED_ACTION_OR_NA}} | {{AFFECTED_OR_FULL_CHECKS_OR_NA}} | {{COORDINATE_AND_ROLLBACK_OR_NA}} | {{OWNER}} |

TEMPLATE NOTE: A concrete optional-profile row uses exactly `SELECTED` or
`OMITTED: <free-form project justification>` in its Decision cell. This is a project decision, not an
eligibility gate. A selected M06 or M07 has at least one `SELECTED` row whose Accepted input,
Action/order, and Checks are concrete; omission-only rows may describe only additional optional
profiles. When neither module is selected, use the one explained table sentinel.

## 14. Tolerances, unresolved decisions, and out-of-scope ledger

TEMPLATE NOTE: a final package marked `PLAN_STRUCTURE=VALID` cannot retain a concrete `UNRESOLVED`
item. Resolve it first. Tolerance and out-of-scope rows remain available when they record settled
boundaries rather than postponed required decisions.

| Item ID | Type | Exact condition | Consequence | Owner | Resolution boundary |
|---|---|---|---|---|---|
| LEDGER-001 | {{TOLERANCE_OR_OUT_OF_SCOPE}} | {{EXACT_CONDITION}} | {{CONSEQUENCE}} | {{OWNER}} | {{WHEN_AND_HOW_RESOLVED}} |

## 7. Validation-file skeleton and structural definitions

Copy the following H1 and Sections 15-16 into `validation.md`. They observe all final package
artifacts but define no workflow behavior.

# {{PROJECT_NAME}} - Plan Validation

## 15. Rule application matrix

| Rule ID | Plan location | Concrete applied behavior |
|---|---|---|
| R1 | {{LOCATION}} | {{BEHAVIOR}} |
| R2 | {{LOCATION}} | {{BEHAVIOR}} |
| R3 | {{LOCATION}} | {{BEHAVIOR}} |
| R4 | {{LOCATION}} | {{BEHAVIOR}} |
| R5 | {{LOCATION}} | {{BEHAVIOR}} |
| R6 | {{LOCATION}} | {{BEHAVIOR}} |
| R7 | {{LOCATION}} | {{BEHAVIOR}} |
| R8 | {{LOCATION}} | {{BEHAVIOR}} |
| R9 | {{LOCATION}} | {{BEHAVIOR}} |
| R10 | {{LOCATION}} | {{BEHAVIOR}} |
| R11 | {{LOCATION}} | {{BEHAVIOR}} |
| R12 | {{LOCATION}} | {{BEHAVIOR}} |
| R13 | {{LOCATION}} | {{BEHAVIOR}} |
| R14 | {{LOCATION}} | {{BEHAVIOR}} |
| R15 | {{LOCATION}} | {{BEHAVIOR}} |
| R16 | {{LOCATION}} | {{BEHAVIOR}} |
| R17 | {{LOCATION}} | {{BEHAVIOR}} |
| R18 | {{LOCATION}} | {{BEHAVIOR}} |
| R19 | {{LOCATION}} | {{BEHAVIOR}} |
| R20 | {{LOCATION}} | {{BEHAVIOR}} |
| R21 | {{LOCATION}} | {{BEHAVIOR}} |
| R22 | {{LOCATION}} | {{BEHAVIOR}} |
| R23 | {{LOCATION}} | {{BEHAVIOR}} |
| R24 | {{LOCATION}} | {{BEHAVIOR}} |
| R25 | {{LOCATION}} | {{BEHAVIOR}} |
| R26 | {{LOCATION}} | {{BEHAVIOR}} |
| R27 | {{LOCATION}} | {{BEHAVIOR}} |
| R28 | {{LOCATION}} | {{BEHAVIOR}} |
| R29 | {{LOCATION}} | {{BEHAVIOR}} |
| R30 | {{LOCATION}} | {{BEHAVIOR}} |
| S1 | {{LOCATION}} | {{BEHAVIOR}} |
| S2 | {{LOCATION}} | {{BEHAVIOR}} |
| S3 | {{LOCATION}} | {{BEHAVIOR}} |
| S4 | {{LOCATION}} | {{BEHAVIOR}} |
| S5 | {{LOCATION}} | {{BEHAVIOR}} |
| S6 | {{LOCATION}} | {{BEHAVIOR}} |
| S7 | {{LOCATION}} | {{BEHAVIOR}} |
| S8 | {{LOCATION}} | {{BEHAVIOR}} |
| S9 | {{LOCATION}} | {{BEHAVIOR}} |
| S10 | {{LOCATION}} | {{BEHAVIOR}} |
| S11 | {{LOCATION}} | {{BEHAVIOR}} |
| S12 | {{LOCATION}} | {{BEHAVIOR}} |
| S13 | {{LOCATION}} | {{BEHAVIOR}} |
| S14 | {{LOCATION}} | {{BEHAVIOR}} |
| S15 | {{LOCATION}} | {{BEHAVIOR}} |
| S16 | {{LOCATION}} | {{BEHAVIOR}} |
| S17 | {{LOCATION}} | {{BEHAVIOR}} |

## 16. Structural validation result

TEMPLATE NOTE: Use the exact V01-V30 definitions in Section 5 of this reference. Replace this token
with all 30 completed rows, delete the note, and end with exactly one terminal marker.

{{STRUCTURAL_VALIDATION_ROWS}}

PLAN_STRUCTURE={{VALID_OR_INVALID}}

## 5. Independent step-file schema

Create one `steps/{{STEP_ID}}.md` from this exact schema for every independently gated workflow step.
A step composes M01-M10 ingredients through configured `MI-*` references and owns exactly three
distinct entry paths. It never copies module rules, actions, task cards, or concrete agent selections.

# {{STEP_ID}} - {{PROJECT_SPECIFIC_STEP_NAME}}

## Step contract

| Field | Value |
|---|---|
| Step ID | {{STEP_ID}} |
| Objective and independently decidable outcome | {{OBJECTIVE_AND_OUTCOME}} |
| Acceptance owner | {{OWNER_ROLE}} |
| Deliverable and requirement coverage | {{DEL_AND_REQ_IDS}} |
| Global policy and exception references | {{P_AND_EXC_IDS}} |
| Public compatibility boundary | {{INTERNAL_EDIT_BOUNDARY_AND_PUBLIC_INVALIDATION_TRIGGER}} |

## Activation, inputs, and protected boundaries

{{EXACT_ACTIVATION_PREDECESSOR_OUTPUTS_PUBLIC_INPUTS_AND_PROTECTED_SCOPE}}

## Normal and FAST_LANE_V2 entry flows

### FAST_LANE_V2 — canonical usage

Every STEP MUST contain both complete FAST_LANE_V2 rows and their configured, disjoint MI paths. This
is an unconditional plan-construction requirement. The runtime activation conditions below govern
only which configured path executes for a particular event; they can never remove, weaken, relabel,
reason away, or replace required plan content.

Activate `FAST_LANE_V2` only for a compatible set of small, scoped edits with deterministic impact and a
known motivating test. In an affected earlier step, `FAST_LANE_V2_SERIES_1` takes the distinct
`MI-FL2-S1-*` outbound-patch path to make the scoped repair, run only changed-source compile and
motivating tests, independently review and integrate the repaired output, and exit forward to the
current progress-bound step. At that current progress-bound step, `FAST_LANE_V2_SERIES_2` takes the
distinct `MI-FL2-S2-*` inbound-reconcile path to receive all accepted repairs, calculate invalidation,
preserve unaffected PASS credit, run only failed, unresolved, affected, uncertain, or uncredited
checks from the earliest required unit, and then continue normal forward progress. Use these paths to
avoid redoing heavy computations, broad review/test campaigns, or full restarts when their inputs and
PASS credit remain valid; if the activation predicate, deterministic impact, or safe credit reuse cannot be proven,
use R15's normal material classification for that event. That event-level route does not change either
required FAST_LANE_V2 row or its configured contract.

| Entry flow | Status and activation | Consumes | Ordered distinct MI-* path | Produces and exit | Destination or continuation | Checkpoint and invalidation rule | Concrete saved work | Failure/fallback route |
|---|---|---|---|---|---|---|---|---|
| NORMAL | {{NORMAL_ACTIVATION}} | {{NORMAL_INPUTS}} | {{MI_NORMAL_PREFIXED_PROJECT_SPECIFIC_PATH}} | {{NORMAL_OUTPUT_AND_EXIT}} | {{NORMAL_SUCCESSOR}} | {{NORMAL_CREDIT_RULE}} | Original full path; no fast-lane claim | {{NORMAL_FAILURE_ROUTE}} |
| FAST_LANE_V2_SERIES_1 | {{COMPLETE_POOL_AND_SCOPED_CORRECTION_TRIGGER}} | {{COMPLETE_POOL_AND_SCOPED_CORRECTION_INPUTS}} | {{MI_FL2_S1_PREFIXED_SCOPED_REPAIR_SMOKE_REVIEW_INTEGRATION_PATH}} | {{ACCEPTED_INTEGRATED_REPAIRED_STEP_OUTPUT_AND_CHANGE_MAP}} | {{ROOT_SELECTED_LATER_CURRENT_PROGRESS_BOUND_STEP_SERIES_2_ENTRY}} | {{COMPILE_AND_MOTIVATING_TEST_SMOKE_CREDIT}} | {{CONCRETE_NORMAL_BROAD_WORK_AVOIDED}} | {{NORMAL_MATERIAL_ROUTE_ON_FAILURE}} |
| FAST_LANE_V2_SERIES_2 | {{THIS_STEP_IS_CURRENT_PROGRESS_BOUND_TRIGGER}} | {{ACCEPTED_SERIES_1_EXITS_FROM_ALL_AFFECTED_EARLIER_STEPS}} | {{MI_FL2_S2_PREFIXED_RECEIVE_JOIN_INVALIDATE_REMAINING_CHECK_CONTINUE_PATH}} | {{UPDATED_CHECKPOINT_AND_STEP_OUTPUT}} | {{NORMAL_SUCCESSOR_AFTER_REMAINING_CHECKS}} | {{PRESERVE_UNAFFECTED_PASS_AND_RUN_EARLIEST_REQUIRED_REMAINING_SET}} | {{CONCRETE_FULL_RESTART_WORK_AVOIDED}} | {{NORMAL_CHECKING_OR_MATERIAL_ROUTE_ON_FAILURE}} |

TEMPLATE NOTE: The example responsibilities illustrate the required behavior, not a fixed count or
M-module sequence. Use only `MI-NORMAL-*`, `MI-FL2-S1-*`, and `MI-FL2-S2-*` in their respective rows,
with no ID shared across rows. `NORMAL` may contain any justified composition. A fast path should
generally contain fewer MIs, but must in all cases contain purpose-built lighter work. Series 1 must
be materially narrower than its normal broad repair/check path; Series 2
must be materially narrower than restarting normal verification. Both rows always contain complete,
disjoint configured MI paths; runtime trigger state cannot alter or waive either required row.

TEMPLATE NOTE: Copy the `### FAST_LANE_V2 — canonical usage` heading and its paragraph into every
generated `STEP-*` file exactly as written. Keep it directly under the entry-flow H2 and immediately
before the entry table. Do not replace it with project-specific prose.

## Ordered M-module composition

| Order | Instance ID | Module type | Consumes | Produces | Activation/condition |
|---|---|---|---|---|---|
| 1 | {{MI_NORMAL_FL2_S1_OR_FL2_S2_PREFIXED_ID}} | {{M01_TO_M10}} | {{DECLARED_MODULE_INPUT_INTERFACE}} | {{DECLARED_MODULE_OUTPUT_INTERFACE}} | {{EXACT_ACTIVATION_OR_BRANCH}} |

TEMPLATE NOTE: Inventory each configured ingredient once, name it with the prefix of its sole entry,
then reference it from exactly one of the three entry paths above. Do not copy its flow,
rules, recipe actions, reviewer/check count, task card, or agent selection. Internal fan-out and joins
belong to the owning M file when its public interface remains compatible.

## Public outputs and successors

{{STABLE_OUTPUTS_CONSUMERS_AND_DEFAULT_FORWARD_SUCCESSORS}}

## Gate, completion, and return boundary

| Gate/loop ID | Gate class | Shared input | Decided behavioral outcome | Checking module instances | Shared failure family/invariants | Blocking scope | Continuation/loop eligibility | Default-forward edge | Failure return target | Aggregation payoff | Manageability proof | Prior-result boundary | Split/merge trigger |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GATE-001 | {{PRODUCT_OR_OPERATION_BOUNDARY}} | {{SHARED_INPUT}} | {{ONE_GATE_QUESTION}} | {{MI_IDS}} | {{COHERENT_FAILURE_FAMILY}} | {{EXACT_OUTCOME_OPERATION_OR_RESOURCE_ONLY}} | {{REQUIRED_PRODUCT_CRITERION_OR_NARROW_NONPRODUCT_CONTINUATION_RULE}} | {{SATISFIED_SUCCESSOR_EDGE}} | {{SAME_LOGICAL_TASK_ROLE_OR_EXACT_BLOCK_TARGET}} | {{SAVED_REPEAT_COST}} | {{ONE_REPAIR_OBJECTIVE_PROOF}} | {{AFFECTED_AND_PRESERVED_RESULTS}} | {{OBSERVED_TRIGGER}} |

TEMPLATE NOTE: Every STEP has exactly one concrete populated gate/completion row. `N/A`, malformed,
or additional gate rows are invalid; split a second independently decidable gate into its own STEP.

## Failure, continuation, and preserved results

{{CLASSIFIED_EXITS_FIRST_UNRESOLVED_ACTION_COMPLETE_POOL_RETURN_AND_CREDIT_BOUNDARIES}}

## Concurrency, isolation, resources, and lifecycle

{{PARALLEL_GROUPS_WRITABLE_ROOTS_RUNTIME_IDS_CLAIMS_CLEANUP_AND_TERMINAL_STATE}}

## Cost and critical-path effect

{{EXPECTED_RANGE_LAUNCHES_GATES_OVERLAP_AND_CRITICAL_PATH_DELTA}}

## 6. M01-M10 module-file and instance schema

Create exactly one `modules/{{MXX}}.md` from this schema for each of M01 through M10. The file is the
sole project-specific definition of that reusable ingredient. A compatible internal process edit stays
in this one file and is inherited by every step that composes one of its `MI-*` occurrences.

# {{MXX}} - {{CATALOG_MODULE_NAME}}

## Module contract and selection

| Module type | Decision | Instance IDs | Reason |
|---|---|---|---|
| {{MXX}} | {{SELECTED_OR_OMITTED}} | {{MI_IDS_OR_NA}} | {{PROJECT_SPECIFIC_SELECTION_OR_OPTIONAL_OMISSION_JUSTIFICATION}} |

## Public interface and compatibility boundary

{{STABLE_MODULE_INPUT_OUTPUT_PRECONDITIONS_CONSUMERS_AND_PUBLIC_INVALIDATION_TRIGGER}}

## Rules, process, recipe actions, and allowed variations

{{MODULE_SPECIFIC_RULES_DECISIONS_ROUTES_CONCURRENCY_ISOLATION_LIFECYCLE_AND_P_OR_EXC_CITATIONS}}

| Order | Recipe action ID | Project-specific action/process | Allowed parameterization | Decision owner |
|---|---|---|---|---|
| 1 | {{MXX_A1}} | {{CONCRETE_REQUIRED_ACTION_OR_OPTIONAL_PROFILE_DECISION}} | {{ALLOWED_VARIATION_OR_FIXED}} | {{OWNER}} |

TEMPLATE NOTE: Include every required action from this M module's recipe exactly once and in order.
An optional internal branch is represented by the required action's concrete
`SELECTED: <concrete action>` or
`OMITTED: <free-form justification>` decision; the action row itself never becomes `N/A`.
An internal fan-out, reviewer/check count, join, or correction-process change belongs here when the
public interface, semantic/parameter contracts, and declared role pool capacities remain compatible. Add or remove complete member
cards in the configured MI below; do not add an MI or edit a step merely to change an internal worker
count. Global rules remain P*/EXC-* citations. Rewiring existing `MI-*` references is a step-only edit;
adding, removing, or reconfiguring an `MI-*` also changes this owning M file.

## Configured module instances

TEMPLATE NOTE: A `SELECTED` module repeats the exact 16 required schema headings below once per
declared `MI-*`: one MI H3 plus the 15 ordered H4 fields. Name it `MI-NORMAL-*`, `MI-FL2-S1-*`, or
`MI-FL2-S2-*` according to its sole owning entry. Nested H5 task-card labels do not alter that
count. An `OMITTED` module has no instance block. `DEFERRED` and any other third state are forbidden;
resolve selection facts and make the binary decision. Each selected instance is executable,
specializes only allowed parameters, retains exactly one governing 20-field card, and contains at least
one member card. No field in a configured instance or its cards may use `N/A`; express an inapplicable
profile through the owning recipe's omission decision instead of creating a non-executable instance.

### {{MI_NORMAL_FL2_S1_OR_FL2_S2_PREFIXED_ID}} - {{MODULE_TYPE}}: {{PROJECT_SPECIFIC_NAME}}

#### Purpose

{{MODULE_TYPE_DELIVERABLE_OBJECTIVE_AND_PAYOFF}}

#### Coverage

{{REQUIREMENT_IDS_AND_ACCEPTANCE_CLAIMS}}

#### Selection basis

{{PROJECT_SPECIFIC_USEFULNESS_PAYOFF_AND_CHEAPER_ALTERNATIVE_REJECTION}}

#### Owner and roles

{{DECISION_OWNER_EXECUTING_ROLES_POOL_THREAD_RULE_AND_EXACT_MEMBER_DISPATCH_INVENTORY_AS_CARD_ID_EQUALS_WORKFLOW_ROLE}}

#### Preconditions

{{PREDECESSOR_OUTPUTS_SOURCE_AUTHORITY_CAPABILITIES_AND_LOCKS}}

#### Inputs

{{PATHS_OPTIONAL_REQUIRED_REVISIONS_ARTIFACTS_FACTS_AND_MANDATORY_RUNTIME_INSTANCE_IDS}}

#### Local instructions

TEMPLATE NOTE: Use all 20 rows below for the one governing card. Its `ordered_actions` row cites every
owning-M-file action ID exactly once in order and binds instance parameters without copying module
prose. For every actual internal worker dispatch, repeat an H5 `##### Member task card: CARD-*` plus
the exact 20-row table. A member's `ordered_actions` cites only its nonempty applicable ordered
subsequence. Member cards remain inside this MI/M file and never become step entries. Every selected
instance has at least one member card, and all governing/member fields are concrete; `N/A` and bare
equivalents such as `none`, `omitted`, or `not required` are forbidden.
The `Owner and roles` H4 is the authoritative dispatch inventory and lists every member exactly once as
`CARD-ID=workflow_role`; it must match the H5 member-card set and each card's `workflow_role` field.
The governing card's role is ROOT or the MI's explicitly authorized lane sub-orchestrator; each member
role is a terminal WORKER. Every identity-row deliverable/gate/loop reference resolves to a declared
object. Each member's 20 fields name one unique preassigned `INVOCATION-*` ID and one unique
launch-time `PROCESS-*`/process-tree record ID, and its reciprocal handoff repeats both IDs in
`Correlation needed`.

##### Governing task card: {{CARD_ID}}

| Field | Value |
|---|---|
| schema/card_id/module_instance_id/deliverable_id/stage_cohort_id/gate_id/loop_id | {{REQUIRED_DOCUMENT_AND_RUNTIME_REFERENCES_INCLUDING_H5_CARD_ID}} |
| workflow_role | {{ROLE_ONLY}} |
| objective | {{BOUNDED_OBJECTIVE}} |
| why_now | {{ACTIVATION_REASON}} |
| starting_state | {{ROOT_BRANCH_OR_WORKTREE_CURRENT_STATE_PRIOR_RESULTS_AND_CLAIMS}} |
| dependencies_and_predecessor_outputs | {{EXACT_DEPENDENCIES}} |
| working_scope | {{CONCEPTUAL_IN_OUT_AND_EXACT_WRITE_SCOPE}} |
| required_behavior | {{REQUIRED_BEHAVIOR}} |
| initial_entrypoints | {{PATH_REASON_FIRST_ACTION_COUNT_SCORE_AND_JUSTIFICATION}} |
| failure_case_brief | {{REQUIREMENT_TRIGGER_INVARIANT_ORACLE_OWNER_OR_EXPLICIT_NO_REALISTIC_CASE_STATEMENT}} |
| ordered_actions | {{GOVERNING_FULL_MXX_ACTION_LIST_OR_MEMBER_APPLICABLE_ORDERED_SUBSEQUENCE_WITH_BINDINGS}} |
| allowed_tools_capabilities_resources | {{ALLOWED_SET}} |
| forbidden_actions_and_boundaries | {{FORBIDDEN_SET}} |
| verification | {{SHORTEST_DECISIVE_AFFECTED_CHECKS}} |
| deliverables_and_result_paths | {{OUTPUTS_AND_OPTIONAL_RESULT_PATHS}} |
| acceptance_criteria_and_tolerances | {{CRITERIA_AND_AUTHORIZED_TOLERANCES}} |
| completion_review_owner_and_handoff | {{OWNER_CONSUMER_AND_PUBLICATION_RULE}} |
| failure_classification_and_routes | {{MATERIAL_TEST_ONLY_ADMIN_AND_INCOMPLETE_ROUTES}} |
| thread_resume_and_terminal_rule | {{SAME_LOGICAL_TASK_PREFERRED_INVOCATION_REUSE_STRUCTURED_HANDOFF_AND_ACCEPTED_TERMINAL_RULE}} |
| cited_global_policy_ids_and_exception_ids | {{POLICY_AND_EXCEPTION_IDS}} |

TEMPLATE NOTE: Read the governing card as the complete campaign/instance contract authored by ROOT or,
within an explicitly authorized lane, its sub-orchestrator. Read each member card with that governing
contract as one complete worker dispatch; the worker must not assemble its task by interpreting
separate boxes. For an executable non-review member, the worker must be able to execute without discovering the
task's problem, goals, desired result, permitted/protected scope, proof obligations, pitfalls, or
success criteria. A review/audit worker must receive a frozen input, exact investigation surface,
governing requirements/invariants, watch areas, exclusions, materiality threshold, output, and handoff
while remaining free to return no finding or newly discovered in-boundary findings. A material
omission, contradiction, missing member card, `N/A`, `TBD`, `TODO`, `UNKNOWN`, or appeal to worker
judgment makes the dispatch undispatchable. No free-form justification can waive a required card field.

TEMPLATE NOTE: Include the
[finding-admissibility rule](../../acceptance-design.md#finding-admissibility-requirements-define-the-review-boundary)
in each reviewer/auditor block's existing `ordered_actions`, acceptance and result
bindings, without changing the 20-field schema. Require requirement/source linkage,
acceptance impact, test/evidence status and disposition. A genuine gap that leaves
current requirements satisfied and required tests passing is `REJECT-OUT-OF-SCOPE`,
invalid as a required correction or blocker; retain only a truthful nonblocking
note. Green tests alone do not waive a requirement violation or inadequate proof.

TEMPLATE NOTE: Audit action verbs as well as fields. A worker may choose implementation mechanics
inside the complete contract, but every semantic `define`, `select`, `resolve`, `continue`, `resume`,
or `start` must point to the owning authority's already-stated decision or deterministic rule. M03
behavior/oracle, M06 conflicts, M07 assurance-path selection, and M09 new attempts may not be
delegated. Review/audit findings remain independent inside the stated boundary. Preserve the
insufficiency, continuity, and terminal requirements. A module-internal process edit with the same
public and parameter contracts does not require edits to the step or unchanged instance bindings.

#### Outputs and results

{{EXACT_OUTPUTS_OPTIONAL_RESULTS_OWNER_AND_WRITE_ROOT}}

#### Concurrency and isolation

{{PARALLEL_GROUP_PEERS_MUTABLE_ROOTS_CACHE_AND_RESULT_SEPARATION}}

#### Resources and side effects

{{CLAIMS_PERMISSIONS_EXPENSIVE_ACTIONS_AND_CLEANUP_OWNER}}

#### Checks and acceptance

{{FOCUSED_CHECKS_CRITERIA_TOLERANCE_AND_ACCEPTING_OWNER}}

#### Failure and exception routes

{{CLASSIFIED_EXITS_AND_PREDECLARED_EXCEPTION_IDS}}

#### Prior results and change effects

{{PRIOR_RESULTS_CHANGED_INPUTS_RERUNS_AND_PRESERVED_WORK}}

#### Repeat, join, and terminal behavior

{{GATE_LOOP_QUESTION_COMPLETE_POOL_RETURN_REPEAT_SUCCESSOR_JOIN_AND_RETIREMENT}}

#### Cost and critical-path effect

{{EXPECTED_RANGE_LAUNCHES_GATES_OVERLAP_AND_CRITICAL_PATH_DELTA}}

## Structural validation definitions

Place these exact rows under Section 16's table header:

`Check ID | Result | Basis`

Every result is `PASS` or `FAIL`. Basis is one concise project-specific pointer or explanation; it does
not require a durable evidence artifact.

Evaluate V10, V13, V14, and V27 under the recipe-verb rule: field presence is insufficient when a
specialized action still asks a worker to decide unstated task semantics. Review/audit finding judgment
is permitted only within its explicit boundary and does not include scope, editing, acceptance, or
routing authority.

| Check ID | Definition |
|---|---|
| V01 | The exact execution-package files exist once with no extra package item; each required section exists once, in order, and only in its owning artifact; `plan-workflow.md` has exact final status `VALIDATED`; `steps/` contains exactly the indexed `STEP-*` files; and `modules/` contains exactly M01.md through M10.md. |
| V02 | Every required table in every package artifact has exact columns; no hard table or STEP gate uses `N/A`; and only the explicitly allowlisted optional tables use one explained sentinel row when empty. |
| V03 | Every outcome, boundary, requirement, and deliverable row uses its exact ID family; every required outcome and requirement has final status `COVERED`; every requirement maps to one known deliverable, mapped implementation role, verification path, and acceptance owner; every deliverable lists exactly its mapped requirements, has exactly one risk/cost row, and every requirement and deliverable is covered by at least one STEP contract without unknown IDs. |
| V04 | M01-M10 each have one authoritative module file and decision; every selected `MI-*` occurs exactly once in its matching M file using the exact 16 required schema headings—one MI H3 plus 15 ordered, substantively populated H4 fields—and recipe, and is composed by its declared `STEP-*`; nested H5 task-card labels do not change the schema count. |
| V05 | Every inter-step and intra-step edge connects a declared output to a declared input; every fan-out joins or has independently terminal outputs; and the transitive module composition agrees with the public step graph. |
| V06 | No omitted module appears in graph, cards, gates, or handoff routes. |
| V07 | Every non-minimal step, module, and serial edge has a concrete payoff or dependency. |
| V08 | Selected review/check instances on one shared input use a parallel group unless a real dependency or exception is cited. |
| V09 | Every material repair consumes one complete pooled finding set, every feasible selected check continues after ordinary failures, compatible findings batch before another assurance run, and no intermediate repair revision is reviewed. |
| V10 | Every review M04 instance declares class, boundary, scope, shared input, internal member-card fan-out/join, and affected prior results. Its governing and member cards, authored by the owning authority, fix the governing requirements/invariants, per-member surfaces, watch areas, exclusions, materiality threshold, output, and handoff without prescribing findings or allowing silent scope expansion. |
| V11 | Full-safeguard commands occur only in selected M07 instances, each names one release unit, and each expensive multi-check safeguard declares check units, a conservative input map, checkpoint owner, and complete-pool behavior. |
| V12 | A prior PASS is reused only when its declared source/configuration/runner/environment/external inputs and prerequisites are unchanged; the required execution set contains every failed, unresolved, affected, or uncertain unit and begins with its earliest member, while unaffected PASS units are never replayed merely because an earlier unit failed. |
| V13 | Every selected `MI-*` has exactly one governing 20-field card and at least one member 20-field card, every internal worker dispatch has exactly one member card, every member card names one unique `LANE-*` and terminal `HANDOFF-*` with reciprocal Section 10 rows whose consumer is that role's owning orchestration authority, every field is concrete with no `N/A` or bare equivalent, and every card has applicable global-policy citations. Every M01-M10 file contains every required recipe action ID exactly once in order; each governing card cites the full ordered list with concrete bindings, and each member card cites a nonempty applicable ordered subsequence rather than copied process prose. Those cards form complete contracts from ROOT or an explicitly authorized lane sub-orchestrator, covering the problem, desired result, behavior/proof targets, target/protected scope, required and forbidden changes, authoritative inputs, checks, acceptance, realistic pitfalls, outputs, failure/stop routes, and handoff. |
| V14 | Global rules, step composition, M-module behavior, role semantics, and concrete role-agent selection each have exactly one authoritative owner and are referenced rather than copied. The structured authority graph contains exactly one ROOT and either direct WORKER children only or optional direct LANE_SUB_ORCHESTRATOR children with terminal WORKER children; reciprocal `Reports to`/`Directs` edges agree, every worker directs no role, every STEP acceptance owner is ROOT or a lane sub-orchestrator explicitly scoped to all covered requirements, and no third orchestration tier exists. No step, instance, or task card changes global scheduling, review, gate, authority, resource, or result-handling rules or redefines an M-module process. No worker is assigned task-definition, scope-definition, success-definition, acceptance, or self-dispatch authority. An optional lane sub-orchestrator may hold only its explicitly declared lane-local authority, must direct every worker in that lane, and may not create another orchestration tier. |
| V15 | Every exception has a known affected policy, mapped decision owner, trigger, action, required confirmation, preserved/invalidated results, scope, and expiry; when no exception exists, the sole row explains that no class is declared and unknown routes require amendment. |
| V16 | Runtime, orchestrator, target-tool, and unavailable capability classes are distinguished. |
| V17 | Stable launcher behavior is not attributed to target work-product code. |
| V18 | Every workflow role used by a governing or member task card exists exactly once in the isolated mapping with a concrete non-placeholder launch selection; no Markdown artifact contains concrete launch selection, and the composition root mentions the mapping path once. |
| V19 | Source writers are singular unless proven independence and merge order justify fan-out. |
| V20 | Concurrent result writers have disjoint roots or one correct shared append lock. |
| V21 | Context bounds include necessary seams and every non-maximal entrypoint score is justified. |
| V22 | Failure cases are realistic, requirement-linked, oracle-backed, and not generic hardening. |
| V23 | Test/support/report failures, including a failed strict test-only correction/rerun, return to classification, block only exact consumers, never become material repair without a failed or undecidable product criterion, and activate every independently satisfied successor. Manually exercise the shared worker recovery cases: narrow same-thread report correction, valid failed outcome, stalled correction, unavailable/drifted continuity, and intentionally malformed live-test evidence; verify bounded recovery preserves truth and accepted work. |
| V24 | Every STEP defines exactly one concrete gate declaring `PRODUCT` or `OPERATION_BOUNDARY` according to the fact its failure disproves, exact blocking scope, continuation/loop eligibility, default-forward edge, and return/block target; the step contract, Section 6 index, and Section 8 gate index agree; no pure allocation/join/deployment/promotion/readback/cleanup/retirement failure is labeled PRODUCT while accepted behavior remains intact; each gate passes aggregation/manageability and explains why it is neither smaller nor larger. |
| V25 | A product loop is entered only for a failed/genuinely undecidable required product criterion; continuation executes from the earliest failed, unresolved, affected, or uncertain action/check in the same logical role/task, reuses the active invocation only when available and still selected or records a structured handoff, preserves unaffected credit, prospectively splits/merges unaccepted work, and never reopens unrelated accepted work. |
| V26 | Cleanup never deletes unpreserved, dirty, live, ambiguous, or unretained state. |
| V27 | Governing and member module-instance instructions contain no banned vague phrase or undefined owner/trigger/action/exit. A worker is never told to discover material task meaning or decide an unstated goal, desired result, boundary, proof obligation, pitfall, or acceptance criterion. |
| V28 | R1-R30 and S1-S17 each map once to a concrete plan location and behaviorally consistent content in the artifact that owns that concern, without any `N/A` or duplicated authoritative prose. |
| V29 | Every process/process tree, agent/subagent invocation/session, handoff, lane, claim/lock, and Git worktree has a runtime ID; ordinary plan content has no ID/hash/receipt/immutable evidence artifact without a named operational need. |
| V30 | Every `STEP-*` copies the exact canonical FAST_LANE_V2 usage block once beneath the entry-flow heading and before exactly the ordered `NORMAL`, `FAST_LANE_V2_SERIES_1`, and `FAST_LANE_V2_SERIES_2` entries with disjoint configured MI paths using only `MI-NORMAL-*`, `MI-FL2-S1-*`, and `MI-FL2-S2-*`, respectively. Each path cell is an explicit ordered MI list, never prose containing an MI token. The configured MI public contracts themselves implement the named lane responsibilities: Series 1 owns scoped within-step correction, compile and motivating-test smoke, independent review, integration, and exit to the ROOT-selected later progress bound; Series 2 owns receipt/join of accepted Series 1 exits at the current progress bound, changed-input invalidation, unaffected-PASS reuse, earliest-required remaining checks, and normal continuation. Both fast paths are unconditional required plan content, name concrete saved work, are purpose-built and materially narrower than NORMAL, and are never renamed normal MIs. Runtime trigger state changes timing only and never permits an unsatisfiable predicate, opt-out label, disabling, omission, relabeling, reasoning away, `N/A`, or normal-route substitution. |

In the generated plan, render:

| Check ID | Result | Basis |
|---|---|---|
| V01 | {{PASS_OR_FAIL}} | {{PROJECT_SPECIFIC_BASIS}} |

TEMPLATE NOTE: Repeat through V30 with the exact definitions above. `PLAN_STRUCTURE=VALID` is permitted
only when all 30 rows say PASS and deterministic validation succeeds.
