# Review the necessity, multiplicity and proportionality of acceptance

Apply these questions to every admitted Level 1-4 plan before accepting its
verification design, including compact plans, non-code outcomes and direct formal
compiler use. Review the acceptance activities themselves, not just the graph that
schedules them. Use existing claims, checks, observations and cost fields. A small
plan can answer in a few sentences; equivalent activities can share one assessment
when their claims, boundaries and repetition rationale really are equivalent.
Do not create a test database, proof taxonomy, harness or execution lane to comply.

## Finding admissibility: requirements define the review boundary

Apply this rule to planning reviews and to every implementation/review/audit
assignment authored by this skill, at every tier. A genuine vulnerability or gap
is invalid as a finding requiring correction or blocking the current acceptance
when the current code satisfies the governing requirements, all required tests
pass, and the issue does not undermine either conclusion. Classify it as
`REJECT-OUT-OF-SCOPE` (invalid for this review), even when the observation is true.
Do not demand a fix, new gate, broader test campaign or another review cycle for
that issue. Its existence or severity label alone does not expand the assignment.

Before admitting a finding, the reviewer must name the actual requirement,
acceptance criterion or binding invariant, cite its governing source, and explain
how the observed behavior prevents satisfaction or invalidates required evidence.
Use the current agreed scope, supported inputs/environments and actual threat
model. Do not invent a new requirement or broaden the threat model to admit an
otherwise out-of-scope finding. Apply existing governing security, safety and
correctness requirements where they actually apply; do not infer that every
possible hardening improvement is required.

Requirement satisfaction and test success are separate conditions. Green tests
do not refute a demonstrated violation of a binding requirement or establish that
required assertions are adequate. Such a finding remains valid even if the suite
misses it; add or strengthen the inadequate required tests under the existing
coverage rules. Missing, skipped, blocked, stale or unrun required tests cannot be
reported as passing. In planning-only review, inspect available evidence and the
proposed acceptance contract; do not run product tests or claim future results.

Record the requirement reference (or lack of one), impact on current acceptance,
relevant test/evidence status, and disposition in the existing finding record.
For `REJECT-OUT-OF-SCOPE`, retain any true observation as a nonblocking note in the
existing findings/optional-work record; do not call the vulnerability nonexistent,
claim it was fixed, or count it as a failed requirement. That note grants no repair
authorization and creates no prerequisite for completing the current work.
If an existing BLOCK was based on that finding, the owning reviewer must explicitly
correct its disposition after checking this rule; ROOT cannot silently rewrite
its verdict. A genuinely undecidable required criterion follows the existing
incomplete route, with the specific missing evidence identified.

## Three decisions, with evidence

| Decision | Required writer explanation and independent reviewer action |
| --- | --- |
| Necessity | Name the requested claim or binding requirement, the observation/assertion that decides it, the actual boundary observed, and why the chosen environment is needed. The reviewer traces the claim to its authority and inspects the proposed observation and available implementation/artifact, challenging both missing evidence and stronger-than-required proof. A test name or environment label is insufficient. |
| Multiplicity | Explain what each repetition, dimension and material interaction adds: distinct behavior, compatibility, risk, uncertainty reduction or a binding exhaustive requirement. The reviewer inspects those distinctions and checks justified grouping against real dependencies. Needing evidence in an environment does not imply needing every combination in that environment. A single representative observation also does not establish all combinations. |
| Proportionality | Compare the proposed acceptance design with a plausible simpler adequate alternative, or explain concretely why the existing design is already the simplest adequate choice. The reviewer assesses retained claims and the cost of constructing, operating, interpreting, maintaining and rerunning the acceptance system where material. Reject unnecessary machinery or repeated work without imposing a removal quota or weakening required evidence. |

Apply the questions to every selected acceptance activity or equivalent family,
including non-test readbacks, measurements and operation-only steps. Inspect actual
assertions or decision rules when available; when assets do not yet exist, inspect
the proposed observation contract and bind later readiness to that contract. Do
not claim to have reviewed unseen implementation. A large family cannot hide a
different environment, unsupported repetition or unobserved failure/recovery claim.
Single-check plans still explain why that check suffices and has no repeated scope;
they need no invented matrix or alternative infrastructure proposal.

## Resolve completeness and economy without weakening either

1. Preserve explicit user/specification requirements and justified safety/correctness
   obligations, including exhaustive evidence when actually required. Missing proof
   must be added or strengthened, never converted to PASS by reducing the claim.
2. Select evidence sufficient for those claims, then choose the least complex
   adequate design. Neither matrix completeness nor a structural-validator PASS
   establishes that the selected acceptance activities are justified.
3. Justify environment necessity and multiplicity separately. Terms such as native,
   realistic, comprehensive or end-to-end do not establish either one. A canary is
   sufficient only for claims and variations it actually establishes; it is neither
   a universal ceiling nor an automatic extra gate.
4. Uncertain equivalence does not authorize dropping required cases. Retain them or
   resolve the uncertainty with a scoped investigation. Uncertainty alone also does
   not justify adding an unbounded campaign beyond the requested claims. If required
   evidence and resource constraints cannot both be met, report the conflict and
   incomplete claim; do not silently waive coverage or invent resources/authority.

The assigned reviewer returns BLOCK for material unsupported activities, unjustified
multiplication or acceptance machinery, or inadequate required proof. It identifies
the affected claim/activity, source, missing rationale or demonstrated excess, and
smallest supported correction. A large count or high cost alone is not a blocker;
neither is a reviewer's preferred implementation style. PASS may retain every check
when the actual requirements and evidence justify them.

## Conditional questions, not a prescribed test architecture

- **External or expensive environments:** Separate the property requiring that
  environment from properties observable elsewhere, and justify repeated use by
  distinct claims or relevant variation. Real local boundaries may suffice for
  some claims; substituted environments cannot establish external behavior they
  do not exercise. No fixed number of live probes, mandatory mock layer or universal
  proof classification follows from this rule.
- **Stochastic behavior or uncertain setup:** Identify the preconditions needed to
  interpret an observation and how their validity is established. Distinguish a
  failed measurement/setup from a product result. If variability is itself under
  evaluation, justify the observation method, repetitions and stopping criterion;
  do not require deterministic fixtures or retry until a convenient PASS appears.
  Prompt-generated setup is one possible source of uncertainty, not a forbidden
  implementation technique in every project.
- **Reusable verification infrastructure:** Review the actual dependencies between
  shared controls, observations and conclusions, and the cost of changes. Challenge
  avoidable broad coupling where consequential, but do not mandate component splits
  or duplicate code. A change may invalidate observation production, interpretation,
  or only presentation; preserve credit only when the dependency evidence supports
  it. If a shared control really invalidates every result, broad rechecking remains
  necessary. A hoped-for cheap rerun is not evidence of independence.

These examples apply only when the plan contains those conditions. Other domains
use their own observation methods. Do not insert external probes, stochastic
experiments or shared-control qualification into an ordinary local plan.

## Assign the decisions to the selected review owners

Use the [review assignment template](../assets/plan-review-assignment.md) when
dispatching each planning reviewer. Give it the same frozen candidate and raw
authority sources, its own group mandate, relevant acceptance surfaces and the
existing cost/dependency information. Preserve independent judgment; do not prescribe
findings or demand a predetermined reduction.

| Group | Required acceptance-design work |
| --- | --- |
| SCOPE_AUTHORITY | Trace claimed acceptance obligations to the request and binding sources; identify optional campaign scope masquerading as a prerequisite. Check that any mandated environment or exhaustive set is genuinely required and authorized as applicable. |
| TOPOLOGY_SIMPLICITY | Challenge the structure and coupling of the acceptance system as well as the delivery topology. Compare a simpler adequate design or justify retaining the current one, including its construction and maintenance burden. |
| VERIFICATION | Inspect claims, observations/assertions and actual boundaries. Decide whether chosen environments and repeated variations supply necessary evidence; check both unjustified expansion and insufficient grouping/sampling. Record necessity and multiplicity assessments with retained coverage. |
| EXECUTION_RESOURCES | Evaluate material setup, execution, cleanup, interpretation/repair and rerun costs and dependencies of the proposed and simpler designs. Check that the cost rationale includes the acceptance machinery, not just the product critical path. |

Use the assignment map in [plan conformance](plan-conformance-review.md): Levels
1-2 normally pair these domains across two reviewers, splitting only an overbroad
pair; Levels 3-4 retain four separate domain reviewers. These rows define duties,
not four additional agents for a paired panel. No reviewer repeats unassigned
audits. Cross-domain tradeoffs require the affected owners: a cheaper evidence
choice needs VERIFICATION's adequacy judgment as well as relevant cost/scope
decisions, with distinct reasoning even when the same assignment owns two domains.
Preserve every selected independent approval, final revision binding, bounded
follow-up and no-ROOT-override rules.

Record the actual assessments and source references, not bare YES/PASS declarations.
For compact plans use the existing verification/review section. For formal plans,
the existing per-STEP audit rows carry Necessity assessment, Multiplicity assessment
and Proportionality assessment, referring to the owning families/cards for all three
entry paths. This extends review results only, not STEP/card schemas or package files.
Structural validation can require those declarations; reviewers must judge their truth.

## Preserve the reviewed decisions during implementation

Compile the accepted claims, environment/repetition rationale and material dependency
assumptions into existing check/readiness/operation contracts. Later executors use
them when authoring or selecting checks. A materially different observation method,
acceptance scope, environment, repetition strategy or costly shared dependency
returns to the owning authority and affected review groups before dependent costly
execution. Unaffected authorized work may continue.

Use existing asset review/readiness stages to inspect concrete assertions or
measurement controls when new information makes that necessary. This is a focused
delta review, not another full panel before every test, and does not authorize
execution from this planning skill. Ordinary mechanics within the accepted contract
do not reopen the plan. Reuse evidence only where actual dependencies justify it.
