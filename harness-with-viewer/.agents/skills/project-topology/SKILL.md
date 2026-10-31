---
name: project-topology
description: Build and validate a significant project execution workflow and plan, including justified roles, dependencies, independently gated STEP-* units, verification, repair returns, resources, and integration. Use only when the user explicitly wants to design or build a substantial workflow/plan for executing a project. Do not use for general coding, ordinary task execution, questions, diagnosis, implementation, or merely deciding how to perform routine work. At Tier 4, scan for and prefer a suitable subagent harness, but retain a no-harness fallback. This skill plans work without executing it.
disable-model-invocation: true
user-invocable: true
---

# Build a significant project execution topology

## Multi-agent workspace orchestration

Prefer direct ROOT-to-worker dispatch. At Tier 4, a justified bounded lane may
use `ROOT -> lane sub-orchestrator -> workers`: ROOT delegates explicit local
authority, the lane sub-orchestrator authors and directs its worker contracts,
and ROOT accepts the terminal lane result. The formal compiler and validator
support `ROOT_DIRECT_WORKERS` and `ROOT_WITH_LANE_SUB_ORCHESTRATORS`, with one
global ROOT and at most two orchestration tiers. Verify the selected runtime's
delegation capabilities before binding this hierarchy; installed launch helpers
alone do not establish them. The selected planning review panel remains global
and flat, with all required approvals and final ROOT acceptance across every lane.
Tier 4 retains its four distinct reviewer assignments.

## Admission boundary

Use this skill only to design the significant workflow and plan the user requested. Do not invoke it
as background ceremony for general coding or task execution, and do not execute the planned project
while compiling its topology. If the request is not to build a substantial reusable or durable
execution plan, handle it without this skill.

After the admission boundary passes, start at Level 1 and escalate only for a concrete reason. Use
Level 0 only as an out-of-scope verdict that this skill should not have been invoked; do not perform
the underlying coding or task from this planning skill. Project size, file count, or available
subagents alone do not justify coordination.

## Inspect before routing

### Freeze the requested outcome and authority

Before selecting a tier, state the user's actual deliverable, acceptance claims,
non-goals, requested tier/constraints and already-authorized execution. Background
project or research documents constrain the requested deliverable; they do not
silently expand it into a larger campaign. Trace every material stage and gate to
a requested outcome, binding requirement or justified necessary dependency.

### Review plan conformance and simplicity at every admitted tier

Apply [Adversarial plan review](references/plan-conformance-review.md) to every
Level 1-4 plan, including compact/no-harness plans. Levels 1-2 normally use two
independent assignments: SCOPE_STRUCTURE (scope/authority + topology/simplicity)
and EVIDENCE_EXECUTION (verification + execution/resources). Split an overbroad
pair into its separate domain reviewers under the reference's risk-based rule.
Levels 3-4 retain four distinct domain reviewers. Every active assignment gives
an evidence-backed PASS/BLOCK covering its domains; all required assignments
must approve the final revision before ROOT can accept. ROOT cannot override
a BLOCK. The reference defines group boundaries, bounded follow-up, cross-group
changes, requested-tier conflicts and executor handoff. Scale review depth to the
plan; this panel adds no execution lanes or execution tier.

### Require a justified acceptance design at every admitted tier

Before expanding checks, measurements or matrices, apply
[Acceptance design](references/acceptance-design.md): necessity of the evidence and
environment, multiplicity of repetitions/combinations, and proportionality of the
acceptance system itself. Required coverage remains binding; neither a representative
probe nor a complete matrix is automatically sufficient. Use the
[review assignment template](assets/plan-review-assignment.md) for each focused
reviewer, with its concrete inspection duties and evidence-backed PASS/BLOCK return.
The four domains have the assigned owners above; add no duplicate audit or execution lane.
Record concise assessments in compact plans and the specified per-STEP audit fields
in formal plans. Apply conditional guidance only when relevant, without prescribing
a universal test architecture or importing formal machinery into smaller tiers.

Apply [finding admissibility](references/acceptance-design.md#finding-admissibility-requirements-define-the-review-boundary)
to every reviewer and include it in planned reviewer task blocks. A true gap or
vulnerability that leaves the current requirements satisfied and all required
tests passing is `REJECT-OUT-OF-SCOPE`, invalid as a blocking/correction finding.
Require a concrete violated requirement or invalidated acceptance evidence before
admitting a finding. Passing tests alone never excuses a requirement violation.

### Assign test-scope and scheduling checks to their review groups

For every admitted plan, apply [Test-scope audit](references/test-scope-audit.md)
after drafting its suites and matrices and before final validation. A separate
read-only reviewer owning VERIFICATION audits all proposed verification surfaces for sufficient coverage,
over-specified oracles, redundant combinations, and repeated full suites. Functional coverage takes priority over reducing test count: the reviewer checks
actual assertions and missing failure/recovery boundaries as well as duplication.
The plan writer adjudicates criticism, adds or strengthens missing proof, and trims
only justified excess; ROOT owns the final scope. Preserve every binding requirement and every existing workflow rule
unless a specific conflict is established through the governing authority.

This is a narrow exception to this skill's no-dispatch planning boundary: launch
only the selected focused reviewers of the draft planning artifacts, never the planned
execution workers or product tests. Reuse valid group reviews under the shared
identity/revision rules instead of adding duplicate audits. This planning review does not by itself require a higher
execution tier. The reference defines bounded feedback and the incomplete route
when independent review is unavailable.

For substantial plan revisions driven by execution incidents, read
[execution efficiency](references/execution-efficiency.md). Compile applicable
fixes into the existing owning policies and modules, using the latest corrected
evidence; do not convert historical estimates into guaranteed savings or add
runtime automation claims without implementation proof.

For every substantial post-step matrix at Levels 3 and 4, and at Level 2 when
verification cost, stateful resources, dependencies or repair risk warrant it, apply
[Matrix execution](references/matrix-execution.md) and its reusable binding template.
Require concurrent isolated coordinates, immediate exit on incompatible terminal
states, complete failure collection, an explicit dependency graph, cause-group
repairs, affected-only reruns and reviewed coordinate/total wall-clock budgets.
The independent EXECUTION_RESOURCES reviewer rejects unnecessary serialization,
long terminal-state waits and repair-after-each-test loops. Preserve functional
coverage; test-process concurrency does not add writers or escalate the level.

That reference owns test scheduling and its review criteria, including local versus
live resource limits. Fill its concrete command/capacity binding in existing plan
fields and include it in the EXECUTION_RESOURCES audit; do not duplicate the contract.

Evaluate:

- independently deliverable outcomes;
- dependency order and likely file overlap;
- codebase breadth and architectural uncertainty;
- consequence and reversibility of mistakes;
- available deterministic checks;
- external, scarce, destructive, or stateful resources;
- value of independent review;
- coordination cost relative to implementation cost; and
- available native subagents or a suitable command-line agent.

## Choose the level by execution capacity, not by project size

Choose execution tier and plan organization separately. The tier follows required
coordination, ownership, authority and recovery controls. Organization follows
change ownership: one cohesive document or independently editable sections/files.
Requests for a "modular plan", separate step/lane files or reusable components do
not by themselves select Tier 4 or the formal compiler. File names, including
`STEP-*`, are not evidence of a need for formal orchestration.

Use [Change locality](references/change-locality.md) at every tier. Levels 1 and 2
normally stay in one compact document; permit separate components when justified
without adding writers, gates or another tier. Level 3 normally organizes work by
its proven independent lanes, using sections or files according to their size and
revision needs. Level 4 may also use either organization; explicitly selecting the
full formal framework selects its exact package and all its guardrails.

Workspace installation paths: the canonical skill is `.agents/skills/project-topology/`
and its Claude mirror is `.claude/skills/project-topology/`. Source-project examples in
the shipped blocks use `.codex/skills/project-topology/`; when binding a command here,
substitute the installed `.agents/skills/project-topology/` prefix (or the Claude mirror).
Include `.agents/` in the harness scan alongside the directories listed below.

For Tier 3 and Tier 4, read [Shipped execution blocks](references/execution-blocks.md) when constructing
the plan. Bind the applicable packaged helpers and project adapters to existing stages/cards. Prefer
an equivalent host implementation; do not make each project rebuild readiness, isolation, result
recording, or repair-selection machinery. Select the smallest sufficient blocks from observed risks.
The skill ships executable mechanics, not an application-specific simulator or an OS sandbox.
Planning may validate profiles and skill helpers; it must not execute the planned product or live work.

Record which dependencies can be checked early, an early executable path through risky shared seams,
review/retest invalidation boundaries, supporting-tool payoff, expected critical path, and the event
that triggers reassessment. Preserve user-selected models and accepted work. The shared reference
defines the contracts once; Tier 4's existing rules and fixed package remain authoritative.

In this skill, **level** and **tier** mean the same thing. The tier is not a
measure of how many files, tickets, or agents exist. It is a decision about how
much work, uncertainty, and checking can be safely held by one execution
context before the agent is likely to miss a dependency, make an unexamined
assumption, or integrate a locally correct change into a globally wrong result.

Judge the whole execution job, not merely the first implementation action. The
job includes learning the relevant system, making the important design choices,
making the changes, running the right checks, understanding ordinary failures,
repairing them, and deciding that the integrated result meets the acceptance
conditions. A project with many files can still be Tier 1 when all of that work
is coherent and predictable. A small diff can require Tier 2 or higher when a
mistake has a large blast radius or the correct choice depends on knowledge the
primary agent cannot reliably establish alone.

### The one-sitting test

"One sitting" does not mean a stopwatch estimate or an expectation that the
agent works without tools. It means one competent agent can keep a coherent
mental model from initial inspection through final verification, including the
normal surprises that reasonably occur. Ask whether that agent can do all of
the following without becoming a weak single point of failure:

1. Map the relevant code, data, contracts, and operating constraints.
2. Resolve the material unknowns rather than guess through them.
3. Make and revise the design decisions that affect the result.
4. Implement every required change and understand the interactions among them.
5. Run the appropriate checks, diagnose ordinary failures, and repair them.
6. Inspect the integrated result and make a credible final acceptance decision.

If the honest answer is yes, the work can be Tier 1. If the answer is "maybe,
but a missed assumption or a fresh set of eyes could easily expose a serious
problem," do not call it Tier 1 just because one agent might finish a patch.
Use Tier 2. The point is not whether an agent can produce bytes; it is whether
one agent can produce and verify the correct result without an unacceptable
chance of a major mistake.

### Tier 1: one agent owns the complete delivery

The planning panel still checks acceptance necessity, multiplicity and
proportionality. For a small coherent verification route, a short claim/check and
environment rationale, explanation of any repetitions, and justification of the
simple existing approach suffice. These planning checks do not add execution roles.

Choose Tier 1 when one agent can safely own discovery, decisions,
implementation, integration, and verification in one coherent pass. The work
may still be significant: it can have several ordered stages, touch multiple
areas, or require a durable written plan. What makes it Tier 1 is that the
agent does not need a separate implementation lane, independent investigation,
or fresh review in order to make the work safe.

Use Tier 1 when the relevant architecture is understandable, the interfaces are
known or can be decided locally, the changes are tightly related, and the
available checks give the agent useful feedback. A feature concentrated in one
service with established conventions and deterministic tests is often Tier 1,
even if it changes more files than a supposedly smaller task elsewhere.

Do not use Tier 1 merely because the request sounds contained. Move up if the
agent would have to carry too many coupled decisions at once, if important
behavior is hidden behind unfamiliar boundaries, if verification is weak, or if
a wrong choice could quietly damage data, security, users, or a later release.

### Tier 2: one delivery agent, plus independent evidence or review

Choose Tier 2 when a single agent should not be trusted to work entirely alone,
but one agent can still remain the sole implementation owner after receiving
independent evidence or feedback. Tier 2 adds a real second perspective: an
investigator maps an unknown area, a reviewer challenges a plan or draft, or a
tester independently checks a defined risk. That second lane is not ceremonial.
It exists because the work would otherwise be too easy to misunderstand,
under-test, or accept too confidently.

The primary delivery agent still owns every write, the final integration, and
the final decision. The helper lane is normally read-only and returns evidence,
critique, or test findings; it does not become a competing author. The useful
shape is usually primary investigation or draft, independent review or
investigation, primary correction, then verification. The review can happen
before implementation when it must inform a design choice, or after a draft
when it must find omissions in the concrete result.

Tier 2 is appropriate when an independent look makes the remaining work safe:
for example, an unfamiliar subsystem needs focused mapping, a change crosses a
meaningful interface and needs a design critique, a security or data assumption
needs separate scrutiny, or a non-obvious regression needs targeted test
discovery. The primary agent must still be able to absorb the findings,
implement the correction, and validate the result in one coherent delivery
context. A reviewer is not a way to hide implementation that is already too
large or too interdependent for one writer.

#### Design a Tier 2 plan as one delivery route with one purposeful support lane

Do not write a Tier 2 plan as "primary agent implements; reviewer reviews." The
plan must say what uncertainty or risk the second agent removes, when it does
so, and exactly how the primary agent uses the result. Begin by naming one
delivery owner. That owner is responsible for the scope, every implementation
write, integration, corrections, and final acceptance. Then turn the reason for
Tier 2 into a bounded support assignment.

Use this sequence when designing the plan:

1. State the primary outcome, acceptance checks, and the one or two risks that
   make solo delivery unsafe. Do not send a helper to "look around" without a
   decision it is meant to inform.
2. Choose the support-lane type that addresses that risk: repository mapping or
   test discovery before design; a plan critique before implementation; a diff
   review after a draft; or an independent targeted test after the primary
   change. One lane may answer several tightly related questions, but do not
   turn it into an unbounded audit.
3. Give the support agent a read-only task card with the exact question, allowed
   repository area, relevant entrypoints, evidence to return, checks it may run,
   and its completion condition. Require concrete findings--paths, call flows,
   test results, risks, or an explicit "no issue found"--rather than a general
   opinion.
4. Put a collection checkpoint in the plan. The primary agent reads the
   returned evidence, resolves conflicts, records the implementation decision,
   and only then continues or corrects the draft. Findings are inputs to the
   delivery owner, not a vote and not permission for the helper to change code.
5. End with primary-owned implementation, focused verification selected from the
   evidence, and final acceptance on the integrated result. The plan must say
   which finding causes a correction loop and which result is sufficient to
   proceed.

The timing should match the risk. Investigate before implementation when the
unknown determines the design. Review a concrete draft when the danger is an
omission or bad interaction that only appears in the diff. Run an independent
test after the draft when the danger is behavioral regression. A good Tier 2
plan can therefore be written as `scope -> primary map/draft -> independent
evidence -> primary decision/correction -> verification`, with a clear reason
for every arrow.

If the support findings are likely to require several agents to write separate
subsystems, create substantial test infrastructure, or repeatedly reopen the
shared design, Tier 2 is too small. Replan at Tier 3 rather than attaching more
reviewers to one overloaded writer.

### Tier 3: multiple implementation lanes with parallel review and testing

Choose Tier 3 when one delivery agent plus one independent reviewer is still
not enough to safely complete the work. At this point the problem contains
several substantial pieces that need active ownership, not merely advice on a
single writer's patch. Typical signs are separate implementation areas that
must move together, specialist testing or evaluation work that cannot be
treated as a final spot check, or a total cognitive load that remains too large
after a good review has reduced uncertainty.

Tier 3 uses multiple lanes. A decision owner defines the shared outcome,
interfaces, and integration order. Two or more implementation lanes own
different, genuinely independent deliverables. Independent review and testing
lanes run in parallel where they can expose risks early. The decision owner
then integrates the lanes, resolves cross-lane findings, and runs checks on the
combined result. This is the right tier when the work must be divided to make
it reliable, but the divisions can be made explicit and stable.

Before choosing Tier 3, prove that the implementation lanes are real. Each lane
needs a disjoint write boundary, declared inputs and outputs, an acceptance
check, and an integration order. If two writers would both redesign the same
contract, edit the same migration, update the same generated output, or decide
the same release behavior, they are not independent lanes. Stage that shared
work under one owner, or choose Tier 4 if the staging itself becomes a serious
coordination problem. Extra agents, worktrees, or a desire for speed do not by
themselves make a project Tier 3.

#### Design a Tier 3 plan around stable lanes and a deliberate integration path

Start the plan with the shared outcome, the decision owner, and the integration
contract--the interfaces, invariants, compatibility rules, and acceptance
criteria that every lane must honor. If a shared contract still needs to be
designed, put that work in an explicit serial stage owned by one agent before
parallel writing starts. Do not ask multiple lanes to discover and negotiate the
same seam while they implement it.

For every implementation lane, write an ownership row before assigning work:

| Lane | Deliverable | Allowed write boundary | Inputs it may rely on | Local acceptance check | Integration order |
| --- | --- | --- | --- | --- | --- |
| <name> | <finished outcome> | <paths, component, or worktree> | <frozen contract or prior stage> | <specific check> | <number> |

The row must describe a finished deliverable, not a vague activity such as
"work on backend" or "help with tests." A lane begins only after its declared
inputs are available. It returns a result that the decision owner can integrate
without rediscovering its scope: changed files or patch, checks run and results,
assumptions, integration notes, and unresolved risks. Use separate worktrees or
other isolation when the boundaries require it; do not use isolation as a
substitute for a real boundary.

Then design the plan in this order:

1. **Prepare the shared seam.** Define or freeze the contracts, common
   configuration, generated artifacts, migration decisions, and acceptance
   rules that writers must not independently alter. Assign one owner to any
   unavoidable shared edit.
2. **Dispatch independent implementation lanes.** Give each lane its ownership
   row plus a task card: objective, exact write boundary, accepted inputs, local
   checks, return format, and completion condition. State which lanes may run in
   parallel and which must wait; do not imply parallelism from their numbering.
3. **Run targeted review and test lanes beside the writers.** A review lane
   should inspect a named contract, threat, behavior, or lane output. A test
   lane should exercise a named integration, regression, performance, or
   compatibility risk. Specify when each receives artifacts and whether its
   findings route to the lane owner or directly to the decision owner.
4. **Integrate serially.** Name the order in which the decision owner brings
   lane results together, the checks after each material integration point, and
   the full-system verification after all lanes are present. Workers do not
   merge each other's changes or make final release decisions unless the plan
   specifically grants that authority.
5. **Define the repair rule.** A local defect returns to the owner of that
   lane. A problem that changes a frozen contract, overlaps two write
   boundaries, or invalidates the integration order stops parallel writing and
   returns to the decision owner. Re-stage under one writer or promote to Tier 4
   when the repair itself needs durable multi-stage coordination.

Tier 3 is successful only when the plan makes the parallel work and the serial
work equally visible. If reviewers and testers are merely listed at the end, or
if the integration owner has to invent ownership after workers return, the plan
is not ready. Read the Level 3 reference when constructing the detailed task
cards and isolation strategy; the main plan must still show the lane table,
dependencies, review/test routes, integration order, and repair path.

### Tier 4: formal full-project orchestration

Choose Tier 4 when Tier 3's clear lanes and one integration cycle cannot safely
contain the project. This is the full-project tier: the work needs durable
staging, explicit gates, and active control over dependencies, not just more
people working in parallel. It is appropriate when tightly coupled changes,
external or live state, irreversible operations, rollout and rollback
decisions, scarce resources, long dependency chains, or repeated integration
and repair cycles make an informal multi-lane plan too fragile.

#### Prefer a subagent harness; scan the repository first

At Tier 4, a suitable subagent harness is preferred. Before choosing the
execution shape, scan the repository and its documented tooling for one. Inspect
the repository instructions, Claude and Codex configuration, `.agent/`,
`.codex/`, and `.claude/` directories, workflow or automation folders, agent
skills, scripts, CI definitions, templates, and project documentation. Do not
treat a directory or script named "agent" or "harness" as sufficient evidence.
Determine whether it actually provides useful control for the planned work:
scoped worker dispatch, isolated write ownership, task or result collection,
verification gates, integration, and repair or recovery handling.

When a usable native or repository-provided open-source harness is present, the
Tier 4 plan uses it. Name the harness and its entrypoint, map the planned stages
and lanes to the controls it provides, and keep the plan's ownership, gates, and
handoffs consistent with that harness. Do not create a parallel coordinator,
status system, or task-card format that duplicates controls the selected harness
already supplies.

If the repository has no suitable harness, a compatible open-source harness may
be selected when the project permits its adoption, or a small purpose-built
harness may be planned when the missing controls genuinely repay the effort.
Neither option is automatic: this planning skill does not install, run, or build
the harness, and it must not invent a generic framework merely to satisfy a
Tier 4 label. If no harness is available or selected, use the no-harness Tier 4
guidance below and continue planning normally.

Whenever the topology recommends Tier 4 to the user, make a harness
recommendation explicit. Name the suitable native, open-source, or scoped
purpose-built harness that the plan recommends using. If the scan finds no
usable harness and none is selected, state that plainly and recommend the
no-harness Tier 4 path. Do not bury this choice in implementation detail or
present a Tier 4 plan as if a harness decision had not been made.

The formal compiler is mandatory when the user explicitly requests the full formal
execution-package framework, its M01-M10 library, FAST_LANE_V2, or the formal harness
workflow, or the applicable project workflow requires that framework. Generic
requests for modular organization, reusable components or independently editable
step/lane files do not select it. Record the actual framework-selection reason.
Once selected, do not downgrade to a compact/no-harness plan because an input is
missing, the schema is demanding, or validation fails. Obtain the missing input or
report the formal package incomplete; never omit the selected requirements.

At Tier 4, make the control structure part of the plan. Name one final decision
owner; define dependent stages, acceptance gates, resource authority,
integration points, rollback or recovery paths, stop conditions, and the
evidence required to proceed. Give each lane a bounded outcome and a terminal
handoff. Keep a record of the decisions that later lanes must not silently
re-open. Verify the whole system at the risk-appropriate levels, not only each
lane's local patch.

"Full" does not mean maximizing the agent count or forcing the creation of a
new harness when none fits. A tightly coupled Tier 4 stage may deliberately use
one writer, including inside a harness, because parallel edits would make it
less safe. Tier 4 means using the strongest coordination and recovery structure
that the project actually needs. Examples include a live data migration coupled
to application versions, access policy, observability, rollout, and rollback;
or a multi-service change with shared contracts, phased compatibility, and
release gates that no single parallel integration pass can safely settle.

### Resolve the boundaries directly

- **Tier 1 versus Tier 2:** Ask, "Would I accept this result if the same agent
  performed every important inspection and review?" If a fresh independent
  investigation or review is needed for confidence, choose Tier 2.
- **Tier 2 versus Tier 3:** Ask, "After the reviewer returns, can one delivery
  agent still own all implementation and verification without overload?" If
  not, and the work has provable independent implementation or test lanes,
  choose Tier 3.
- **Tier 3 versus Tier 4:** Ask, "Can fixed ownership boundaries plus a defined
  integration order control the whole project?" If not--because sequencing,
  external state, recovery, or coupled decisions require continuing formal
  control--choose Tier 4.

Always choose the lowest tier that makes a correct outcome realistically
achievable. De-escalate when later inspection proves the work is smaller or
more coherent than expected. Escalate immediately when new evidence invalidates
the current tier's safety assumptions; do not keep a too-small topology merely
because it was selected first.

## Levels and construction references

| Level | Use when | Construct it by |
| --- | --- | --- |
| 0 — Out of skill scope | The request is general coding, diagnosis, a question, ordinary task execution, or does not ask for a significant workflow/plan. | Stop using this skill and return control to the ordinary task handler; do not execute that task from this skill. |
| 1 — Significant single-agent plan | One agent passes the one-sitting test and can safely own the whole delivery. | Author the requested plan: outcome, ordered stages, affected areas, material assumptions/risks, ownership, and verification. Keep one writer and one integration context. |
| 2 — Planned delegated investigation or review | One agent should not work alone, but one delivery owner plus independent evidence or review makes the work safe. | Read [Level 2 — investigation and review](references/level-2-investigation-and-review.md) and encode the delegation contract in the plan without dispatching it. |
| 3 — Planned parallel implementation | One delivery owner plus review is insufficient, and the project has proven non-overlapping implementation or test lanes. | Read [Level 3 — parallel implementation](references/level-3-parallel-implementation.md) and encode writers/worktrees in the plan without launching them. |
| 4 — Formal multi-agent execution plan | Neither a single delivery owner with review nor fixed lanes with one integration pass can safely control the project. | First scan the repository for a suitable subagent harness and use one when available; otherwise write the concise durable no-harness plan below. When the project has (or the user explicitly requests) the formal harness workflow, use the preserved [Level 4 plan compiler](references/level-4-design-project-topology/SKILL.md) and every reference it requires. |

### Level 4 without a formal harness

Use this path when the Tier 4 harness scan finds no suitable harness, or when no
harness is selected for the project. It is a normal fallback, not a failure and
not a reason to stop planning.

Keep one global decision owner and construct a readable durable plan with only:

1. outcomes and acceptance checks;
2. dependent stages and their order;
3. writer/reviewer ownership, including where one writer is required;
4. resource authority, rollback/recovery, and stop conditions where genuinely relevant;
5. integration points; and
6. focused, relevant, and full verification gates appropriate to the risk.

An ordinary non-formal Level 4 plan may remain one cohesive artifact or use
independently editable components under [Change locality](references/change-locality.md).
Its organization alone does not select the formal compiler. If the full formal
framework is selected under the routing rule above, emit its exact modular
plan/workflow package: a composition root for outcomes and inter-step order,
shared rules defined once near the top, concrete role-to-agent allocation in one separate mapping, one
file per independently gated `STEP-*`, and configured instances of the reusable M01-M10 modules. Give
every STEP file exactly three entry-flow definitions: its normal flow, `FAST_LANE_V2_SERIES_1` as the
outbound-patch path for a scoped repair inside that step that exits toward the later current progress
bound, and
`FAST_LANE_V2_SERIES_2` as the inbound-reconcile path for receiving accepted repairs when that step is
the current progress bound.
Both fast-lane paths are unconditional required plan content in every STEP. A step may not disable,
omit, relabel, reason away, or replace either path with the normal flow. Runtime execution waits for
the stated trigger, but trigger state changes execution timing only and has zero effect on the required
rows, configured MI paths, contracts, or validation obligations.

Within the selected formal Tier 4 framework, hard requirements have no waiver mechanism: `N/A`, eligibility/ineligibility,
justification, omission, deferral, trigger state, cost, or missing facts cannot remove them. Only the
formal compiler's explicitly named optional module/profile/manifest/topology choices may be omitted,
and their free-form justification has no authority over fixed package, STEP, fast-lane, gate, coverage,
policy, card, mapping, or validation requirements.
Give their configured module instances the exclusive prefixes `MI-NORMAL-*`, `MI-FL2-S1-*`, and
`MI-FL2-S2-*`, respectively. Never reuse an MI across entries. Derive each fast path as a genuinely
lighter, purpose-built route; do not rename or replay the normal entry's heavy MI sequence.
Directly beneath every STEP's `## Normal and FAST_LANE_V2 entry flows` heading, copy the exact
canonical FAST_LANE_V2 usage block from the formal execution-plan template without editing it. Put the
step-specific three-entry table immediately after that identical block.
Give each M module one authoritative rule/process file and make steps reference its stable public interface
rather than copy module behavior. Preserve those interfaces so an internal M-module change propagates
to every consuming step without parallel edits. Do not present a reduced formal package or empty
sidecars as compliant; every formal compiler output uses the full fixed package.
These formal contracts do not apply to other plans merely because they use modular organization.

Subagents remain optional. A tightly coupled Level 4 task may still have one
writer. Do not invent a role registry, lock service, evidence database, fixed
plan grammar, or generic harness just because the task is serious. The Tier 4
harness preference requires a repository scan and use of a suitable harness when
one is available; it does not require manufacturing one when none fits.

The default Level 4 shape remains one root orchestrator dispatching workers
directly. A two-orchestrator-tier shape, `root orchestrator -> lane
sub-orchestrators -> workers`, is also available when separately bounded lanes each need enough
internal sequencing, local finding triage, or coordination to repay another
orchestrator. It is never required merely because work is large or parallel.
When selected, the root plan defines each lane's outcome, boundaries,
cross-lane dependencies, resource authority, and terminal acceptance. The
authorized lane sub-orchestrator concretely authors, dispatches, and directs
the worker cards within that lane, then returns one terminal lane handoff to
the root. Do not add a third orchestration tier; use direct workers when that
extra coordination does not earn its cost.

## Escalate and de-escalate

- Level 0 to a planning tier: the user explicitly requests a significant
  workflow/plan. Choose Level 1 only when one agent passes the one-sitting test;
  otherwise start at the first higher tier whose safety shape is actually needed.
- Level 1 to 2: one agent can no longer safely deliver alone; independent
  investigation, critique, or testing is needed to make a single-writer delivery
  credible.
- Level 2 to 3: even after that independent input, one delivery owner cannot
  safely contain all implementation and verification, and real non-overlapping
  implementation or test lanes can be proven.
- Level 3 to 4: fixed lane boundaries and one defined integration pass no longer
  control the dependencies, state, recovery, or release risk; the project needs
  formal stages and gates.
- Promote directly to Level 4 when those formal-control conditions are already
  clear. Do not spend time pretending that a Tier 2 or Tier 3 shape is safe.
- De-escalate only when new evidence shows that the lower tier can safely own
  the work; do not retain added structure that no longer reduces real risk.

Do not keep a task multi-agent merely because it was initially described that
way. Never create a role registry, model map, roster, lock service, module graph,
or plan validator for ordinary repository work.

## Preserve progress across worker recovery

For every plan with worker lanes, read
[Worker continuity and recovery](references/worker-continuity-and-recovery.md).
Plan two narrow same-thread correction attempts after an initial malformed or missing result when
the runtime supports verified continuity, stopping early when the result becomes valid. Give the
second attempt even if the first repeats the error or makes no progress. Persistent malformed output
or nonprogress warrants a fresh lane only after both attempts fail; unavailable or unsafe continuity
still requires earlier reconciliation. Carry retained work and attempt history into recovery from
the first unresolved action. Preserve accepted work and native
compaction; a report defect must not cause a full implementation, review, or test replay.
Compile this behavior into the plan's existing recovery rules without adding a coordinator or
relaxing its required gates. This remains planning guidance; do not launch recovery workers here.

For recurring failures, plan prevention as well as recovery: repair authoritative launch
configuration and prove the required headless tool action; use a shared native result emitter and
preflight; and require replacement assignments to retain useful discovery and name what changed
after nonprogress. Preserve worker-authored judgments and existing independent-review obligations.

## Keep plan changes local

Apply [Change locality](references/change-locality.md): one authoritative owner per
fact, stable public contracts, and references or generated views instead of manually
synchronized copies. A private step/instance change must not require rewriting
unrelated steps. Shared authority, interface and capacity changes still reach their
real consumers. Distinguish full structural checking from affected semantic review
and runtime evidence invalidation; rebuilding a view does not reopen completed work.

For new formal Level 4 plans, use the
[normalized authoring compiler](references/level-4-design-project-topology/references/normalized-authoring.md).
Its separate source owns step-local instances and reusable defaults; the exact
expanded Markdown package remains the validated execution view. Compact Levels 1-4
retain simple owners and references without adopting this source/compiler machinery.

## Delegation contract

Every delegated task represented in the plan states:

- exact scope and question/outcome;
- relevant files or repository area;
- whether it may write and its ownership boundary;
- expected response (findings, patch, or implementation summary);
- checks it may or must run; and
- completion condition.

Workers return concise findings, changed files, checks run, and unresolved risks.
The planned primary agent remains responsible for truth, integration, and final claims. Author these
contracts only; do not dispatch workers while using this skill.

## Output

Normally return:

```text
Topology: Level <0-4> — <name>
Reason: <one or two observed reasons>
Execution: <single agent, delegated reads, isolated writers, or staged plan>
Construction: <out-of-scope / significant plan / named reference>
Organization: <one document / independently owned sections or files; ownership and revision rationale>
Formal framework: <not selected / selected with explicit user or project-workflow basis>
Verification: <focused, relevant, or full strategy>
Acceptance design (Levels 1-4): <claim/boundary/environment necessity; repetition or combination rationale; simpler adequate choice and material cost basis>
Plan review (Levels 1-4): <selected assignments, covered domains and split rationale if any; distinct reviewer identities/verdicts, final revision, evidence, unresolved findings, aggregate PASS / BLOCK / PENDING>
Execution handoff (Levels 1-4): <authorized actions, conditional operations and stopping point>
Harness recommendation (Level 4 only): <named harness to use, or "none found; use the no-harness Tier 4 path">
```

For Levels 1–4, add only enough plan detail for a later executor to execute safely. Do not perform the
planned work in this skill.
