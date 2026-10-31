# Macro-Module Recipes

These recipes define the complete semantic contract of each selectable macro-module. The plan compiler
decides which M modules are selected, how configured `MI-NORMAL-*`, `MI-FL2-S1-*`, and `MI-FL2-S2-*`
occurrences form the distinct `NORMAL`, `FAST_LANE_V2_SERIES_1`, and `FAST_LANE_V2_SERIES_2` paths
inside independent `STEP-*` boundaries,
and how typed step outputs connect. Once a module is selected, its recipe is mandatory; do not
extract its internal substeps into extra top-level modules or silently omit them.

## Contents

1. Universal instance contract
2. M01 - Prerequisite and admission closure
3. M02 - Product implementation and repair tranche
4. M03 - Independent verification asset construction
5. M04 - Review and checking campaign
6. M05 - Adjudication, acceptance, and correction routing
7. M06 - Integration and release assembly
8. M07 - Accumulated final assurance
9. M08 - Expensive or external readiness proof
10. M09 - Practical or external validation
11. M10 - Project extension
12. Local recipe validation

## 1. Universal instance contract

Under [normalized authoring](normalized-authoring.md), reusable recipe definitions
and permitted defaults belong to the module library; configured instances, their
bindings and local dispatch lifecycle belong to their owning step. A change for
one instance must not alter the shared recipe for unrelated consumers. The compiler
expands inherited fields into the complete concrete governing/member cards required
below and derives their inventories. Inheritance cannot omit required actions,
weaken authority or leave a worker to decide missing task meaning. Change a shared
recipe only when the intended behavior really changes for its actual consumers.

Every substantial post-step checking matrix implements
[Matrix execution](../../matrix-execution.md) through existing actions/cards:
M03 defines the coordinate oracles and terminal predicates; M04/M07/M09 run ready
independent coordinates concurrently with isolated resources, honor explicit graph
edges, exit incompatible terminal waits and collect all feasible results before
repair. M08, when selected, proves changed fragile controls. M05 groups failures by
evidenced cause, assigns one coherent repair per group and selects only invalidated
coordinates/dependents for rerun, preserving compatible credit. Bind per-coordinate
and total budgets and have EXECUTION_RESOURCES reject unnecessary serial
execution, terminal-state waits and per-test repair loops. An ordinary coordinate
failure does not invoke M09-A7's whole-attempt stop authority; R23 still controls
unsafe stops. No new action IDs, modules or policy definitions are introduced.

Compile the accepted [test-scope audit](../../test-scope-audit.md) into existing
owning actions: M03 materializes the accepted scenario/oracle families; M04 and
M07 consume justified check/review selections; M08 verifies new or changed concrete
controls through their executable decision/cleanup boundary before expensive use;
M09 executes only the authorized matrix. ROOT's M05 decisions separate product
correctness, provider compatibility and control validity. Workers return a proposed
new scope or stronger oracle to ROOT instead of silently enlarging the campaign.
This supplements the recipes below without removing any required action, review,
readiness or acceptance obligation, and does not add a scope audit at every runtime
gate. Changed evidence scope is reviewed only for the affected delta.

Carry the reviewed [acceptance design](../../acceptance-design.md) into existing
actions/cards. M03-A2 translates the accepted claim, boundary, environment and
repetition rationale; M03-A6 checks authored observations against it. M04/M07/M09
consume the justified selection, not an automatically expanded cross-product.
When M08 is selected, its readiness result covers only the boundary actually proved.
M05 distinguishes product evidence from invalid setup/measurement and maps actual
changed dependencies before retaining credit or selecting reruns. A material change
to the evidence method/scope or costly dependency goes to the owning authority and
affected planning-review groups before dependent expensive execution. Keep this a
focused delta check in existing stages; do not add a panel at every test or force
fixture determinism, external probes, new harness layers or component splits.

Apply [execution efficiency](../../execution-efficiency.md) to applicable actions:
M03-A2/A5 map changed controls to executable tests; M05-A3/A7 compare contract,
observation and oracle and preserve compatible repair groups; M08 rehearses
changed control branches and queue recovery; M09 binds command advancement,
checkpoint reconciliation and terminal publication. Keep cross-cutting supervision,
native-error diagnosis and administrative recovery in their owning P policies.
Specialize these obligations inside existing actions/cards, not extra MIs.

Every selected `MI-*` instance uses this local compilation sequence:

1. **Bind the work.** Name module type, owning step entry path (`NORMAL`,
   `FAST_LANE_V2_SERIES_1`, or `FAST_LANE_V2_SERIES_2`) and enforce its corresponding
   `MI-NORMAL-*`, `MI-FL2-S1-*`, or `MI-FL2-S2-*` instance prefix. Then name the deliverable/release
   unit, gate/loop references, owner, roles,
   and inputs. Include mandatory IDs for every orchestrator/agent/subagent process or process tree,
   provider invocation/session/thread, handoff, lane, claim/lock, and Git worktree. Include another
   live-resource ID only when targeting or lifecycle control requires it. Include a source revision
   only when the operation must target or preserve that revision. Do not turn plan-local references
   or ordinary content into runtime identities.
2. **Bind activation.** Name the exact predecessor output and predicate that make the instance ready.
   `The prior module finished` is insufficient; cite its output and required state.
3. **Bind inputs.** List only consumed paths, revisions when required, facts, accepted prior results,
   authority, resources, and changed-input domains. Do not add identity checks to ordinary content.
4. **Bind local actions.** Put every `<module>-A<number>` action reference exactly once, in order, in
   the owning `modules/Mxx.md` action/process table; specialize the reusable process without changing
   action order or decision owners. Each selected `MI-*` has one governing 20-field card that cites
   every recipe action in order and binds project-specific nouns, paths, inputs, and allowed parameters
   instead of copying the module-wide process. Add one complete member card per internal worker
   dispatch; each member cites only its applicable ordered recipe-action subsequence. Member cards are
   module-private dispatch contracts, not additional `MI-*` components or step entries. Every selected
   instance is executable, has at least one member card, and uses concrete values in every instance and
   task-card field; `N/A` is forbidden there. Its `Owner and roles` field inventories every member
   dispatch exactly once as `CARD-ID=workflow_role` and must agree with the member cards.
   If an internal profile is optional and omitted, retain its required action ID and record
   `OMITTED` plus a concrete free-form justification; never mark the action `N/A`.
   Only a local action that invokes a manifest-selected finite command must use the plan-adopted
   bounded-execution architecture with its realistically calibrated expected upper bound, bounded
   cleanup allowance, computed lifetime/basis, heartbeat, terminal result, and timeout route. Agent and
   nested-subagent sessions remain unbounded; their task card and prompt carry the command policy only
   when they are instructed to invoke a selected finite command.
5. **Bind outputs.** Name outputs, optional durable result path, required fields, publication rule,
   accepting consumer, and exact condition under which the output exists. The producing runtime
   instance already has its mandatory ID; add no separate output/result ID unless a consumer needs a
   durable result reference.
6. **Bind corrections.** Name every possible classified exit and its already-declared graph target.
   A module may not invent a repair route while running.
7. **Bind terminal behavior.** Name success, incomplete, unrecoverable, stall, cleanup, retirement,
   and retained-result conditions. Accepted work cannot be reopened by an unrelated later task.
8. **Bind cost.** State expected range, launches, parallel overlap, expensive actions, and critical-path
   effect. A non-minimal local action must point to its payoff in Section 5.

Every instance is default-forward: once its typed output satisfies a successor input, activate that
successor without waiting for unrelated support/admin cleanup. A fault may hold only the exact
consumer named in its failure route. Every continuation starts at the first unresolved recipe action
when no earlier action/check was invalidated; otherwise it starts at the earliest failed, unresolved,
change-affected, or uncertain action/check. It preserves completed actions, needed results, and
unaffected passing work.

Each M01-M10 file owns its ingredient's public interface, reusable rules/process, recipe actions,
variation contract, and configured instances. Each `MI-*` owns its eight instance-level bindings,
one complete governing task card, and every complete internal member task card. One MI occurrence is
owned by exactly one of its step's three entry paths, and its prefix must identify that path. A
`STEP-*` file only orders and connects those configured ingredients through
their interfaces. Global rules and concrete role-agent selections remain in their own authoritative
artifacts. An internal M-module edit therefore stays in that M file when its public interface,
authority, semantic contract, and parameter contract remain unchanged; every consuming step inherits
the edit. A real interface or meaning change updates its actual step consumers.

The same instance keeps the same functional role and logical task across its own correction loop. The
producer stays the producer; each reviewer/check/observer assignment stays on its declared surface.
Reuse its active invocation where it remains available and the current mapping and user direction
still select it, but never make persistence mandatory. If the user changes subagent/provider/allocation,
the invocation is unavailable, or the runtime cannot resume it, dispatch a new invocation for the same
workflow role with the same concrete task card, first unresolved action, working source, accepted state, and
complete accumulated results. Record the prior/new invocation IDs and handoff ID because runtime
correlation requires them.
Do not silently replace a role, re-partition a surface, restart completed work, or change task meaning
on a loop return.

ROOT/orchestrator authors the complete execution meaning before every direct-worker dispatch.
Each member card, read with its governing instance contract, must give a non-review worker the concrete
problem/activation fact, objective and desired result, observable behaviors or proof targets, exact
target surfaces and entrypoints, permitted and protected scope, required and forbidden changes,
authoritative inputs and prior results, mandatory checks, acceptance/tolerances, realistic task-specific
pitfalls, outputs, failure/stop routes, and handoff owner. When R3 explicitly justifies the optional
two-orchestrator-tier topology, ROOT first authors the lane sub-orchestrator's bounded contract; that direct
sub-orchestrator authors this same complete contract for every worker in its lane. The worker owns
implementation mechanics inside those bounds; it does not own task definition, scope definition,
success definition, acceptance, correction classification, or the next graph edge. A material omission
or contradiction is an `INCOMPLETE` result to its owning authority, not permission to reconstruct
history, infer hidden requirements, widen the work, or self-dispatch.

A reviewer or auditor receives a bounded-investigation variant of the same contract. The owning
orchestration authority fixes the frozen input, review class, conceptual/product surface, governing
requirements and invariants, risk hypotheses or pitfalls to examine, exclusions and protected
boundaries, severity/materiality threshold, required output shape, completion condition, and handoff.
It does not prescribe the conclusion. The reviewer may discover new in-boundary problems and inspect
the minimum adjacent code needed to understand or substantiate them, recording why; it may recommend a
separately authorized expansion but may not silently broaden the task or edit the product.

Apply this authority interpretation to every recipe below. When a worker-facing action says
`define`, `select`, `choose`, `classify`, `resolve`, `decide`, `authorize`, `continue`, `resume`, or
`start`, the worker may only materialize or mechanically apply a target, rule, branch, or procedure
that the owning authority already supplied in the card. The verb does not transfer semantic authority.
A new behavioral choice, test meaning, oracle, repair objective, nontrivial conflict, external attempt,
scope expansion, acceptance decision, or graph edge terminates the worker card and returns to its owner;
anything outside a lane's declared boundary returns to ROOT. Review and audit retain independent
finding judgment inside their exact assigned boundary, but no other independent task-definition or
routing authority.

An instance is locally complete only when all eight bindings are concrete, its governing card cites
its owning M file's complete ordered recipe actions with concrete parameter bindings, it has at least
one member card, every internal worker has one member card citing an applicable ordered subsequence,
and every instance/card field has a concrete non-placeholder, non-`N/A` value.

## 2. M01 - Prerequisite and admission closure

### Purpose

Establish one missing fact or capability that a later selected module cannot truthfully proceed
without. Keep prerequisite work separate from product implementation.

### Inputs

- downstream instance ID and exact failed/unknown precondition;
- authoritative source that defines the required state;
- current repository/runtime/resource state and only the IDs required to target live objects;
- role/authority allowed to establish or decide it; and
- cheapest decisive proof.

### Required local actions

1. `M01-A1` - Re-read the named downstream precondition and its authority source.
2. `M01-A2` - Observe current state without mutation and record `SATISFIED`, `MISSING`, or `INDETERMINATE`.
3. `M01-A3` - If satisfied, publish the observation and stop; do not perform setup again.
4. `M01-A4` - If missing and authorized, perform only the named prerequisite action.
5. `M01-A5` - Read back or otherwise independently verify the resulting state.
6. `M01-A6` - Publish the prerequisite result; persist a record only when a downstream consumer needs it.
7. `M01-A7` - If indeterminate or unauthorized, publish `INCOMPLETE` and the exact unresolved fact/owner.

### Decision and routes

- `SATISFIED` unlocks only consumers that declare this result as an input.
- Failed prerequisite setup returns to the same M01 owner only when the failure is correctable within
  the original card; otherwise it is `INCOMPLETE`.
- Discovery of product work exits to plan amendment; M01 cannot absorb it.

### Completion test

Pass only when the downstream predicate can be evaluated from the result. Fail the
local recipe if it merely says setup was attempted, relies on unverified state, or changes product scope.

## 3. M02 - Product implementation and repair tranche

### Purpose

Give one serial writer the full coherent deliverable, its high-value failure brief, implementation,
self-testing, and all later material repairs for the same unaccepted task.

### Inputs

- `DEL-*`, its `REQ-*` rows, acceptance claims, shared seams, and exclusions;
- exact starting revision/worktree and write scope;
- selected realistic failure cases from Pass 6;
- existing accepted credit and dependency domains;
- shortest available self-checks; and
- M05 return contract for pooled material findings, if a loop is possible.

### Required local actions

1. `M02-A1` - Verify starting source state, cleanliness, ownership, dependencies, and active claim/worktree IDs.
2. `M02-A2` - Read the initial entrypoints and governing requirement/acceptance rows; do not reconstruct history.
3. `M02-A3` - Convert the selected failure brief into implementation invariants and focused self-check targets.
4. `M02-A4` - Implement the complete coherent deliverable serially; internal commits do not create review gates.
5. `M02-A5` - Run the shortest self-checks that can catch producer mistakes before publishing.
6. `M02-A6` - Inspect the final diff for scope, unintended files, debug artifacts, and requirement coverage.
7. `M02-A7` - Produce one reviewable tip and publish the diff/check/result information its consumers need.
8. `M02-A8` - On an M05 material return, continue this same logical task and workflow role; reuse the
   active invocation when available and still selected, otherwise use its structured handoff. Consume
   the entire pooled finding set, repair all admitted findings as one batch, rerun only implicated
   self-checks, and publish one new tip.

For M02-A3 and M02-A5, the owning authority's card must already name the required behavior, protected
behavior, admitted failure cases, proof goals, mandatory checks, and acceptance boundary. The writer may derive
code-level invariants, choose implementation mechanics, and add the smallest local self-check needed
to catch its own implementation mistake; it may not create a new product requirement, redefine the
proof obligation, or substitute its own acceptance standard. M02-A8 begins only from the owning
authority's complete admitted repair objective and bounded correction card, not from a raw finding pool
that leaves the writer to decide what should change.

### Decision and routes

- Self-check failure remains inside M02 only when it proves or leaves genuinely undecidable a required
  product criterion; continue from the first failed action/check until corrected, unrecoverable, or stalled.
- A complete frozen tip proceeds to M03 when independent assets must be constructed, otherwise to the
  graph-selected check or acceptance consumer.
- Only M05 may admit external findings into the material return. Do not repair reviewer comments piecemeal.
- A strict test-only or administrative correction never enters M02.
- A Series 1 M02 occurrence is separate from the step's normal M02 occurrence and is available only
  under `incremental-verification.md` after the complete feasible pool yields one scoped compatible
  correction objective. It repairs only that objective, runs the compile-plus-motivating-test smoke,
  never invokes the normal broad affected campaign, and ends at ROOT for the Series 1 review,
  integration, and repaired-output exit. A Series 2 M02 occurrence exists only when remaining
  checkpoint results establish a new material correction objective at the current progress bound; it
  is never an automatic replay of the normal implementation path.

### Completion test

Pass only when one writer owns one coherent frozen tip, every requirement is addressed or explicitly
blocked, self-check results are current, and no material finding pool remains partially repaired.

## 4. M03 - Independent verification asset construction

### Purpose

Construct missing acceptance or regression assets independently from product implementation so the
product writer cannot silently define both behavior and its only oracle.

### Inputs

- exact acceptance claims lacking trusted executable/static proof;
- frozen product/source base supplied by the graph;
- test/fixture/script/document write scope separated from M02;
- existing verification conventions and any check selector/registry that the actual checker or runtime consumes; and
- semantic constraints that the asset must not weaken.

### Required local actions

1. `M03-A1` - Confirm each requested asset closes a named verification gap; drop duplicates of trusted existing checks.
2. `M03-A2` - Define scenario, trigger, expected behavior, oracle, and check selection before authoring.
3. `M03-A3` - Assign one writer per shared asset; parallelize only disjoint conceptual outputs and paths.
4. `M03-A4` - Author only verification assets. Do not change product behavior, policy, acceptance meaning, or
   locked configuration to make the asset pass.
5. `M03-A5` - Run asset syntax/discovery/self-tests that do not consume prohibited real resources.
6. `M03-A6` - Inspect the asset diff for oracle strength, coverage fidelity, ownership collisions, and scope.
7. `M03-A7` - Publish one independently owned asset tip/result and the claims/check IDs it supplies.

For M03-A2, `Define` means translate the owning authority's already-concrete behavior and proof
contract into the asset's executable form. Before dispatch, that authority must name every behavior to prove, scenario goal,
trigger, expected result, protected/no-change behavior, oracle property, test-only versus product-
repair classification, target surface, and acceptance strength. The M03 worker may choose test-code
mechanics, fixture construction, assertion syntax, and the narrow selector needed to execute that
contract. It must return any semantic ambiguity, missing expected behavior, proposed oracle change,
or newly discovered product defect to its owner; it may not decide those matters itself.

### Decision and routes

- A semantic ambiguity in expected behavior returns to the decision owner, not to M03 invention.
- A strict test-only correction later returns to this same logical role/task through M05 and reruns
  only the known affected IDs after deterministic eligibility is proved. Reuse or hand off its
  invocation under the universal instance contract.
- A product defect discovered while authoring is a finding for M05; M03 does not repair product source.

### Completion test

Pass only when every asset maps to a named acceptance claim, preserves or strengthens its oracle,
uses the declared ownership scope, and can be consumed by M04 without hidden setup.

## 5. M04 - Review and checking campaign

### Purpose

Run all selected non-producer checking paths for one gate against one shared reviewable input, in parallel where
independent, then return one complete result set. Smoke, focused checks, review, observation, fan-out,
and join are internal campaign parts, not separate top-level modules.

### Inputs

- one shared reviewable product/integration/release input;
- gate question, acceptance claims, selected checking paths, and review class;
- per-path conceptual surface, functional role, invocation/handoff state, read/write roots, and
  relevant changed inputs;
- for every review/audit path, the owning authority's governing requirements/invariants, risk hypotheses or pitfalls,
  exclusions/protected boundaries, severity/materiality threshold, permitted adjacent inspection,
  required output shape, and handoff owner;
- existing green credit and invalidation classification; and
- R23 live-harm stop conditions, if any selected path can cause live harm.

### Required local actions

1. `M04-A1` - Verify every path consumes the same declared frozen input or record a real dependency that forces a
   different subgroup; never compare results from silently different tips.
2. `M04-A2` - Put the cheapest decisive check in the M04-A3 parallel group unless a named output
   dependency requires it first. Do not serialize it merely to discover an ordinary failure early.
3. `M04-A3` - For all remaining independent review, deterministic-check, and observer paths, allocate disjoint
   writable roots and launch every member before awaiting any member.
4. `M04-A4` - Require each path to finish its assigned surface and return its complete findings/results.
   A deterministic multi-check path checkpoints each runnable unit and continues after ordinary failure;
   stop early only for a named failed prerequisite or the exact R23 containment exception.
5. `M04-A5` - Preserve each required path result; do not let one writer overwrite another's output.
6. `M04-A6` - Join exactly once. Deduplicate equivalent findings, preserve disagreements,
   and bind the combined set to the frozen input and campaign ID.
7. `M04-A7` - Publish the complete result set, unit checkpoints, and reused/invalidated PASS credit to
   M05. Do not repair, accept, or rerun inside M04.
8. `M04-A8` - On an affected-repair repeat, keep the same declared functional roles and cover the
   repair surface, violated invariants, and only dependencies invalidated by the new tip. Reuse each
   invocation when available and still selected; otherwise dispatch that role through its structured
   handoff.

For every action assigned to a reviewer or auditor, the finding set remains open: a valid result may
contain no findings or newly discovered in-boundary findings. Watch areas guide attention but are not
findings the reviewer is required to produce.

Every M04 reviewer block includes the
[finding-admissibility rule](../../acceptance-design.md#finding-admissibility-requirements-define-the-review-boundary).
Require the governing requirement/source, acceptance impact and test/evidence
status for every admitted finding. If current requirements are satisfied and all
required tests pass, a genuine vulnerability/gap that does not undermine those
conclusions is `REJECT-OUT-OF-SCOPE`, invalid as a correction or blocking finding.
Return it only as a nonblocking observation. A violation of a binding requirement
remains valid even when existing tests miss it. M07 and other review/audit paths
use the same rule; no review path silently broadens scope.

The owning authority also predeclares every deterministic check selection used by M04-A2/A3 and any
named dependency skip or R23 containment trigger. The campaign executor may apply those rules and
launch the named paths; an unexpected result that would require a different check, surface, or
ordering decision returns to that authority and, if it crosses a lane boundary, to ROOT. This mechanical
scheduling limit does not narrow the reviewer's independent judgment about findings inside its assigned
surface.

### Decision and routes

- A failed prerequisite may skip only the dependent path, and R23 may contain live harm. Record the
  reason and incomplete path. An ordinary product failure does not cancel another feasible path.
- Support/report faults use M05 administrative/support classification, do not become product findings,
  and cannot delay the campaign's M05 handoff when required product results are decidable.
- Campaign completion always proceeds to M05, including mixed, failing, incomplete, or disagreeing results.
- A reviewer may justify minimum adjacent inspection needed to understand behavior or substantiate a
  finding. Broader investigation requires a recommendation to its owning authority and a separately
  authorized card; cross-lane expansion returns to ROOT and is not an implicit extension of M04.
- A `MI-FL2-S1-*` M04 occurrence performs the declared independent frozen-tip review and only the
  minimal smoke evidence not already produced by its separate `MI-FL2-S1-*` M02 occurrence; it must
  not import the `MI-NORMAL-*` M04 broad deterministic campaign. A `MI-FL2-S2-*` M04 occurrence consumes the progress-bound
  checkpoint input map and runs only failed, unresolved, affected, uncertain, or uncredited units.
  Both use their required prefix, remain distinct from the normal M04 occurrence, and state the saved work.

### Completion test

Pass only when every selected path reached a terminal result or has a named dependency skip/R23
containment reason, independent paths actually overlapped, result roots are non-colliding, the join
happened once, and the output is one complete set.

## 6. M05 - Adjudication, acceptance, and correction routing

### Purpose

Turn producer/campaign/integration/practical results into exactly one authoritative semantic verdict
or one classified correction route. This module owns decisions; it performs no product repair itself.

### Inputs

- gate question, acceptance criteria, tolerances, and decision owner;
- producer result and every selected M04/M06/M07/M09 output;
- working source and request;
- existing accepted credit and dependency map; and
- predeclared material, strict test-only, administrative, incomplete, and stall routes.

### Required local actions

1. `M05-A1` - Validate required result shape without treating shape validity as product success.
2. `M05-A2` - Pool and deduplicate findings once; retain source, severity claim, violated requirement/invariant,
   reproducible results, and disagreements.
3. `M05-A3` - Classify every follow-up as `production/material`, `strict test-only`, or `administrative/support`.
4. `M05-A4` - For every test/support fault, issue `PRODUCT_INVALIDATING`, `NONBLOCKING_TEST_ERROR`, or
   `INDETERMINATE` with the product checks/observations and affected claims.
5. `M05-A5` - Decide each finding against realistic product behavior, R25 and the finding-admissibility
   rule. Classify genuine but acceptance-irrelevant gaps as `REJECT-OUT-OF-SCOPE`; retain truthful
   nonblocking notes in Section 14, admit no repair tranche for them, and continue satisfied edges.
   Drop gold-plating to Section 14. Passing tests never waive a demonstrated required violation.
6. `M05-A6` - Compute invalidated and preserved credit by dependency, not whole-document change alone.
7. `M05-A7` - If admitted material findings remain, partition only by incompatible owner, source
   context, or acceptance criterion, then send each complete compatible group once to the same M02
   logical instance and workflow role, reusing or handing off its invocation under the universal
   contract. Do not rerun assurance while a compatible group from the current pool remains open.
8. `M05-A8` - If strict test-only eligibility is proved, return once to the same M03 logical role/task,
   reusing or handing off its invocation under the universal contract. Run the deterministic eligibility
   check and authorize exactly the known failed-ID rerun. If the correction or rerun fails, return to
   M05-A3 classification; never infer a production/material route from fast-lane failure.
9. `M05-A9` - If the issue is administrative and facts remain decidable, correct/reconstruct from existing
   result only when an exact consumer still requires it and correction is cheaper than recording it;
   otherwise record it and take every independently satisfied successor without product/test rerun.
10. `M05-A10` - Issue exactly one verdict: `ACCEPTED`, `ACCEPT-WITHIN-TOLERANCE` only for a
    predeclared non-required tolerance (never a required criterion), `CONTINUE`, or
   `INCOMPLETE`; permit `CONTINUE` only for a failed/genuinely undecidable required product criterion.

M05 is a ROOT/orchestrator decision module for terminal, cross-lane, integration, release, and global
product decisions. Within an explicitly authorized lane, its lane sub-orchestrator may apply M05 only to
the declared local finding pool and routes. Before M05-A7 or M05-A8 activates another worker, the
owning authority must convert the admitted pool into a concrete correction contract naming the diagnosed
problem, required result, exact behaviors/proof goals, target and protected surfaces, allowed changes,
pitfalls, mandatory reruns, acceptance criteria, and first unresolved action. Supplying findings alone is
not a complete repair or test-authoring assignment.

### Decision and routes

- Material return: M05 -> same M02 logical role/task -> affected M04 -> same M05; reuse or hand off
  the invocation under the universal contract.
- Strict test-only return: M05 -> same M03 logical role/task -> exact affected check path -> same M05;
  reuse or hand off the invocation under the universal contract.
- Failed strict test-only correction/rerun: return to M05 classification. Enter M02 only when separate
  product results satisfy R12/R24; otherwise mark only the affected claim unavailable or
  `INDETERMINATE` and advance all nonconsumers.
- Administrative correction, when still consumed: remain in the originating result lane, resume at
  the first unresolved artifact action, validate, then return to the same M05. Otherwise record and advance.
- Accepted work unlocks only declared graph successors and makes the logical task terminal; every
  invocation associated with it is then terminal or retired under the plan's lifecycle rule.
- Every correction, repeat, or integration successor is activated only by a separately authored card
  containing the complete revised problem/result/scope/proof/pitfall/acceptance contract. ROOT authors
  terminal, cross-lane, and integration successors; an authorized lane sub-orchestrator may author only
  its declared local successor. An M05 verdict or route never authorizes a worker to continue on its own.
- A non-product fault with independently decisive product results cannot select `CONTINUE` or
  `INCOMPLETE`, cannot enter M02, and cannot hold a successor that does not consume that fault.

### Completion test

Pass only when every finding has one disposition, all preserved/invalidated credit is explicit, no
repair pool was fragmented, and exactly one route/verdict is emitted.

## 7. M06 - Integration and release assembly

### Purpose

Combine accepted inputs in a declared order, prove the combined coordinate, optionally promote it,
retain rollback state when needed, and retire only release-level state that is safe to close.

### Inputs

- exact accepted revisions/artifacts and their M05 verdicts;
- integration order, destination coordinate, conflict owner, and write authority;
- affected integration checks and dependency domains;
- promotion target when in scope; and
- rollback, required-result retention, and retirement conditions.

### Required local actions

1. `M06-A1` - Revalidate every accepted input and verdict before mutation.
2. `M06-A2` - Verify destination state/cleanliness and record a rollback base when rollback is required.
3. `M06-A3` - Integrate inputs serially in the declared order; one owner resolves conflicts without changing scope.
4. `M06-A4` - Inspect the combined diff/manifest and run only checks implicated by integration seams;
   reuse pre-join PASS credit when the join leaves a check's declared inputs unchanged.
5. `M06-A5` - Publish the integrated coordinate and required post-join results.
6. `M06-A6` - If promotion is selected, advance only the accepted coordinate and read back the destination state.
7. `M06-A7` - Preserve required rollback state and consumed acceptance results before retiring temporary state.
8. `M06-A8` - Retire only clean, terminal, unclaimed lanes/resources; failed archival remains visible for recovery.

M06 execution begins only after ROOT has accepted the inputs and separately dispatched the exact
integration/assembly card. Even when the same workflow role or provider invocation is requested for
continuity, no producer/check/review run crosses the ROOT decision boundary into M06. The executor
performs only the authorized coordinate mechanics and declared post-join checks; ROOT retains conflict,
scope, acceptance, rollback, and next-edge decisions unless the card explicitly assigns one mechanical
conflict-free action.

For M06-A3, the `conflict owner` is ROOT or another explicitly named decision authority, never the
mechanical integration executor. The executor may complete an already-declared conflict-free join or
apply an exact preauthorized mechanical resolution whose resulting bytes are predetermined by the
card. Any content conflict, ambiguous destination, altered accepted input, or choice among valid
resolutions causes a terminal handoff to ROOT before integration continues.
Any differently named `conflict owner` in a project plan must be an alias or explicitly delegated
mechanical function of the plan's ROOT/orchestrator decision owner; it cannot be an independent
subagent authority and cannot override R6.

### Decision and routes

- A mechanically resolvable conflict, destination mismatch, or interrupted join remains inside the exact
  M06 operation and resumes only at its first unresolved action while accepted input behavior stays intact.
- Only a result showing that required post-join product behavior or contract correctness failed/remains genuinely
  undecidable goes to M05, then to the owning accepted input only if its dependency is invalidated; do not
  broadly reopen all deliverables.
- Promotion/deployment/readback mismatch is an operation-boundary failure when accepted source behavior
  remains intact. Stop and report the verified contradiction; never guess, promote another tip, or enter
  product repair without a failed or undecidable product criterion.
- Archive or retirement support failure leaves that exact state visible and blocks only its direct
  retirement/reuse consumer.
- No promotion scope means stop after accepted integration; do not create a dummy release action.
- A Series 1 M06 occurrence is a separate minimal integration/readback instance for the repaired step
  output and its changed-input map. It exits to the ROOT-selected progress-bound step's Series 2 entry
  and never advances the repaired step's normal successor path as a substitute for that handoff.

### Completion test

Publish M06's terminal result when the destination either equals the declared integrated/promoted
coordinate or the exact unresolved operation is recorded with accepted source credit preserved; affected
checks are decided or explicitly routed, rollback is retained, and no live/dirty/unpreserved state was
retired. Only a verified operation result advances its direct destination consumer.

## 8. M07 - Accumulated final assurance

### Purpose

Provide proportionate whole-product assurance for one named release unit by combining whichever final
independent audit and accumulated deterministic safeguard paths risk actually requires.

### Inputs

- one declared integrated/release input;
- complete goal and acceptance set;
- accepted deliverable results and unresolved/tolerance ledger;
- selected final audit surfaces and/or full accumulated check command; and
- release-unit acceptance consumer.

### Required local actions

1. `M07-A1` - Confirm deliverable acceptance and integration results belong to the declared release unit.
2. `M07-A2` - Select final audit, accumulated deterministic safeguard, or both from risk; do not add a path merely
   because this module supports it.
3. `M07-A3` - If both are selected and independent, launch them concurrently with disjoint result/cache roots.
4. `M07-A4` - The final audit reviews the accumulated accepted product, not superseded intermediate tips.
5. `M07-A5` - The full safeguard uses the declared independently runnable units and conservative
   input map. It checkpoints each completed unit, continues after ordinary failures, records dependency
   skips, reuses only unaffected PASS credit, and executes every failed, unresolved, change-affected,
   or uncertain unit in declared order beginning with the earliest member of that set. Include check
   IDs only when the actual checker/runtime uses them for selection, correlation, or pass-credit reuse.
6. `M07-A6` - Complete all selected paths and every feasible safeguard unit, then join once into one
   final result pool; the first failure is never the terminal result by itself.
7. `M07-A7` - Send that pool to M05 for the release-unit verdict. A regression invalidates only implicated credit.

M07-A2 is a ROOT planning/dispatch decision, not a choice delegated to the assurance executor. ROOT's
card must name the final audit path, accumulated safeguard path, or both; the exact release input;
their bounds, commands, concurrency, cancellation conditions, and acceptance consumer; and the risks
that justify the selection. The executor only runs and joins those selected paths. An apparent need
for a different or additional assurance path returns to ROOT.

### Decision and routes

- A material final finding routes through M05 to the owning M02 as one compatible batch and returns
  through affected M04 before M07 executes only the failed, unresolved, input-invalidated, or uncertain
  set beginning with that set's earliest unit.
- A support fault follows M05 support isolation; it does not fabricate a safeguard pass, rerun a green
  product path, or hold a successor whose required release result is independently decidable.
- If M07 is omitted, Section 6 and Section 13 must explain why deliverable checks are sufficient.
- When the current progress-bound step uses M07 in Series 2, configure a distinct checkpoint-resume
  occurrence. It joins accepted Series 1 exits, recalculates invalidation, and runs only the required
  remaining unit set; it must not invoke the normal full safeguard as a disguised restart.

### Completion test

Pass only when every selected final path terminates on the same declared release input, joins once, and no
local card duplicates the accumulated safeguard.

## 9. M08 - Expensive or external readiness proof

### Purpose

Prove fragile execution/control machinery cheaply before spending an expensive runner or scarce,
irreversible external attempt. Recordability preflight and external rehearsal are genuinely optional
profiles inside one readiness module. Decide each as `SELECTED: <concrete action>` or
`OMITTED: <free-form project justification>`. Strongly select recordability preflight for fragile custom
runners and external rehearsal for scarce, irreversible, hardware, service, or other external control
flows; these examples are recommendations, not exhaustive eligibility gates.

### Inputs

- exact expensive runner/procedure or external control-flow inputs;
- fields/control properties the real operation depends on;
- disposable fake inputs and prohibited real side effects;
- expected readiness result; and
- downstream M04 or M09 consumer.

### Required local actions

1. `M08-A1` - Check whether prior readiness work still applies under unchanged relevant inputs; stop if it does.
2. `M08-A2` - For a fragile custom runner, execute one side-effect-free fake and check inputs, process/worker
   IDs needed for correlation, timing, command, outputs, cleanup, readback, and exit. When
   checkpointed verification is selected, also check checkpoint write/read and the unit-resume boundary.
3. `M08-A3` - For an external flow, exercise exact admission, target binding, retained authorization, observation,
   stop/abort, idempotence/recovery, cleanup, and terminal closure against disposable local fakes.
4. `M08-A4` - Verify no product, service, deployment, hardware, or scarce namespace was consumed.
5. `M08-A5` - Publish profile results separately under one module output; persist input comparison data only if reuse needs it.
6. `M08-A6` - On procedure/report failure that still blocks the exact expensive/real operation, rerun
   each failed, input-affected, or uncertain readiness profile in declared order beginning with its
   earliest required action; reuse only an unaffected prior PASS. Otherwise record and stop readiness
   work.

ROOT's card supplies the relevance comparison for M08-A1, selected readiness profiles, exact fake
inputs, properties to prove, prohibited effects, pass criteria, and downstream consumer. The worker
may perform those comparisons and observations mechanically; it may not decide that a different
profile, property, external topology, or real attempt should be added.

### Decision and routes

- Pass unlocks only the checked downstream operation and never counts as a product pass.
- Failure blocks only the exact expensive/real operation, never an independently decidable product result
  or other release work, and does not invalidate unrelated product credit.
- A project may omit either profile only with its recorded free-form justification; omission decides
  that optional profile and cannot waive M08's selected-instance, card, result, or validation contracts.

### Completion test

Pass only when every selected readiness property is observed from disposable execution, prohibited
side effects are absent, and reuse/invalidation dependencies are explicit.

## 10. M09 - Practical or external validation

### Purpose

Own one real authorized attempt from admission through observation, result, stop, cleanup, and durable
closure. Bundle checkpoint/resume and observation because they are part of controlling the same attempt.

### Inputs

- real acceptance scenario and pass/fail result;
- exact target/resource ID needed for safe targeting and the authorization boundary;
- accepted M08 readiness result when required;
- controller, worker, observer, and cleanup roles;
- attempt ID/namespace, lock/claim IDs, timeouts, retained session ID, and resume predicate; and
- live-harm containment triggers.

### Required local actions

1. `M09-A1` - Verify authorization, target/resource ID, prerequisite product coordinate, readiness result, and
   absence of conflicting claims before allocation.
2. `M09-A2` - Create one retained attempt ID and bind controller, process/worker IDs,
   observer, result roots, and cleanup owner.
3. `M09-A3` - Launch only the predeclared topology. Serialize shared real resources; parallelize only isolated work.
4. `M09-A4` - Start independent observation before the behavior it must observe. Observation is read-only unless
   its exact containment authority is triggered.
5. `M09-A5` - Execute the real scenario, record commands/actions, timings, outputs, target state, and failures.
6. `M09-A6` - On interruption, checkpoint the semantic task plus session/worktree/resource IDs and
   each completed practical check unit's consumed target/resource state. Reuse a unit only when that
   state remains verified unchanged; otherwise close safely and start only the affected declared work.
7. `M09-A7` - Stop/abort immediately only for an R23 observation; preserve what diagnosis/recovery needs and contain identified descendants/resources.
8. `M09-A8` - Reach terminal state, stop cooperatively, verify cleanup by process/resource IDs, and retain required result/observer/cleanup information even on failure.
9. `M09-A9` - Join real-attempt results once and send them to M05. Do not repair product inside a live attempt.

For M09-A6, `start a new declared attempt` always means close the interrupted attempt, publish its
terminal state, return to ROOT, and wait for a separate authorization and complete new-attempt card.
No controller, worker, or observer self-starts a replacement attempt, changes the target/resource,
alters the scenario, or decides that retry is warranted. ROOT predeclares the current attempt's
scenario, target, success/failure observations, containment triggers, and stop/cleanup boundary.

### Decision and routes

- Product/practical failure closes the attempt safely, then goes to M05 classification.
- Support/observer/report failure isolates only affected claims unless the real outcome becomes unknowable;
  every practical claim not consuming that result remains decidable and advances.
- Authorization or target mismatch stops before allocation and reports `INCOMPLETE` or contradiction.
- Cleanup uncertainty leaves the attempt terminal-but-visible and blocks resource reuse, not unrelated product credit.

### Completion test

Publish the terminal attempt output when every scenario fact is decidable or the exact affected claim is
explicitly indeterminate, observer/controller results are correlated by runtime IDs wherever needed, every allocated
resource is either verified terminal or terminal-visible with its exact owner and reuse block, and cleanup
required result is retained. M05 decides product acceptance; cleanup uncertainty blocks only the exact resource
reuse or downstream operation that consumes verified cleanup and never forces already-decidable product
behavior to repeat.

## 11. M10 - Project extension

### Purpose

Express one required workflow capability that cannot be composed from M01-M09. Extension is a last
resort, not permission to create a project-specific duplicate of an existing module or policy.

### Inputs

- exact uncovered requirement or runtime behavior;
- attempted M01-M09 compositions and why each fails;
- owner, roles, inputs, outputs, graph placement, cost, and risks; and
- proposed standard-schema local recipe.

### Required local actions

1. `M10-A1` - Name the missing expressive capability in one sentence.
2. `M10-A2` - Prove that no existing module can own it internally and no policy/edge parameter can express it.
3. `M10-A3` - Record the selected extension's concrete expressive gap and payoff, typed inputs/outputs,
   exact ordered actions, decisions, failure routes,
   credit/invalidation, isolation, lifecycle, and cost using the universal instance contract.
4. `M10-A4` - Check that the extension does not create a second role mapping, policy source, result ledger,
   scheduler, or acceptance owner.
5. `M10-A5` - Add one M10 instance and its graph edges; do not renumber or alter M01-M09.

M10-A1 through M10-A5 are plan-compiler/ROOT decisions. If a selected M10 later has a worker-executable
portion, ROOT must first finish the expressive-gap proof, module contract, graph placement, and exact
task card; the worker implements only that explicitly scoped portion and cannot define the extension itself.

### Decision and routes

- If an existing recipe can be parameterized without changing its invariant, use that module and omit M10.
- If the capability is product scope rather than workflow, return it to goal/decomposition, not M10.
- If the capability requires unavailable authority/runtime behavior, route through M01 or `INCOMPLETE`.

### Completion test

Pass only when the expressive gap is proven, the extension has the complete standard schema, and its
benefit exceeds its added coordination and maintenance cost.

## 12. Local recipe validation

For every selected instance, answer `PASS` to all of these before graph composition:

1. Does it use exactly one M01-M10 recipe and the universal instance contract?
2. Are activation, inputs, roles, preferred invocation reuse, structured handoff, ordered actions,
   outputs, and every exit concrete across the M-module definition, instance, and owning step?
3. Are all bundled internal steps kept inside the macro-module rather than promoted into fake modules?
4. Does every optional internal profile/path have a concrete `SELECTED` or `OMITTED` decision and justification?
5. Does a loop return to the same functional role/logical task with the complete accumulated results,
   reusing its invocation when available and still selected or otherwise recording a structured handoff?
6. Does the instance produce one typed output that a declared successor consumes?
7. Are concurrency, writable roots, required runtime-object IDs, affected prior results, cleanup, and cost explicit?
8. Does the instance avoid changing global policy, acceptance ownership, or module graph locally?
9. Does every failure block only its exact consumer, and does every other satisfied successor advance?
10. Is every product loop tied to a failed/undecidable required criterion and every continuation bound
    to the earliest failed, unresolved, change-affected, or uncertain action/check with unaffected
    completed work and green credit preserved, with failed test-only correction routed back to
    classification rather than automatically promoted to material repair?
11. Did ROOT, or an explicitly authorized lane sub-orchestrator, supply a complete executable contract
    rather than delegate task meaning to the worker? For review/audit, are the input, surface,
    invariants, watch areas, exclusions, materiality, output, and handoff concrete while findings remain
    open and scope expansion requires the owning authority's authorization?
12. Is the M-module's interface, rule/process, recipe action, variation, instance, and task-card content
    defined only in `modules/Mxx.md`, with the owning step limited to ordered `MI-*` interface
    composition and every global rule and concrete role-agent selection left in its own artifact?
13. Does the instance belong to exactly one of its step's three entry paths and use that path's exact
    `MI-NORMAL-*`, `MI-FL2-S1-*`, or `MI-FL2-S2-*` prefix? When it belongs to a fast path, does it
    implement purpose-built lighter work for that series without importing or renaming the normal
    broad campaign or full restart?

Any `FAIL` means the instance is not ready to appear in the plan.
