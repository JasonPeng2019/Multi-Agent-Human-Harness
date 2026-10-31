# Audit test scope before plan acceptance

This is a planning-time independent review of every proposed suite, matrix, and
step-end verification surface. It applies after a significant plan's evidence design
exists and before final acceptance; it does not execute the planned project.

This audit is part of the [adversarial plan-conformance review](plan-conformance-review.md)
for every admitted Level 1-4 plan. Read that reference for panel selection and
unanimous approval: Levels 1-2 normally use two paired assignments, expanding only
an overbroad pair; Levels 3-4 use four distinct reviewers. VERIFICATION owns functional
evidence; EXECUTION_RESOURCES owns scheduling and resource efficiency. SCOPE_AUTHORITY
and TOPOLOGY_SIMPLICITY own outcome, authority and topology judgments. A reference
to a domain reviewer means its assigned owner, including an authorized paired owner. Retain all verification obligations below. Cost-effective tests
cannot rescue a plan for the wrong deliverable.

Read [Acceptance design](acceptance-design.md) for the all-tier necessity,
multiplicity and proportionality contract. It governs acceptance activities beyond
tests as well. Use the [review assignment](../assets/plan-review-assignment.md) to
dispatch concrete group duties; do not accept a generic "looks complete" response.

## Establish functional coverage, then remove redundant work

Functional adequacy comes first; economy is a constraint on how to prove it, not
permission to lower the acceptance bar. The objective is reliable required
behavior, not the fewest tests or the fastest green run. No finite suite guarantees
all behavior; report what is established and what remains uncertain. Add or
strengthen checks when the existing evidence cannot decide a required claim.

Before trimming, trace each in-scope required behavior and material failure risk
to concrete assertions. Cover applicable normal operation, refusal/invalid input,
boundary conditions, state transitions, failure recovery and cleanup. Include
concurrency, persistence and cross-component interactions where the contract or
observed defects make them relevant; do not manufacture a universal Cartesian
matrix or a quota of cases. A family label or PASS cell is not an assertion map.
For a grouped case, distinguish its individually required observations so an
unexecuted recovery or failure path cannot disappear behind its happy-path PASS.

Audit evidence strength as well as presence. Does the assertion observe the actual
implementation and boundary claimed, with an independently derived expected
outcome? Could the known broken behavior still pass it? Helper mocks, source-string
checks and tests of reference models/oracles prove only those narrower things;
they do not alone prove the caller sequence, installed artifact, OS interaction
or provider integration. For changed high-risk seams, retain both the motivating
failure and the adjacent valid/recovery behavior, using real local boundaries
with controlled fault injection where practical. Existing trustworthy evidence
can satisfy these obligations; no blanket mutation-testing campaign is required.

Map each selected test or coherent test family to an accepted product requirement
or concrete material risk and its observation oracle. Group equivalent cases instead
of creating thousands of paperwork rows. Name matrix dimensions, their cardinalities,
applicability exclusions, interaction risks and resulting case count. Explain the
distinct confidence each dimension and each repeated suite adds. Include construction,
execution and repair cost, likely wall-clock range, external cost and estimate basis;
record uncertainty honestly when measurements do not exist.

Use the cheapest trustworthy evidence that decides the required behavior. Consider
existing checks, local deterministic failure injection, representative equivalence
classes, pairwise coverage and adapter-specific integration before a full Cartesian
product. Sampling requires an explicit equivalence/interaction argument tied to the actual
implementation path, state and environment, plus retained tests that would expose
the relevant faults; absence of a previously seen failure is not that argument.
When equivalence cannot be established, keep the affected cases.
Pairwise testing is not automatically sufficient. Preserve required security,
data-integrity, lifecycle, concurrency and compatibility coverage. Cheap broad suites
can be appropriate; a high test count alone does not establish waste.

An oracle must not silently require stronger behavior than the accepted contract.
Separate product correctness, provider compatibility and control validity. Correct
containment of a misbehaving provider can prove a harness invariant while leaving a
provider-specific capability undecided. Use live providers only for claims that need
their actual integration; use deterministic fixtures for prescribed malformed-output
sequences where that suffices. Do not mistake an unavailable observation for PASS.

Distinguish a binding exhaustive-test requirement from a planner's interpretation of
words such as "complete" or "comprehensive". A binding user/spec/repository requirement
stays unless its governing authority changes it. Recommend a change when justified,
but do not silently trim required cells. ROOT may resolve planning choices within its
authority; it cannot waive a user requirement. This audit neither removes the formal
package's fixed rules, gates or fast-lane paths nor permits weaker product acceptance.

## Independent review and disposition

For substantial matrices, also audit the complete
[matrix execution contract](matrix-execution.md), not only counts and assertions.
Require the coordinate dependency/resource graph, implemented runner controls,
terminal exits, complete collection, cause-group repair and affected-rerun rules,
and per-coordinate/total wall-clock budgets with their basis. Reject unnecessary
serialization, long waits after incompatible terminal states and per-test repair
loops. Assign these schedule/control checks to EXECUTION_RESOURCES, with
VERIFICATION retaining functional coverage and oracle adequacy. Use the shared
bounded feedback and audit record; cross-reference related findings.

Use its concrete binding and rejection criteria, including concurrency inside
suites. Record scheduling findings in the existing cost, findings and disposition
fields with their owning group; do not add another group or duplicate full audit.

1. The writer supplies the draft plan, authoritative acceptance sources, suite/family
   inventory with dimensions and cost, and the exact proposed verification boundaries.
   Include each activity/family's claim, observation boundary, environment necessity,
   repetition/combination rationale and comparison with a simpler adequate choice.
   Reuse existing plan fields; do not commission another evidence database or scheduler.
2. Dispatch the independent read-only assignment owning VERIFICATION. Give it all
   suites and step-end surfaces, the relevant source contracts, and a bounded question:
   which required behavior could still be broken while these checks pass, and which
   evidence is missing, stronger than required, duplicated or unnecessarily expensive?
   Inspect representative concrete assertions and callers when available, not just
   matrix counts. It may recommend adding tests or retaining everything. Never
   require a removal quota. Require VERIFICATION to return explicit necessity and
   multiplicity assessments based on those surfaces, including justification of any
   live/external multiplicity separately from needing that environment at all.
   TOPOLOGY_SIMPLICITY and EXECUTION_RESOURCES provide the complementary structure
   and cost judgments for proportionality; SCOPE_AUTHORITY checks their governing
   claims. Preserve every group's actual reasoning and route cross-group changes.
   This is the panel's VERIFICATION responsibility, not an additional reviewer.
   The reviewer may inspect artifacts but cannot edit, execute product tests, launch
   project workers, alter requirements, or make final acceptance decisions.
3. Require specific findings: affected suite/family/dimension, source requirement and
   assertion, redundant or missing evidence, suggested change, retained coverage and
   estimated cost effect with uncertainty. Inspect cross-step duplication as well as
   each individual matrix. Test authoring and later runtime selection remain separate
   from this planning review. A structurally complete but materially unjustified
   acceptance design is a blocker under the shared contract.
4. The writer validates every criticism. Record ACCEPT-ADD, ACCEPT-STRENGTHEN,
   ACCEPT-REMOVE, ACCEPT-MERGE,
   ACCEPT-SAMPLE, ACCEPT-REPLACE, ACCEPT-SCHEDULE, REJECT-REQUIRED, REJECT-OUT-OF-SCOPE,
   or UNRESOLVED with reasons. Apply the acceptance-design finding-admissibility rule:
   do not require new tests solely to cover a genuine gap outside current requirements.
   Inadequate evidence for an actual requirement still requires stronger tests. Rejection
   cites the required claim or concrete risk and why the proposed cheaper evidence is
   insufficient. Apply accepted changes to the owning plan fields/cards and update the
   requirement-to-evidence map, counts, costs and invalidation boundaries. Findings
   remain advice until adjudicated; do not trim automatically to obtain reviewer PASS.
5. Use the panel's per-assignment initial review and bounded focused follow-up. ROOT may
   be the plan writer but cannot supply any independent approval. Route disagreement
   to ROOT for an evidence-based correction; the owning reviewer must approve the
   result. ROOT cannot override BLOCK. Retain draft status when disagreement remains.
   A materially new scope/risk can justify a newly bounded delta review, not an
   unlimited loop. Confirm every assignment's approval against the final candidate revision.
6. ROOT accepts the final scope only after all selected reviewers approve with all four domains covered, every finding
   has a disposition, every required claim has adequate evidence planned, and no material coverage hole is
   hidden by grouping, sampling or reused credit. Additions need the same specific
   claim, oracle, boundary and cost justification as removals. If review is unavailable
   or a material requirement remains
   unresolved, retain a draft and report planning validation incomplete. Do not invent
   a reviewer result or silently substitute self-review. No user confirmation is needed
   for ordinary within-authority trimming.

The runtime cards consume the accepted scope and may not silently expand or weaken
it. A new uncovered risk returns to ROOT. Preserve unaffected test credit and rerun
only evidence invalidated by changed inputs under the existing verification rules.
After concrete tests are authored, use the existing asset review/readiness stage to
check their actual assertions and execute realistic new/changed control branches
before expensive reuse. That targeted readiness work is planned here, not performed
by the planning reviewer, and does not repeat the full scope audit. Material changes
to the reviewed evidence method, environment, multiplicity or costly dependencies
use the affected-group delta route in [Acceptance design](acceptance-design.md).
Ordinary implementation mechanics within the accepted contract do not reopen it.

## Record and validate without another package

For non-formal plans, record the selected assignments and domain ownership, actual
independent reviewer identities, selection/split reason, final revision, assignment
verdicts, reviewed surfaces, findings, dispositions and final ROOT decision in the
existing verification section. A paired reviewer records separate domain reasoning
and one joint verdict; do not invent four independent identities or dispatch four
agents just to fill a table. The concise record can use these fields in prose:

```text
Panel: Level <1-4>; <two paired / three split / four domain>; <selection/split reason>
Assignment: <name>; domains: <owned domains>; reviewer: <actual identity>
Revision and evidence: <final candidate and actual response reference>
Assessments: <reasoning for each owned domain, including applicable acceptance decisions>
Findings/dispositions: <actual findings and resolutions or evidenced no-material-findings>
Verdict: <PASS / BLOCK / PENDING>; aggregate and ROOT decision: <actual result>
```

Repeat the assignment record once per active assignment. Two paired PASSs require
both distinct reviewers and adequate coverage of every domain; a material blocker,
missing owner or unresolved split prevents acceptance. Levels 3-4 still need four
separate domain approvals even when their plan uses a compact format.

The following exact tables and four-identity validation apply only to formal
Level 4 output. Retain evidence selections in their existing owning cards/manifests; add the
following three tables under `validation.md` Section 16. They are review results and
references, not a second definition of execution policy. Do not add a module, policy
ID, V-check ID, runtime role, or package file for this planning audit.

| Audit field | Value |
|---|---|
| Plan writer | Actual writer agent/session identity |
| Review panel | Four group rows below, each with a distinct independent agent/session |
| Plan revision | Unambiguous final candidate revision shared by every group approval |
| Review evidence | Readable review response reference and follow-up reference, or explicit unchanged-scope reason why no follow-up was needed |
| Requested outcome and non-goals | Original request and scope references distinguishing implementation, verification and any optional operation |
| Scope and authority review | Stage/gate traceability and applicable skill-rule findings, dispositions and final owning references |
| Topology and simplicity review | Lowest sufficient tier, user-selected constraints, actual lane boundaries and coordination-cost assessment |
| Verification and budget review | Required claims, concrete evidence boundaries, material wall-clock/resource costs and reviewed simplifications |
| Execution authorization boundary | Already-authorized actions and source; conditional operations, missing authority/trigger and stopping point |
| Plan review verdict | PASS |
| ROOT acceptance | ROOT decision reference accepting the final revised scope and resolving every material disagreement |
| Audit status | ACCEPTED |

| Review group | Reviewer | Plan revision | Review evidence | Findings and dispositions | Verdict |
|---|---|---|---|---|---|
| SCOPE_AUTHORITY | Actual independent scope reviewer identity | Final candidate revision | Actual review and final approval reference | Scope/authority findings and resolved dispositions, or explicit no-material-findings | PASS |
| TOPOLOGY_SIMPLICITY | Different independent topology reviewer identity | Same final candidate revision | Actual review and final approval reference | Topology/simplicity/rule findings and resolved dispositions, or explicit no-material-findings | PASS |
| VERIFICATION | Different independent verification reviewer identity | Same final candidate revision | Actual review and final approval reference | Functional coverage/oracle findings and resolved dispositions, or explicit no-material-findings | PASS |
| EXECUTION_RESOURCES | Different independent scheduling reviewer identity | Same final candidate revision | Actual review and final approval reference | Execution/budget findings and resolved dispositions, or explicit no-material-findings | PASS |

| Step | Evidence scope | Requirement and oracle | Dimension rationale | Cost basis | Necessity assessment | Multiplicity assessment | Proportionality assessment | Review findings | Writer disposition | Final status |
|---|---|---|---|---|---|---|---|---|---|---|
| STEP-001 | References to every suite/family/card in all three entry paths of this step | References to governing claims and assertions | Counts, exclusions and distinct interaction risk, or concrete reason no cross-product applies | Runtime/external/build cost range and estimate basis, with uncertainty | Claim/observation/boundary and chosen-environment justification; reviewed source/family references | Distinct evidence from repetitions/dimensions/interactions or concrete reason no repeated scope is needed; reviewed references | Simpler adequate alternative or justified retention, preserved claims and material construction/operation/maintenance/rerun costs; reviewed references | Actual findings, or explicit no-material-findings result; include cross-step duplication | Disposition of every finding with coverage justification and final owning artifact references | ACCEPTED |

Plan review verdict PASS requires all four group verdicts PASS for the metadata's
final Plan revision, distinct independent identities, resolved material findings
and ROOT acceptance. Preserve each group's actual response and explicit reapproval
or carry-forward confirmation in Review evidence. ROOT cannot override BLOCK;
PENDING, absent or stale approvals cannot validate. Group rows occur exactly once
in the order shown; no group is waived. The added review table extends Section 16
only, not fixed STEP/card schemas or the module library. Compact plans record the
same approval facts without importing this formal table grammar.
The validator checks declarations, not whether actual agents reviewed the plan or
whether an action is authorized at execution time.

Emit exactly one coverage row per STEP; a row can reference the existing complete
family inventory instead of copying its cases. The three acceptance-design assessment
cells summarize actual reviewer decisions or point to specific reviewed family/card
assessments covering every selected activity in all three paths. Generic PASS,
ACCEPTED, N/A or PENDING is not an assessment. A single local readback can explain
its boundary, why there is no repetition and why the existing check is sufficient;
do not invent matrix dimensions or another system to fill the cells. Include operation-only steps with
their readback/check scope. No hard field accepts an empty or N/A waiver. Use
PENDING while drafting and ACCEPTED only after adjudication on the final scope.

The formal validator checks table shape, four distinct declared reviewer identities
different from the writer, matching final revisions, unanimous PASS, all indexed
STEP rows, populated evidence/cost/disposition fields and accepted status.
It cannot authenticate a reviewer, prove coverage completeness, evaluate oracle
soundness or certify minimum cost. The plan writer and ROOT must inspect the actual
review and final artifacts; plausible table text is not evidence that an audit ran.
Existing formal plans require this audit on their next compilation/amendment before
claiming validation under the updated skill. Do not fabricate retrospective approval
or invalidate already accepted product evidence merely because the plan schema changed.
