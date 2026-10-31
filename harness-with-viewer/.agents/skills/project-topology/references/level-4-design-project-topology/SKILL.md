---
name: design-project-topology
description: "Compile and structurally validate a significant project execution workflow and plan whose independent gated STEP-* building blocks each define a project-specific NORMAL path using MI-NORMAL-* instances, a distinct lightweight FAST_LANE_V2_SERIES_1 repair/exit path using MI-FL2-S1-* instances, and a distinct lightweight FAST_LANE_V2_SERIES_2 progress-bound re-entry path using MI-FL2-S2-* instances from fixed M01-M10 modules. Use when the user explicitly selects this formal compiler, its full execution-package framework, M01-M10, FAST_LANE_V2 or formal harness workflow, or the governing project workflow requires it. Generic requests for modular organization use the parent project-topology skill. Do not use for general coding, ordinary task execution, diagnosis, or implementing the planned project."
disable-model-invocation: true
user-invocable: true
---

# Compile a modular project topology

This entrypoint implements the full formal Level 4 framework. A generic request
for modular organization or independently editable step/lane files is handled by
the parent [tier selection](../../SKILL.md) and does not select this framework.
Explicitly invoking this formal skill or requesting its full package, M01-M10,
FAST_LANE_V2 or formal harness workflow does select it, as does an applicable
project workflow requiring it. Once selected, all contracts below remain binding.

For new formal plans, first read
[Normalized authoring](references/normalized-authoring.md). Author the versioned
source and use [compile_topology.py](scripts/compile_topology.py) to produce the
expanded execution package. Source owners replace manually synchronized indexes;
the exact expanded contracts and all safety rules below remain binding. Legacy
Markdown packages remain supported; migrate conservatively before adopting source
ownership. This source/output distinction governs every later instruction to edit,
fill or own a package field: edit its source owner, regenerate the projection, and
never keep both independently authoritative.

Act as a deterministic plan compiler:

`goal/spec + repository/runtime truth + resource constraints -> customized execution plan`

Produce one modular execution-plan package and ensure the project has exactly one role-agent mapping
configuration. Use the fixed package grammar, composition root, global-rule file, independent-step
schema, M01-M10 module library, module-instance schema, task-card schema, and validation procedure below.
Select, omit, repeat, and connect modules according to the project;
do not impose a universal workflow chain. Do not execute the plan, launch agents, change product code,
create runtime state, or run product tests. Read, plan, write the plan and mapping when needed, and
validate those design artifacts only.

This compiler is design-only. Do not invoke it merely because a coding task is large or benefits from
ordinary planning; the requested deliverable must itself be a significant execution workflow or plan.

The sole planning-time exception to the agent-launch prohibition above is the
four independent read-only groups in [plan review](../plan-conformance-review.md),
including the [test-scope audit](../test-scope-audit.md). Read both references
even when this compiler is invoked directly. After drafting all suites/matrices,
obtain all four approvals, resolve findings and accept the final evidence scope before
Pass 16 validation. This permits review of planning artifacts only; it does not
launch the authored workflow or execute product tests. Its three result tables extend
validation.md Section 16; preserve M01-M10, P01-P15, R/S rules, V01-V30 and all
existing STEP/fast-lane contracts. Establish functional adequacy before optimizing
cost; missing assertions, realistic boundary proof and required adverse/recovery
coverage require additions or stronger tests. Cost criticism cannot waive a binding requirement.

Read [Matrix execution](../matrix-execution.md) for every substantial post-step
matrix, including normal and both repair-entry selections. Bind its concurrent
isolated execution, coordinate terminal exits, complete collection, dependency
graph, cause-group repair, affected reruns and reviewed wall-clock budgets in the
existing module/card fields. Assign its rejection criteria to EXECUTION_RESOURCES
and affected functional evidence to VERIFICATION. Its template is an authoring aid, not a new package schema or scheduler.

Read [Matrix execution](../matrix-execution.md) for every substantial post-step
matrix, including normal and both repair-entry selections. It owns scheduling and
review criteria; map its concrete binding template into existing module/card fields
and the EXECUTION_RESOURCES review. The template adds no package schema or runtime scheduler.

All four distinct reviewer agents must apply their assigned portions of
[Adversarial plan review](../plan-conformance-review.md), including on direct
compiler invocation. Freeze the requested outcome before decomposition; challenge
stage traceability, skill conformance, topology/simplicity, costs and authority
before accepting the expanded Section 16 audit record. Planning acceptance never
makes a live operation authorized. Include the reference's executor handoff in
existing scope/authority and external-operation fields; add no package artifact.

Before selecting evidence and expanding matrices, apply
[Acceptance design](../acceptance-design.md) and instantiate the
[review assignment](../../assets/plan-review-assignment.md) for each group. The
compiler must carry necessity, multiplicity and proportionality from proof design
through external-profile selection, cost simplification and final review. Record
the three explicit per-STEP audit assessments in Section 16, covering NORMAL and
both repair-entry paths. This adds no STEP/card field, module, package artifact or
universal testing architecture; structural validity never overrides a review BLOCK.

## Inputs

Require:

- product goal/spec and acceptance criteria;
- reference plan, if one exists;
- project path, runtime/orchestrator path, and operative documentation;
- available slots, workflow roles, and concrete launch choices for the single role-agent mapping;
- the existing canonical role-agent mapping path, or authority to create one beside the plan;
- separate authoring-source and generated execution-package directories;
- costly, scarce, destructive, or external resources.

If required inputs are absent, ask one consolidated question. Treat a reference plan as an outcome inventory, not a mandatory decomposition.

Once this formal compiler is selected, every fixed package, policy, step, module, card, coverage, and
validation requirement below remains binding. Missing facts, difficult composition, or validator
failures may produce a named unresolved input or an incomplete package; they never authorize a switch
to a compact topology, a dummy value, a reasoned-away required row, or a weaker local substitute.

### Hard requirements versus optional decisions

Hard requirements have no waiver mechanism. `N/A`, eligibility/ineligibility, free-form reasoning,
omission, deferral, dormant status, cost arguments, missing facts, and validator difficulty cannot
remove or weaken them. Hard requirements include the exact package files and fixed schemas; P01-P15;
requirement/deliverable coverage; one concrete gate per STEP; all three STEP entries with complete,
disjoint MI paths; both FAST_LANE_V2 contracts; selected-instance/card contracts; M05 selection; the
canonical mapping boundary; reciprocal lane and terminal-handoff rows for every member dispatch;
V01-V30; and final semantic plus deterministic validation.

Only explicitly identified choices are optional: selecting M01-M04 or M06-M10, selecting their
optional internal profiles, populating the allowlisted optional manifest categories, and choosing the
R3/R6 lane-sub-orchestrator topology. Decide these choices from project facts. A free-form omission
justification may explain only that optional decision and has no authority over any hard requirement.

A bare synonym is still a waiver. In any selected executable instance, governing/member card, STEP
entry/composition, gate, or mandatory policy field, `none`, `disabled`, `skipped`, `omitted`,
`ineligible`, `unavailable`, `not needed`, `not required`, and `no action` are invalid substitutes for
the concrete contract. Describe a legitimate absence concretely, including its controlling fact and
route, or make the owning explicitly optional decision; never hollow out a selected executable field.

Read current authoritative files first. Read history only to resolve a named ambiguity. Inspect the live runtime/orchestrator before assigning it a capability; a harness is optional, never assumed.

## Read the packaged compiler resources

For repair, fragile-control, repeated-command or recovery workflows, also apply
[execution efficiency](../execution-efficiency.md). Its ownership table extends
the existing compiler passes and M03/M05/M08/M09 obligations without changing the
package schema, module count, worker-continuity contract or authority boundaries.

Read these files completely before drafting. They are parts of this compiler, not examples to copy selectively:

1. [references/artifact-architecture.md](references/artifact-architecture.md) - the exact ownership,
   dependency, encapsulation, and change-propagation boundaries of the emitted plan package.
2. [references/project-truth-audit.md](references/project-truth-audit.md) - how to turn live project,
   repository, runtime, verification, and resource facts into a bounded source packet.
3. [references/execution-plan-template.md](references/execution-plan-template.md) - the exact output
   package skeletons, table schemas, policy blocks, step/module/instance shapes, and structural
   check definitions.
4. [references/compiler-pass-recipes.md](references/compiler-pass-recipes.md) - the exact local
   inputs, ordered actions, decision table, emitted rows, and completion test for Passes 1-16.
5. [references/module-recipes.md](references/module-recipes.md) - the exact local input, action,
   decision, output, correction, and completion contract for each selectable macro-module.
6. [references/incremental-verification.md](references/incremental-verification.md) - the required
   checkpointed-gate, pass-reuse, scoped-product-fast-lane, and batch-repair rules. Its event predicates
   decide runtime routing only; both FAST_LANE_V2 paths remain required plan content in every STEP.
7. The current project's authoritative sources identified by the truth audit. Live project facts
   override defaults or assumptions, but they never change this skill's grammar or global rules.

The source compiler provides projection freshness, ownership and impact checks;
it never manufactures semantic review, runtime evidence or authority. Its build/check
path uses this workspace's existing strict validator, preserving the Generic/Multi
orchestration distinction. A direct legacy-validator PASS alone cannot certify that
generated output still matches its source.

Use [scripts/validate_execution_plan.py](scripts/validate_execution_plan.py) only after semantic
composition and manual validation. The script proves document shape and decidable cross-references;
it cannot prove that a risk is realistic, a module is worth its cost, or an acceptance oracle is sound.

Also read [Worker continuity and recovery](../worker-continuity-and-recovery.md), including when
this compiler is invoked directly. Compile its two same-thread correction attempts after an initial
missing/malformed result into P02/P09: the second must not depend on first-attempt progress. Retain
the reference's continuity exceptions, progress/stall detection and fresh-lane handoff. Validate its semantic cases before
declaring the plan ready; table-shape validation alone cannot establish correct recovery routing.
When recurring failures justify it, also compile the reference's scoped configuration repair,
disposable tool-action proof, native result emission/preflight, and changed-assignment requirement
into P02/P09 and the exact owning prerequisite. Do not treat authentication as permission proof or
make fresh workers rediscover a known failed assignment.

## Compiler contract

### Bind shipped execution mechanics without expanding the package

Read [Shipped execution blocks](../execution-blocks.md) when this compiler is used directly or through
the parent skill. R3, R14-R22 and S7-S12 already require proportional infrastructure, bounded review
surfaces, retained check credit, rehearsal, and critical-path pricing. Use the packaged mechanics to
make those controls concrete; do not create parallel policies or another M-module library.

During Passes 4/6, classify prerequisites checkable before dispatch versus live facts, and map each
gap to its exact consumer. Bind effective storage roots and child inheritance, not merely the name of
a temporary directory. During Passes 7/9, select an existing host tool or a packaged block plus a thin
adapter before commissioning a new runner. Schedule an early fresh-state-to-protected-use proof for
coupled lifecycle seams. M08 rehearsals exercise the actual public transport/serialization with a
deterministic backend; canned caller-shaped responses alone are insufficient proof of that transport.

Use existing M01 prerequisite results, M03 verification assets, M08 readiness, M09 attempt lifecycle,
M04/M07 scoped checking, and M05 semantic decisions. Bind helper commands and adapter gaps inside the
existing Inputs, Outputs, Isolation and lifecycle, Critical-path effect, and Local instructions fields.
Any profile is an ordinary referenced tool input, not a new mandatory package artifact. Shipped helpers
are TARGET_TOOL_INVOKED mechanics; they are not runtime enforcement or a replacement supervisor.

During Passes 11/15, distinguish a changed fixture/parser from changed product authority, batch
compatible findings, preserve unrelated credit, and keep review at declared boundaries. Include actual
elapsed observations in existing results when reassessment consumes them; do not add a timing database
or total overlapping worker durations as wall clock. R30 remains the sole finite-command deadline
policy. Reuse verified immutable artifacts, recheck live authority/state, and retire terminal lanes.

This binding adds no schema, module, rule ID, or waiver. Keep M01-M10, P01-P15, V01-V30, all three STEP
entries, and FAST_LANE_V2 contracts intact. Existing structural validation remains required for formal
outputs; profile validation and executable helper tests prove only the new mechanical contracts.

Every emitted plan uses the exact directory layout and per-artifact grammar defined by
`artifact-architecture.md` and `execution-plan-template.md`. `plan-workflow.md` is the sole composition
root; `global-rules.md` owns global policies; every `STEP-*` has one independent file with the exact
canonical FAST_LANE_V2 usage block followed by the `NORMAL`, `FAST_LANE_V2_SERIES_1`, and
`FAST_LANE_V2_SERIES_2` entry contract; `modules/M01.md`
through `modules/M10.md` own all M-module rules, flows, configured `MI-*` occurrences, and task cards;
`validation.md` owns rule/check results; and the canonical JSON mapping alone owns concrete
role-to-agent selection. Every selected workflow component is an instance of one catalog module and
uses the exact module-instance field order.
Project-specific judgment changes module selection, count, connections, contents, and parameters; it
does not change the package grammar or silently invent a new module shape.

Use reference-based composition as an invariant:

- define each global policy once and cite its `P*`/`EXC-*` ID from steps and modules;
- define each M01-M10 module's public interface, rules, process, and allowed variations once in its
  `modules/Mxx.md` file;
- make each step define three project-specific ordered entry paths using disjoint MI references with
  the exclusive `MI-NORMAL-*`, `MI-FL2-S1-*`, and `MI-FL2-S2-*` prefixes, while keeping every MI's
  rules in its owning M file;
- keep exactly one complete 20-field governing task card in each selected module instance and one
  complete 20-field member task card for each internal worker dispatch, all inside the owning M file;
- keep concrete provider/model/effort/tier selection only in the mapping and use role keys everywhere
  else; and
- change dependent artifacts only when a public input/output contract, semantic meaning, authority,
  or graph edge changes. An internal implementation edit with a stable interface stays local to its
  authoritative component; rerun validation without rewriting unaffected dependents.

The catalog is composable, not a predetermined state machine:

- start from coverage, dependencies, risk, runtime truth, and the smallest useful topology;
- select an optional module whenever project facts show it adds useful behavior; treat catalog scenarios
  as strong, non-exhaustive recommendations rather than exhaustive eligibility conditions;
- omit an optional module only after deciding it adds no useful behavior, recording a free-form
  justification in that M file's selection table;
- connect selected modules only where one module's declared output satisfies another's declared input;
- repeat a repeatable module only for a named independent deliverable, checking tranche, or affected
  repair tranche;
- derive execution order from those connections; never copy a canned chain merely because the
  catalog lists modules in an order;
- preserve local invariants inside selected modules. If independent review and deterministic checks
  are both selected for one frozen tip, schedule them concurrently. If a repair module is selected,
  pool and deduplicate all findings assigned to that tranche before repair;
- compile every expensive multi-check gate into resumable, independently runnable check units when
  the actual runner supports it or a small justified prerequisite can provide it. Continue ordinary
  checks after ordinary failures, reuse only conservatively unaffected PASS credit, and return one
  complete finding pool rather than stopping at the first failure;
- do not add a smoke, review, repair, full safeguard, external rehearsal, worktree, or cleanup module
  unless the project's behavior, risk, and verification needs justify it;
- make forward progress the default: activate every successor whose consumed product inputs are satisfied. A support, administrative, readiness, or cleanup fault may hold only the exact claim, resource, or operation that consumes the failed fact; it must not hold an independently decidable product result or an unrelated successor;
- never omit coverage, ownership, semantic acceptance, or a necessary verification merely to simplify the
  graph.
- always select `M05` in a formal package: the required deliverable/requirement acceptance and concrete
  STEP product gate necessarily require its decision, disposition, and rework-boundary recipe.

### Directive hierarchy

The emitted plan must declare and enforce this project-document hierarchy:

1. Current direct user instructions and the authoritative product goal/spec define the required
   outcome and authority boundary.
2. The sole operative `plan-workflow.md` defines package composition, project coverage, and the typed
   graph between independent `STEP-*` boundaries.
3. `global-rules.md` defines cross-cutting workflow behavior exactly once.
4. A `STEP-*` file defines one independently gated project building block with three distinct entry
   compositions: `NORMAL`, `FAST_LANE_V2_SERIES_1`, and `FAST_LANE_V2_SERIES_2`. It may rely only on
   the configured `MI-*` ingredients' declared public interfaces.
5. Each `modules/Mxx.md` file owns that M01-M10 ingredient's rules, process, stable interface, allowed
   variations, and configured instances.
6. One governing task card binds each selected `MI-*`; each member task card binds one internal
   worker dispatch inside that MI. Either may narrow only its authorized scope, add project-specific
   inputs, or cite a declared exception, but may not change global scheduling,
   review cadence, gate scope, authority, resource, or result-handling rules.
7. A handoff/status document records current state and the next already-authorized transition; it
   does not define or override workflow.
8. Runtime artifacts record only facts that a consumer actually needs, such as a process, subagent,
   handoff, claim, or worktree ID. They are not a second configuration or policy source.
9. The role-agent mapping controls only concrete launch selection for roles. It never controls task
   semantics or workflow order.

If a lower layer conflicts with a higher layer, the plan is invalid. A local instruction may use an
exception only when the plan already defines the exception class, trigger, owner, allowed alternate
action, required confirmation, optional result/record location, and scope/expiry. Classifying a newly observed fault through the plan's ordinary material, test-only, administrative/support, readiness, or live-harm policy is not an exception. Only a genuinely new graph, authority, acceptance, or scope route requires an explicit plan amendment or an `INCOMPLETE` decision; it is never improvised inside a task card.

## Rules

Every directive below is normative. Cite its ID wherever the emitted plan applies it.

### Product and complexity

**R1 — Preserve scope.** Implement every required outcome; do not weaken, reinterpret, or add product scope. Surface contradictions.

**R2 — Separate coverage from execution.** Give requirements, outcomes, deliverables, checks, and other plan content plan-local labels only when cross-references need them. A label is document navigation, not a runtime identity, persistent record, or evidence obligation. An ordinary feature such as a website button does not need its own ID or hash merely because it appears in the plan. Never create a lane merely because an item, file, or module exists.

**R3 — Make complexity earn its cost.** Start with `orchestrator -> one worker -> one check -> orchestrator`. Add a worker, fan-out, gate, artifact, lock, rehearsal, loop, or optional lane sub-orchestrator only for a named realistic failure, safety need, or net wall-time gain. A two-orchestrator-tier shape, `ROOT -> lane sub-orchestrator -> lane workers`, is justified only when a bounded lane has enough internal sequencing, local finding triage, or coordination to repay the additional handoff and ROOT still has a clear terminal lane result to decide. State the payoff. Omit it when rereading, coordination, merge, verification, and maintenance cost plausibly outweigh the benefit.

**R4 — Optimize for deployed behavior.** Admit realistic correctness, reliability, recovery, safety, security, required record-integrity, and required-usability defects. Drop cosmetic, invisible, unreachable, speculative, duplicate-guard, and net-negative-complexity work to an out-of-scope ledger. Admission is limited to defects that affect the governing requirements or invalidate their acceptance evidence under R25; a genuine out-of-scope gap does not create a new requirement.

**R5 — Report truth.** Never invent a result, infer success from missing information, or call uncertainty failure or success. Record `INCOMPLETE` or `INDETERMINATE` when the available checks or observations cannot decide.

### Roles, context, and compute

**R6 — Keep one global decision owner.** The persistent ROOT/orchestrator alone accepts global work, blocks cross-lane progress, changes the plan or scope, triages cross-lane findings, authorizes integration or real attempts, and releases shared resources. By default, ROOT authors every worker contract and dispatches every worker directly. When R3's payoff is explicit, ROOT may instead authorize a direct lane sub-orchestrator for one bounded lane. The plan must name that lane's outcome, inputs, protected scope, mutable resources, workers, local decisions, terminal handoff, and return conditions. Within those declared bounds, the lane sub-orchestrator concretely authors and dispatches its worker cards, directs its workers, triages lane-local findings, and makes only the local acceptance or correction decisions the plan assigns. It must return any changed requirement, cross-lane dependency, shared-resource issue, integration choice, real attempt, or global acceptance question to ROOT. ROOT accepts the terminal lane result. A lane sub-orchestrator may not create another orchestration tier. Every other worker returns facts, results, or recommendations and never self-dispatches.

**R7 — Keep product writing singular.** Use one serial production writer per coherent deliverable. Do not concurrently mutate one project tip. Split writers only across proven-independent deliverables with explicit ownership, merge order, and payoff.

**R8 — Default every pool to one.** Fan out only over disjoint conceptual surfaces that can run concurrently and whose time or isolation benefit exceeds startup and merge cost. Respect the available-slot cap. Every fan-out rejoins one owning-orchestrator decision: a lane-local join returns to its authorized lane sub-orchestrator, and every terminal lane join returns to ROOT.

**R9 — Resolve roles through one adjustable mapping.** Use deterministic scripts for mechanical
checks, focused economical agents for routine review/test work, and strongest reasoning only for
planning, hard defects, risk judgments, and final acceptance. Give every executable workflow role
exactly one entry in the project's sole role-agent mapping. Concrete provider/model, reasoning effort,
service tier, and other provider launch-selection values live only in that mapping. Workflow plans,
role tables, task cards, lane manifests, prompts, examples, and launcher call sites refer only to the
role. Honor user/repository Fast or priority policy through the mapping without silent substitution.

The role/agent boundary is normative:

1. Reuse the project's canonical versioned mapping when one exists. Otherwise create exactly one
   versioned JSON mapping beside the plan, named `SUBAGENT_ROLE_MODEL_MAPPING.json` unless the project
   declares another canonical location. Never create per-stage or per-lane copies.
2. Mention the canonical mapping path exactly once in Section 0's Agent mapping dependency row.
   Every later dependency says only the workflow role. Do not repeat the path in role tables, lane
   graphs, task cards, examples, or prose.
3. Put no concrete model name or concrete provider launch selection in the plan or any other generated
   design document. The mapping is the sole editable allocation source; changing one role entry must
   require no workflow-document or launcher-code edit.
4. A task card and launcher receive a role, not copied model settings. The runtime resolves that role
   from the current mapping at the actual launch boundary. If a compatibility projection was created
   earlier, dispatch refreshes its provider selection from the current role entry rather than treating
   earlier materialized values as configuration. An unknown role is rejected.
5. A provider invocation may necessarily contain the resolved concrete values sent to the provider.
   Treat that as a runtime fact, not a second configuration source. Retain a launch record only when
   resume, debugging, audit, or another named consumer requires it.
6. When the runtime has no role resolver, make that resolver an explicit prerequisite deliverable
   before any agent launch. Never work around the gap by copying concrete values into each launch
   command.
7. Do not make a particular provider invocation, model, or persistent worker a workflow
   prerequisite. Within an unaccepted logical task, reuse an active invocation only when it is
   available and the current mapping and user direction still select it. If the user changes a
   subagent/provider/allocation, the invocation cannot resume, or the runtime cannot retain it,
   dispatch a new invocation for the same workflow role with the same concrete task card, accepted state,
   complete finding/result pool, working source, and first unresolved action. Record the old and
   new invocation IDs and the handoff ID because those runtime objects require correlation. The mapping
   change or lost persistence alone neither invalidates product credit nor requires a product loop.

Use the runtime's accepted mapping schema when it has one. If it has none, use a strict versioned JSON
object with a `roles` object keyed by workflow role; each entry contains the provider launch-selection
fields required by that runtime. Keep workflow behavior, permissions, ownership, and task semantics in
the plan under the role rather than mixing them into provider-specific branches.

**R10 — Send bounded context and preserve logical-task continuity.** Give each focused worker one task card containing: objective, why now, current state, accepted prior results, dependencies, in/out scope, required behavior, exact inputs, its preassigned invocation/session, handoff, lane, claim/lock, and Git-worktree IDs, the required launch-time process/process-tree ID record, allowed actions, acceptance criteria, outputs, failure route, and the fewest useful initial entrypoints. Before dispatch, put the fewest high-value failure cases directly into that card when a realistic trigger could otherwise cause a later serial repair. Each case names its requirement, trigger, invariant, focused oracle, and owner; generic checklists and speculative hardening do not qualify. Tell the worker not to reconstruct history or read other files unless the card is insufficient. Broad whole-product review may receive the governing set. Within one unaccepted logical task, keep the same functional role, bounded card, accepted state, and first unresolved action. Every completed worker card publishes a terminal handoff before its owning orchestration authority makes an acceptance, classification, correction, or integration decision; one running invocation must never cross that decision boundary. The owner is ROOT in the direct topology and the explicitly authorized lane sub-orchestrator only for its declared local lane boundary. A later explicitly dispatched card may request available provider continuity for the same role, but persistence is never required. If the user changes the subagent/provider/allocation, continuity is unavailable, or it cannot resume, dispatch the same workflow role through the structured handoff in R9; do not restart completed work or silently change task meaning. Apply R21's runtime-instance ID rule without extending it to ordinary features, files, sources, caches, facts, checks, or outputs. Once semantically accepted, the logical task is terminal; unrelated later work starts from a new bounded card.

### Dispatch-authority contract

R6 and R10 make task definition a non-delegable orchestration responsibility. In the default topology,
ROOT converts accepted plan state into every complete executable worker contract. In the optional
two-orchestrator-tier topology, ROOT first converts the lane boundary into a complete sub-orchestrator contract;
that authorized lane sub-orchestrator then converts accepted lane state into complete contracts for
every worker it directs. Across the 20 task-card fields, each worker contract must state all information
material to correct execution:

- the concrete problem or activation fact and why this work is the next authorized action;
- the exact objective, desired result, and observable behaviors or claims the work must produce or
  prove;
- the required changes or operations, specific target surfaces and initial entrypoints, conceptual
  in-scope and out-of-scope boundaries, exact write authority, and protected behavior that must not
  change;
- authoritative inputs, predecessor outputs, accepted prior results, current source/runtime state,
  dependencies, resource/lock constraints, and required commands or checks;
- acceptance criteria, authorized tolerances, deliverables, result and handoff consumers, failure
  classifications, stop/escalation conditions, and the first unresolved action; and
- realistic task-specific pitfalls and expensive-late failure cases worth watching, each tied to a
  requirement, trigger, invariant, and oracle, plus explicit forbidden actions and non-goals.

The owning orchestration authority may delegate implementation mechanics and local code choices inside
those bounds; it must not delegate discovery of the task's meaning, success condition, permitted scope,
or acceptance boundary to a worker. A worker executes and reports against the supplied contract. It
must not redefine the problem, invent hidden requirements, widen scope, weaken or replace the requested
oracle, choose a new workflow edge, or self-dispatch follow-up work. If a material instruction is
missing, contradictory, or cannot be reconciled from the named authoritative inputs, the worker returns
the exact missing/contradictory fact to its owning authority and stops at the safe boundary. A lane
sub-orchestrator returns anything outside its declared boundary to ROOT; neither it nor a worker fills
the gap by reconstructing project history or making an unauthorized product/workflow decision.

The R10 phrase `unless the card is insufficient` permits only the minimum read needed to identify and
report the insufficiency or to follow an already-stated implementation dependency. It never permits a
worker to recover unstated goals, choose the behavior to prove, infer what may change, invent an
acceptance oracle, or broaden the task. Implementation discovery is allowed only inside the owning
authority's concrete semantic and scope boundary: a worker may inspect how the named behavior is
implemented and choose how to realize it, but ROOT (or its explicitly authorized lane sub-orchestrator
within the declared lane) must already have decided what result is required, which surfaces may and may
not change, and what evidence will count. If those facts are absent, the only authorized output is the
bounded insufficiency report and terminal handoff.

Interpret every worker-facing action verb in this skill under the same authority rule. `Define`,
`select`, `choose`, `classify`, `resolve`, `decide`, `authorize`, `continue`, `resume`, `start`, and
similar verbs give a worker no semantic discretion unless this skill explicitly assigns that exact
decision to the worker. In an executable worker card, those verbs mean materialize, compare, or carry
out the owning authority's predeclared target, criteria, branch, or mechanical procedure. An unexpected
choice, nontrivial conflict, new attempt, new repair objective, altered test meaning, or new workflow
edge returns to the owning authority and, if it crosses a lane boundary, to ROOT. Review/audit finding
discovery is the sole broader epistemic exception: it permits
independent conclusions inside the assigned investigation boundary, not independent task definition,
scope expansion, editing, acceptance, routing, or follow-up authorization.

Review and audit cards are intentionally open only as to findings. The owning orchestration authority
must not prescribe the reviewer's conclusion or predeclare the defects it is supposed to discover. It
must still name the frozen input, review class, exact product/conceptual surface, governing requirements
and invariants, risk hypotheses or pitfalls to examine, exclusions and protected boundaries,
severity/materiality threshold, required output shape, completion condition, and handoff owner. A reviewer may inspect the
minimum adjacent code needed to understand behavior or substantiate a finding and must state why that
expansion was necessary. It may discover and report new problems within the assigned boundary, and
may recommend a separately authorized scope expansion; it may not silently expand the audit, edit the
product, or convert the authority's watch areas into a required finding. A whole-product audit is valid
only when ROOT explicitly assigns that breadth and supplies the governing set.

**R11 — Price context.** Apply the runtime- or harness-provided entrypoint-count score when available. Record count, score, allowed range, and a concrete justification for every non-maximal score. If no scorer exists, record the count and justification in the plan; do not invent enforcement.

**R12 — Accept semantically.** A shape-valid result enters `ACCEPTANCE_PENDING`; it does not unlock dependents. Never call a malformed artifact valid. The owning orchestration authority decides the required product criteria from the task result, requested checks, and relevant observations. An authorized lane sub-orchestrator may issue only the lane-local verdicts and correction routes assigned under R6; ROOT decides every terminal lane, cross-lane, integration, release, and global product verdict. The decision owner must issue exactly one verdict: `ACCEPTED`, `ACCEPT-WITHIN-TOLERANCE` only for an explicitly predeclared non-required tolerance with product rationale, `CONTINUE` with exact missing product work, or `INCOMPLETE`. No tolerance may waive a required criterion. `CONTINUE` is eligible only when a required product criterion failed or remains genuinely undecidable. When required product criteria are decided and satisfied, an administrative/support fault is recorded under R18 and the decision must advance; do not create or perfect paperwork, hashes, receipts, or evidence artifacts merely to support the verdict.

**R13 — Prevent and recover malformed reports cheaply.** Add a deterministic read-only report preflight only when repeated structural handoff faults justify its cost and the inspected harness or target project actually provides it. The preflight may decide only parse/schema, declared paths, required fields, clean-tip, diff, and explicitly required outputs; it cannot decide product behavior or semantic acceptance. A producer corrects `REPORT_ONLY_ERROR` while its turn is active without changing code or rerunning product checks unless the missing product fact genuinely requires it. The owning orchestration authority records an administrative error and advances whenever the product criteria remain decidable; a lane sub-orchestrator returns any effect outside its lane to ROOT. Re-enter the same logical role/task only when an exact required fact is missing or ambiguous. Do not add revisions, hashes, immutable records, or separate evidence artifacts merely to make a report preflight possible.

Under R9/R10/R13, a missing or malformed required terminal report should first receive a narrow
correction card in the same resumable thread, with verified runtime identities and retained work.
An incomplete report does not need a fabricated terminal handoff before that correction can be
dispatched: the owning authority uses the observed failure and available state. Apply the shared
worker-continuity reference's bounded attempts, stall criteria and fresh/split recovery route.
R13's administrative continuation never labels an invalid launch successful or bypasses an exact
consumer's required result. Report-only recovery does not activate a product repair loop or repeat
unaffected review/testing, and does not independently qualify a model/provider fallback.

### Review, testing, and repair

**R14 — Complete and pool before repair.** Each reviewer, test selection, observer, and deterministic
gate finishes its assigned runnable surface, except under R23 or a named failed prerequisite. A gate
records an ordinary failure, continues every remaining independent unit, and records each dependency
skip truthfully. Merge and deduplicate the complete result set once; the owning orchestration authority
triages once; the writer repairs every compatible admitted finding once as a batch. A lane
sub-orchestrator may pool only its declared lane; ROOT pools any cross-lane or terminal results. Do
not stop on the first ordinary finding or reopen review after every edit. Apply the concrete checkpoint
and batch rules in `references/incremental-verification.md`.

**R15 — Classify every follow-up.** Route it as `production/material`, `strict test-only`, or `administrative/support`. For every test or scaffolding error, the owning orchestration authority decides `PRODUCT_INVALIDATING`, `NONBLOCKING_TEST_ERROR`, or `INDETERMINATE`. A lane sub-orchestrator may classify only its declared local route; a changed requirement, cross-lane consequence, shared resource, or global product effect returns to ROOT. A product repair requires a failure tied to product behavior, contract, oracle, or coverage—not merely a broken support process. A test or scaffolding error never blocks a product result when other required checks or observations still decide the behavior. After classification, activate every successor that does not consume the affected claim, capability, resource, or operation.

**R16 — Use one material route.** Compose the material route only from selected modules. When independent review and deterministic focused checks both consume the same input, launch them concurrently with disjoint result/cache roots and no shared result writer; split either path further only when its slices are independently useful. Join each selected result tranche once, batch its accepted findings once, and repeat only affected work. A selected follow-up reviewer covers the repair surface and previously violated invariants; reopen the whole surface only when a changed input affects earlier review. Do not review intermediate repair revisions. A smoke or full safeguard participates only when its module is selected.

**R17 — Use the strict test-only fast lane.** The owning orchestration authority may admit a semantic-preserving test repair when an accepted product requirement shows that the repaired test still checks the same scenario and behavior with equal or stronger rigor. It may correct fixture, mock, setup, runner, metadata, test-code, expected-literal, or test-selection mistakes. It may not change production code, policy, contract, locked configuration, covered scenario, oracle, assertion strength, expected behavior, or coverage obligation. Continue the same logical worker role only through a terminal handoff and a newly dispatched correction card after the owning authority classifies the prior result; the completed test/check run cannot automatically continue or start integration. A lane sub-orchestrator may use this route only for its declared lane. The later card may request available provider continuity, otherwise use the R9 handoff. Rerun exactly the affected test selection once when the current gate needs it and preserve every unrelated pass. A semantic change, indeterminate impact, or failed repeat returns to R15 classification; material repair requires a failed or genuinely undecidable required product criterion.

`FAST_LANE_V2` is a separate, mandatory two-series scoped-product route configured explicitly in every
`STEP-*`. Series 1 is the outbound-patch path: it activates inside an affected original step after R14
returns a complete feasible pool with one compatible scoped correction objective. It uses a distinct, materially narrower
`MI-FL2-S1-*` path
for the local repair, changed-source compile plus deterministic motivating-test smoke, independent
frozen-tip review, separate integration, and repaired public-output exit to the ROOT-selected later
current progress-bound step. Series 2 is the inbound-reconcile path: it activates only when a step is
that current progress bound. It
uses a different distinct `MI-FL2-S2-*` path to receive and join every accepted Series 1 exit, calculate the
changed-input/invalidation map, preserve unaffected PASS credit, execute only failed, unresolved,
change-affected, uncertain, or uncredited units from the earliest required unit, and continue the
normal successors. The normal entry uses only `MI-NORMAL-*` instances and may use any justified
module composition; neither fast entry may
invoke, duplicate, or rename its heavy normal broad campaign or full restart. The exact MI count and
M01-M10 combination remain project-specific, but each fast path must state the concrete work it saves.
Every step must configure both fast paths with their required disjoint MI paths; neither path may be
disabled, omitted, or replaced by the normal route. Activation remains conditional: uncertain impact,
changed test/runner/configuration selection, external/hardware state, an absent motivating test, broad
shared/public or security/lifecycle behavior, or a pool requiring a broader repair batch does not
satisfy the fast-lane trigger and follows R15's normal material classification for that event. Every
series requires a terminal handoff and newly dispatched card; a failed or indeterminate fast-lane
result returns to R15 classification.

**R18 — Isolate administrative and support failures.** Correct a reconstructable path, schema, report, fixture, runner, watcher, executor-environment, supervision, or cleanup fault only when an exact consumer still needs the correction and it is cheaper than recording the limitation. An administrative fault must not block a product result whose required criteria remain decidable. Mark only the exact support-dependent claim or operation unavailable and activate all other satisfied successors. If the failed support step was the only required way to decide a product criterion, block only that criterion or record `INDETERMINATE`; never infer material product repair from the support failure alone.

**R19 — Preserve passing work with conservative checkpoints.** For every expensive multi-check gate,
define the smallest economical independent check units, their source/configuration/runner/environment
and external-state inputs, prerequisites, and dependents. Checkpoint each completed unit and continue
after ordinary failures. On a changed tip, select every failed, unresolved, change-affected, or
uncertain unit; execute that set in declared order beginning with its earliest member, and do not
replay an unaffected PASS. Reuse a PASS only when its declared inputs and prerequisites are unchanged.
The checkpoint still records the first unresolved unit; when no earlier unit was invalidated, that is
the resume point. Use a repository revision or external attempt state only when it is required to
decide reuse; do not blindly hash ordinary content. A full restart is valid only without usable
progress or when a global input reaches every selected unit. For hardware/practical work, reuse a pass
only after the consumed target/resource state is verified unchanged. Run an accumulated safeguard only
to the extent remaining or invalidated units require it; its initial cold pass remains a complete
release unit when risk warrants it. Apply `references/incremental-verification.md`.

Interpret declared order under
[Matrix execution](../matrix-execution.md#preserve-checkpoint-recovery-and-ownership-boundaries).

**R20 — Preflight only fragile expensive runners.** Before an expensive selection that depends on a
custom runner or child process, use one side-effect-free disposable fake to prove the inputs, arguments,
process ID/correlation, start, outputs, cleanup, exit, and—when incremental execution is
selected—its checkpoint write/read and check-unit resume boundary. Reuse the preflight while those
inputs remain unchanged. Ordinary runners need no preflight record.

### Locks, practical work, and stopping

**R21 — Identify runtime instances, not ordinary content.** Give every independently running or lifecycle-owned orchestration instance an ID: orchestrator/root processes and process trees, agent and subagent processes, provider invocations/sessions/threads, handoffs, lanes, claims/locks, and Git worktrees. Those IDs are mandatory because a multi-agent orchestrator must correlate, route, monitor, resume, stop, clean up, and retire the exact instance. Give another live resource an ID only when targeting or lifecycle control requires it. Plan-local labels such as `REQ-*`, `DEL-*`, and `CHECK-*` are optional cross-references, not runtime identities. Do not assign an ID, hash, receipt, immutable record, or evidence artifact to an ordinary feature, file, source, cache, configuration, fact, check, result, or workspace merely because it exists; a website button, for example, needs none of them by default. Require a repository revision only when an operation must target or preserve a particular repository state, a receipt only when an operation must later prove or reverse its changes, a hash only for a named byte-integrity or content-comparison decision, and immutability only for a record or history that must not change after acceptance. Rerun only direct consumers of changed inputs and continue every non-consuming edge.

**R22 — Rehearse costly external control flow.** Before scarce, irreversible, hardware, service, or other external allocation, run the exact project and control flow against disposable fakes. Check only the control properties the real attempt depends on. Reuse rehearsal while those inputs remain unchanged; never count it as a real-world pass. Name one owner for attempt state, abort/stop, observation, and cleanup. When no such resource exists, mark this optional rehearsal `OMITTED` with a free-form justification.

**R23 — Stop immediately only to contain live harm.** Immediate stop requires an observed unauthorized/wrong-resource action, loss of live-process containment or cleanup, or irreversible corruption of information needed for judgment. Preserve only what diagnosis or recovery needs, contain safely, then apply R18. Pool every other observation through R14.

**R24 — Admit and end loops on product results.** Enter a product repair loop only when R12 identifies
a failed or genuinely undecidable required product criterion and one coherent repair objective can
change that outcome. A non-product fault may receive a narrow same-task continuation only when an
exact downstream operation consumes the failed capability; it never becomes a product loop. Resume
with the earliest failed, unresolved, change-affected, or uncertain action/check and preserve every
completed action and passing unit whose inputs remain unchanged. Batch compatible findings before a
writer or new assurance pass. Do not impose arbitrary iteration caps. End on success, unrecoverable
error, or stall: repeated failure signature, no passed-set growth, pass/fail oscillation, or
scope-only churn.

### Design and runtime truth

**R25 — Review proportionately.** Trivial mechanical work may omit review with a reason. Any non-trivial design review assigns at least one existing reviewer—not an automatic extra worker—to correctness, simplicity, generalizability, organization, usability, and composability. Guard verified caller mistakes and real trust boundaries; do not add speculative abstraction, hostile-input defenses outside the threat model, arbitrary limits, double guards, or paternalistic blocks on intended correctly targeted work. Apply the [finding-admissibility rule](../acceptance-design.md#finding-admissibility-requirements-define-the-review-boundary): a real vulnerability/gap that does not prevent current requirement satisfaction or required test success is invalid as a blocking/correction finding. Require concrete requirement linkage; a green suite alone cannot waive a demonstrated required violation. Include this rule in every reviewer block.

**R26 — Plan only real runtime behavior.** Inspect current docs/source and distinguish runtime-enforced rules from orchestrator policy. Also distinguish the stable launcher/supervisor, the target project's own executable tooling, and document-only workflow requirements: a command available from an exact target revision may be invoked by the workflow without claiming that the stable launcher implements or automatically enforces it. Use the actual launch, wait, event, acknowledgement, isolation, result, and cleanup mechanisms available in the project; if a harness exists, inspect its real behavior rather than assuming it. State the command source, invocation owner, prerequisites, and every manual responsibility. Never name a fictional feature as automatic enforcement.

### Runtime footprint and concurrent results

**R27 — Allocate only necessary source isolation.** Give a lane a full linked worktree only when it may mutate source or its execution writes source-local state. Give each lane or Git worktree an ID because its owning orchestrator must own and retire the exact allocation. A lane sub-orchestrator may manage only allocations explicitly assigned to its lane; shared and cross-lane allocations remain with ROOT. A static read-only lane may use the current declared source plus a separate writable result root unless a particular revision is required. A test lane uses the cheapest mode that prevents source, cache, output, and peer contamination. Do not freeze or hash a source view without a concrete need.

**R28 — Retire terminal lanes.** After semantic acceptance, remove the lane from active discovery, close its identified clean Git worktree through verified Git operations, retain only results or revisions that a named consumer still needs, and discard disposable caches. Never delete needed results, an unretained required revision, a dirty worktree, or a path used by an identified live process. Archival failure leaves the lane terminal and visible for recovery; it never reopens accepted product work.

**R29 — Serialize required shared append-only records.** When concurrent processes must write one event log, use one cross-process lock keyed to that log. A writer waits, appends one complete record, flushes, and releases the lock. Require a concurrent-process regression test. Do not create the log in the first place unless a consumer needs it, and do not invent per-controller logs or a merge layer when one lock is sufficient.

**R30 — Bound only explicit finite command fragments.** The repository's declared bounded-command
manifest defines the literal fragments of finite scripts, tests, builds, servers, watchers, or other
commands that must use the existing bounded-execution architecture. Do not infer coverage from a
language, a launcher category, or whether a command sounds like a test. Agent and subagent sessions are
always outside that boundary, including native sessions, `codex exec`, `claude -p`, and repository
agent-launch wrappers; never list or wrap those sessions. A finite command run from inside an unbounded
agent session is covered only when it independently matches the declared manifest. During the runtime
audit, discover the applicable instruction and provider configuration chain, including `AGENTS.md`,
`.codex/`, `.claude/`, or another CLI/provider-specific directory; inspect hooks, supervisors, and
task-prompt composition, and reuse the existing mechanism rather than mandating one provider's filenames
or creating a parallel runner. For every covered finite command, require an exact command, working
directory, result path, heartbeat interval no greater than 60 seconds, realistically calibrated expected
upper-bound runtime, bounded cleanup allowance, computed maximum lifetime, and basis derived from a
protocol/resource constraint, accepted plan upper bound, or measured history with stated headroom.
Maximum lifetime must equal expected upper bound plus cleanup allowance. Cleanup is capped at the smaller
of 120 seconds or 25% of the upper bound, with a five-second minimum cap for short commands. The
supervisor must poll and flush heartbeats independently of the caller, preserve stdout/stderr, return the
command exit status, and at deadline terminate the exact process tree, verify cleanup, and emit a
terminal timeout result. A pre-execution command hook or equivalent provider guard must reject a direct
covered finite command that bypasses the supervisor where the inspected runtime supports interception;
it must exempt agent/session launches and must not grow an unrelated catalog of executable languages.
Every card or prompt that invokes a covered finite command must carry the policy reference and invocation
contract, even when its nested worktree does not inherit the outer instruction files. The owning
orchestration authority must classify timeout as administrative/support pending product-impact
information, preserve unaffected green credit, and never treat timeout alone as product pass or failure.
If a selected manifest entry has no bounded architecture or guard, represent its smallest
provider-appropriate implementation as an M01 prerequisite and mark only that command unavailable until
it is accepted.

## Structural rules for emitted plans

These rules close the gap between a correct rule list and an executable plan structure. They apply to every plan produced by this skill.

**S1 - Use a fixed modular envelope and composable internals.** Emit the exact package layout from
`artifact-architecture.md`. Keep the composition-root sections in their exact order, put P01-P15 only
in `global-rules.md`, put each independent gated `STEP-*` only in `steps/<STEP-ID>.md`, put every
M01-M10 rule/process and its configured `MI-*` occurrences only in the matching `modules/Mxx.md`, and
put the rule/check matrices only in `validation.md`. Never create a different package layout for a
different project.

**S2 - Make selection explicit.** Each of `modules/M01.md` through `modules/M10.md` records exactly one
catalog decision: `SELECTED` or `OMITTED`. `SELECTED` names all instance IDs. `OMITTED` gives a
concrete free-form justification for this genuinely optional module. There is no `DEFERRED` state:
resolve missing facts before compiling the final package, then decide. The
composition root indexes all ten files and every selected step. Do not silently omit a familiar module
or gated step.

**S3 - Compose from typed dependencies.** Every selected module instance declares exact predecessor
outputs and successor inputs inside its owning step; every step declares a stable public input/output
boundary; and the whole-plan graph is the transitive composition of the step edges and their internal
module connections. Catalog, step-file, and module-file order have no execution meaning. Whenever an
output satisfies a successor input, that edge is default-forward and activates without waiting for
unrelated administrative/support cleanup; an exception must identify the exact consumed missing fact.

**S4 - Define every shared concern once.** Scheduling, review cadence, gate scope, prior-result reuse,
logical-task and invocation continuity, role resolution, resources, exceptions, and acceptance live
only in `global-rules.md`. Each M01-M10 ingredient's project-specific flow lives only in its
`modules/Mxx.md`; step files compose `MI-*` interfaces and never copy module flow; modules and steps
cite policy IDs and do not copy or reinterpret the prose. Concrete role-to-agent selection lives only
in the canonical mapping.

**S5 - Use mandatory language for mandatory behavior.** Write `must`, `must not`, `only when`, and `exactly when` for obligations. Use `may` only for a genuinely optional choice whose decision owner, allowed choices, and confirmation/output handling are named. Ban `as needed`, `appropriate`, `standard`, `best practice`, `if useful`, and equivalent phrases in executable instructions.

**S6 - Bound local authority.** A step file may select, parameterize, and connect declared `MI-*`
interfaces. An M module instance or its governing/member task cards may customize its objective, scope, inputs,
entrypoints, failure cases, checks, outputs, and declared exception references only within the owning
M file's allowed variation contract. Neither may copy or change a global invariant, redefine another
M module, or invent an undeclared inter-step edge. Needed new macro behavior must use a catalog module
or an explicitly defined M10 project extension with the same schema.

ROOT must fully author those customizable values before direct-worker dispatch. In the optional
two-orchestrator-tier topology, ROOT authors the lane sub-orchestrator's bounded authority and that sub-orchestrator
fully authors its workers' values before dispatch. A worker's freedom to choose implementation
mechanics within the card is not authority to discover or redefine the task's problem, goals, target
behavior, protected surfaces, success criteria, or next graph edge.

**S7 - Define review cadence, not just review presence.** Every selected review instance declares one class: `INITIAL_IMPLEMENTATION`, `AFFECTED_REPAIR`, `MACRO_INTEGRATION`, `FINAL_PRODUCT`, or a project-defined class with a precise boundary. State what creates the reviewable frozen tip and what invalidates prior review credit. Do not treat each internal edit or commit as a review boundary.

Every review card also carries the bounded open-investigation contract from R10: the owning
orchestration authority fixes the input, surface, governing requirements/invariants, watch areas,
exclusions, materiality threshold, output, and handoff, while leaving the existence and content of
findings for the reviewer to determine.

**S8 - Parallelize selected independent checking paths.** Within M04 or M07, when selected review and deterministic-check paths consume the same input, put them in one parallel group, launch both before awaiting either, give them disjoint writable roots, and join them once. A serial edge is valid only when one consumes the other's output or a declared serial exception applies. Do not create a timing ledger merely to justify the parallel group.

**S9 - Pool selected repair work.** M05 triages and deduplicates the complete finding set from every
selected M04/M07/M09 checking path assigned to a gate, then returns all compatible admitted material
findings once to the same M02 logical instance and workflow role. Reuse its active invocation when
available and still selected; otherwise make the R9 structured handoff before repair. The writer
receives the whole compatible group plus relevant similar-failure seeds and returns one reviewable
repaired tip. Split only when findings require different owners, source contexts, or acceptance
decisions. Do not stop an ordinary checking path at its first finding, issue one repair per finding,
or review internal repair commits. R23 live-harm containment remains the only immediate-stop exception.

**S10 - Make full-gate scope singular and visible.** A selected M07 final-assurance instance declares
its release unit, selected audit/safeguard paths, exact dependencies, independently runnable check
units, conservative input map, checkpoint owner, and resume rule. Its executor completes every
runnable unit and returns one pool. Do not put full-suite commands in M02 repair cards. If M07 selects
no accumulated safeguard path, state why risk does not justify it. If independently released units
require separate safeguards, use one M07 instance per release unit and prove they are not duplicate
reruns.

**S11 - Select failure cases across real seams.** Before dispatching a high-coupling or high-risk producer, examine every category: authority/targeting, input grammar and platform semantics, concurrency/order, lifecycle/cleanup, failure/rollback, compatibility/migration, external-resource boundaries, result truth, and public usability. Mark each optional case category `SELECTED` or `OMITTED` with a free-form justification. Select realistic expensive-late-failure cases; do not optimize entrypoint score by omitting a necessary seam.

**S12 - Price the graph, not just its nodes.** Estimate a range for each selected module and for the critical path. Count expensive gates, launches, external allocations, and serial joins. State the expected overlap. If observed execution exceeds the plan's upper range and another material cycle is required, the orchestrator reassesses module selection, task size, risk brief, review scope, and role allocation before another launch. This is an result-based topology reassessment, not an iteration cap.

**S13 - Compile exceptions before use.** Each exception class declares: exception ID, affected policy, trigger, decision owner, alternate action, required confirmation, preserved results, invalidated results, scope, and expiry. Local instructions may cite it but cannot broaden it. Do not use an exception to make an ordinary path vague.

**S14 - Validate cross-layer consistency.** Compare the composition-root graph, global policies,
step files, M01-M10 module files, lane manifest, task cards, role-agent mapping boundary,
handoff rule, and final gates. Reject duplicated authoritative prose or any lower-layer instruction
that changes an edge, serializes a required parallel group, adds a broad gate, reopens credited work,
changes review cadence, expands authority, blocks a non-consuming successor, or turns a non-product
fault into a product continuation without a declared exception.

Also reject any worker-facing recipe or specialized action whose verbs could transfer an unstated
semantic choice from its owning authority to a worker. The plan must name the ROOT-owned decision, or
the explicitly delegated lane-local decision, or a deterministic decision rule and limit the worker to
its execution. Review/audit may independently determine findings only within its explicit frozen-input,
surface, invariant, materiality, output, and handoff bounds.

**S15 - Separate runtime truth from workflow intent.** For each action, label enforcement as `RUNTIME_ENFORCED`, `ORCHESTRATOR_ENFORCED`, `TARGET_TOOL_INVOKED`, or `UNAVAILABLE`. Name the source, owner, prerequisites, and concrete confirmation. `UNAVAILABLE` is not a waiver: select M01 and make the fallback name its exact recovery instance. Never describe target work-product code as active development infrastructure merely because the workflow can execute it as a check.

**S16 - Classify and size each gate as one repairable failure family.** A gate is a decision boundary over selected module outputs or one exact operation/resource activation; a loop tranche is the connected unaccepted work that may return one complete finding pool to the same producer logical task and workflow role, with invocation reuse or structured handoff under R9. Give every gate exactly one class:

- `PRODUCT` may block only an observable behavior, contract, capability, or correctness outcome and downstream consumers of that outcome. It may enter a material loop only under R12/R24.
- `OPERATION_BOUNDARY` may block only its exact unsafe, unauthorized, unavailable, unready, or incomplete operation or resource. This class includes required allocation, integration-coordinate mutation, deployment, promotion, readback, cleanup, or retirement mechanics whenever their failure leaves the accepted product behavior intact. An operation being required by the goal does not make it a product outcome. An operation boundary never invalidates accepted product credit or enters a product repair loop; all independent work advances.

For every gate, record its class, exact blocking scope, continuation/loop eligibility, default-forward edge, and failure return or exact-block target. Do not represent an advisory/admin checkpoint as a gate. Do not size a gate or loop by file count, module count, stage labels, or an arbitrary duration/iteration cap. Assume a first pass may expose several mistakes: aggregate enough related work to discover and
repair them together, but never combine so many independent mechanisms that one failed gate becomes
several unrelated repair jobs disguised as one.

Apply this two-sided sizing method to every candidate gate or loop boundary:

1. State one gate question about one independently acceptable behavioral outcome or one exact operation boundary. Identify its class, owning authority, blocking scope, invariants/failure family, likely repair surface, acceptance method, default-forward edge, and affected-prior-result domain.
2. Pass the **aggregation test** only when grouping the work avoids meaningful repeated context loading, setup, launch, review, test, or integration cost and the grouped findings should be triaged and repaired together because they share the outcome, owner, invariants, root-cause surface, or verification.
3. Pass the **manageability test** only when the owning orchestrator can state one pooled repair objective, one writer/workflow role can own it, the expected findings fit one coherent source context and failure taxonomy, and a failure can invalidate affected credit without reopening unrelated accepted work. A lane sub-orchestrator may satisfy this test only within its declared lane. Split at the behavioral, mechanism, authority, writer, source-context, or invalidation boundary when any condition fails.
4. Merge candidates only when both tests pass. If aggregation fails, keep independent gates. If manageability fails, split even when one larger gate would save launches. When uncertain, split at the smallest independently acceptable behavior, not at an arbitrary task-size limit. Record why each retained boundary is not smaller and not larger.
5. Reassess prospectively from observed results: split an unaccepted tranche before repair when its pooled findings require independent repair objectives, owners, or change domains; merge adjacent future gates when findings repeatedly cross their boundary and they duplicate substantial setup. Preserve accepted work and never rewrite completed history merely to change the topology.

**S17 - Give every STEP three distinct entry paths.** Every step file contains exactly the ordered
`NORMAL`, `FAST_LANE_V2_SERIES_1`, and `FAST_LANE_V2_SERIES_2` rows from the step schema. `NORMAL`
uses the full project-specific composition. Series 1 owns the step-local scoped repair and accepted
exit toward the later current progress bound. Series 2 owns checkpointed re-entry when this step is
that bound. Allocate only `MI-NORMAL-*` IDs to NORMAL, only `MI-FL2-S1-*` IDs to Series 1, and only
`MI-FL2-S2-*` IDs to Series 2; no MI occurrence belongs to two entry paths. The fast paths need not
have a universal module count or sequence, but should generally use fewer MIs and must implement
their required behavior, name the concrete normal work they avoid, and be materially narrower than
replaying `NORMAL`. Both fast paths must always have configured disjoint MI paths. Trigger state affects
runtime execution timing only; it never changes required plan content and never permits disabling,
omission, relabeling, reasoning away, or substitution with `NORMAL`.
Directly under the entry-flow heading, copy the template's canonical FAST_LANE_V2 usage block exactly
once and unchanged before the table. This block is an immutable generic reminder, not editable
step-local policy.

## Workflow module catalog

The catalog supplies ten macro-level construction parts. It does not define a default sequence. Read
[references/module-recipes.md](references/module-recipes.md) completely before instantiating one; that
reference fixes each selected module's internal local procedure. Select, omit, repeat, and connect the
macro-modules from project needs. Do not split an internal substep back into a top-level module.

`M05` is mandatory by design. The other modules are genuinely optional, but default toward selection
whenever they would materially improve readiness, implementation, independent proof, review,
integration, accumulated assurance, external safety, real-world validation, or catalog coverage.
The scenarios below are strong recommendations and non-exhaustive examples, not eligibility gates.
Omit an optional module only after deciding it adds no useful behavior for this project, and record a
free-form justification; that justification can decide only the optional module and can never waive a
required artifact, STEP entry, gate, policy, coverage row, card, validation, or FAST_LANE_V2 path.

| Type | Macro-module | Deliberately bundles | Strongly select for these and similar applications | Skip only when | Required output |
|---|---|---|---|---|---|
| `M01` | Prerequisite and admission closure | Missing capability, mapping, fixture, authority, or readiness check needed only to start later work | A required downstream precondition is false or undecidable | Every selected module's preconditions already hold | One prerequisite result; no product work |
| `M02` | Product implementation and repair tranche | Risk brief, singular product writing, implementation self-checks, and same-task material repair | A deliverable needs product/source/artifact changes or later accepted findings may return to its writer | The plan is decision-only | One coherent reviewable product tip plus self-check results |
| `M03` | Independent verification asset construction | Missing independent tests, fixtures, verification scripts, and required verification documentation | Acceptance needs an oracle or asset that must remain independent of M02 | Existing trusted verification assets prove every selected claim | One independently owned verification-asset tip/result |
| `M04` | Review and checking campaign | Cheap affected smoke, deterministic focused checks, independent review, optional observation, parallel launch, and one result join | A reviewable input needs one or more non-producer checks | Existing accepted results already decide the claims and proportional review is omitted with reason | One complete deduplicated result set over one shared input |
| `M05` | Adjudication, acceptance, and correction routing | Finding classification, test-impact decision, semantic verdict, pooled material return, strict test-only route, and administrative recovery | Every formal package; especially deliverable verdicts, finding routing, correction disposition, and release acceptance | Never; M05 is mandatory by design | One verdict or one exact same-task correction route with preserved/invalidated credit |
| `M06` | Integration and release assembly | Ordered joins, conflict ownership, post-join affected checks, promotion, rollback when needed, and release-level retirement | Accepted revisions/artifacts must combine or advance to another coordinate | No integration or promotion boundary exists | One integrated/promoted coordinate with required rollback state |
| `M07` | Accumulated final assurance | Cross-deliverable final audit, full accumulated safeguard, parallel final checks, and release-unit acceptance handoff | Product/release risk needs assurance beyond deliverable-level results | Deliverable checks already decide the complete goal and omission is justified | One final result pool over one named release unit |
| `M08` | Expensive or external readiness check | Fragile-runner preflight and disposable external-control rehearsal | An expensive custom executor or scarce/irreversible external operation has an unproven control path | Runner/control path is ordinary or already checked under unchanged relevant inputs | One readiness result that is not a product pass |
| `M09` | Practical or external validation | Authorization, retained attempt state, real execution, independent observation, stop/abort, checkpoint/resume, result join, and cleanup | Acceptance requires a real environment, service, deployment, provider, hardware, or long-lived practical result | Static/synthetic checks satisfy the goal | One contained real-attempt result with required observation and cleanup |
| `M10` | Project extension | Only behavior no composition of M01-M09 can express | A required capability is genuinely absent from the catalog | Existing macro-modules and policies cover it | One standard-schema module with a named expressive gap and no duplicate policy |

## Exact step schema

Render every large independently gated workflow unit in exactly one `steps/<STEP-ID>.md` file using
the exact step schema in `references/execution-plan-template.md`. A step owns its objective,
activation, public interface, exact three-entry table, disjoint per-entry MI paths with the required
`MI-NORMAL-*`/`MI-FL2-S1-*`/`MI-FL2-S2-*` prefixes, union MI
inventory, gate/completion rule, failure and
default-forward routes, result-credit boundary, isolation/lifecycle, and cost. It references module
interfaces and global policy IDs; it does not copy module actions, rules, task cards, or concrete agent
selection. File order has no execution meaning.

## Exact module and module-instance schema

Render exactly `modules/M01.md` through `modules/M10.md` using the exact M-module file schema in
`references/execution-plan-template.md`. Each file owns that module type's selection decision, stable
public interface, project-specific rules/process, recipe actions, allowed variation points, and all of
its configured `MI-*` occurrences. Render every selected instance exactly once inside its matching
M file using the original exact 16 required schema headings: one `MI-*` H3 plus the 15 ordered H4
fields. Nested H5 governing/member task-card labels do not change that count. Fill every required heading in order, including
gate/loop references, complete-pool return, affected prior results, isolation, critical-path effect,
and local instructions. Do not add a custom instance shape; use M10 only when a genuinely missing
module behavior requires extension.

## Exact local-instruction schema

Use the exact 20-field task-card table in `references/execution-plan-template.md` inside every
selected `MI-*` local-instructions section. Give the instance exactly one H5-labeled governing card;
it binds the full ordered module recipe and owning orchestration authority. Add one H5-labeled member
card for every internal worker dispatch, with at least one member card for every selected executable
`MI-*`. A member card is not another `MI-*` and does not appear
in a step; it specializes an allowed internal fan-out and cites only its applicable ordered recipe-action
subsequence. Every configured `MI-*` is executable because it is selected and composed into a STEP
entry; every field of every governing/member card is therefore a concrete dispatch contract and may
not use `N/A`. Represent an omitted optional profile through its recipe-owned omission decision rather than
creating a non-executable instance. The instance's `Owner and roles` field must inventory every member
dispatch exactly once as `CARD-ID=workflow_role`; the inventory and member cards must agree. If the runtime has a stricter accepted schema, map all 20 semantic fields
to it explicitly. A task card may customize only the authorized task
content; it may not change role, required runtime-object correlation, completion ownership,
failure/thread rules, global policy citations, module interface, or graph edges. A handoff records facts
and the next authorized edge.

Every governing card uses ROOT or, only in the selected Multi-agent lane topology, that MI's explicitly
authorized lane sub-orchestrator. Every member card uses a terminal WORKER role. Its identity row must
resolve to real declared deliverable, gate, loop, MI, and card objects. Each member card also names one
unique preassigned `INVOCATION-*` ID and one unique launch-time `PROCESS-*`/process-tree record ID; its
reciprocal terminal handoff repeats both correlation IDs. These are mandatory runtime-object identities,
not permission to assign IDs to ordinary content.

Treat each set of 20 fields as one module-instance-owned contract authored by ROOT or, within an
explicitly authorized lane, by its lane sub-orchestrator—not as independent boxes that a worker must
interpret into a task. The governing card records the complete campaign recipe and authority; every
member card is the complete contract for one actual worker. For
non-review work, the fields collectively must define the problem, desired result, exact
behaviors/claims, required and forbidden change boundaries, targets, protected behavior, checks,
acceptance, pitfalls, and escalation route. For review/audit work, they must define the bounded
investigation and its materiality/output contract without prescribing findings. `N/A`, `TBD`,
`TODO`, `UNKNOWN`, a bare equivalent such as `none`/`omitted`/`not required`, or appeal to worker
judgment in any field makes the card undispatchable.

## Build the plan step by step

Perform these passes in order. Finish each named output before starting the next pass; later passes may
send a specific unresolved fact back to its owning pass, but may not silently rewrite earlier decisions.
This procedure authors a plan. It never executes the resulting workflow. For every pass, instantiate
all five local fields in `references/compiler-pass-recipes.md`: `Inputs`, `Ordered actions`, `Decision
table`, `Emit`, and `Complete only when`. The prose below is the high-level route; the referenced local
recipe is normative and no field may be inferred, skipped, or replaced with free-form judgment.

### Pass 1 - Freeze the request and destinations

- **Read:** direct user instructions, goal/spec, acceptance material, requested output directory, project
  root, runtime root, resource limits, and the canonical role-agent mapping if it exists.
- **Decide:** which documents are operative, which are reference-only, what is explicitly excluded,
  and whether the task authorizes creation of a missing mapping.
- **Write:** the source register and exact package/mapping coordinates in working notes. Do not draft workflow prose.
- **Stop when:** a missing input would change scope, authority, or provider allocation; ask one
  consolidated question. Do not stop for facts discoverable from the named project.

### Pass 2 - Build the authority and contradiction register

- Follow the authority audit in `references/project-truth-audit.md`. Record each source's path or
  reference, what it governs, and the conflict rule. Add a revision or hash only if R21 identifies a
  concrete operation that needs one; the source table has no identity column.
- Compare goal, acceptance, repository instructions, existing plan, and runtime documentation. Record
  each contradiction as a decision item; never blend incompatible directives into vague prose.
- Produce the complete Section 1 authority rows and Section 14 unresolved rows before decomposition.

### Pass 3 - Normalize outcomes and atomic coverage

- Turn the required product behavior into plan-local `OUT-*` outcomes and `REQ-*` requirements when
  cross-references need labels. Split only when two clauses can independently pass, fail, be owned, or
  require different verification.
- Bind every requirement to one observable acceptance claim and one decision owner. Preserve exact
  source citations; record exclusions and authorization boundaries separately from requirements.
- Check that satisfying all requirement rows would satisfy the goal without relying on implied work.
  The output is Sections 2 and 3, not an execution sequence.

### Pass 4 - Audit repository and runtime truth

- Inspect relevant Git state/cleanliness, source seams, available checks, launch/wait/result behavior,
  isolation, locks, lifecycle, and external capabilities. Prefer source and executable help over prose.
- Classify each needed action as `RUNTIME_ENFORCED`, `ORCHESTRATOR_ENFORCED`,
  `TARGET_TOOL_INVOKED`, or `UNAVAILABLE`; name its source, invocation owner, prerequisite, confirmation,
  and fallback. Never turn desired behavior into a claimed runtime feature.
- Produce Section 4 and the raw facts needed by Sections 7, 10, and 12. A missing required capability
  becomes a prerequisite candidate; an unavailable optional convenience is not invented.

### Pass 5 - Form coherent deliverables

- Group requirements by independently useful behavioral output, dependency order, shared invariant,
  integration seam, and acceptance method. Ignore equal-size aesthetics and file counts.
- For each `DEL-*`, state inputs, outputs, requirements, dependencies, shared seams, release unit, and
  why separating or combining it would improve or hurt correctness, context, or wall time.
- Identify candidate `STEP-*` boundaries only where a coherent independently decidable gate and stable
  public input/output justify one; a step may serve one or more deliverables and is not inferred from
  file count or module count.
- Keep two units separate when either can be accepted and used without the other or when they require
  different authorities/writers/change domains. Merge them when partial acceptance is meaningless
  and the same owner must reason across their shared behavior.

### Pass 6 - Model risk, failure cases, and cost

- For every deliverable, list only realistic late-expensive failures, their impact/coupling, earliest
  decisive oracle, context demand, expensive operations, and expected duration range.
- Apply S11 to decide which failure cases belong in the producer's existing card. Reject generic
  hardening, cosmetic concerns, and duplicated checks. Record why each selected case is worth its cost.
- Produce both Section 5 tables. Use the risk/cost rows as the reason for every later non-minimal
  module, fan-out, serial edge, gate, rehearsal, and safeguard.

### Pass 7 - Select workflow modules

- Start with the smallest topology that can produce and semantically accept each deliverable. Evaluate
  M01-M10 individually against project facts and the catalog's non-exhaustive recommendations; do not
  treat examples as eligibility gates or trace a remembered workflow.
- Mark every catalog row `SELECTED` or `OMITTED`. A selected module receives one or more plan-local
  `MI-*` references and a named payoff. An omitted optional module records a concrete free-form
  justification. Resolve missing facts before this pass; they may not create a third decision state.
- Recheck coverage: module omission may remove ceremony, never a requirement, decision owner, or needed
  verification path. Record each decision in its sole `modules/Mxx.md` owner; Section 6 indexes the
  ten module files without copying their decision prose.

### Pass 8 - Define roles and bind the sole mapping

- Derive workflow roles from selected module responsibilities. Set role pool capacity one by default;
  increase that ceiling only for named independent slices with measurable time, isolation, or coverage
  benefit. M modules own the active member count within that capacity.
- Put role semantics, authority, resources, activation, and lifetime in `plan-workflow.md` Section 7. Put concrete
  provider/model/effort/tier selection only in the canonical mapping. Every executable role appears
  exactly once there, and changing the mapping must not require a plan edit.
- If the runtime cannot resolve roles at launch, select M01 for that prerequisite instead of copying
  provider values into cards or commands.
- Define every non-ROOT role as an executor, reviewer, checker, observer, or—only when R3 justifies
  it—an authorized lane sub-orchestrator. A worker role never receives task-definition,
  scope-definition, success-definition, acceptance, or self-dispatch authority. A lane
  sub-orchestrator receives only the declared lane-local authority from R6, directs every worker in
  that lane, and cannot create another orchestration tier. Preserve the bounded review/audit discovery
  exception without giving the reviewer authority to expand its assigned surface or prescribe the next edge.

### Pass 9 - Instantiate M modules and compose independent steps

- Fill exactly `modules/M01.md` through `modules/M10.md`. Each file owns its one selection decision,
  stable interface, complete project-specific module rules/process, ordered recipe actions, allowed
  variations, and every configured `MI-*` occurrence of that type.
- Preserve every selected module recipe action in order. Specialize it inside the matching `MI-*`
  local instructions without copying global policy; an omitted M file has no active instance.
- Fill the governing 20-field task card inside each selected `MI-*` and one complete member card per
  internal worker dispatch. The governing card cites every recipe action exactly once in order; a
  member card cites its applicable ordered subsequence. Every selected instance has at least one member
  card, and no configured instance or task-card field may use `N/A`. Give exact initial entrypoints and enough shared-seam
  context to perform executable work without reconstructing project history.
- Create the fewest coherent `STEP-*` files justified by independently decidable gates. Each step
  uses the exact step schema and compiles `NORMAL`, `FAST_LANE_V2_SERIES_1`, and
  `FAST_LANE_V2_SERIES_2` as three distinct ordered paths using only `MI-NORMAL-*`,
  `MI-FL2-S1-*`, and `MI-FL2-S2-*`, respectively, through stable public interfaces.
  Copy the canonical FAST_LANE_V2 usage block exactly once beneath the entry-flow heading and before
  those rows; do not paraphrase or specialize it.
  Derive their project-specific module combinations; do not copy a universal example or let a fast
  path invoke the normal broad path. Inventory every configured MI once without copying module rules,
  flow, task cards, or concrete agent assignments.
- Keep authority local and singular: a step owns composition; an M file owns its module process and
  instances; global policy and concrete agent selection remain in their own artifacts.
- Before an executable instance is dispatchable, compile all 20 fields into the complete R6/R10
  contract authored by ROOT or, within an explicitly authorized lane, by its lane sub-orchestrator.
  Verify that a worker can begin at the named entrypoints, execute the desired result, preserve named
  non-goals, recognize task-specific pitfalls, run or return the required proof, and stop/escalate
  correctly without inventing task meaning or reconstructing history. For review or audit, verify
  instead that the investigation is concretely bounded while its findings remain open.

### Pass 10 - Compose the typed execution graph

- Connect instances inside a step only when a declared module output satisfies another instance's
  input. Connect steps only when one step's public output satisfies another's public input. Draw the
  actual serial spine, conditional branches, fan-outs, parallel groups, joins, repair returns, external
  authorization boundaries, and terminals; catalog and file order supply no edge.
- Verify each step's three entry paths separately: `NORMAL` follows ordinary predecessor activation;
  Series 1 exits an accepted integrated repaired output toward the ROOT-selected later progress-bound
  step; Series 2 enters only at that bound, joins every accepted Series 1 exit, and resumes from the
  earliest required checkpoint unit. No MI ID may occur in two entry paths.
- Give every edge a condition and failure branch. Give every real fan-out one join or prove its outputs
  are independently terminal. Do not draw a split for a singleton or serialize independent checks
  merely because one path was written first.
- Mark every satisfied successor as default-forward. A failed support/admin/readiness fact may remove only edges that consume it; preserve and activate all other ready edges at the earliest failed, unresolved, change-affected, or uncertain action/check while retaining unaffected credit.
- Produce the inter-step edge and parallel-group tables in `plan-workflow.md` Section 8, then verify
  the transitive composition through Section 10 manifests, `STEP-*` module-composition tables, and
  `MI-*` public interfaces. Any disagreement is a compiler error.

### Pass 11 - Size gates and repair loops

- Apply S16's gate classification, aggregation, and manageability tests to every proposed gate. State class, one behavioral/operation question, shared input, checking instances, shared failure family, exact blocking scope, continuation/loop eligibility, default-forward edge, return/block target, prior-result boundary, aggregation payoff, and split/merge trigger.
- Classify by what a failure disproves, not by whether the step is required. If accepted behavior remains true and only an allocation, join, deployment, promotion, readback, cleanup, retirement, or other coordinate mutation is incomplete, emit `OPERATION_BOUNDARY`; never disguise the required operation as a product gate.
- Assume a first pass may find several related defects. Make the tranche large enough to pool them,
  but split whenever one return would require independent repair objectives, writers, source contexts,
  authorities, or invalidation decisions.
- Apply S8 within retained M04/M07 gates: selected independent review and deterministic-check paths over
  the same shared input run in one parallel group. Apply S9: M05 returns the complete admitted material
  pool once to the same M02 logical task and workflow role, reusing or handing off its invocation under
   R9. Compile the selected gate's check-unit checkpoint and conservative input map, including the
   remaining-unit route after ordinary failures and the earliest failed, unresolved, change-affected,
   or uncertain resume unit. Neither rule adds a macro-module that Pass 7 omitted.

### Pass 12 - Compile global policy and exceptions

- Fill P01-P15 once in `global-rules.md` from R1-R30 and S1-S17. For every policy name its owner, trigger, mandatory action,
  exit, optional result/record location when a consumer needs one, and applicable module IDs.
- Define an exception only for a concrete alternate route. Give it an ID, affected policy, exact trigger,
  decision owner, allowed action, required confirmation, preserved/invalidated results, scope, and expiry.
- Compile R12/R14/R15/R17/R18/R19/R21/R24 into P04/P07/P08/P09/P10/P11/P12/P13 so decided product
  work advances immediately, non-product faults block only direct consumers, every ordinary gate failure
  returns a complete runnable finding pool, compatible repairs batch, and continuation resumes from
  the earliest failed/unresolved/change-affected/uncertain unit with unaffected credit preserved.
- Put the literal `CHECKPOINTED_VERIFICATION_V1` in Section 0 of every formal modular plan because
  every step defines both FAST_LANE_V2 series. It selects this verification protocol for structural
  validation; it is not a runtime
  identity, hash, or required record.
- Compile R30 into P02/P04/P09: only cards that invoke an explicitly listed finite command adopt the
  discovered bounded-command policy; its runtime supervisor owns heartbeat/deadline/cleanup, an
  available provider hook blocks recognized bypasses, and timeout returns to support classification.
  Agent and subagent sessions remain unbounded and are explicitly exempt from that command boundary.
- Reject any local phrase such as `as needed` that hides an undeclared decision. Unknown exceptions
  require a plan amendment or `INCOMPLETE`, not runtime improvisation; ordinary classification through
  the compiled failure routes is not an exception.
- Compile the dispatch-authority contract into P01 and P02. P01 must make ROOT the owner of the
  concrete problem, desired result, required behavior/proof, target and protected boundaries, repair
  classification, pitfalls, acceptance criteria, and next-edge decision, except for lane-local
  decisions explicitly delegated under R6. P02 must require workers to execute within their owning
  authority's contract, return insufficiency or contradictions, terminate at each decision boundary,
  and continue only through a separately issued card.

### Pass 13 - Compile lanes, resources, checks, results, and lifecycle

- Derive `plan-workflow.md` Section 10 from the graph: create rows only for real lanes, claims/locks, named checks,
  required durable results, every handoff, source allocations, and retirement actions. Only the
  explicitly optional claim/lock, check, source-allocation, and retirement category tables may use one
  explained not-applicable sentinel when that category has no items. Every member dispatch requires a
  concrete reciprocal lane row and terminal handoff row; those two tables never use a sentinel. IDs are mandatory for the runtime instances named by R21;
  never create an ID or artifact for ordinary content merely to fill a category.
- Give concurrent writers disjoint roots or one correct shared append lock. Give mutating work the
  cheapest safe source isolation. Correlate every process, agent/subagent invocation, handoff, lane,
  claim/lock, and Git worktree with its mandatory runtime ID; do not impose IDs on ordinary content.
- State activation, completion, failure, cleanup, recovery visibility, and affected prior results.
  Terminal cleanup never erases a revision or result that a named consumer still needs.

### Pass 14 - Compile external, integration, and terminal behavior

- In `plan-workflow.md` Section 12, record only selected practical/external modules. Separate disposable rehearsal
  claims from real-world acceptance, state exact authorization, and name the controller and cleanup owner.
- In `plan-workflow.md` Section 13, record only selected integration, safeguard, audit, promotion, rollback, and
  retirement modules. Name accepted inputs, order, affected checks, release unit, and rollback state when needed.
- Resolve every semantic selection before dispatch: ROOT chooses the admitted integration inputs and
  order, conflict route, audit/safeguard profile, real-attempt authorization, retry/new-attempt route,
  and acceptance boundary. An executor may apply only the named mechanical comparison, branch, or
  operation and must return any undeclared choice or conflict to ROOT.
- A selected M06, M07, M08, or M09 must have at least one corresponding `SELECTED` behavior row in
  Section 12 or 13. Additional genuinely optional profiles may be `OMITTED: <free-form justification>`,
  but omission-only rows cannot hollow out a selected module. Every field consumed by a selected
  behavior is concrete; an optional unused field may remain `N/A` only where the template expressly
  allows it.
- Do not manufacture a universal final phase. An omitted optional module remains visibly omitted in
  Section 6, and only explicitly optional structural tables may use one explained not-applicable row.

### Pass 15 - Price and simplify the completed graph

- Compute module ranges, overlap, launches, expensive gates, external allocations, serial joins, and
  the critical path. Compare the result with the cheapest adequate topology named in Section 5.
- Remove every node, edge, repeated read, rerun, artifact, isolation boundary, or fan-out whose named
  benefit does not plausibly exceed startup, context, coordination, merge, and maintenance cost.
- Remove any wait, continuation, or repair edge whose only purpose is to perfect a non-product artifact after the required product result is independently decidable; retain only the exact dependent operation block or claim-level incompleteness.
- Re-run coverage and safety checks after removal. Simplicity may remove machinery, never required
  behavior, necessary verification, live-harm containment, or semantic acceptance.

### Pass 16 - Fill, cross-check, and validate the final package

- Fill every artifact skeleton in `references/execution-plan-template.md`: `plan-workflow.md`,
  `global-rules.md`, every `steps/STEP-*.md`, exactly `modules/M01.md` through `modules/M10.md`, and
  `validation.md`. Replace
  every template token, delete all template notes, and use exact headings, tables, policy names, and
  schemas.
- Populate `validation.md`'s rule matrix only after behavior exists in its authoritative artifact; a
  rule citation cannot substitute for implementation. Run every V01-V30 semantic check and record a
  one-line basis.
- Run the packaged validator with the plan-directory and mapping paths. Fix all failures, reread affected artifacts,
  and rerun until both manual semantic validation and deterministic structural validation pass.
- During manual V10/V13/V14/V27 validation, inspect the substance of every worker card, not merely the
  presence of its fields. Reject a card that delegates discovery of its task semantics to the worker;
  reject a review card that lacks a concrete investigation boundary or improperly dictates findings.
- Audit every specialized recipe verb under the dispatch-authority interpretation above. Confirm that
  test authors materialize ROOT-supplied or explicitly delegated lane-local behavior and proof goals,
  integration executors stop for ROOT conflict decisions, assurance executors run ROOT-selected paths,
  and practical workers never start a new attempt without a separate ROOT decision and card.

## Fill the exact package templates

Use `references/execution-plan-template.md` as a set of artifact schemas, not as prose to paste
unchanged. Preserve the package layout, composition-root title/section order, exact table headers,
P01-P15 order, step headings, M-module headings, module-instance headings, task-card fields, and structural-check
IDs. Replace every `{{TOKEN}}` with project-specific content and remove every `TEMPLATE NOTE`. Use one
one explained `N/A` sentinel only in the exact optional tables allowlisted by the template; every hard
table rejects it regardless of justification.

Write each artifact from its upstream compiler output: authority before coverage, coverage before
deliverables, deliverables before module selection, module definitions and step composition before
graph verification, and `validation.md` last. This is an authoring dependency, not a mandatory runtime
sequence. Never copy global rules into modules, module flow into steps, step internals into the
composition root, or
concrete mapping values into Markdown. Never edit the packaged template to make one plan validate;
fix the package or, when the compiler contract itself is intentionally changed, update the skill,
architecture, template, validator, and self-tests together.

## Validate the plan

1. Perform the template's semantic checks manually against the goal, sources, and selected graph.
   Record an honest `PASS` or `FAIL` basis in `validation.md`; this does not require another evidence artifact.
2. Run the validator from the project root. In this workspace, use the installed canonical copy:

```powershell
python .agents/skills/project-topology/references/level-4-design-project-topology/scripts/validate_execution_plan.py <plan-directory> --mapping <mapping-path>
```

   The source-project installation uses the equivalent command below. Select the installed
   path; these are alternative locations for the same validator.

```powershell
python .codex/skills/project-topology/references/level-4-design-project-topology/scripts/validate_execution_plan.py <plan-directory> --mapping <mapping-path>
```

3. Fix every reported structural or cross-reference error, then rerun both affected semantic checks
   and the script. Do not weaken the validator, insert dummy rows, or mark a failure N/A to gain a pass.
4. Finish only when the script prints `execution plan validation: PASS`, every V01-V30 row is `PASS`,
   `plan-workflow.md` has exact final status `VALIDATED`, every outcome and requirement has status
   `COVERED`, and `validation.md` ends with `PLAN_STRUCTURE=VALID`.

A validator pass is not permission to waive a semantic requirement. Every `PASS` basis must identify
the concrete artifact behavior that satisfies the check; bare assertions, keyword lists, copied rule
text are failures even when document shape is valid. Any `N/A` in a hard field fails regardless of explanation.

## Deliver

Write the package to the requested directory and create the sole mapping only when the project does
not already have one. Report the composition-root path, package directory, mapping path, input
sources, selected/omitted module
summary, role set, critical path, non-minimal complexity decisions, unresolved inputs, and validation
result. Do not repeat concrete model assignments, do not execute the plan, and do not create runtime
state.
