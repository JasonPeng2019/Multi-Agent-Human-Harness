# Level 3 — parallel implementation

Use this level only to design future execution when independent deliverables have
real, non-overlapping ownership. If two changes touch the same contracts, files,
migrations, or release decision, plan one writer or use Level 4 staging instead.
This reference defines the topology; it does not launch writers, create
worktrees, or implement the deliverables.

Keep local task facts with their owner under [Change locality](change-locality.md).
Reference the public contract from other lanes rather than restating private check
or dispatch inventories. Do not introduce the formal source compiler at this tier.
Scope later review/evidence invalidation to actual changed dependencies.

Apply [Acceptance design](acceptance-design.md) before selecting or expanding
verification. Bind the required claim/observation, why the environment is needed,
what repetitions or combinations add, and the simpler adequate acceptance design.
Use the [planning-review assignment](../assets/plan-review-assignment.md) for the
four scoped reviewers; record their actual assessments in the existing verification
section. Material later changes return to affected groups, not a new blanket audit.

## Prove the split before planning parallel writers

The [plan-conformance review](plan-conformance-review.md) must challenge the
requested outcome before accepting the lane split. A requested Tier 3 label does
not authorize expanding product scope or inventing independent deliverables.
Assign these checks to SCOPE_AUTHORITY and TOPOLOGY_SIMPLICITY in the planning
panel; they do not replace or add an execution assurance lane.

Write a compact ownership table before delegation:

| Deliverable | Owner | Allowed write area | Inputs from others | Acceptance check | Integration order |
| --- | --- | --- | --- | --- |
| <outcome> | <worker> | <paths/components> | <declared interface> | <focused check> | <number> |

Do not authorize parallel writers in the plan until every row has a disjoint
write area and a clear integration order. Shared tests, generated files,
schemas, lockfiles, and configuration are common reasons that a split is not
actually independent.

## Organize the plan by lane ownership

Modularity does not promote this plan to Level 4. Use independently owned sections
for small lanes and separate files when substantial lanes need independent revision
or the user requests them. An optional layout is:

```text
plan.md                 # outcome, shared contracts, assurance, integration, review
lanes/component-a.md     # lane A's owned work, local verification and handoff
lanes/component-b.md     # lane B's owned work, local verification and handoff
```

File names and directory shape are choices, not a new fixed schema. The root owns
the public ownership table above, shared input/output contracts, cross-lane
assurance and serial integration. Each lane owns its task details, local sequence,
verification and return contract, referencing its root ownership row and shared
contracts. Link from the ownership table to the lane section/file; do not repeat
an independently editable copy of its write boundary or acceptance criteria.

A local implementation/check change belongs in that lane. Changes to shared
interfaces, ownership, integration order or acceptance meaning reach their real
consumers and the relevant review groups. The integrator still verifies integrated
bytes. Splitting documents does not prove disjoint implementation ownership, create
new agent roles, or remove the independent assurance lane. Do not import M01-M10,
three-entry paths, formal card schemas or the source compiler solely to make a
Level 3 plan modular. Explicit selection of that full framework follows Level 4
routing and retains its complete requirements.

## Build the topology

1. Keep one primary agent as decision owner and integrator.
2. Freeze the shared contract or have the primary agent make the shared change
   first. Writers must not independently redesign the same seam.
3. Specify future isolation proportionately:
   - a shared workspace for truly non-overlapping paths;
   - a Git worktree for isolated writers or experiments; or
   - a `codex exec` / `claude -p` worker that returns a patch when that is easier
     to integrate.
4. Give each writer the ownership row plus a scoped task card: objective, write
   boundary, accepted inputs, local check, expected return, and completion
   condition.
5. Schedule at least one independent read-only check or review lane against a named cross-lane,
   integration, or high-risk behavior. Run independent review/check lanes concurrently with writers
   whenever their declared inputs are available; do not omit this Tier 3 assurance lane.
6. Require serial integration in the declared order. The planned primary agent
   resolves conflicts and runs final checks on the integrated bytes, not on
   worker claims.
7. Require the future executor to retire temporary worktrees only after
   inspecting status and never discard dirty work.

## Bind reusable execution blocks

Every substantial post-step matrix must bind [Matrix execution](matrix-execution.md)
and its template in the existing verification/task-card fields. Serial integration
does not serialize independent tests on a stable snapshot. Specify concurrency and
isolation, terminal-state exits, complete collection, dependency graph, cause-group
repairs, affected reruns and reviewed coordinate/total budgets. Include these in the
EXECUTION_RESOURCES planning review, with VERIFICATION retaining coverage review;
do not create another execution assurance lane for it.

Use [the shipped blocks](execution-blocks.md) inside the existing ownership rows and task cards.
Before release to writers, classify document/pack/fixture/authority dependencies and name their
consumers. Only current live identities wait until allocation; unresolved external prerequisites
must be visible early and cannot hold unrelated implementation. Missing adapters get one scoped owner.

For stateful test startup, bind effective writable paths and child inheritance to an executable
startup/shutdown proof before broad checks. For costly live acceptance, bind one real public-transport
rehearsal against a deterministic backend and one early path through fresh setup, commit, reconnect,
and protected use. A canned session model alone does not prove those boundaries.

Choose the host runner or packaged blocks plus thin adapters before commissioning a new framework.
Share mechanics without sharing independent oracles. Preserve accepted implementations on a resumed
plan; optimization does not authorize rebuilding the runner or replaying completed stages.

Name review milestones and what changes invalidate them; pool compatible repairs and rerun affected
checks. Full gates need a release/invalidation reason, not a reporting milestone. Put ranges and their
basis on the critical path, observe actual progress, and reassess after an overrun before another
expensive cycle. Do not hard-timeout agents. After integration, keep ROOT and only the roles whose
remaining outputs are consumed. Independent local checks need not wait for serial integration.

Reuse one factual result per consumer and summarize it in handoffs. `execution_blocks.py` supplies
mechanical profile validation, scoped readiness, environment mapping, footprint comparison, check
selection, and result recording; it does not make semantic acceptance decisions.

All planned review/check assignments carry the
[finding-admissibility rule](acceptance-design.md#finding-admissibility-requirements-define-the-review-boundary)
in their task block: require requirement linkage and acceptance impact; reject
out-of-scope gaps even when genuine, without weakening required assertions or
misreporting test status. A nonblocking note creates no new implementation lane.

## Return contract

Each worker returns: completed outcome, changed files, checks run and results,
assumptions made, integration notes, and unresolved risks. It does not merge,
commit, push, or alter another worker's area unless explicitly authorized.

A Level 3 plan is invalid unless it contains at least two genuinely disjoint implementation lanes,
the independent assurance lane required above, one decision owner/integrator, and a serial integration
order. If any element is absent, select the level whose required structure actually matches the plan.

## De-escalate when needed

If a shared seam, conflict, or changing requirement invalidates the ownership
table during execution, the plan must stop parallel writing and route the work
under one writer or promote it to Level 4 staging. Do not compensate with locks,
a roster, or an elaborate coordination protocol.
