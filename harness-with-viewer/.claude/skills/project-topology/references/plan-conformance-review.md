# Adversarial review of plan scope, simplicity and skill conformance

Apply this review to every admitted Level 1, 2, 3 or 4 plan, including compact
and no-harness plans and direct use of the formal compiler. Level 0 remains an
out-of-scope verdict, not a reason to launch reviewers. Scale independent reviewer
assignments using the panel selection below: Levels 1-2 normally use two focused
reviewers; Levels 3-4 use four. All required assignments must approve before the
plan is ready; a single catch-all review is insufficient. All four responsibility
domains remain covered even when related domains share one reviewer.
Include the [test-scope audit](test-scope-audit.md) and applicable
[matrix execution](matrix-execution.md) checks under their designated owners.
These are planning reviews, not execution lanes or a reason to raise the execution
tier. At small tiers keep each review short and specific; do not create new project
work, a matrix, a harness or a formal package just to occupy a reviewer.

## Freeze the actual assignment before designing the topology

Record the requested deliverable and acceptance claims in the user's terms,
explicit exclusions, any user-selected tier or constraints, and which execution
actions are already authorized. Distinguish implementation, verification,
launch/initial health, and completion of a live campaign. Permission for one does
not silently authorize the others. Cite the relevant request and governing
requirement rather than relying on the planner's paraphrase alone.

Inspect specifications and surrounding documents for constraints on that
deliverable. Their descriptions of a larger research program, deployment,
migration or operational campaign do not automatically become requested outcomes.
Keep a material stage only when it implements a requested outcome, satisfies a
binding requirement on that outcome, or is a necessary dependency with an explicit
causal justification. A document title, available resource, ambitious background
goal or preferred topology is not that justification.

Put plausible later work in existing non-goals/optional-operation text, with its
own activation and authority boundary. Do not make it an implementation acceptance
gate unless the requested claim actually requires it. Do not remove real safety,
compatibility, functional coverage or other binding requirements to make a plan
look smaller.

## Give each independent reviewer a focused adversarial question

Supply the original request and relevant follow-ups/authorizations, applicable
repository and skill instructions, the draft plan, acceptance sources, selected
tier rationale, and verification/cost bindings. Each reviewer must inspect these
sources, not only the plan writer's summary. It remains read-only: inspect the
plan and supporting artifacts, but do not implement, run product tests, allocate
live resources, launch the planned workers, or accept the project.

Ask: **Could this plan obey its own internal graph yet violate the user's request
or the skill's rules? What is the smallest complete correction?**

Before dispatch, instantiate the [review assignment](../assets/plan-review-assignment.md)
with the raw sources, frozen candidate, assigned surfaces and expected return. Each
reviewer performs its assigned [acceptance-design](acceptance-design.md) decisions;
an instruction merely to "review the plan" or count checks is insufficient. Preserve
open findings and independent judgment; specify the questions, not their answers.

### Preserve four responsibility domains

| Review group | Owned decision and required challenge |
| --- | --- |
| SCOPE_AUTHORITY | Outcome/stage traceability, binding versus background authority, non-goals, reachable execution permissions and executor stopping point. Does every material stage serve the actual request, and can anything run beyond its authorization? |
| TOPOLOGY_SIMPLICITY | Lowest sufficient tier, explicit tier constraints, genuine lane independence, ownership/delegation, gates and recovery structure, coordination cost, admission and structural skill conformance. Is this the smallest complete valid topology for that outcome? |
| VERIFICATION | Functional sufficiency, concrete assertions, independent oracles, failure/recovery coverage, evidence boundaries, necessary versus redundant test dimensions and retained credit. Could required behavior remain broken while this evidence passes? Own the functional portions of the test-scope audit. |
| EXECUTION_RESOURCES | Dependency/resource graph, actual runner capabilities, isolation and concurrency, terminal exits, collection before cause-group repair, affected reruns, setup/cleanup, wall-clock budgets and operational stop handling. Is the proposed schedule executable, bounded and economical while preserving the selected evidence? Own the matrix-execution contract and scheduling portions of the audit. |

### Select assignments proportionately

A domain is a responsibility, not automatically an additional agent. References
elsewhere to the SCOPE_AUTHORITY, TOPOLOGY_SIMPLICITY, VERIFICATION or
EXECUTION_RESOURCES reviewer mean the independent assignment owning that domain.
Use this ownership map before dispatch and record the selection reason:

| Plan | Required independent assignments | Covered domains |
| --- | --- | --- |
| Level 1 or 2, bounded review scope | SCOPE_STRUCTURE and EVIDENCE_EXECUTION: two distinct reviewers | SCOPE_STRUCTURE owns SCOPE_AUTHORITY + TOPOLOGY_SIMPLICITY; EVIDENCE_EXECUTION owns VERIFICATION + EXECUTION_RESOURCES |
| Level 1 or 2 with one overbroad paired assignment | Split that pair into its two domain assignments: three distinct reviewers total | The other pair remains together; all four domains still have exactly one owner |
| Level 1 or 2 with both pairs overbroad, or an explicit four-reviewer requirement | Four distinct domain reviewers | One reviewer per domain |
| Level 3 or 4, including non-formal plans and the formal compiler | Four distinct domain reviewers | One reviewer per domain; the existing formal approval schema remains unchanged |

For Levels 1-2, default to the two focused assignments. Do not commission four
reviews and merge their reports afterward. SCOPE_STRUCTURE covers what should be
delivered and how simply it can be organized; EVIDENCE_EXECUTION covers how the
claims will be established and the practical cost and operation of those checks.
Each returns separate reasoning for its two domains and one explicit overall
verdict covering both. A material blocker in either domain blocks that assignment.
Use a brief domain-specific rationale when a concern is inapplicable; do not add
work to create an assessment surface. One agent must never own both pairs.

Split only an assignment whose actual scope would obscure independent judgment:
for example, coupled authority/topology decisions spanning several boundaries, or
complex evidence interpretation alongside consequential live-resource, recovery,
isolation or scheduling decisions. Mere file count, a matrix label, reviewer
availability or a larger prompt is not by itself a reason. Name the concrete
complexity/risk and which pair needs separation. Either the writer or reviewer
may identify it; a reviewer unable to assess both domains adequately reports the
coverage gap and required split instead of giving PASS. Keep acceptance PENDING
unless there is already a BLOCK, until the required reviews are complete.

Splitting replaces the paired assignment with its two domain assignments; it does
not stack extra reviews on top. Carry existing findings and reviewed evidence to
the new owners, preserve unresolved BLOCKs, and obtain actual final approvals.
The original reviewer may retain one domain, with another independent reviewer
owning the other. A split is never permission to discard dissent or shop for PASS.
Carry each domain's completed review and follow-up history forward; splitting does
not reset the bounded round budget or restart an already adequate assessment. A
new owner still inspects inherited findings and explicitly approves its scope.
Review size does not itself escalate the execution tier; reassess the tier only
if the work's coordination needs have changed.

Each active assignment has a distinct agent/session identity, different from the
plan writer and other active assignments. The approved Level 1-2 pairing is not
four independent approvals and must not be recorded as such. ROOT assigns each
review directly and receives its result; reviewers are terminal read-only workers,
do not supervise one another, and do not approve their own authored plan. This
flat planning panel applies in both workspaces. It does not remove the multi-agent
workspace's separately justified execution sub-orchestrators or permit them in the
generic workspace. Planning reviews do not add future execution support lanes.

Give all assignments the same frozen candidate revision and raw authority sources,
plus their focused mandates and relevant artifacts. A revision is an unambiguous
existing commit, snapshot or draft identifier; no new hashing system is required.
Run independent reviews concurrently where slots allow, otherwise in bounded waves
on that snapshot. Slot limits do not permit merging active assignments, waiving a
domain or reducing a required four-reviewer panel. Collect all feasible reviews
before revising the draft; one BLOCK does not cancel other independent reviews.
No reviewer repeats domains outside its assignment. Flag discovered cross-domain
contradictions and name their owner; ROOT routes them for explicit disposition.

TOPOLOGY_SIMPLICITY must assess execution tier separately from plan organization.
A request for modular output, independent sections/files or `STEP-*` names alone
cannot justify Tier 4 or the formal package. Inspect the stated coordination need
or actual explicit/project-workflow framework selection. Accept proportionate
lane-owned Level 3 organization and normally compact Level 2 plans; do not force
extra roles or formal schemas to justify their file split. Once the full formal
framework is selected, preserve all its required paths, cards, recipes and checks.

TOPOLOGY_SIMPLICITY also applies [Change locality](change-locality.md). Inspect the
editable source and one concrete private-change boundary: identify the owning fact,
stable public interface and actual consumers. Reject independently maintained copies
that force unrelated edits, not the existence of automatically generated indexes.
VERIFICATION and EXECUTION_RESOURCES assess real evidence and resource consequences;
a generated-file diff alone does not establish that every contained unit changed.

All groups apply the relevant skill rules within their boundary. TOPOLOGY_SIMPLICITY
checks that the ownership map covers every applicable planning rule, including the
formal R/S and V matrices, without becoming a second reviewer of every detail.
Cross-group changes require all affected owners: for example, removing live
calibration needs SCOPE_AUTHORITY to establish necessity, VERIFICATION to retain
required proof, and EXECUTION_RESOURCES to revise resource/cost bindings.

For ordinary short verification with no matrix, EXECUTION_RESOURCES can approve a
brief assessment of the actual commands, dependencies, cost and stopping boundary,
explaining why matrix controls are inapplicable. This is an evidenced PASS, not an
N/A waiver. The other groups likewise scale depth to the actual plan.

The following detailed obligations remain binding under those group assignments:

| Dimension | Required challenge and evidence |
| --- | --- |
| Outcome and stage traceability | Map every material stage, artifact, prerequisite and gate to the request or a necessary dependency. Reject a broader campaign substituted for a bounded delivery. Identify the exact unsupported scope rather than declaring the plan generally too complex. |
| Governing authority and skill rules | Distinguish binding constraints from background context and planner assumptions. Check applicable admission, ownership, tier, gate, recovery and no-execution rules against actual plan behavior. For formal plans, consume and challenge the existing R/S and V matrices; a claimed PASS is not proof. |
| Lowest sufficient tier and real lanes | Compare the chosen shape with the cheapest adequate alternative. At Tier 1, challenge unsafe solo assumptions; at Tier 2, bound the evidence lane; at Tier 3, prove disjoint implementation ownership; at Tier 4, justify durable coordination and any permitted sub-orchestrators. Agent availability and matrix size do not establish need. |
| Simplicity and coordination cost | Identify the risk or dependency each role, schema, harness, gate, handoff and repeated review removes. Compare startup, context, integration and maintenance costs with the benefit. Remove or defer only unjustified structure; do not impose a deletion quota or weaken required formal schemas. |
| Verification necessity and strength | Map each acceptance claim to concrete assertions and the boundary they observe. Distinguish local deterministic, integration/dry-run, hardware and live-environment evidence. Add or strengthen missing proof; reject stronger-than-required or duplicate campaigns. A mock cannot establish a property requiring real execution. |
| Time, resources and stopping | Review setup, execution, cleanup, concurrency and dependency costs for every material verification stage. Epoch/job counts alone are not wall-clock budgets. Require honest estimates or uncertainty, a bounded qualification when needed, finite-test stop conditions and the requested stopping point; never turn them into agent-session deadlines. |
| Execution authority and handoff | Trace implementation, expensive/live commands and external mutations to current authorization. Planning approval, a gate label or a printed command is not authorization. Make unapproved operations unreachable until their explicit activation condition is met; preserve existing authorization without asking for it again. |

A user-selected tier constrains topology, not product scope. Honor it where a
valid lean composition exists and state if a lower tier would otherwise suffice.
If its required structure cannot be justified within the requested work, report
that concrete conflict and offer the lower-tier alternative; do not silently
downgrade, manufacture lanes, widen the outcome, or label an invalid requested-tier
plan ready. The formal compiler's fixed-package requirements remain binding once
selected; simplify the actual work and optional choices without inventing a
reduced schema.

## Findings, dispositions and acceptance

Apply [finding admissibility](acceptance-design.md#finding-admissibility-requirements-define-the-review-boundary)
before treating an observation as a required correction or BLOCK. This applies
regardless of factual severity: an otherwise real vulnerability/gap that leaves
requirements satisfied and required tests passing is `REJECT-OUT-OF-SCOPE`, invalid
for the current review. Preserve the observation without making it a prerequisite.
All reviewers must apply the rule in their dispatch block; the owning reviewer
must correct an unsupported BLOCK rather than asking ROOT to override it.


For each active assignment, record its covered domains, actual reviewer identity, reviewed revision, inspected
surfaces, findings/dispositions, evidence location and explicit PASS or BLOCK.
PENDING denotes an absent or unfinished review, never approval. Each finding names
the affected stage/field, governing request or rule, concrete violation or
uncertainty, smallest correction, acceptance claims preserved, and cost effect when
relevant. A blocker includes unsupported scope, unjustified topology, missing
required evidence, reachable unauthorized execution or unresolved material cost.
Preserve actual reviewer responses and dissent; do not rewrite them into agreement.
Include each assignment's necessity, multiplicity or proportionality assessments
with claim/activity references and concrete reasoning. The panel must cover all
three questions. BLOCK material unsupported acceptance work, multiplication or
machinery even when the plan is structurally valid; also BLOCK missing required proof.
High count/cost alone is not a defect, and a cheaper choice must preserve required claims.

The writer assesses each finding and changes the owning artifacts. Retain existing
test dispositions and ACCEPT-SIMPLIFY, ACCEPT-DEFER and REJECT-EVIDENCE for other
findings. A rejection cites source evidence, not preference. ROOT resolves factual
conflicts and chooses within-authority corrections, but cannot turn a reviewer's
BLOCK into PASS. The owning reviewer must assess the response and explicitly
approve the resolved result. No majority vote, merged summary, structural-validator
PASS, ROOT acceptance or missing response substitutes for any required assignment's approval.
Do not replace a dissenting reviewer to shop for approval. If a reviewer becomes
unavailable, a replacement independent agent must inspect its scope, prior findings
and their dispositions; report the replacement and its actual assessment.

Use one complete initial review per assignment and at most one focused follow-up
per assignment for the collected revisions/dispositions. If material disagreement remains,
retain BLOCK and report the concrete unresolved issue instead of looping until
approval. A genuinely new scope/risk may justify a newly bounded delta review;
the round limit never waives a blocker or an approval. Reuse prior independent
reviews only if their identities, domain coverage, revision and actual approvals
satisfy the selected assignment map. A former catch-all review supplies at most
one assignment and only when its actual evidence covers every assigned domain;
it cannot supply both independent Level 1-2 approvals or multiple separate domain
approvals in a four-reviewer panel.

Bind every active assignment's approval to the final candidate revision. After
changes, obtain focused reapproval from owners of affected domains; a paired
assignment returns one final verdict retaining both domains' coverage. Unaffected
assignments may give a short explicit
carry-forward confirmation naming the final revision and unchanged reviewed scope;
they need not repeat the full audit. A carry-forward-only confirmation is bookkeeping
within that review, not another substantive follow-up. If the reviewer finds changed
assumptions, use the affected-group review route and its existing round limit. The
writer cannot issue the confirmation for them. Harmless wording does not require another full review, but neither a stale
revision nor an unconfirmed writer claim counts as final approval. Cross-group
contradictions or changes to outcomes, authority, lanes, gates, resources, costs or
evidence invalidate all approvals whose reviewed assumptions changed.

Record Plan review verdict PASS and ROOT acceptance only after every required
independent assignment approves the final revision, all four domains are covered,
every material finding is resolved, and ROOT
checks that the results are mutually consistent. ROOT can withhold acceptance for
an unresolved seam even when all assignments say PASS; route the seam to its owners.
Any BLOCK leaves the plan blocked; any missing, stale or PENDING assignment leaves it
incomplete. Never substitute self-review or fabricate evidence when agents are
unavailable. Plan approval remains separate from permission to execute.

For non-formal plans, record the selected assignment-to-domain map, any split
rationale and each assignment's actual result concisely in the existing verification
section, with writer/reviewer identities, final revision, evidence,
dispositions, outcome/non-goals, scope/authority, topology/simplicity,
verification/budget assessments and execution boundary. No extra file is needed.
For formal output, use the metadata, group-approval and per-STEP tables in
[test-scope audit](test-scope-audit.md#record-and-validate-without-another-package)
under validation.md Section 16. Keep authoritative facts in their existing owning
artifacts. The structural validator checks declarations, not reviewer authenticity,
semantic adequacy or live authorization.

## Keep plan acceptance separate from execution

This skill ends at the reviewed planning artifact. Its sole agent-dispatch
exception is the selected independent planning reviews described above; splitting the review
does not authorize project execution.

The plan's executor handoff must state: accepted deliverable and non-goals, final
review verdict, already-authorized actions and their source, conditional operations
and their missing trigger/authority, and the point at which execution must stop.
A later executor reconciles these against the current user request before acting.
When implementation/execution is already authorized, continue within that authority
using the ordinary execution workflow; do not demand redundant confirmation.
When only planning was authorized, do not start implementation. Authorization to
implement does not by itself authorize an experimental campaign, deployment or
other distinct live operation. Ask only for genuinely missing authority immediately
before dependent work; continue independently authorized work.

A conditional future operation may remain in a sound plan without present launch
authority if it is explicitly gated and cannot block or expand the separately
accepted implementation outcome. It is not executed merely because it appears in
the plan. If live evidence is actually required for an acceptance claim, keep that
claim unverified until the authorized operation establishes it; never relabel CPU
or synthetic evidence as a live pass.

## Semantic checks for this review

- A request to correct a trainer and implement a safe two-device queue gains a
  comparator study, long calibration, live smoke campaign and full research screen:
  BLOCK the scope expansion unless each addition is required by the request or a
  demonstrated dependency. Preserve focused trainer/queue/cleanup tests. Consider
  a lower tier if sufficient; do not override an explicit tier without resolving it.
- A request includes launching two queue lanes and checking initial worker health:
  bind that authorized launch and stopping point; do not wait for training completion
  unless requested. A planning-only invocation still hands off rather than launching.
- A request requires a measured device-performance result: do not remove the real
  measurement as unnecessary merely because local tests are cheaper. Plan its
  resources, cost and authorization honestly.
- A small Tier 1 plan has an adequate single execution owner: use the independent
  planning panel with two brief paired approvals, without inventing execution lanes
  or promoting it. A bounded Tier 2 plan likewise uses two focused reviewers.
- A Tier 2 plan has simple scope/topology but complicated live verification and
  recovery: split EVIDENCE_EXECUTION into VERIFICATION and EXECUTION_RESOURCES,
  retaining SCOPE_STRUCTURE, for three reviewers. Preserve every finding and do
  not promote the execution tier solely to obtain the specialist review.
- A paired reviewer cannot inspect both domains adequately: report the gap and
  split that assignment; two bare PASS labels cannot substitute for four-domain
  coverage. A pending split never clears an existing BLOCK.
- A user requests Tier 3 but the writes overlap one shared contract: BLOCK the claimed
  lane independence; stage the shared work and prove any remaining independent lanes,
  or report that a lower-tier alternative fits. Never add unrelated work to fill lanes.
- A formal Tier 4 plan is overbuilt: simplify justified optional choices and scope,
  while preserving mandatory package, gate and fast-lane contracts.
