# Plan substantial verification matrices

Apply this contract to every substantial post-step matrix in Levels 3 and 4,
including repair/re-entry paths and Level 4 without a harness. Apply it in Level 2
when multiple coordinates have meaningful execution cost, stateful resources,
dependencies, or repeated repair risk. A coordinate is one independently reportable
test configuration/scenario. A short ordinary local check needs no matrix machinery;
test count alone does not determine applicability. Concurrent test processes do not
add implementation writers or require a higher topology level.

A coordinate is one independently reportable
test command, shard or configuration, not another agent or review stage.

Use the [matrix binding template](../assets/matrix-execution-binding.md) inside the
existing verification section or block/card. Reference one authoritative binding;
do not copy it into every consumer or create another mandatory package artifact.
Retain the functional coverage and independent oracles required by
[test-scope audit](test-scope-audit.md). Scheduling efficiency does not reduce scope.

## Required execution contract

### Schedule test processes by the resources they consume

Separate these execution classes in the existing binding:

- **Isolated deterministic/local tests:** run graph-ready commands concurrently
  up to a host-capacity budget based on available CPU, memory, process fanout and
  observed contention. Agent slots, writer count and live-provider limits are not
  their concurrency ceiling.
- **Stateful local tests:** isolate temporary files, ports, caches, fixture stores
  and owned child processes. Serialize only an actual conflicting resource or a
  named prerequisite; deterministic behavior alone does not prove isolation.
- **Live/external tests:** apply the relevant provider/home/service quota in
  addition to the shared host budget, only to tests consuming that resource.
  Tests of an adapter with local fakes do not consume a live-provider slot merely
  because the test names that provider. Preserve the required native proof.

Declare a concrete worker count or executable sizing rule for each applicable
class, its measurement/estimate basis, and how simultaneous classes share host
capacity without oversubscription. Parallel reviewer/checker agents alone do not
parallelize their scripts. Reuse existing measurements; when unavailable,
plan a small representative qualification and a conservative provisional setting
with its reassessment trigger. Do not invent a universal number or require a new
benchmark campaign for ordinary short checks. One aggregate host limit is useful;
one provider-derived ceiling imposed on unrelated local work is not justified.

Use an existing runner's supported parallel mode or stable module/file shards
when the saved execution time exceeds startup and fixture cost. Preserve discovery,
fixtures, assertions, per-test failure reporting and coverage accounting across
shards; a failed shard must still run its independent tests without suite-wide
fail-fast. Keep tiny suites together when sharding costs more than it saves.
Do not assume a command such as unittest discovery runs its tests concurrently.
Fill the template with actual commands (including cwd and relevant environment),
runner flags or exact shard selectors, prerequisites, resource limits and their
basis. "Run concurrently" is not a completed binding. If the capability is missing,
name its owner, smallest prerequisite and blocked consumer instead of claiming it.

Refill capacity as each command completes; do not wait for the slowest member of
a batch before starting another ready command. Immediate terminal exit ends an
unreachable scenario wait, not independent assertions or tests that can still run.
Collect their failures before cause-group repairs under the contract below.

1. **Concurrent independent coordinates.** Name the runner entrypoint, immutable
   input snapshot, resource isolation, and supported concurrency limit. Run ready
   independent coordinates concurrently up to that limit. Include writable stores,
   fixtures, ports, provider sessions, output paths and cleanup ownership as relevant;
   separate working directories alone do not prove isolation. Declare shared-resource
   conflicts and serialize only the affected operations. Justify limits from measured
   capacity, provider limits or actual contention; list order and serial integration
   are not dependencies. One coordinate's cleanup must not stop another's resources.
2. **Immediate coordinate exit on incompatible terminal state.** Define successful
   observations, incompatible terminal predicates, and the source of state for each
   scenario. Once an incompatible terminal state is observed, stop waiting for an
   unreachable success, capture evidence, publish the failure and perform bounded
   cleanup. Do not consume the remaining success timeout or retry silently. Expected
   failure/recovery states are judged against that scenario's contract, not a global
   failure label. Recovery deliberately exercised by the test remains executable.
   A live PID alone is not proof of progress; distinguish slow/transient states from
   proven terminal states. Polling/event delivery must bound detection latency.
3. **Complete collection despite failures.** Coordinate fail-fast is not matrix
   fail-fast. Continue every independent feasible coordinate after ordinary failures,
   collect all their failures once, and record a terminal outcome for every selected
   coordinate: passed, failed, timed out, blocked by a named dependency, or not run
   with a reason. Never treat blocked/unrun rows as PASS or a complete success. Genuine
   safety, authorization, shared-infrastructure or total-budget stops contain the
   affected scope, preserve results, and explicitly report incomplete coverage.
4. **Explicit dependency graph.** Declare each prerequisite and its required output
   or state, including an explicit empty set for independent roots. Schedule ready
   nodes by this acyclic graph plus resource constraints. A success-dependent test
   blocks after prerequisite failure; a cleanup/recovery test that consumes failure
   evidence may still run. Do not serialize a whole family because one pair depends
   on each other. Hold the input snapshot stable until collection ends.
5. **Group before repair.** Finish the feasible matrix and collect the complete
   failure set before product, fixture or runner repairs begin. Group by evidenced
   shared root cause, separating product, test-control, oracle and environment faults.
   Similar messages alone do not prove a common cause; keep uncertain causes explicit.
   Give each cause group one coherent repair assignment and one owner, covering all
   affected coordinates. Do not repair after each failed test. Overlapping repairs
   keep one writer; unrelated fixes may run concurrently when ownership is disjoint.
   A repair that does not resolve its cause requires new diagnosis under the existing
   bounded repair rules, not an assumption that one patch must always succeed.
6. **Rerun affected evidence only.** Map changed code, fixtures, configuration, oracle
   and external state to invalidated coordinates and dependent consumers. Rerun that
   set, including previously passing coordinates whose evidence was invalidated, and
   preserve compatible PASS credit. Blocked or unrun required coordinates still need
   execution once ready. Shared-input changes may legitimately affect the full matrix;
   document that dependency instead of rerunning everything by habit. A report-only
   correction does not invalidate valid execution evidence.
7. **Review wall-clock budgets.** Estimate expected duration and maximum finite-test
   budget per coordinate, terminal-detection latency and cleanup allowance. Estimate
   the total elapsed range/deadline from the graph's critical path, concurrency limit,
   resource contention, setup and cleanup; do not sum overlapping durations as wall
   time. State measurement sources or uncertainty, and what exhaustion/overrun does.
   Review budgets before execution; compare actual elapsed times before another
   expensive cycle. No arbitrary giant success wait after known terminal failure,
   no silent budget resets, and no dropping required coverage to meet an estimate.
   These are finite-test budgets, not hard timeouts on agent sessions; honor the
   host's existing finite-command supervision policy.

### Example: local scripts and live tests share host capacity

Illustrative only: measurements support four simultaneous command trees, while
each provider home allows one. Local scripts A/B/C/D are isolated; live X1/X2
share home X, and Y1 uses home Y. Start A, B, X1 and Y1. A fails: record it and
start C immediately; B, X1 and Y1 continue. If B fails, start D. X2 waits only
for X's release and a host slot. A check requiring B's successful output is
recorded dependency-blocked; a recovery check consuming B's failure may run.
After feasible collection, group A/B only if evidence shows a shared cause,
repair that group once, then rerun invalidated tests and ready blocked consumers.
Four is this example's measured budget, not a skill default.

## Decide the evidence scope before scheduling it

[Acceptance design](acceptance-design.md) governs whether coordinates and their
environments belong in the acceptance scope. A complete, concurrent matrix is not
proof that every combination is needed. Review environment necessity separately
from multiplicity; preserve required native evidence at the boundary and breadth
its claim requires. Neither "native" nor a representative canary sets that breadth.
Fill the existing binding's acceptance rationale before scheduling the selected set.

For shared-control changes, establish the actual observation/interpretation/result
dependencies before selecting reruns. Avoidable costly coupling is a design-review
question, not permission to retain invalid credit. The affected-evidence rule above
still requires broad reruns when a genuinely shared change invalidates all results.

## Review and implementation binding

Assign this contract to the independent owner of EXECUTION_RESOURCES in the
[selected review panel](plan-conformance-review.md). VERIFICATION retains coverage
and oracle review; route changed evidence selection to the owners of both domains.
At Levels 1-2, EVIDENCE_EXECUTION normally owns both; preserve distinct adequacy
and scheduling judgments, and split this pair if complexity prevents focused review. The execution
reviewer must reject unnecessary serialization, long waits after incompatible
terminal states, matrix-wide fail-fast on ordinary failures, repair-after-each-test
loops, unjustified full reruns, missing isolation/dependency contracts, and budgets
that ignore actual concurrency or cleanup. Findings identify the affected binding,
evidence, smallest correction and estimated cost effect with uncertainty. ROOT
coordinates dispositions using the panel's bounded rules; the owning reviewer
must approve the correction, and ROOT cannot override its BLOCK.
Also reject local tests inheriting provider/agent caps, independent scripts ordered
serially without a dependency, avoidable wave barriers, and expensive serial suites
whose supported, economical parallel mode/shards were ignored. Do not demand
parallelization of tiny suites or shared fixtures without a net benefit and isolation.

Name the actual host runner/adapter implementing each control. The shipped
`execution_blocks.py` can select affected checks and record results; it does not
schedule concurrent tests, monitor terminal states, or clean up processes. If a
control is missing, plan the smallest scoped prerequisite to implement/prove it,
or record a concrete constraint and reviewed execution limitation. Do not claim
that markdown or a structural validator provides runtime enforcement. Before broad
use, reuse existing evidence or plan focused readiness proof of changed scheduling,
terminal-exit, collection and cleanup branches; do not launch the product here.

For formal Level 4, bind this contract in existing module/card fields: M03 owns test
assets; M04/M07/M09 own their selected checking matrices; M08 proves changed fragile
controls when selected; M05 groups findings, assigns repairs and adjudicates retained
credit. Put graph/resource/budget bindings in the existing Inputs, Outputs, Isolation
and lifecycle, Critical-path effect and Local instructions fields. Preserve M09
authorization/observation and R23 stop authority: an ordinary coordinate failure
ends that coordinate's wait, not the whole attempt's authorized independent work.
Keep all fixed package schemas, policies, gates and three-entry STEP paths intact.

## Bind to the exact formal fields

The shorthand "Outputs", "Isolation and lifecycle", and "Critical-path effect"
above describes concerns, not new schema headings. The formal compiler's exact
module-instance headings and 20 task-card fields remain authoritative:

| Matrix concern | Existing module-instance heading(s) | Existing task-card field(s) |
| --- | --- | --- |
| Snapshot, graph, prerequisites and runner entrypoint | Inputs; Preconditions; Local instructions | starting_state; dependencies_and_predecessor_outputs; initial_entrypoints; ordered_actions |
| Required claims, independent assertions and terminal predicates | Coverage; Checks and acceptance; Repeat, join, and terminal behavior | required_behavior; verification; acceptance_criteria_and_tolerances; thread_resume_and_terminal_rule |
| Concurrent scheduling, isolated resources and cleanup | Concurrency and isolation; Resources and side effects; Local instructions | working_scope; allowed_tools_capabilities_resources; forbidden_actions_and_boundaries; ordered_actions |
| Collection, terminal statuses and evidence | Outputs and results; Repeat, join, and terminal behavior | deliverables_and_result_paths; completion_review_owner_and_handoff |
| Cause groups, repair ownership and exceptional stops | Owner and roles; Failure and exception routes | workflow_role; failure_classification_and_routes; completion_review_owner_and_handoff |
| Affected reruns and preserved credit | Prior results and change effects | starting_state; dependencies_and_predecessor_outputs; verification |
| Expected/maximum durations, cleanup allowance and overrun route | Cost and critical-path effect; Resources and side effects; Local instructions | allowed_tools_capabilities_resources; ordered_actions; failure_classification_and_routes; cited_global_policy_ids_and_exception_ids |

Fill these existing fields or reference their authoritative binding; do not paste
the drafting template's table into a fixed-schema package as an additional table.
Keep global scheduling/timeout policy in its existing owner and record the review
in the Section 16 scope-audit tables. The mapping adds no heading, card field or
independent policy source.

## Preserve checkpoint, recovery and ownership boundaries

"Declared order" and "earliest unresolved unit" in checkpointed verification identify
dependencies and retained progress; they do not turn independent ready coordinates
into a serial queue. Apply the graph and resource constraints to normal and repair
entries while preserving each entry's scope, gates and accepted credit. Coordinate
labels correlate selected test results; they do not require another runtime registry,
content hashes or evidence database.

Recovery deliberately inside a scenario and bounded cleanup remain part of that
coordinate's execution. Product, fixture and runner repairs wait for collection of
the feasible matrix on its stable snapshot. Correcting only an outer worker report
uses the existing continuity rules and two same-thread attempts when safe; it must
not rerun accepted checks, alter scenario evidence or reset a finite-test budget.
Collection closure records every selected coordinate, including blocked, timed-out
and unrun work; incomplete coverage cannot authorize a gate that requires it.

ROOT owns cross-lane dependencies, shared-resource capacity, live-attempt authority
and global acceptance. In the explicitly selected Tier 4 hierarchy, a lane
sub-orchestrator may direct its matrix and local repairs only within ROOT's declared
lane contract. Share the actual concurrency/resource budget across lanes; each lane
must not independently spend the full global capacity. Lane-local collection may
close independently only when its snapshot, resources and repairs cannot invalidate
another active lane; otherwise join the affected collection at ROOT before mutation.
Return cross-lane causes and terminal lane results to ROOT. Workers remain terminal,
and a lane sub-orchestrator cannot create another orchestration tier.
