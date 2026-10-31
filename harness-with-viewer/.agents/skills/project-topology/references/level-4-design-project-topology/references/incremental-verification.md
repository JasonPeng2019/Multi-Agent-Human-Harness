# Incremental verification and batch repair

Use this reference for every newly compiled formal modular plan. Each `STEP-*` defines
`FAST_LANE_V2_SERIES_1` and `FAST_LANE_V2_SERIES_2`, so checkpointed verification is part of the
package contract. Both fast-lane entries must have configured, disjoint MI paths in every step.

Put `CHECKPOINTED_VERIFICATION_V1` in Section 0 of every newly compiled or amended formal modular
plan. It is a plan-level protocol selector for the validator, not a runtime ID, hash, or evidence
requirement. Legacy plans remain subject to their accepted contract until explicitly amended.

## Plan revision is separate from execution invalidation

Apply [Change locality](../../change-locality.md). A source compiler may regenerate
global indexes or an M-module view when one step-local instance changes. That file
diff does not by itself invalidate other instances or completed runtime evidence.
Use changed authoritative units and their actual consumed contracts to assess impact.
The impact report is advisory; it cannot certify semantic compatibility or grant
runtime PASS reuse. Preserve historical results and inspect actual input/state
dependencies under the rules below, even for completed steps.

Full-package structural checking remains mandatory and does not mean replaying
product work. The review panel uses focused affected-scope review and explicit
unchanged-scope confirmations; compiling changed source never renews its approvals.

## Checkpointed verification contract

For substantial matrices, also apply [Matrix execution](../../matrix-execution.md).
The ordered units and earliest unresolved checkpoint below preserve dependency and
resume order; they do not serialize independent ready units. Schedule those units
concurrently within the declared isolation, capacity and finite-test budgets, collect
all feasible results before repairs, and keep blocked, timed-out and unrun evidence
explicit. This applies to normal and both repair entries without broadening their
required check scope or weakening their gates.

Compile a selected expensive gate as an ordered set of the smallest independently runnable check units
that saves more rerun time than it adds in setup. Do not make one process per individual test merely
to claim resumability. When an existing runner cannot resume at a useful unit boundary, select the
smallest prerequisite or verification-asset work needed to expose that boundary before promising
incremental execution.

For each unit, the task card must state:

1. the command/operation and result owner;
2. source, configuration, runner, environment, fixture, and external-state inputs that can affect it;
3. prerequisites and dependent units;
4. the exact pass-reuse condition;
5. the result location only when a later consumer needs it; and
6. the failure action: continue, dependency-skip with reason, or R23 containment.

The executor writes progress after each completed unit: passed, failed, skipped, or unresolved; the
first unresolved unit; the repository revision when source identity is needed; and any actual external
attempt/target state needed for a practical run. Do not hash ordinary inputs or create a receipt just
for a checkpoint.

An ordinary failure records a failure and does not stop the remaining runnable units. A unit may be
skipped only when a named prerequisite failed or R23 requires containment. The terminal result is a
complete pool, not the first failure.

On a new tip or resumed attempt, ROOT calculates the changed inputs before dispatch. A prior PASS is
reusable only when its source and non-source inputs are declared unchanged and none of its prerequisites
are invalidated. A FAIL is never reusable as a PASS. If the map, input comparison, or runner state is
uncertain, rerun the unit. Form the required execution set from every failed, unresolved,
change-affected, or uncertain unit, then execute it in declared order beginning with its earliest
member. The checkpoint still records the first unresolved unit; that unit is the resume point when no
earlier unit was invalidated. Do not replay unaffected passes. A complete restart is valid only with
no usable progress record or a change that reaches every selected unit.

For a stateful practical/hardware operation, compare the target identity and the state that the unit
actually consumed. Reuse a PASS only when it was non-mutating or the relevant state still holds. A
new fixture, lease, image, server behavior, or target state invalidates the units that consume it.

## FAST_LANE_V2

`FAST_LANE_V2` is a two-series product-repair route across the original `STEP-*` building blocks; it
does not replace the strict test-only fast lane. Every step file defines all three of its entry modes:

1. `NORMAL` - the original planned activation, module path, gate, and successors.
2. `FAST_LANE_V2_SERIES_1` - the local repair-and-exit flow when a compatible set of small scoped
   production edits belongs within this step.
3. `FAST_LANE_V2_SERIES_2` - the checkpointed re-entry flow when this step is the current progress
   bound and receives accepted repaired outputs from one or more earlier affected steps.

Every emitted step repeats the execution template's canonical FAST_LANE_V2 usage block exactly and
unchanged beneath its entry-flow heading so the purpose, activation, and saved-work rule remain
visible at the point of use.

Every step must contain both fast-lane series as unconditional required plan content with complete,
disjoint paths. Runtime execution waits for each stated trigger, but trigger state affects timing only
and has zero effect on required configuration. It never permits disabling, omission, relabeling,
reasoning away, normal-route substitution, or `N/A`.

Give the three entries distinct configured paths. `NORMAL` may use any project-justified number and
composition of M01-M10 instances, all named `MI-NORMAL-*`. Series 1 uses only `MI-FL2-S1-*`; Series 2
uses only `MI-FL2-S2-*`. Never share an ID or point either series at the normal path's heavy review,
broad deterministic campaign, or full restart. Fast paths should generally contain fewer MIs, but
must always be purpose-built and materially lighter even when their MI count is not smaller. The
common pattern is illustrative rather than fixed: Series 1 composes
scoped repair, compile-plus-motivating-test smoke, independent review, and integration/exit behavior;
Series 2 composes repair receipt/join, input invalidation, remaining-check execution, and continuation.
An emitted plan may combine or further partition those responsibilities when the selected M-module
interfaces justify it, but it must state the concrete saved work and prove that each fast-lane path is
materially narrower than replaying `NORMAL`.

For example only, one step could compile this shape:

```text
NORMAL
-> MI-NORMAL-IMPLEMENT
-> MI-NORMAL-REVIEW-AND-BROAD-TEST
-> MI-NORMAL-ACCEPT

FAST_LANE_V2_SERIES_1
-> MI-FL2-S1-SCOPED-REPAIR
-> MI-FL2-S1-COMPILE-AND-MOTIVATING-TEST
-> MI-FL2-S1-INDEPENDENT-REVIEW
-> MI-FL2-S1-INTEGRATE-AND-EXIT

FAST_LANE_V2_SERIES_2
-> MI-FL2-S2-RECEIVE-REPAIRS
-> MI-FL2-S2-CALCULATE-INVALIDATION
-> MI-FL2-S2-RUN-REMAINING-CHECKS
-> MI-FL2-S2-CONTINUE-NORMAL-PROGRESS
```

Do not copy that count or sequence automatically. Derive NORMAL from the step's full project work and
derive each fast path from the smallest safe work needed for its outbound-patch or inbound-reconcile
responsibility.

### Series 1 - local repair and exit

ROOT may activate a step's `FAST_LANE_V2_SERIES_1` only after the originating checking tranche
completes every feasible unit and its complete pool contains one scoped compatible material
correction objective owned by that step. One objective may batch several compatible findings; split
incompatible objectives even when they belong to the same step. ROOT writes a card containing:

- the affected `STEP-*`, complete finding pool, one correction objective, observed defects, and exact
  deterministic motivating test or tests;
- the bounded production surface, intended corrections, and no-change behavior;
- compile checks for changed production source plus the motivating tests as the required smoke;
- the review class and scope for the repaired frozen tip;
- the separate integration destination;
- the repaired public step output, changed-input/invalidation map, and reusable smoke credit; and
- the ROOT-selected later current progress-bound `STEP-*` that will receive the exit handoff through
  its Series 2 entry.

The `MI-FL2-S1-*` path runs only that minimal smoke. Its changed-source compile and motivating-test
PASS become checkpoint credit. When selected for this step, a Series 1 M04 instance retains
independent review but omits the normal broad affected deterministic campaign, and a Series 1 M06
instance reads back integration without duplicating green smoke when the fast-forward leaves the
bytes unchanged. Series 1 ends only after the affected step's repaired public output is
accepted and integrated; it does not silently advance the normal successors or perform Series 2.

### Series 2 - progress-bound re-entry

ROOT activates the step's `MI-FL2-S2-*` path through `FAST_LANE_V2_SERIES_2` only on the `STEP-*` that
is the current progress bound. It
waits for the accepted integrated Series 1 outputs from every affected earlier step in the current
repair set, deduplicates them, and calculates how their changed inputs affect this step's checkpoint
map. When the progress-bound step is also an affected source step, treat it as one set member rather
than adding a duplicate step or handoff.

Series 2 reuses each prior PASS whose declared source and non-source inputs and prerequisites remain
unchanged. It forms the required execution set from every failed, unresolved, change-affected,
uncertain, or otherwise uncredited unit, begins with the earliest such unit, runs the remaining
runnable checks in declared order, and then continues through the step's normal completion and
successor rules. Any intermediate `STEP-*` whose public input or guarantee is affected joins the
affected-step set and must produce an accepted Series 1 exit; an unaffected intermediate step keeps
its valid credit and is not replayed merely because it lies between the source and progress bound.

Do not activate either series for an uncertain impact, no deterministic motivating test, changed test or
runner selection/configuration, external/hardware state, a change that alters a shared/public
protocol, security boundary, broad lifecycle owner, or multiple unrelated mechanisms, or a pool whose
compatible findings require a broader repair batch. Use the normal M02 -> M04 route instead.

## Batch rule

The final safeguard, M04 campaign, and practical observation each return all feasible findings once.
ROOT deduplicates them and groups only compatible material findings into a writer tranche. A tranche
is compatible when one writer can state one correction objective, own the same source context, and
prove the repairs together. The writer receives the complete compatible group, makes one reviewable
tip, and ends at ROOT. It does not receive one card per failure.

Keep independent groups separate when they require different writers, authority, source context,
external state, or acceptance criteria. Do not rerun final assurance until every admitted compatible
group for the current pool has reached an accepted integrated coordinate. Then resume the safeguarded
units according to their checkpoint and input map.
