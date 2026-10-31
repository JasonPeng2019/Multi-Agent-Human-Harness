# Normalized authoring and generated execution packages

Use the versioned source compiler for new formal Level 4 plans. Its purpose is
change locality: edit a fact at one owner and regenerate its readable indexes.
The full legacy execution-package grammar remains the output contract, so existing
validators and executors still receive concrete instructions. This is an authoring
tool, not a runtime scheduler, test runner or automatic plan reviewer.

## Source, output and mapping are different boundaries

Keep the authoring directory separate from the exact generated execution package.
Keep concrete agent launch settings in the project's existing canonical mapping.
Do not place the authoring source or compiler state inside the generated package;
the legacy validator intentionally rejects extra artifacts there.

Source owns workflow decisions. Generated Markdown is a read-only execution view.
Reviewers inspect relevant source owners and the compiled contracts; executors
consume only the current reviewed build. A generated root manifest may mention all
workers without making every worker an independently editable root-level decision.

For a still-unmigrated legacy package, the existing Markdown ownership rules remain
in force. Do not start editing half of a package as source and half as generated
output. Migrate into a separate source directory, inspect the conversion, and build
to a new output directory before switching consumers.

## Source schema and local editing

Schema version 1 uses this layout, produced by `init` or `migrate`:

```text
plan-source/
  topology.json
  card-defaults.json
  review.json
  steps/STEP-001.json
  modules/M01.json ... modules/M10.json
  .build-state.json                 # compiler-owned output hashes and impact baseline
```

JSON is data, not executable code. Duplicate keys, unknown fields and unresolved
generated slots are errors. Preserve narrative in `layout` strings: `@@NAME@@`
marks a generated view, never a second editable table. Use the initialized source
as the complete schema shape; the field descriptions below explain its ownership.

| Source object | Authoring contract |
|---|---|
| `topology.json` | `schema_version: 1`; `root_layout` and `global_layout` retain authored shared prose/decisions and generated slots. `roles` contains the role columns except `Directs`, derived from each child's `Reports to`. `policies` contains stable policy-row objects. `shared_manifests` and `shared_handoffs` retain genuinely shared lifecycle facts. `mapping_name` identifies the sole mapping; declared `mapping_roles` cannot substitute for validating the actual mapping file. |
| Step `contract` | The existing step contract fields except `Step ID`, derived from the filename. Acceptance owner is authored here, not again in the root index. |
| Step `public_interface` | Two distinct public input/output summary strings used in the root index. These are public composition promises, not copies of the step's internal instance sequence. |
| Step `gates` | Each `definition` supplies the existing 14 gate-table cells; `public_summary` supplies the three distinct public outcome/forward/return descriptions. Gate IDs and class in the root index are derived from the definition. Keep checking-instance subsets explicit. |
| Step `entries` | Exactly the required three entries. Each has the eight `values` cells from the entry table excluding its MI path, plus one ordered `path` array of instance IDs. The composition union/order/type is derived, not separately authored. |
| Step `instances` | Keyed by the uniquely owned MI ID. Each owns `module`, its narrative `layout`, `binding` (consumes, produces, activation), `cards`, and `policy_rows`. Use `${instance_id}` and `${module_id}` in the initialized heading rather than a second hard-coded identity. |
| Instance card | `kind` is Governing or Member; `id` is its sole card identity. `identity` owns schema, deliverable, cohort, gate and loop context; enclosing MI/card IDs are generated. `fields` contains task fields other than the composite identity, optionally inherited through `extends`. `layout` keeps the card presentation and generated field slot; use its generated card-identity binding. |
| Member `dispatch` | Owns `lane_id`, `handoff_id`, `process_id`, `invocation_id`, plus the meaningful `lane` and `handoff` lifecycle cells. `${lane_id}`, `${handoff_id}`, `${process_id}` and `${invocation_id}` references expand from this one object. Member inventory, root lane/terminal-handoff identities and producer roles are derived. |
| Step `manifests` | Optional local rows under `MANIFEST_1` (claims/locks), `MANIFEST_2` (checks), `MANIFEST_4` (source allocations), and `MANIFEST_5` (retirements), using the existing root manifest column order. These aggregate with genuinely shared root rows. Place a row locally only when that step truly owns its lifecycle. |
| Module JSON | `layout` owns reusable public interface, invariant recipe and allowed variations; `selection_reason` supplies the real selection/omission rationale. Selected instance IDs and configured instance bodies are generated from step ownership. |
| `card-defaults.json` | Named objects with `fields` and optional single-parent `extends`. Parent fields are overlaid by child fields, then explicit card fields. Identity is contextual, not inherited. All final task fields remain mandatory and concrete. Unknown parents/fields or cycles fail. |
| `review.json` | Actual `validation_markdown` and `approved_source_sha256`. The current hash is supplied by compiler output for recording after completed review. The compiler neither signs approvals nor generates semantic verdicts. |

Policy-row IDs are stable references, for example
`{"id":"P01-ROW-001","values":["owner","trigger","action","exit","result"]}`.
An instance's `policy_rows` cites that ID, not its position in an array. Reordering
policy rows must not rebind consumers; changing behavior under an existing ID is a
real shared-policy change requiring assessment of its consumers.

Optional step/instance `depends_on` entries use semantic unit keys such as
`interface:STEP-002`, `instance:MI-NORMAL-PREPARE`, `module:M03`, `policy:P02`,
`role:worker` or `default:read_only`. Use a public interface dependency when consuming
another step's public contract; a private implementation dependency is a stronger
coupling and needs a reason. The compiler also derives dependencies from actual
instance references, inheritance and root typed step edges. These keys are planning
references, not extra runtime identities or an evidence database.

For example, change one worker's private objective by editing only its card's
`fields.objective` in `steps/STEP-006.json`. Add a worker by adding one complete
member card and dispatch binding to that instance; do not also edit module selections,
member lists or root lane/handoff tables. Reorder existing work by changing only the
owning entry's `path`. Change a shared default only when the intention is to change
all its actual inheriting consumers. Each edit still requires appropriate semantic
review; local source ownership is not permission to change acceptance silently.

## Authoritative ownership

| Fact | Owner | Derived information |
|---|---|---|
| Shared requirements, role semantics/parents, actual cross-step dependencies and shared resource contracts | Root source | Root indexes and reciprocal role children |
| Step public boundary, gate and three ordered entry paths | Step source | Root step/gate indexes and ordered composition union |
| Configured module use, private bindings, cards and local dispatch lifecycle | Instance inside its owning step | M-module instance views, selection IDs, member inventory, lanes and handoffs |
| Reusable recipe, public module contract and permitted shared defaults | Module/default source | Fully expanded concrete instance/card instructions |
| Policy behavior | Policy source | Consumer inventory derived from actual citations |
| Actual rule assessments and independent review approvals | Review source and original evidence | Validation report presentation; no inferred PASS |
| Agent/provider/model selection for unchanged roles | Canonical mapping JSON | Runtime role resolution; no duplicated launch settings in Markdown |

References are not duplicate ownership. A gate may name a selected checking subset;
it is not automatically every MI. A role capacity and a member's cleanup instructions
are different facts. Preserve meaningful inputs such as activation, mutable roots,
durable-result location, publication and failure routes; never infer them from a
worker name or discard them merely because a manifest looks repetitive.

## Author, compile and review

Use the shipped `scripts/compile_topology.py` commands described by `--help`. Run
them from the formal skill directory or supply its script path explicitly.

```powershell
python -B scripts/compile_topology.py init --source C:/work/plan-source
python -B scripts/compile_topology.py build C:/work/plan-source --output C:/work/plan --mapping C:/work/mapping.json --draft
python -B scripts/compile_topology.py impact C:/work/plan-source
python -B scripts/compile_topology.py build C:/work/plan-source --output C:/work/plan --mapping C:/work/mapping.json
python -B scripts/compile_topology.py check C:/work/plan-source --output C:/work/plan --mapping C:/work/mapping.json
```

Initialization is a draft scaffold, never a preapproved project. Replace illustrative
values with inspected project facts, compose the required NORMAL and both fast-lane
entries, and author genuine semantic decisions. Do not use synthetic scaffold or
self-test identities as real review evidence. Draft output is not dispatch-ready.

Before acceptance, obtain the four independent group reviews under
[plan conformance](../../plan-conformance-review.md) and
[acceptance design](../../acceptance-design.md). Bind their final approvals to the
actual candidate. The compiler detects stale source approval but cannot authenticate
a review or assess the truth of prose. Updating an approval binding is an explicit
recording of completed review, not a workaround for compilation failure.

The source fingerprint concerns this compiler's material plan definition; it is
not a mandate to hash ordinary project inputs, cache entries or runtime observations.
Keep runtime evidence reuse under its actual input and state dependencies. Allocation
changes still require capability/capacity assessment where relevant; unchanged role
semantics do not justify rewriting every topology document.

Run full structural validation of every resulting package. Source freshness and
existing `validate_execution_plan.py` checks are complementary: the legacy validator
alone cannot establish that hand-edited generated bytes still match their source.
Do not hand-edit a generated table to obtain PASS; fix the owning source definition.

## Change procedure

1. Identify whether the change is private instance behavior, shared recipe/default,
   public step contract, policy, role/authority, shared resource or requirement scope.
2. Edit only its authoritative owner and real consumers. A local addition belongs in
   the step/instance source; no independently maintained root lane/member inventory
   is needed. Shared resources and cross-step edges remain explicit composition work.
3. Inspect the impact report and compiled diff. Unrelated step outputs should remain
   unchanged for a compatible private edit. A generated library/root file can change
   because it aggregates instances; that is not evidence that all instances changed.
   Impact compares against the last accepted build. Draft builds do not advance
   that baseline, so cumulative changes remain visible throughout review.
4. Obtain affected reviews and explicit unchanged-scope confirmations under the
   existing bounded panel rules. Preserve original findings and historical approvals;
   never manufacture approval by copying a new fingerprint into an old verdict.
5. Build/check the final candidate. Reuse runtime results only where actual source,
   non-source inputs, prerequisites and external state permit it. Full structural
   checking never automatically resets completed execution.

Reusable defaults reduce authoring repetition but do not relax the complete 20-field
dispatch contract. Use explicit inheritance and local overrides only within the
declared variation contract. Unknown fields, unresolved parents or cycles are errors.
Changing a shared default intentionally affects its consumers; a one-off variation
belongs in one instance. Semantic overrides that alter authority, acceptance or
required actions require the same review as writing those fields directly.

## Conservative migration

```powershell
python -B scripts/compile_topology.py migrate C:/work/legacy-plan --source C:/work/plan-source --mapping C:/work/mapping.json
```

Migration must preserve authored narrative and meaningful lifecycle values. It may
extract explicitly structured facts and remove their derived copies, but it must
reject an unsupported or ambiguous conversion instead of guessing or deleting data.
Inspect the source/output comparison before redirecting any executor. Keep the old
package as historical evidence; a migration is not permission to overwrite it.
Old reviews do not become new approvals by virtue of conversion. Retain the original
review evidence and follow the source compiler's explicit approval-binding rules.

Legacy claims, checks, allocations and retirements initially remain in
`shared_manifests`: their semantic owner cannot always be inferred from a table row.
When inspection establishes that a step owns a record, move that exact row to its
`manifests` once, preserving its lifecycle values. Subsequent local changes then
have one local owner; migration does not pretend to infer this boundary automatically.

## Limits and failure handling

- A local edit can still change public meaning. The impact report is advisory, not
  a semantic-equivalence proof or automatic permission to retain test credit.
- Missing facts and stale approvals leave the plan a draft. Structural output and
  placeholder material must never be called an accepted plan.
- Unexpected files, unresolved references, unsafe paths or manually altered generated
  output must be resolved at their owner. Do not force replacement of unknown data.
- Keep each generated package together when publishing it. A successful rendering
  does not authorize execution, deployment, resource allocation or project acceptance.
- Compact tiers use the same ownership principle with ordinary references. They do
  not need this compiler, its JSON source layout, or the formal review tables.
