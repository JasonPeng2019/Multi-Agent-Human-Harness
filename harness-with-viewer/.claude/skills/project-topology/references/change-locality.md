# Make changes at their owners

Apply this principle at every admitted tier. Modularity means that a private change
preserving a component's public contract has one authoritative edit location. A
directory split alone does not establish that property. Avoid imposing a registry,
compiler or package on a compact plan; clear owners and stable references suffice.

## Organization is independent of execution tier

Choose the lowest sufficient execution tier from the work's coordination needs.
Modular organization is available at every tier and is usually useful at Levels 3
and 4. Levels 1 and 2 normally need only one cohesive document; a justified local
split does not add implementation owners or change the tier. Sections can provide
ownership boundaries before separate files become worthwhile.

At Level 3, the root owns the requested outcome, shared interfaces, cross-lane
constraints, assurance and integration decisions. Each proven independent lane
owns its implementation detail, local verification and handoff contract. Keep
shared decisions once and link to lane-owned details. A private lane revision
that preserves those public contracts must not require rewriting other lanes.
Use the concrete organization in [Level 3](level-3-parallel-implementation.md).

Do not infer the formal Level 4 framework from the words "modular", "step", a
`STEP-*` filename, or a request for separate files. Explicit selection of the full
formal framework, or a governing project workflow requiring it, retains all its
mandatory paths, recipes, cards and validation. A non-formal modular plan must
not claim formal-package compliance. The named M/MI/P contracts below apply when
that framework is selected; otherwise apply their ownership principles using
ordinary references without creating formal registries or schemas.

## Separate decisions from their projections

- A step owns its internal sequence and configured uses of reusable modules. A local
  instance owns its particular task bindings, member dispatches and local lifecycle
  data. Adding an internal check does not add a new cross-step graph edge unless the
  public dependency really changes.
- Shared module definitions own invariant behavior and permitted defaults. An
  instance-specific variation belongs to that instance, not the definition inherited
  by every other step. A shared behavior change must intentionally identify consumers.
- The root owns cross-step dependencies, shared capacities and authority. These are
  real composition decisions. A root index of local members is a derived view, not
  another editable source of their identity, order, role or terminal handoff.
- Policy definitions own behavior; consumers cite policy IDs. Reverse consumer lists
  are derived. Role parents determine child inventories. Do not maintain both sides
  manually in a source format that can derive the reverse relation.
- Resource activation, cleanup, result durability and acceptance are distinct facts,
  not incidental strings the compiler may guess. Put each with its actual owner;
  only genuinely shared resource contracts belong in a global authored registry.
- Actual reviewer findings, authorization and semantic acceptance cannot be derived
  from graph shape. Keep them authored evidence, even when their presentation is
  generated. Compiling a plan never grants permission to execute it.

For new formal Level 4 plans, use the
[normalized authoring compiler](level-4-design-project-topology/references/normalized-authoring.md).
Its source definitions own behavior; the existing fully expanded execution package
is a generated projection. All existing runtime, fast-lane, card and validation
requirements still apply to the expanded package. Do not edit source and projection
independently. Legacy packages remain supported until explicitly migrated.

## Review a change for locality

TOPOLOGY_SIMPLICITY must inspect at least the concrete change boundary at issue:
identify its authoritative definition, public inputs/outputs and actual consumers.
Challenge any manually maintained second definition or need to rewrite unrelated
steps. Ask whether a member addition, private instruction change or entry reordering
can be expressed at one owner. For a new formal design, inspect the source and its
compiled views; complete generated tables are not evidence of good ownership.

VERIFICATION checks that claimed compatibility really preserves observations and
acceptance meaning. EXECUTION_RESOURCES checks genuine shared-capacity, isolation
and lifecycle effects. SCOPE_AUTHORITY checks any changed authority or requirement.
An internal edit is not an excuse to hide a public semantic change. If a contract
changes, update its actual consumers and obtain the affected review decisions.

Do not require exactly one changed file for every change. A new requirement, shared
resource limit, interface or authority relationship legitimately affects multiple
owners. Count authoritative decisions that must be edited, not generated file count.
A global generated module file may change because one instance changed; that does
not invalidate every other instance using the same module type.

## Three different validation boundaries

1. **Structural closure:** checking the complete composed graph is cheap and remains
   mandatory for formal output. It catches broken references across otherwise local
   edits. A valid old fragment cannot excuse an invalid composed package.
2. **Semantic review:** use changed definitions and consumed contracts to bound
   affected review, preserving the selected independent assignments and explicit
   unchanged-scope confirmation rules. A compiler impact report is a review aid,
   not a substitute for reviewers or an automatic declaration of equivalence.
3. **Runtime evidence:** retain accepted results only where their actual inputs,
   dependencies and external state remain compatible. Completed steps need no
   automatic replay because a plan projection was regenerated. Conversely, completed
   status never protects evidence invalidated by a real dependency change.

Keep historical results and their original claims intact; record changed scope
separately. Do not reset completion, relabel FAIL as PASS or rewrite old approvals
to make a revision look accepted. Uncertain dependency impact requires an explicit
assessment and the existing affected/uncertain-evidence rules.
