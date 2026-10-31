# Modular Execution-Package Architecture

This reference defines the authoritative ownership and dependency boundaries for every formal Level 4
output. The package is one plan and workflow assembled from independent gated steps. Each step composes
configured instances of the existing M01-M10 macro-modules into three explicit entry paths: `NORMAL`,
`FAST_LANE_V2_SERIES_1`, and `FAST_LANE_V2_SERIES_2`. A fact, rule, or
process has one authoritative definition; dependents cite its stable reference instead of copying or
paraphrasing it.

## Authoring authority versus expanded execution views

For new formal plans, [normalized authoring](normalized-authoring.md) owns the
editable definitions and generates the exact package described below. The table
schemas and contracts in this reference continue to define the expanded runtime
view and the supported legacy format; they do not require duplicate source entry.

| Concern | Editable source owner | Generated views |
|---|---|---|
| Shared requirements, role semantics/parents, cross-step graph, shared resource contracts | Root source | Root tables, reciprocal role children and shared manifests |
| Step public boundary, gate, three entry paths and local configured instances | One step source | Step file, composition union, root step/gate indexes and module-instance views |
| One member dispatch and its meaningful lifecycle data | Its step-local instance/member | Complete member card, MI member inventory, lane and terminal-handoff rows |
| Reusable module interface, invariant recipe and permitted defaults | Module library/default source | Expanded M01-M10 library and concretely bound cards |
| Policy behavior | Policy source; consumers cite its ID | Policy behavior plus derived reverse consumer index |
| Independent review and semantic rule/check decisions | Review source and actual reviewer evidence | Validation tables; never compiler-invented PASS |
| Concrete agent allocation | Existing canonical mapping JSON | Consumed directly, never copied into plan semantics |

A private instance variation is not a shared module-type edit. Generated module
files may contain several steps' instances for runtime readability; the editable
instances belong to their individual steps. Reuse defaults explicitly without
changing meaning for unrelated instances. Fully expanded dispatch contracts remain
mandatory; inheritance is an authoring convenience, not missing runtime instructions.

## Contents

1. Package layout
2. Dependency direction
3. Single-source ownership
4. Composition-root contract
5. Step contract
6. M01-M10 module-library contract
7. Global-rule contract
8. Agent-mapping boundary
9. Validation contract
10. Change rules

## 1. Package layout

The following exact layout is the generated execution package. The separate
authoring-source directory is defined by normalized-authoring.md and is not an
extra runtime package artifact.

Emit this exact directory shape at the requested plan destination:

```text
<plan-directory>/
|-- plan-workflow.md
|-- global-rules.md
|-- validation.md
|-- steps/
|   |-- STEP-001.md
|   `-- <one file per STEP-* gated step>.md
`-- modules/
    |-- M01.md
    |-- M02.md
    |-- M03.md
    |-- M04.md
    |-- M05.md
    |-- M06.md
    |-- M07.md
    |-- M08.md
    |-- M09.md
    `-- M10.md
```

Keep the project's sole concrete role-to-agent mapping in its canonical JSON file. Prefer placing a
new mapping beside the package directory—not inside its exact file envelope—and naming it
`SUBAGENT_ROLE_MODEL_MAPPING.json`; reuse another canonical path when the project already defines one.
Never copy provider/model/effort/tier selections into Markdown or create step-local or module-local mappings.

These artifacts are one operative plan. None is an optional commentary sidecar. `plan-workflow.md` is
the composition root and names every imported artifact class exactly once. `global-rules.md`, every
`steps/STEP-*.md`, every `modules/Mxx.md`, the mapping, and `validation.md` are authoritative only for
the concerns assigned below.

## 2. Dependency direction

Use this one-way dependency graph:

```text
user/spec + project/runtime truth
              |
              v
       plan-workflow.md
              |
              v
        STEP-* definitions
              |
              v
    MI-* references to M01-M10
         /             \
        v               v
 global-rules      workflow roles
                         |
                         v
               isolated agent mapping

validation.md observes every artifact but defines no workflow behavior.
```

Interpret arrows as references to public contracts, not permission to duplicate content. The
composition root orders steps through typed edges. A step combines ordered `MI-*` occurrences of
M01-M10 modules. The owning `modules/Mxx.md` file defines that ingredient's rules, flow, public
interface, and every configured occurrence. Modules cite global-policy IDs and workflow-role keys. At
dispatch, the runtime resolves each role through the sole mapping.

`MI-*` is an identity for one configured use of an M01-M10 module, not an additional behavioral layer.
Its prefix also declares its sole step entry: `MI-NORMAL-*` for `NORMAL`, `MI-FL2-S1-*` for
`FAST_LANE_V2_SERIES_1`, or `MI-FL2-S2-*` for `FAST_LANE_V2_SERIES_2`. The M01-M10 recipes themselves
are the reusable building blocks.

Never make a lower layer redefine an upper layer. Never make an upper layer repeat a lower layer's
internal process merely to explain it.

## 3. Single-source ownership

[Acceptance design](../../acceptance-design.md) decisions remain in existing owning
scope, proof, cost and dependency fields. The Section 16 per-STEP audit summarizes
necessity, multiplicity and proportionality assessments by the assigned reviewers;
it does not redefine execution policy or duplicate the activity inventory. The
dispatch template is an authoring aid, not another required output package file.

The [plan-conformance review](../../plan-conformance-review.md) extends the existing
Section 16 audit metadata with outcome, scope/authority, topology/simplicity,
verification/budget and execution-boundary assessments and a final verdict. It
records four distinct independent group approvals bound to the final revision,
with shared finding references and bounded per-group follow-up. Plan scope and
permissions remain in their existing owning artifacts; the audit is not execution
authorization and introduces no new package file, policy or runtime role.

The planning-time [test-scope audit](../../test-scope-audit.md) adds review results
and per-STEP coverage references to validation.md Section 16. That file records
the audit, dispositions and acceptance only. Suite selections and runtime scope
continue to live in their existing owning manifests/cards; the audit creates no
additional package file, runtime role or policy authority.

| Concern | Sole authoritative location | Other artifacts may contain |
|---|---|---|
| Goal, scope, authority, outcomes, requirements, deliverables, step index, workflow-role semantics, typed step graph, lanes/resources, external/integration decisions, unresolved ledger | `plan-workflow.md` | Stable references and consumed public-interface facts only |
| Cross-cutting scheduling, authority, context, checking, review, repair, acceptance, exception, containment, and lifecycle rules | `global-rules.md` | `P*`/`EXC-*` citations only |
| One independently gated workflow unit's objective, activation, public inputs/outputs, three distinct ordered `MI-*` entry paths, gate, returns, successors, isolation, and cost | `steps/<STEP-ID>.md` | M-type/MI/policy/role references only |
| One M01-M10 ingredient's selection decision, public interface, reusable rules/process, recipe actions, variation contract, configured `MI-*` occurrences, and task cards | `modules/<Mxx>.md` | M-type or `MI-*` references plus consumed public-interface facts only |
| Concrete provider/model/effort/tier or other launch selection for each workflow role | Sole canonical mapping JSON | Role key only; mapping path once in `plan-workflow.md` |
| Rule-application matrix and V01-V30 results | `validation.md` | Terminal validation status only in the delivery report |

If two artifacts contain independently editable prose for the same concern, the package is invalid.
Delete the duplicate and replace it with a reference to the authoritative ID.
The sole required exception is the immutable canonical FAST_LANE_V2 usage block copied verbatim into
every `STEP-*`. It is a non-editable usage reminder whose authoritative text lives in the execution
template, not a second step-local policy definition.

## 4. Composition-root contract

`plan-workflow.md` is the readable entrypoint. Put its dependency/import table immediately after the
plan contract so global rules and replaceable components are visible before workflow detail. It must:

1. name `global-rules.md`, `validation.md`, the steps directory, the M01-M10 module directory, and the
   canonical mapping once;
2. define the artifact authority and edit boundary for each import;
3. retain the full source/authority, goal, outcome, coverage, truth, deliverable, risk/cost, structured
   role-authority graph,
   typed-step graph, gate index, lane/resource/result/handoff, external, integration, and ledger content;
4. list every `STEP-*` and its file without copying the step's normal or fast-lane entry composition;
5. index M01-M10 and their files without copying their selection decisions, rules, actions, configured
   instances, or task cards; and
6. define inter-step runtime order only through typed edges, never through file order, module catalog
   order, or presentation order.

The composition root may state a step's public input/output because graph composition consumes that
interface. It must not restate a step's internal `MI-*` order or an M module's actions, reviewer count,
check fan-out, task-card text, failure procedure, or other module-owned process.

## 5. Step contract

Place each large, independently gated workflow unit in `steps/<STEP-ID>.md`. A step is a project-level
composition boundary, not an eleventh macro-module and not a replacement for M01-M10. Use the fewest
steps that give coherent independently decidable gates, useful public outputs, and maintainable
failure/continuation boundaries. Do not create a step merely for a file, role, command, or internal
module action.

Every step owns:

- its ID, objective, independently decidable outcome, and acceptance owner;
- activation predicate, predecessor outputs, public inputs, protected boundaries, and public outputs;
- the exact canonical FAST_LANE_V2 usage block, unchanged and directly beneath the entry-flow heading;
- exactly three ordered entry paths named `NORMAL`, `FAST_LANE_V2_SERIES_1`, and
  `FAST_LANE_V2_SERIES_2`, each with activation, consumed inputs, a distinct sequence using only its
  `MI-NORMAL-*`, `MI-FL2-S1-*`, or `MI-FL2-S2-*` prefix,
  produced exit, destination/continuation, checkpoint effect, concrete saved work, and fallback;
- one union inventory of the configured `MI-*` occurrences used by those entry paths, with
  consumed/produced values and conditions;
- its gate question/class, completion rule, failure/return routes, default-forward successors, and
  preserved prior results;
- concurrency, isolation, resource, lifecycle, expected-range, and critical-path effects that apply to
  the step as a whole; and
- citations to global policies, module instances, roles, graph edges, and external/integration records.

Directly after that canonical block, the exact entry-flow table is:

`Entry flow | Status and activation | Consumes | Ordered distinct MI-* path | Produces and exit | Destination or continuation | Checkpoint and invalidation rule | Concrete saved work | Failure/fallback route`

Its rows are exactly `NORMAL`, `FAST_LANE_V2_SERIES_1`, and `FAST_LANE_V2_SERIES_2` in that order.
`NORMAL` may use any project-justified combination and number of `MI-NORMAL-*` M01-M10 occurrences.
Series 1 uses a separate set of `MI-FL2-S1-*` occurrences in a
materially narrower path for a compatible set of scoped edits within this step, minimal
compile-plus-motivating-test smoke, independent review, integration, and exit to the ROOT-selected
later current progress bound. Series 2 uses a separate set of `MI-FL2-S2-*` occurrences in a
materially narrower path when this step is
that progress bound: receive/join accepted Series 1 exits, calculate input invalidation, preserve
unaffected PASS credit, run the earliest required remaining checks, and continue normal successors.
These responsibilities are behavioral requirements, not a fixed module count or universal sequence.
Fast paths should generally contain fewer MIs than NORMAL, but their decisive requirement is that
their configured work is purpose-built and materially lighter, not a renamed normal MI campaign.
Both series must always have configured, disjoint MI paths. Trigger state affects runtime timing only;
no step may disable, omit, relabel, reason away, or substitute the normal route for either fast path.

The exact configured-instance inventory table is:

`Order | Instance ID | Module type | Consumes | Produces | Activation/condition`

A step says which configured ingredients are combined, which one of the three disjoint entry paths
owns each occurrence, and how their public interfaces connect. Each fast path must identify
the concrete broad work or restart it avoids and must not be a renamed copy of `NORMAL`. It
does not copy how an ingredient operates. Editing a step's internal composition cannot require edits
to another step while the edited step's public interface, authority, and graph meaning stay compatible.
A step-only composition edit reorders or rewires already-declared `MI-*` references. Adding, removing,
or reconfiguring an `MI-*` also edits its owning M file because that file owns the instance definition;
other steps remain unchanged unless a public step interface changes, in which case update its actual
predecessor/successor consumers.

## 6. M01-M10 module-library contract

The `modules/` directory is the sole reusable component library for the emitted plan. It contains
exactly `M01.md` through `M10.md`, matching the unchanged macro-module catalog and recipe semantics.
Each file is one authoritative ingredient and owns:

- the module type, purpose, binary select/omit decision, free-form justification for an optional omission, and
  selected `MI-*` IDs;
- a stable public input/output interface and the compatibility promise steps may rely on;
- all module-specific rules, ordered recipe action IDs, decisions, routes, concurrency, isolation,
  lifecycle, and configurable variation points;
- every project-specific `MI-*` occurrence of that type, using the exact module-instance schema; and
- exactly one complete 20-field governing task card and at least one complete 20-field member task card
  for every selected occurrence, plus one member card for each internal worker dispatch. Every selected
  occurrence is executable and all card fields are concrete; `N/A` is forbidden in configured instances.
  The instance `Owner and roles` field inventories the exact member set as `CARD-ID=workflow_role`.

Every required recipe action remains present and in order. An instance specializes nouns, paths,
roles, inputs, checks, and allowed parameters without copying the module-wide rules or changing the
recipe's invariant. Global behavior remains a policy citation rather than module prose.

Treat M01-M10 like stable object types and `MI-*` like configured objects. For example, a NORMAL entry
may consume `MI-NORMAL-REVIEW-CAMPAIGN.complete_result_pool`, whose type is M04. Changing M04 from one reviewer to
two parallel reviewers plus a join changes only `modules/M04.md` as an authoritative workflow edit
when the public input, `complete_result_pool` output, authority, and semantic/parameter contracts
remain stable and the existing reviewer-role pool capacity/runtime slot cap already permits two
concurrent invocations. Add the second complete member task card inside that same M04 instance, rerun
validation, and refresh `validation.md` only if its recorded result or basis changes. Every step using
M04 inherits the behavior without editing its composition. If the public M04 contract changes, update every
step that actually consumes the changed interface. If the requested fan-out exceeds the existing role
capacity, update that Section 7 capacity contract too; that is a public resource-contract change, not
an internal M04-only edit.

An omitted optional module file retains its exact decision and justification but declares no active
instance. Its recipe definition is not an executable hidden phase. M10 remains the only extension
route when M01-M09 cannot express required workflow behavior.

This artifact split does not relax the orchestrator-to-worker boundary. ROOT remains the sole global
decision owner and authors direct-worker contracts by default. Only when the plan explicitly selects
the R3/R6 two-orchestrator-tier shape may ROOT give one lane sub-orchestrator a complete lane contract: outcome,
inputs, protected scope, mutable resources, workers, permitted local decisions, terminal handoff, and
return conditions. That sub-orchestrator then authors the governing/member cards and directs workers
inside that lane. A worker still owns only implementation or investigation mechanics within its card;
it never defines task meaning, scope, success, acceptance, correction routing, or another orchestration
tier. Cross-lane, shared-resource, changed-requirement, integration, real-attempt, and global acceptance
questions return to ROOT.

## 7. Global-rule contract

`global-rules.md` owns P01-P15 and every `EXC-*` definition. The composition root imports it before any
step or module behavior. Each policy retains its owner, trigger, mandatory action, exit, optional
result/record location, and consuming module IDs.

Steps and modules cite policy IDs. They may bind project-specific parameters inside those policies but
must not copy, weaken, strengthen, or reinterpret global prose. A compatible policy edit therefore
changes only `global-rules.md` as workflow authority; dependents retain their references. Rerun
validation and refresh its recorded result only when needed. If a policy's public contract changes,
validation identifies affected consumers from their citations.

## 8. Agent-mapping boundary

Keep workflow-role semantics in the composition root and concrete role-to-agent allocation only in the
canonical mapping JSON. Every module instance and step uses role keys. The mapping contains each
executable role exactly once and no workflow behavior.

Changing the agent, provider, model, effort, tier, or other concrete launch setting for an unchanged
role requires only a mapping edit. Rerun validation, but do not rewrite `plan-workflow.md`, global
rules, steps, M module files, task cards, or launcher code. A role-semantic change is different: edit
the role definition and validate every M module instance that cites the role.

## 9. Validation contract

`validation.md` owns the R1-R30/S1-S17 application matrix, V01-V30 results, and terminal
`PLAN_STRUCTURE=VALID` marker. It records validation; it defines no workflow behavior and cannot repair
a missing rule by citation.

The deterministic validator receives the plan directory plus the canonical mapping path. It loads all
required artifacts, rejects every missing or extra package item (including non-Markdown root files), resolves every graph-to-step,
step-to-instance, instance-to-module, module-to-policy, module-to-role, and plan-to-mapping reference,
and rejects duplicated authoritative definitions. It verifies that every step has exactly one
unchanged canonical FAST_LANE_V2 usage block in the required position followed by the three exact
entry rows, all entry paths use disjoint configured IDs with the required
`MI-NORMAL-*`/`MI-FL2-S1-*`/`MI-FL2-S2-*` prefix, every active `MI-*` is consumed by
exactly one entry path in its intended step composition, every M01-M10 recipe retains its required actions, and the
structured authority graph contains exactly one ROOT plus either direct terminal WORKER children or one
optional direct LANE_SUB_ORCHESTRATOR tier whose children are terminal WORKER roles, with reciprocal
parent/child declarations and no third orchestration tier. It also rejects malformed required ID-family
rows, STEP acceptance by a worker or an out-of-scope lane authority, a member lane/handoff whose
consumer is not that member role's owning orchestration authority, a selected M06-M09 represented only
by omitted behavior rows, bare N/A-equivalents or empty required STEP/module bodies, missing/unknown
typed STEP successors, duplicate gate-index identities, invalid governing/member authority classes,
unresolved card deliverable/gate/loop references, and missing member process/invocation correlation.
Validate semantic behavior manually before
recording `PASS`.
The validator also rejects an opt-out status or prose-disguised MI path in any entry, a step without
one concrete gate, uncovered or unknown requirement/deliverable references, bare
policy/rule/instance fields, unresolved exception definitions, and validation rows without a
substantive basis.
Structural checks can detect copied action IDs, headings, tables, and broken references; manual V14
must also reject paraphrased duplicate policy/module process and authority prose that a parser cannot
prove equivalent. The exact canonical FAST_LANE_V2 usage block is the sole intentional prose copy.

## 10. Change rules

For normalized source, classify changes at source owners first. The table below
describes the expanded/legacy locations of those facts, not a list of files to
hand-edit after compilation. In particular, a private MI/member edit changes its
step source, a shared recipe edit changes its library source, and all reciprocal
indexes are regenerated. Do not edit global source for a private addition unless
it actually changes a shared contract. See the normalized guide for build/check
and impact commands.

Classify each edit before changing artifacts:

| Edit | Authoritative workflow/configuration edits | Required follow-up |
|---|---|---|
| Concrete agent allocation for an unchanged role | Mapping JSON only | Rerun validation; do not edit plan Markdown or launcher code |
| Internal M module flow/process with unchanged public interface, authority, semantic contract, and role-capacity ceiling | That `modules/Mxx.md` only; all consuming steps inherit it | Rerun validation without editing consumers |
| One `MI-*` configuration within the owning module's allowed variation contract | That `modules/Mxx.md`; edit a step only if its composition/reference changes | Rerun validation |
| One step's internal module composition with unchanged public step interface | Reorder/rewire existing `MI-*` references in that `steps/<STEP-ID>.md` only; edit the affected M file too when adding, removing, or reconfiguring an `MI-*` because it owns the instance | Rerun validation |
| Global policy behavior with compatible policy ID/contract | `global-rules.md` only; dependent files remain references | Rerun validation |
| Concrete role semantics or authority | Role table and actual affected M module references/contracts | Rerun validation |
| Public M module interface | That M file and every step consuming the changed interface | Rerun validation |
| Public step interface or inter-step graph topology | That step and its actual predecessor/successor graph consumers in `plan-workflow.md` or other steps | Rerun validation |
| Requirement, deliverable, or step selection | `plan-workflow.md` and actual affected steps/modules | Rerun validation |

Do not edit every dependent artifact merely because an internal implementation detail changed. Do edit
real consumers when a public contract, semantic meaning, authority, or typed graph edge changes. This
is encapsulation, not permission to leave stale interfaces.
