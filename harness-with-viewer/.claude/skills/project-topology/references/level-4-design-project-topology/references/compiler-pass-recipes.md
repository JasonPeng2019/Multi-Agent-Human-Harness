# Compiler Pass Recipes

Execute these recipes in order when authoring one modular execution-plan package. Each pass has the same five
mandatory local fields: `Inputs`, `Ordered actions`, `Decision table`, `Emit`, and `Complete only when`.
Do not start the next pass until the current completion test passes.

## Contents

1. Universal pass protocol
2. Pass 1 - Freeze request and destinations
3. Pass 2 - Build authority and contradiction register
4. Pass 3 - Normalize outcomes and atomic coverage
5. Pass 4 - Audit repository and runtime truth
6. Pass 5 - Form coherent deliverables
7. Pass 6 - Model risk, failure cases, and cost
8. Pass 7 - Select macro-modules
9. Pass 8 - Define roles and bind the mapping
10. Pass 9 - Instantiate M modules and compose independent steps
11. Pass 10 - Compose the typed graph
12. Pass 11 - Size gates and repair loops
13. Pass 12 - Compile policies and exceptions
14. Pass 13 - Compile lanes, resources, results, and lifecycle
15. Pass 14 - Compile external, integration, and terminal behavior
16. Pass 15 - Price and simplify the graph
17. Pass 16 - Fill, cross-check, and validate

## 1. Universal pass protocol

For applicable execution risks, apply the pass-to-owner mapping and semantic
acceptance examples in [execution efficiency](../../execution-efficiency.md).
This applies to prospective runtime repair-card generation as well as initial
compilation: preserve adjudicated mechanism groups and distinguish manual policy
from implemented supervision. Pass 16 must assess these semantics separately
from structural validation; do not add a second authoritative plan sidecar.

For every pass:

1. Copy its `Inputs` list into working notes and bind every item to its source path or existing
   plan-local reference. Do not invent an ID for an ordinary input. Mark missing items `MISSING`; do
   not substitute an assumption.
2. Perform every `Ordered action` once and in order. A required recipe action may not be marked `N/A`;
   an action that evaluates an optional branch records a concrete `SELECTED` or `OMITTED` branch result.
3. Apply every applicable `Decision table` row. If two rows conflict, return to the named earlier
   pass or record an unresolved item; never merge the actions.
4. Write only the named `Emit` outputs in their authoritative package artifacts. Do not draft later
   sections early, duplicate content into another artifact, or create an artifact outside the exact
   package grammar.
5. Evaluate every `Complete only when` predicate. A single false predicate keeps the pass open.

Working notes are disposable compiler state. Put only consumed facts and useful cross-references in
the owning package artifact, the sole role-agent mapping, or an already-required project artifact. Do not create identity
or evidence machinery merely to preserve working notes.

Throughout these passes, ROOT/orchestrator owns every global semantic planning and dispatch decision.
The default topology is ROOT dispatching workers directly. When R3 explicitly justifies it, ROOT may
authorize one direct lane sub-orchestrator per bounded lane; the plan must state its local authority,
workers, terminal handoff, and no-further-orchestration limit. A worker-facing recipe verb such as
`define`, `select`, `choose`, `classify`, `resolve`, `decide`, `authorize`, `continue`, `resume`, or
`start` must compile either to a ROOT decision, an explicitly delegated lane-local decision made before
dispatch, or an exact deterministic rule the worker can apply without judgment about task meaning. It
never silently delegates goals, desired behavior, change/protected scope, test meaning, oracle,
acceptance, conflict resolution, retry/new-attempt authority, or graph routing to a worker. Review/audit
alone may form independent findings, and only inside its owning authority's investigation contract.

## Authoring and regeneration across all passes

Use [normalized authoring](normalized-authoring.md) for new formal plans. The passes
still determine the same semantics; their emitted tables are compiler projections.
Pass 1 reserves separate source, output and mapping coordinates. Passes 7/9 place
configured instances and local dispatches under their owning step while retaining
shared recipes/defaults in the library. Passes 10/13 author real public edges,
shared capacities and lifecycle facts once; derive indexes, role children, local
lane/handoff rows and consumer inventories. Do not infer lifecycle facts from prose.

Pass 15 assesses change locality as well as execution cost: changing a private
instance must not require editing unrelated source owners. Pass 16 compiles a draft,
obtains the four real scoped reviews on the final candidate and checks source/output
freshness plus full structural closure. Never generate semantic V PASSs, sign review
records or reuse stale approvals merely because compilation succeeds. Keep actual
review evidence and its source binding at the review owner. Later edits repeat only
affected semantic review while retaining the full inexpensive structural check.

An instruction below to write an exact package artifact describes its expanded
owner and output shape. It does not override the normalized source ownership rule.
Legacy packages retain the old editable ownership until migrated successfully.

## 2. Pass 1 - Freeze request and destinations

### Inputs

- current direct user request and all additions/corrections in the active conversation;
- named goal/spec, acceptance source, reference plan, repository root, and runtime root;
- requested plan-package directory or the project convention that determines it;
- available concurrency/resources and any external authorization limits; and
- existing canonical role-agent mapping path or authority to create it.

### Ordered actions

1. Resolve every supplied path to an exact readable location without mutating it.
2. List documents explicitly named operative, reference-only, superseded, forbidden, or user-view-only.
3. Record the exact requested product outcome and planning-only boundary.
4. Record output package directory, its exact artifact paths, mapping path, and project root as separate coordinates.
5. Record supplied concurrency/resource limits exactly; do not infer defaults from another project.
6. List missing inputs and classify each as discoverable from the project or requiring user authority.

### Decision table

| Condition | Required decision |
|---|---|
| Missing fact is discoverable read-only from named roots | Continue and discover it in Pass 2 or 4 |
| Missing fact changes product scope, acceptance, external authority, or concrete role allocation | Ask one consolidated question and stop drafting |
| Reference plan conflicts with direct current instruction | Current instruction controls; record the conflict for Pass 2 |
| No mapping exists and creation is authorized | Reserve the canonical path; create content in Pass 8 |
| No mapping exists and creation is not authorized | Record unresolved prerequisite; do not copy provider values into plan |

### Emit

- working source list with status (`OPERATIVE`, `REFERENCE`, `SUPERSEDED`, `FORBIDDEN`);
- output package-coordinate record naming `plan-workflow.md`, `global-rules.md`, `steps/`, exactly
  `modules/M01.md` through `modules/M10.md`, `validation.md`, and the isolated mapping; and
- missing-input list routed to discovery or user decision.

### Complete only when

- every named input path is readable or explicitly unresolved;
- package-artifact and mapping destinations are unambiguous;
- planning authority and forbidden actions are explicit; and
- no scope/authority/provider-allocation question is being silently guessed.

## 3. Pass 2 - Build authority and contradiction register

### Inputs

- Pass 1 source list;
- direct user instructions, goal/spec, acceptance source, repository instructions, existing plan,
  handoff/status, runtime docs/source, and mapping; and
- authority order from the skill's directive hierarchy.

### Ordered actions

1. Read every operative/reference source needed by `project-truth-audit.md`.
2. Add a `SRC-*` plan label only when cross-reference is useful. Record path/reference, supplied facts,
   and conflict rule. Add no identity field; state any R21-required revision or hash at the operation
   that consumes it.
3. State exactly what each source supplies: scope, acceptance, development rules, workflow, runtime
   truth, status only, or launch selection only.
4. Compare overlapping statements pairwise and record exact contradictions.
5. Resolve a contradiction only when the authority hierarchy decides it mechanically.
6. Route every authority-dependent contradiction to one `LEDGER-*` unresolved item and owner.
7. Draft the fixed nine-layer directive table without project-specific deviations.

### Decision table

| Condition | Required decision |
|---|---|
| Higher-authority source clearly controls | Use it; mark lower clause superseded for this subject |
| Sources govern different subjects | Keep both; state their non-overlapping authority |
| Same-authority sources conflict | Mark unresolved and block `VALID` until owner resolves |
| Historical result differs from current operative source | Current source controls future work; retain history only when a consumer needs it |
| Runtime prose conflicts with inspected runtime source/help | Runtime source/help controls capability truth; record prose mismatch |

### Emit

- complete Section 1 source/authority table;
- fixed directive hierarchy table; and
- Section 14 unresolved rows for undecided contradictions.

### Complete only when

- every operative fact has exactly one authority source;
- the mapping path appears in Section 0's Agent mapping dependency row only;
- every contradiction is resolved by rule or has an owner/boundary; and
- no handoff/runtime artifact is treated as policy authority.

## 4. Pass 3 - Normalize outcomes and atomic coverage

### Inputs

- resolved goal/spec and acceptance sources from Pass 2;
- explicit exclusions, tolerances, and authorization boundaries; and
- source-location scheme for citations.

### Ordered actions

1. Extract every externally observable success/failure/recovery/release outcome.
2. Assign one plan-local `OUT-*` reference per independently decidable outcome represented in the
   acceptance graph. This is document navigation, not a runtime identity; do not label subordinate
   implementation features merely because they are mentioned.
3. Split each outcome into `REQ-*` rows only when clauses can independently pass/fail, have different
   owners, use different verification, require different authority, or affect different prior results.
4. For each requirement, copy the exact source location and write one observable acceptance claim.
5. Assign one acceptance owner; leave implementation owner/deliverable blank until Pass 5.
6. Put exclusions and authorization conditions in `BOUND-*` rows, never negative fake requirements.
7. Test completeness by reading only the `OUT-*`, `REQ-*`, and `BOUND-*` rows as a substitute for the goal.

### Decision table

| Condition | Required decision |
|---|---|
| Two clauses share one pass/fail result, owner, verification, and change domain | Keep one requirement |
| Any one of those dimensions differs | Split requirements |
| Behavior is implied but necessary for named outcome | Add requirement and cite the implication |
| Behavior is desirable but not required by authority | Put it out of scope; do not add requirement |
| No trustworthy check or observation can decide requirement | Keep requirement and create an verification-gap fact for Pass 6/7 |

### Emit

- Section 2 goal, `OUT-*` table, and `BOUND-*` table; and
- Section 3 rows with requirement/source/acceptance owner/verification, leaving Pass 5-owned fields pending.

### Complete only when

- every required behavior appears exactly once as a primary `REQ-*` row;
- every requirement has source, observable claim, and acceptance owner;
- exclusions/authority are not hidden inside task prose; and
- satisfying all rows would satisfy the authoritative goal.

## 5. Pass 4 - Audit repository and runtime truth

### Inputs

- Pass 2 authority rows and Pass 3 requirements/verification;
- repository/runtime roots and current Git coordinates; and
- `project-truth-audit.md` audit checklist.

### Ordered actions

1. Inspect Git root, revision, branch/detached state, cleanliness, nested repositories, worktrees,
   ignored runtime roots, forbidden paths, and existing plan/runtime state.
2. Locate each requirement's public entrypoint, owning source seam, callers, existing tests, shared
   state/protocol, lifecycle owner, and compatibility surface.
3. Inspect real launcher/runtime source and executable help for every relied-on action.
4. Inventory checks, result formats, caches, optional durable result paths, baseline failures, and cost.
   For every expensive multi-check gate, identify the smallest economical independently runnable unit,
   its source/configuration/runner/environment/external-state inputs, whether the current runner can
   checkpoint/resume it, and the smallest truthful prerequisite if it cannot.
5. Discover the repository's agent-instruction and provider configuration chains (`AGENTS.md`,
   `.codex/`, `.claude/`, or observed equivalents), the explicit bounded-command manifest, its
   supervisor and hook/guard coverage, and prompt-inheritance behavior for root agents and nested
   subagents. For every manifest-selected finite command, bind the justified lifetime/basis, heartbeat,
   terminal result, cleanup, and timeout-classification route. Record agent/session launches as
   explicitly unbounded.
6. Inventory concurrency cap, source-isolation modes, claims/locks, external resources, and cleanup.
7. Inventory every current blocker/retry/restart/handoff, its exact consumer, the first unresolved
   check unit, reusable PASS units, invalidated inputs, and the earliest failed, unresolved,
   change-affected, or uncertain unit from which required execution can continue without replaying
   unaffected work. Record whether the active invocation can be reused and the structured-handoff
   inputs required when it cannot or the user changes allocation.
8. Classify every needed capability with one allowed state and record source, owner, prerequisite,
   confirmation method, fallback, and unavailable consequence.

### Decision table

| Observed implementation | State |
|---|---|
| Runtime automatically performs/enforces action | `RUNTIME_ENFORCED` |
| Orchestrator must perform action through available primitives | `ORCHESTRATOR_ENFORCED` |
| Exact target-project revision supplies callable action | `TARGET_TOOL_INVOKED` |
| No truthful current mechanism exists | `UNAVAILABLE` |

| Additional condition | Required decision |
|---|---|
| Required capability unavailable | Candidate M01 or unresolved blocker |
| Optional convenience unavailable | Omit convenience; do not invent framework |
| Source writes local state | Require mutable isolated allocation in Pass 13 |
| Read-only action writes only results/cache | Current declared source plus separate writable root; pin a revision only when the action needs it |

### Emit

- complete Section 4 capability table; and
- fact sets for roles, checks, isolation, resources, results, and lifecycle used by later passes.

### Complete only when

- every planned action can cite actual enforcement/invocation or `UNAVAILABLE`;
- stable launcher and target work-product tooling are distinguished;
- relevant source seams and checks are concrete; and
- every observed blocker/restart has an exact scope, first-unresolved unit, conservative reuse basis,
  earliest-required execution unit, and continuation checkpoint; and
- no runtime capability is inferred solely from desired plan behavior.

## 6. Pass 5 - Form coherent deliverables

### Inputs

- all `REQ-*` rows;
- source seams/dependencies from Pass 4;
- acceptance claims/owners; and
- release/integration boundaries from authority sources.

### Ordered actions

1. Start with each `REQ-*` as ungrouped.
2. Group requirements sharing one independently useful behavioral output, writer context, invariants,
   integration seams, acceptance method, and release unit.
3. For each candidate group, state one sentence: `DEL-* delivers <behavior> to <consumer>`.
4. Apply both split and merge tests below.
5. Assign each requirement exactly one primary `DEL-*` and list cross-cutting dependencies separately.
6. Topologically order deliverables by actual input/output dependency, not presentation preference.
7. Complete Section 3 deliverable and implementation-owner columns.

### Decision table

| Test | Split when | Merge when |
|---|---|---|
| Independent acceptance | Either unit can be accepted/used without the other | Partial acceptance is meaningless |
| Writer context | Different writers/authorities/source contexts are required | Same writer must reason across shared invariant |
| Verification | Different oracles/invalidation domains decide them | The same check or observation necessarily decides combined behavior |
| Dependency | One consumes the other's stable output | Changes are mutually dependent inside one output |
| Cost | Combined context/repair becomes confusing | Separation repeats substantial setup/review/integration |

### Emit

- Section 5 deliverable table with `DEL-*`, behavior, requirements, dependencies, seams, release unit;
- completed Section 3 ownership/deliverable cells; and
- candidate graph dependency facts.

### Complete only when

- every requirement has one primary deliverable;
- every deliverable names one useful behavior and acceptance boundary;
- split/merge decisions pass the table rather than file-count intuition; and
- dependencies form an explainable acyclic production order or name a deliberate feedback boundary.

## 7. Pass 6 - Model risk, failure cases, and cost

Before committing to proof paths or modules, apply
[Acceptance design](../../acceptance-design.md) to each prospective acceptance
activity/equivalent family. Bind claim, observation and boundary, environment
necessity, distinct evidence from repetitions/combinations, and a simpler adequate
choice or concrete reason to retain the proposed design. Include material costs of
the acceptance system itself. This extends the existing owning proof/cost contract,
not a universal test architecture. Unresolved material justification returns to its
owning input/decision rather than becoming a large matrix by default.

### Inputs

- deliverables and seams from Pass 5;
- existing failure/baseline results from Pass 4;
- external/live-harm boundaries; and
- available checks, launch costs, context costs, and resource costs.

### Ordered actions

1. Examine S11 failure categories for each deliverable and mark each `SELECTED` or `OMITTED` with a
   concrete optional-category justification.
2. Select a failure case only when trigger is realistic, invariant is requirement-linked, a focused
   oracle exists, and missing it would create costly late repair, false acceptance, or live harm.
3. Record the earliest cheap decisive check and any downstream work that is genuinely dependent on
   its prerequisite. An ordinary failure does not cancel a separate feasible checking path; only a
   named dependency or R23 containment can do that.
4. Estimate duration range, context demand, coupling, external allocations, and failure impact.
5. Name the cheapest adequate topology in macro-module terms without selecting modules yet.
6. Write one concrete reason for every non-minimal candidate action.
7. For every candidate M03/M04/M07 verification path, record ROOT's concrete behavior/proof goal or,
   for an explicitly delegated lane-local path, the owning lane sub-orchestrator's concretization of
   that goal; record protected behavior, target surface, oracle property, acceptance strength, and
   review/check boundary. Leave review findings open, but do not leave test meaning or check-selection
   purpose for a worker to invent.

### Decision table

| Condition | Required decision |
|---|---|
| Cosmetic/speculative/unreachable/duplicate concern | Exclude; record it in the scope ledger only when a named downstream consumer needs that exclusion |
| Realistic seam failure with cheap early oracle and expensive late cost | Put in M02 failure brief candidate |
| Existing accepted result already covers failure under unchanged inputs | Reuse the result; do not add a check |
| Risk requires independent oracle | Mark M03/M04 candidate |
| Risk requires real external proof | Mark M08/M09 candidate |

### Emit

- Section 5 risk/cost table; and
- per-deliverable selected failure briefs with requirement, trigger, invariant, oracle, owner, and payoff.

### Complete only when

- every selected failure is realistic and oracle-backed;
- every expensive/non-minimal topology candidate has a payoff;
- expected ranges and critical resource costs are recorded; and
- no generic hardening checklist remains.
- every prospective test/review path has a ROOT-owned or explicitly delegated lane-local proof or
  bounded-investigation contract rather than an undeclared semantic choice for its executor.

## 8. Pass 7 - Select macro-modules

### Inputs

- deliverables, dependencies, acceptance claims, risk/cost rows, capability truth, and verification gaps;
- M01-M10 catalog and `module-recipes.md`; and
- existing accepted results.

### Ordered actions

1. For each deliverable, sketch the minimum typed path from prerequisite/product input to M05 decision.
2. Evaluate M01-M10 in numeric order using project facts and the catalog's strong, non-exhaustive
   application recommendations; examples are not eligibility gates and numeric order does not add edges.
3. Mark every module `SELECTED` or `OMITTED`; no third or unresolved decision state is permitted.
4. Assign one or more plan-local `MI-*` references to selected modules, one per independently configured
   deliverable, checking campaign, release unit, readiness rehearsal, or real attempt. Classify each
   occurrence into exactly one candidate step entry and name it `MI-NORMAL-*`, `MI-FL2-S1-*`, or
   `MI-FL2-S2-*` accordingly; never use an unclassified or cross-entry MI ID.
5. For each selected non-minimal instance, cite its Pass 6 payoff.
6. Resolve every selection-relevant missing fact, then make the binary decision. Do not defer it into
   the emitted package.
7. Confirm internal substeps remain inside their macro-module and have not become fake module rows.

### Decision table

| State | Required manifest content |
|---|---|
| Optional module adds useful behavior | `SELECTED`, `MI-*` references, concrete payoff |
| Optional module adds no useful behavior after project-specific evaluation | `OMITTED`, no instance ID, free-form justification |
| Required decision depends on an unresolved named fact | Return to the owning input pass, resolve it, then select or omit; never emit an unresolved state |
| Required behavior not expressible by M01-M09 | Evaluate M10 only after documenting attempted compositions |

### Emit

- the ten selection decisions assigned to their matching `modules/Mxx.md` owners;
- complete `plan-workflow.md` Section 6 fixed module index plus candidate step inventory; and
- instance inventory with type, owning M file, deliverable/release unit, and payoff.

### Complete only when

- all ten rows have one valid decision;
- every selected ID is unique and every omitted row has no instance;
- required coverage/verification/acceptance remains reachable; and
- no internal smoke/join/repair/cleanup/checkpoint substep was promoted to a top-level module.

## 9. Pass 8 - Define roles and bind the mapping

### Inputs

- selected instance inventory and module recipes;
- actual runtime role-resolution behavior and concurrency cap;
- user-selected concrete launch choices; and
- canonical mapping schema/path.

### Ordered actions

1. Enumerate executable responsibilities from each instance recipe.
2. Reuse one workflow role for responsibilities requiring the same authority/context class; split only
   when write authority, independence, or reasoning function differs.
3. Set role pool capacity one. Increase that ceiling only when named slices can run concurrently with
   disjoint mutable roots and saved wall time/coverage/isolation exceeds startup/join cost. M modules
   own the active member count within the declared capacity.
4. Define each role's authority class, reciprocal `Reports to`/`Directs` edges, responsibilities,
   context, write authority, resources, activation, logical-task lifetime, preferred invocation-reuse
   condition, and structured-handoff fallback. Declare exactly one ROOT. Use direct WORKER children by
   default; only the explicit R3 route may add direct LANE_SUB_ORCHESTRATOR children with terminal
   WORKER children.
5. Bind each role exactly once in the canonical mapping using the runtime's accepted schema.
6. Confirm plans/cards/graphs contain roles only and launcher resolves mapping at actual dispatch.
7. For every non-ROOT role, state whether it executes, reviews, checks, observes, or is an optional
   lane sub-orchestrator. Keep task-definition, scope-definition, success-definition, acceptance,
   correction classification, and next-edge authority away from worker roles. A selected lane
   sub-orchestrator may hold only the ROOT-declared local subset, must direct every worker in its lane,
   and may not create another orchestration tier. For review/audit roles, preserve open-ended finding
   discovery inside an exact owning-authority-assigned investigation boundary.

### Decision table

| Condition | Required decision |
|---|---|
| Runtime role resolver exists | Use it; unknown role rejects launch |
| Resolver missing but agent launches are selected | Select M01 resolver prerequisite |
| Candidate parallel slices share writer/root or require mutual output | Keep pool one/serialize |
| Slice independence and net benefit are proven | Increase pool within actual slot cap and define one join |
| Loop returns within unaccepted instance | Keep the same logical role/task and complete accumulated results; reuse the active invocation only when available and still selected, otherwise use an identified structured handoff |
| A proposed worker role must infer the problem, desired result, permitted scope, proof target, or acceptance boundary | Keep that authority with its owning orchestrator and require a complete dispatch card before activation |
| A proposed lane sub-orchestrator lacks a bounded outcome, named local authority, terminal ROOT handoff, or clear payoff | Use direct ROOT-to-worker dispatch instead |
| A reviewer must discover previously unknown defects | Give it open finding authority inside a fixed input/surface/invariant/materiality/output boundary; do not prescribe a conclusion or allow silent scope expansion |

### Emit

- `plan-workflow.md` Section 7 role table and role-resolution behavior; and
- sole canonical role-agent mapping with exactly the plan role keys.

### Complete only when

- plan role set equals mapping role set;
- concrete launch selection appears only in mapping;
- every pool-capacity ceiling has a reason and respects the runtime cap; and
- logical-task continuity, preferred invocation reuse, and structured-handoff behavior across loops are explicit.
- no worker role owns missing task semantics, acceptance, correction classification, or self-dispatch;
  any lane sub-orchestrator has only its declared local authority and review/audit discovery is open only
  inside its concrete assigned boundary; and
- the structured authority graph has exactly one ROOT, reciprocal edges, and either direct WORKER
  children or justified direct LANE_SUB_ORCHESTRATOR children whose children are terminal WORKER roles.

## 10. Pass 9 - Instantiate M modules and compose independent steps

### Inputs

- selected `MI-*` inventory, roles, deliverables, requirements, risks, capability facts, and module recipes;
- exact M-module file schema, step-file schema, governing-card schema, and internal member-card schema; and
- predecessor/successor candidates; and
- the owning orchestrator's per-instance dispatch facts: problem/activation fact, desired result, observable behavior or
  proof targets, target/protected scope, required/forbidden changes, authoritative inputs, mandatory
  checks, acceptance/tolerances, realistic pitfalls, outputs, stop/failure routes, and handoff owner.

### Ordered actions

1. Process M01-M10 in numeric order for file construction only; numeric order creates no runtime edge.
2. Fill each `modules/Mxx.md` contract, selection decision, stable public interface, rules/process,
   allowed variations, and configured-instance manifest from its catalog recipe and project facts.
3. Put every required recipe action exactly once and in order in the owning M file's action table.
   Specialize the reusable process without copying global policy or changing recipe invariants.
4. Apply the universal instance contract to every selected `MI-*`. Fill its 15 H4 subheadings (the MI
   H3 plus those fields are the 16 required schema headings), exactly one governing 20-field card, and
   one complete member card per internal worker dispatch in the matching M file. The governing card
   cites every module action in order; each member card cites only its applicable ordered subsequence.
   Bind concrete instance parameters without copying module-wide process prose.
5. Form the fewest coherent `STEP-*` boundaries justified by independently decidable gates and stable
   public inputs/outputs; never create a step for an internal action, file, role, or catalog position.
6. Under each step file's entry-flow heading, copy the execution template's canonical FAST_LANE_V2
   usage block exactly once and unchanged, then fill exactly three entry rows in order: `NORMAL`,
   `FAST_LANE_V2_SERIES_1`, and `FAST_LANE_V2_SERIES_2`. Build a distinct project-specific ordered
   path for every row and a union instance inventory. `NORMAL` may use any justified number
   and combination of `MI-NORMAL-*` instances. Series 1 uses only `MI-FL2-S1-*` instances and must be
   a materially narrower scoped-repair/smoke/review/integration exit; Series 2 uses only
   `MI-FL2-S2-*` instances and must be a materially narrower receive/join/invalidate/remaining-check
   continuation. These responsibilities are not a fixed module count or sequence. Fast paths should
   generally use fewer MIs, but purpose-built lighter work is the controlling rule. Give no MI ID to
   two rows, do not reuse or rename the normal broad campaign, and require complete configured paths
   for both fast-lane rows even while an activation predicate is false.
   Connect only compatible declared module interfaces and copy no module rules, actions, cards,
   reviewer/check counts, or concrete agents. Treat the canonical block as the one required immutable
   prose copy; do not paraphrase it into step-local policy.
7. Bind initial entrypoints, inputs, optional output/result path, consumer, correction routes, prior results,
   isolation, resources, cleanup, expected range, and terminal behavior.
8. Mark optional internal profiles/paths `SELECTED` or `OMITTED` in the owning M file; do not use `N/A`
   as a substitute for the binary decision.
9. Run the complete local recipe checklist for every instance and the exact step-schema/interface check
   for every step.
10. Read each executable member card's 20 fields as the worker would. Confirm its owning authority has supplied every material
   fact needed to execute without inventing task meaning or reconstructing history. For review/audit, confirm the
   frozen input, class, surface, governing requirements/invariants, watch areas, exclusions,
   materiality threshold, output, and handoff are fixed while the findings remain open.
11. Audit every specialized recipe verb. When an action says define/select/choose/classify/resolve/
   decide/authorize/continue/resume/start, bind the semantic decision to ROOT or its explicitly
   authorized lane-local owner and put only its exact mechanical execution or deterministic comparison
   in the worker card. For M03, bind behavior and oracle before test authoring; for M06, bind conflicts
   back to ROOT; for M07, preselect assurance paths; for M09, require separate ROOT authorization for
   any new attempt.

### Decision table

| Condition | Required decision |
|---|---|
| Recipe field applies | Fill concrete value; no vague phrase |
| Optional internal branch is not used | Record `OMITTED` plus a concrete free-form justification; keep the required recipe action |
| Needed behavior changes global graph/policy | Return to Pass 7/10/12; do not add it as a local module or step override |
| Needed behavior is absent from recipe/catalog | Re-evaluate M10; do not improvise heading/action |
| A material instance/card field is missing, contradictory, contains any `N/A` or placeholder, or is delegated to worker judgment | Keep the instance undispatchable; return the fact to its owning authority's pass and fill or resolve it |
| Review findings cannot be known before inspection | Leave the finding set open; concretely bound the input, surface, invariants, watch areas, exclusions, materiality, output, and handoff |
| Only an M-module's internal reviewer/check count or flow changes and its public/parameter contracts remain stable | Edit that `modules/Mxx.md` only, then rerun affected validation; steps inherit the change |
| An M-module interface, authority, semantic contract, or parameter contract changes | Update the M file and every actual step consumer; do not copy a compatibility shim into step prose |
| Only one step's internal MI composition changes while its public interface remains stable | Reorder or rewire existing MI references in that step only. For any added, removed, or reconfigured MI, also edit its owning M file, which owns the declaration; do not edit unrelated steps or the inter-step graph. |

### Emit

- exactly `modules/M01.md` through `modules/M10.md` with all selected instances in their owning file;
- one exact `steps/<STEP-ID>.md` per independently gated step, each with the three exact entry paths;
- typed module-instance, step, and public input-output inventories for graph composition.

### Complete only when

- every M file's decision and declared instance IDs match its contents;
- every module, instance, governing card, member card, and step passes its exact heading/table/task-field order;
- every recipe action appears exactly once in order in its owning M file, every governing card cites
  the full ordered list with concrete bindings, and every member card cites an applicable ordered
  subsequence; and
- all inputs/outputs/exits are concrete enough to connect without inference.
- no step copies M-module procedure, task cards, global policy, or concrete agent selection; and
- every internal worker has exactly one complete member card authored by ROOT or its explicitly authorized lane
  sub-orchestrator, and every review/audit card is a complete bounded-investigation contract that does
  not prescribe its conclusion.

## 11. Pass 10 - Compose the typed graph

### Inputs

- all instance input/output inventories;
- deliverable dependency order;
- authority/resource boundaries; and
- module-instance and step-local correction outputs/routes.

### Ordered actions

1. Create an intra-step module connection or inter-step edge only when one declared output exactly
   satisfies one declared input.
2. Record intra-step order/conditions separately for all three owning step entry paths and assign `EDGE-*`, condition,
   serial/parallel type, join, and failure branch to every inter-step edge.
3. Group independent same-input checking paths inside M04/M07 into `PG-*`; singleton paths have no split.
4. Create joins only for actual fan-outs or multiple accepted inputs.
5. Add M05 correction returns to the same M02/M03/administrative logical role/task and affected
   checking path. Reuse the active invocation only when available and still selected; otherwise bind
   a structured handoff before the earliest failed, unresolved, change-affected, or uncertain
   action/check.
6. Add external authorization and terminal edges only when M08/M09/M06/M07 are selected.
7. For each failure, remove only successor edges that consume the failed fact and mark every other
   satisfied successor default-forward.
8. Bind every continuation to the earliest failed, unresolved, change-affected, or uncertain
   action/check and preserve predecessor outputs and green credit whose inputs remain unchanged.
9. Trace every selected instance through exactly one owning step, and every step from an activation
   source to a consumer or explicit terminal.

### Decision table

| Condition | Edge type |
|---|---|
| Consumer requires predecessor output | Serial |
| Consumers share frozen input and neither consumes peer output | Parallel group |
| Branch chosen by named result/verdict | Conditional |
| Accepted finding returns to same unaccepted task | Repair return |
| Output has no consumer and is intentionally terminal | Terminal; explain why |
| Support/admin/readiness fault does not feed a successor | Keep that successor active; do not add a wait edge |

### Emit

- `plan-workflow.md` Section 8 inter-step edge and parallel-group tables;
- graph-derived activation/failure/successor fields in each owning step's normal, Series 1, and Series
  2 compositions and M instances;
  and
- cross-references ready for `plan-workflow.md` Sections 10-13.

### Complete only when

- every edge connects declared types, every selected instance belongs to exactly one reachable step,
  and every step is reachable;
- every fan-out joins or proves independent terminal outputs;
- no catalog-order, presentation-order, or singleton fake split creates an edge; and
- correction returns preserve the same logical role/task, complete finding pool, first unresolved
  action, earliest required execution unit, and every non-consuming successor. They either reuse the
  still-selected active invocation or record the structured handoff to its replacement.

## 12. Pass 11 - Size gates and repair loops

### Inputs

- composed graph, M04/M05/M07 result boundaries, risks/costs, change domains, and role contexts;
- candidate acceptance/authorization/integration decisions; and
- S16 aggregation/manageability rules.

### Ordered actions

1. Identify every graph point that decides product advancement or blocks an exact operation/resource.
   Do not promote advisory or administrative bookkeeping into a gate.
2. Classify each candidate as `PRODUCT` or `OPERATION_BOUNDARY` from the fact a failure disproves. Do
   not infer PRODUCT merely because the operation is required for overall completion.
3. State one independently decidable behavioral or operation-boundary question per candidate `GATE-*`.
4. List shared input, checking paths, shared failure family, exact blocking scope, default-forward edge,
   repair owner/context, and affected prior results.
5. For a `PRODUCT` gate, name the required product criterion whose failed/undecidable state alone permits
   a loop. For an `OPERATION_BOUNDARY`, forbid product repair and name the exact operation it may hold.
6. Bind continuation to the earliest failed, unresolved, change-affected, or uncertain action/check
   and enumerate preserved completed work/green credit whose inputs remain unchanged.
7. Apply aggregation test and record saved repeated context/setup/launch/review/check/integration cost.
8. Apply manageability test and prove one owning orchestrator can triage one pool and one writer can own return; a lane sub-orchestrator may do so only within its declared lane.
9. Split/merge candidates according to the decision table; update graph edges/instances, then retest.
10. Define prospective split/merge trigger from observed findings without changing accepted history.

### Decision table

| Aggregation | Manageability | Required boundary |
|---|---|---|
| Pass | Pass | Merge/retain one gate and explain why not smaller/larger |
| Fail | Pass or fail | Split; grouping saves no meaningful repeated cost |
| Pass | Fail | Split at behavior/mechanism/authority/writer/context/invalidation boundary |
| Uncertain | Uncertain | Split at smallest independently acceptable behavior |

| Gate condition | Required class and route |
|---|---|
| Required product criterion failed or its only required proof is genuinely undecidable | `PRODUCT`; exact affected outcome may block and one coherent product loop may be eligible |
| Authority, readiness, containment, cleanup, or required resource targeting prevents one operation | `OPERATION_BOUNDARY`; hold only that operation and advance every independent edge |
| Required allocation, integration-coordinate mutation, deployment, promotion, readback, cleanup, or retirement is incomplete while accepted behavior remains intact | `OPERATION_BOUNDARY`; continue only that exact operation from its first unresolved action or stop it, preserving all accepted product credit |
| Administrative/support artifact is faulty but required product facts are independently decidable | No blocking gate/loop; record error and take default-forward product edge |

### Emit

- Section 8 gate/loop manifest; and
- updated graph/instance return edges plus Section 5 rationale references.

### Complete only when

- every gate has one class, question, exact blocking scope, loop eligibility, default-forward edge,
  return/block target, and passes both tests;
- no required operation is mislabeled PRODUCT merely because terminal completion consumes it;
- a product failure yields one coherent complete pool and same-task return, while a non-product fault
  cannot enter that return;
- unrelated accepted credit has a separate invalidation boundary; and
- no arbitrary file/module/finding/iteration count sizes the gate.

## 13. Pass 12 - Compile policies and exceptions

### Inputs

- R1-R30, S1-S17, selected graph, gates, roles, result/correction routes, resources, and lifecycle;
- fixed P01-P15 headings; and
- discovered exceptional conditions only.

### Ordered actions

1. For each P01-P15, identify consuming `MI-*` IDs and governing R/S rules.
2. Write owner, exact trigger, mandatory action, exit, optional result/record location, and module IDs.
3. Remove duplicated policy prose from steps, M modules, and cards and replace it with policy IDs.
4. For each real alternate route, create `EXC-*` with affected policy, trigger, owner, action, required confirmation,
   preserved/invalidated credit, scope, and expiry.
5. Reject exceptions that merely make an ordinary route vague or bypass acceptance/authority.
6. Make P02 state that the role/card/results stay continuous inside one unaccepted logical task,
   persistent invocation reuse is preferred rather than mandatory, and a user-directed allocation
   change or unavailable resume uses identified structured handoff without invalidating credit.
   Apply the shared [worker recovery reference](../../worker-continuity-and-recovery.md): P02 must
   name runtime result validation, verified resume identities, two same-thread correction attempts
   after the initial missing/malformed result even without first-attempt progress, measurable
   progress/stall criteria, exact owned cleanup, and fresh/split same-role recovery. P09 must keep
   report-only correction separate from product repair and block only exact consumers. A completed
   card may end while its thread remains reusable for a new correction card; a missing report is
   itself enough to classify and dispatch that correction. Preserve current role selection and
   independent-review boundaries; malformed results alone never qualify fallback. Make
   recurring permission/configuration failures route once to the authoritative configuration owner
   with a disposable exact-tool-action/readiness/output/cleanup proof. Require a shared native
   result emitter/preflight when observed handoff errors justify it, with worker-authored semantics
   and invocation-derived identities. Replacement cards retain discovery and state what changed
   after nonprogress. Make
   P04/P07/P08/P09/P10/P11/P12/P13 state that non-product faults block only exact consumers, satisfied
   successors advance immediately, product continuation needs a failed/undecidable required criterion,
   and any continuation executes from the earliest failed, unresolved, change-affected, or uncertain
   action/check with unaffected credit preserved. P08 must return a failed strict-test correction/rerun
   to classification; it must not promote that failure to material repair unless a failed or undecidable
   product criterion satisfies the product-loop rule. For selected checkpointed work, make P04/P11/P12
   state check units, conservative inputs, reuse and uncertain-rerun rules, the earliest-required
   execution unit, ordinary-failure continuation, and—where M09 is stateful—the consumed
   target/resource state. Make P07 batch compatible material findings before another assurance run.
   Make P04/P07 define the always-present STEP fast-lane contract: Series 1 requires the complete
   feasible source pool, a scoped correction objective, distinct narrow `MI-FL2-S1-*` path, repaired-output exit,
   and preserved compile/motivating-test smoke credit; Series 2 binds the ROOT-selected current
   progress bound, joins accepted exits through a distinct narrow `MI-FL2-S2-*` path, calculates
   invalidation, and resumes only the earliest
   required remaining units. Require each fast-lane series to name saved work and reject a renamed
   normal broad path.
7. Make P02/P04/P09 apply the discovered bounded-command policy only to manifest-selected finite
   commands. Require policy-bearing prompts/cards, realistically calibrated expected upper bound,
   bounded cleanup allowance, computed lifetime and heartbeat, supervisor-owned deadline/cleanup,
   available hook enforcement, durable terminal result, and support classification for timeout. State
   that agent/subagent sessions and their launch wrappers remain unbounded. If a selected command has no
   architecture, route its smallest implementation through M01.
8. Search local executable prose for banned vague phrases and replace each with a decision rule.
9. Make P01/P02 state that ROOT authors the complete problem, desired result, required behavior/proof,
   target/protected scope, required/forbidden changes, inputs, checks, acceptance/tolerances, pitfalls,
   stop/failure routes, and next handoff before direct-worker dispatch. A selected lane sub-orchestrator
   must provide the same complete contract to workers in its declared lane. Workers execute inside that
   contract, return material omissions/contradictions, terminate at their owning authority's decision
   boundaries, and never self-dispatch. Reviews/audits retain open finding discovery only inside the
   stated bounded-investigation contract.

### Decision table

| Condition | Required decision |
|---|---|
| Behavior applies across modules | Define once in P01-P15; modules cite it |
| Behavior is M-module-specific within global rules | Keep in the owning `modules/Mxx.md`; steps cite its MI interface |
| Alternate path has concrete known trigger | Predeclare `EXC-*` |
| Alternate path is unforeseen | Plan amendment or `INCOMPLETE`; no local improvisation |
| New fault fits an existing material/test/admin/readiness/live-harm classification | Use ordinary policy; no exception or amendment |

### Emit

- complete `global-rules.md` Section 9 P01-P15 policy blocks and exception table; and
- policy/exception citations in every consuming step, M module, and card.

### Complete only when

- every policy has all six fields and named consumers;
- P02/P09 cover the shared worker recovery reference's semantic cases using inspected runtime
  capabilities, with accepted progress preserved and no unbounded replacement cycle;
- every policy has a concrete mapped owner, trigger, mandatory action, and exit; `P04` itself owns the
  checkpoint/FAST_LANE_V2 protocol and `P07` itself owns complete-pool and Series 1/2 join behavior;
- every exception has all ten fields and bounded expiry;
- no duplicated/conflicting policy exists locally; and
- mandatory behavior uses unambiguous language.
- ROOT's task-definition authority, any explicitly delegated lane-local authority, and the worker
  execution boundary are explicit for ordinary work and for the bounded review/audit discovery exception.

## 14. Pass 13 - Compile lanes, resources, results, and lifecycle

### Inputs

- graph, roles, module-instance cards, source/runtime facts, checks, resources, optional durable results, and cleanup rules.

### Ordered actions

1. Create one `LANE-*` per real executable role invocation; decision-only deterministic local actions may
   have no agent lane when the runtime executes them directly.
2. Create `LOCK-*` only for actual contested resource ownership.
3. Create check rows for selected deterministic checks. Use a `CHECK-*` reference, registry key, or
   dependency fingerprint only when cross-reference, selection, or pass-credit reuse actually consumes it.
4. Create a mandatory `HANDOFF-*` row for every handoff. Create a `RESULT-*` reference only for a
   durable cross-role result that has a named consumer.
5. Create `ALLOC-*` rows using cheapest safe source mode from Pass 4.
6. Create `RETIRE-*` rows for terminal source/resource state that really needs closure.
7. Bind each row to owner, activation, mutable root, consumer, completion, and failure route.
8. Cross-check graph/step/module-instance IDs and shared-writer locking/isolation.

Because every selected executable `MI-*` has at least one member dispatch, the lane and handoff tables
always contain concrete reciprocal rows. Their `N/A` sentinel is forbidden. The other allowlisted
Section 10 category tables remain optional when that category truly has no item.

### Decision table

| Need | Required representation |
|---|---|
| Agent invocation | Lane row |
| Exclusive/shared mutable resource | Claim/lock row |
| Selected deterministic check | Check row; a `CHECK-*` label only when referenced or consumed |
| Handoff | Handoff row with a mandatory `HANDOFF-*` ID |
| Cross-owner durable fact that is not a handoff | `RESULT-*` row only when a consumer needs durability |
| Source read/write isolation | Source allocation row |
| Terminal lane/resource cleanup | Retirement row |
| Allowlisted optional claim/lock, check, source-allocation, or retirement category has no items | One explained no-item sentinel row in that table; no invented machinery |

### Emit

- all six `plan-workflow.md` Section 10 manifests; and
- lane/resource/result references consumed by the graph, steps, modules, and cards.

### Complete only when

- every orchestrator/agent/subagent process or invocation, handoff, lane, claim/lock, and Git worktree
  has the mandatory runtime ID needed to correlate its row; every selected check, required durable
  result, source allocation, and retirement action has exactly one row or optional plan-local reference
  as the table requires;
- every member card names one unique concrete lane and terminal handoff with reciprocal Section 10 rows;
- concurrent writes are disjoint or correctly locked;
- every row has activation, completion, and failure behavior; and
- cleanup preserves live/dirty/unretained state and recovery visibility.

## 15. Pass 14 - Compile external, integration, and terminal behavior

For selected external profiles/attempts, consume Pass 6's recorded necessity and
multiplicity rationale. Requiring real proof of a claim does not select every
profile/feature/environment combination. Each material distinction or repeated
measurement must serve the accepted claim or binding requirement; do not replace
required external evidence with synthetic credit or impose a universal canary cap.

### Inputs

- selected M06-M09 instances, graph, authority, resources, readiness inputs, release units,
  accepted inputs, required rollback state, and cleanup ownership.

### Ordered actions

1. For M08/M09, fill Section 12 rows for selected profiles/attempts and a free-form omission
   justification for unselected optional readiness/practical behavior.
2. Separate synthetic readiness results from real external acceptance results.
3. For M06/M07, fill Section 13 rows with accepted input, ordered action, checks, promotion/rollback/
   retirement coordinate, and owner.
4. Verify all real external actions have exact authorization and all integration/promotion inputs have
   M05 acceptance.
5. Verify stop, cleanup, rollback, and any required terminal result paths match module recipes and graph.
6. Do not add a universal final phase; render only selected module behavior.
7. Confirm ROOT made every integration-input/order, conflict, audit/safeguard selection, real-attempt,
   retry/new-attempt, promotion, rollback, and acceptance decision before its executor card. Encode
   only predeclared mechanical branches in worker actions; route every undeclared choice back to ROOT.

### Decision table

| Selected module/profile | Required section treatment |
|---|---|
| M08 readiness | Section 12 synthetic proof; explicitly not product pass |
| M09 real validation | Section 12 real result, observation, authorization, cleanup |
| M06 integration/promotion | Section 13 accepted inputs, order, affected checks, rollback |
| M07 final assurance | Section 13 release unit, selected final paths, M05 handoff |
| No optional external/integration item exists | One explained no-item sentinel row in the owning allowlisted table |

### Emit

- complete Sections 12 and 13; and
- final external/integration/terminal cross-references.

### Complete only when

- synthetic and real proof are never conflated;
- every external/integration action is authorized and uses only the runtime/resource IDs needed for safe targeting;
- rollback/cleanup/retirement are concrete; and
- omitted macro-modules do not reappear as hidden final steps.
- no integration, assurance, readiness, or practical executor receives semantic selection, conflict,
  retry/new-attempt, acceptance, or next-edge authority.

## 16. Pass 15 - Price and simplify the graph

Price and challenge the acceptance design as well as delivery coordination. Where
material, include construction, operation, cleanup, maintenance, interpretation/
repair and rerun dependencies. Compare a simpler adequate alternative, or justify
why the existing checks already suffice without extra machinery. Preserve required
claims and genuinely invalidated reruns. Record the decision in existing cost/proof
fields for TOPOLOGY_SIMPLICITY, VERIFICATION and EXECUTION_RESOURCES to inspect;
elapsed runtime or matrix cardinality alone does not decide proportionality.

### Inputs

- complete draft graph/modules/lanes/gates/resources; and
- Section 5 cheapest adequate topology, duration ranges, and payoffs.

### Ordered actions

1. Sum serial expected ranges along every terminal path and identify critical path.
2. Record overlap for parallel groups; never subtract time for work that is not actually concurrent.
3. Count launches, context loads, expensive gates, external allocations, joins, integrations, and full
   safeguards.
4. For each node/edge/artifact/isolation/fan-out, cite required correctness/safety or net wall-time payoff.
5. Remove every wait, correction, or loop whose only purpose is a non-product artifact after product
   acceptance is independently decidable; retain only an exact dependent-operation block when needed.
   Treat a failed strict-test fast lane as new result to classify, not automatic product repair.
6. Remove every other item without sufficient payoff and reconnect typed/default-forward edges.
7. Re-run coverage, authority, live-harm, acceptance, isolation, gate, and invalidation checks.
8. Update only the authoritative affected package artifacts and actual interface/graph consumers; do
   not leave stale step/module/edge/lane references or duplicate the change into unrelated files.

### Decision table

| Finding | Required decision |
|---|---|
| Duplicate internal substep represented as module | Fold into owning macro-module |
| Serial edge has no consumed output/authority dependency | Remove/parallelize as allowed |
| Fan-out cost exceeds saved wall time/coverage/isolation | Reduce pool or serialize |
| Artifact has no independent consumer/decision value | Remove it |
| Non-product fault has no direct consumer on a ready product edge | Record it and advance that edge |
| Removal would lose required behavior/verification/containment | Keep and cite requirement/risk |

### Emit

- `plan-workflow.md` Section 8 critical-path table and updated ranges;
- finalized `plan-workflow.md` Section 5 topology reasons; and
- simplified, reference-consistent package across the owning artifacts for Sections 6-14.

### Complete only when

- every non-minimal structure earns its cost;
- critical path and expensive operation count are explicit;
- no stale reference remains after simplification; and
- all requirements and correctness/safety boundaries remain covered.

## 17. Pass 16 - Fill, cross-check, and validate

Dispatch each group with the [review assignment](../../../assets/plan-review-assignment.md),
its raw authority sources, frozen candidate and acceptance surfaces. Require actual
necessity/multiplicity judgments from VERIFICATION, governing-claim traceability
from SCOPE_AUTHORITY, and structure/cost proportionality from TOPOLOGY_SIMPLICITY
and EXECUTION_RESOURCES. Record their three assessments or specific reviewed-family
references in every Section 16 per-STEP audit row, covering all entry paths. An
unjustified acceptance design remains BLOCK despite complete V rows. Missing,
pending or bare verdict-only assessment cells fail structural validation; populated
cells still require semantic review. No new module or fixed STEP/card field is added.

First include [adversarial plan conformance](../../plan-conformance-review.md) in
the four-group independent panel. Compare the original request and authorizations
with the complete plan, not just the verification inventory. Challenge unsupported
outcomes/stages, unnecessary coordination, invalid lane splits, applicable skill
rules, material verification costs and any path from planning into unauthorized
execution. Resolve material findings and record the final Plan review verdict in
the existing audit metadata before claiming PLAN_STRUCTURE=VALID. Keep the formal
schema intact; a valid graph for an inflated outcome is not an acceptable plan.

For substantial matrices priced in Pass 15, include the
[matrix execution contract](../../matrix-execution.md) in EXECUTION_RESOURCES review:
actual runner/control binding, isolation and concurrency, dependency graph,
incompatible terminal exits, complete result collection, cause-group repair,
affected reruns, and coordinate/total wall-clock budgets. Reject unnecessary
serialization, long terminal waits and repair-after-each-test loops. Check these
semantics in existing owning fields; structural validation does not prove runner
capabilities or scheduling efficiency.

Before this pass can complete, apply the independent
[test-scope audit](../../test-scope-audit.md) to the suites and matrices priced in
Pass 15, including every STEP's normal and repair-entry selections and cross-step
duplication. The same frozen draft package is input to all four reviewers. Keep
one writer, collect the independent group findings, update owning selections, and
obtain the bounded focused follow-ups or unchanged-scope confirmations prescribed
by the reference. All four reviewers must approve the final revision; ROOT cannot
override BLOCK and accepts only mutually consistent approvals. Record metadata,
group approvals and per-STEP coverage in the three Section 16 audit tables before claiming PLAN_STRUCTURE=VALID. A missing review or
unresolved material coverage issue leaves the package incomplete even if its other
V checks pass. This bounded planning review is the explicit exception to the
prohibition on launching the authored workflow; it adds no execution module.

### Inputs

- completed outputs of Passes 1-15;
- exact execution-package templates and artifact architecture;
- role-agent mapping; and
- validator plus V01-V30 definitions.

### Ordered actions

1. Fill `plan-workflow.md`, `global-rules.md`, every `steps/STEP-*.md`, exactly `modules/M01.md`
   through `modules/M10.md`, and `validation.md` from their owning pass outputs; replace every token
   and delete template notes.
2. Populate `validation.md` Section 15 by locating actual behavior for R1-R30/S1-S17 in its one
   authoritative artifact; never cite a missing behavior or duplicated proxy, and never use `N/A`
   for a normative R/S rule.
3. Evaluate V01-V30 in `validation.md` and record one-line project basis for each; no additional
   evidence artifact is required.
4. If any check fails, set `PLAN_STRUCTURE=INVALID`, return to the owning pass, fix the authoritative
   artifact and actual interface/graph consumers, and reevaluate affected/downstream checks.
5. When all manual checks pass, set `PLAN_STRUCTURE=VALID` and run the packaged validator on the
   package directory with the isolated mapping.
6. Fix every validator error at its owning pass; never edit validator or insert dummy rows for a pass.
7. Rerun manual affected checks and validator until both pass on final bytes.
8. As part of V10/V13/V14/V27, inspect every worker card semantically. Reject any card that leaves a
   material problem, goal, desired result, target/protected scope, proof, pitfall, success criterion,
   or next-edge decision for the worker to invent. For review/audit, reject both an unbounded inquiry
   and a card that prescribes the conclusion.
9. Search every worker-facing specialized action for semantic choice verbs and prove each is either a
   ROOT-owned pre-dispatch decision, an explicitly delegated lane-local decision, or a deterministic
   application of owning-authority-supplied criteria. Check
   M02 failure/proof targets, M03 scenario/oracle meaning, M04 cancellation/check selection, M06
   conflicts, M07 assurance-path selection, M08 readiness-profile selection, M09 new attempts, and
   any worker-executable portion of M10 explicitly.
10. Confirm M05 is selected, every configured `MI-*` has one governing and at least one member card,
     its `Owner and roles` inventory equals the member-card/role set, every instance/card field is
     concrete without `N/A`, every member card has reciprocal concrete lane and terminal-handoff rows,
     every STEP has exactly one concrete indexed gate, final status is `VALIDATED`, every required
     outcome/REQ is `COVERED`, every REQ/DEL is covered by a STEP, no known schema table is duplicated,
     and both fast-lane paths are explicit configured MI lists with no opt-out language in any entry or
     configured MI contract.
11. Treat authored PASS cells as assertions, not proof: every V basis must name the concrete artifact
    behavior inspected, and every mapping role must contain a nonempty runtime launch-selection field.

### Decision table

| Condition | Required decision |
|---|---|
| Unresolved template token/note | Return to owning pass; plan invalid |
| Rule maps to citation but behavior contradicts rule | Fix behavior; citation is not credit |
| Deterministic shape passes but semantic check fails | Plan invalid; fix semantics |
| Semantic checks pass but validator fails | Fix structure/cross-reference and reevaluate affected semantics |
| All V rows PASS and validator exits zero | Plan may be reported complete |

### Emit

- final modular execution package whose `validation.md` ends `PLAN_STRUCTURE=VALID`;
- canonical role-agent mapping; and
- validator pass output for handoff report.

### Complete only when

- exact package artifacts, owning sections, block/module schemas, and task-card schemas are populated;
- mapping roles equal executable module-instance roles and the mapping path appears once in the composition root;
- V01-V30 all say PASS with a substantive artifact-specific basis;
- validator prints `execution plan validation: PASS`; and
- final report does not execute or launch the authored workflow.
- every executable card passes the dispatch-authority contract audit, including the bounded
  open-finding rules for review/audit cards.
