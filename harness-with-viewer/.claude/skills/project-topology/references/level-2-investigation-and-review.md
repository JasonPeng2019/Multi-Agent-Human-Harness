# Level 2 — delegated investigation and review

Use this level to design how a later executor will gain independent evidence
without creating competing writers. The planned primary agent owns all future
implementation, integration, and final decisions. This reference defines the
plan; it does not launch investigators or perform the implementation.

Keep local task facts with their owner under [Change locality](change-locality.md).
Reference the public contract from other lanes rather than restating private check
or dispatch inventories. Do not introduce the formal source compiler at this tier.
Scope later review/evidence invalidation to actual changed dependencies.

Apply [Acceptance design](acceptance-design.md) before selecting or expanding
verification. Bind the required claim/observation, why the environment is needed,
what repetitions or combinations add, and the simpler adequate acceptance design.
Use the [planning-review assignment](../assets/plan-review-assignment.md) for the
two focused assignments by default: SCOPE_STRUCTURE and EVIDENCE_EXECUTION.
Record both independent identities, their four-domain coverage and actual assessments
in the existing verification section. Split only an overbroad pair under the shared
review rules; this may require three or four reviewers without changing the tier.
Material later changes return to affected owners, not a new blanket audit.

Normally keep this Level 2 plan in one cohesive document. If a component benefits
from independent revision, give it an owned section or linked file under Change
locality; this does not add an implementation writer, a formal package or a tier.
Do not create modular scaffolding merely because the skill supports it.

## Build the topology

Before acceptance, include [plan conformance and simplicity](plan-conformance-review.md)
through the proportionate independent planning panel, including the test-scope audit.
Challenge whether the support lane addresses the requested delivery, preserves one
implementation owner, and avoids making optional live work a delivery prerequisite.

1. State the primary outcome and the decision the extra evidence will inform.
2. Split only read-only lanes that are genuinely independent: for example,
   repository mapping and focused test discovery; a failure reproduction and a
   read-only design review; or two separate external sources.
3. Give each lane a concrete, scope-bounded task card:

   ```text
   Objective:
   Scope and entrypoints:
   Write authority: none
   Deliverable: findings with file/line or command evidence
   Reviewer rule: cite the violated requirement and acceptance impact; apply finding
     admissibility from acceptance-design.md. A genuine gap that leaves requirements
     satisfied and required tests passing is REJECT-OUT-OF-SCOPE, invalid as a blocker
     or required correction. Green tests do not excuse a requirement violation.
   Checks allowed:
   Completion: the question is answered or the uncertainty is named
   ```

4. Specify a native subagent when available. Otherwise specify the installed matching
   command-line worker—an unbounded `codex exec` or `claude -p` agent session—when that isolation is
   worth the startup cost. State that the future executor must never put the agent launch or session under the finite-command supervisor;
   only an explicitly manifest-selected finite command invoked inside it is bounded.
5. Define a single collection point where the planned primary agent compares
   evidence, resolves conflicts, and makes the implementation decision. Findings
   are inputs, not votes.
6. Route future implementation through one writer, followed by focused
   verification selected from the combined evidence.

## Useful shapes

When verification includes a substantial costly or stateful matrix, apply
[Matrix execution](matrix-execution.md) and embed its compact binding in the existing
verification section. One delivery owner can schedule isolated independent test
processes concurrently, collect all failures and repair by cause group. This does
not authorize parallel implementation writers, worktrees or another coordinator.
Have the reviewer owning EXECUTION_RESOURCES assess the graph, terminal exits, isolation,
rerun selection and wall-clock budgets. Ordinary short checks need no matrix template.

| Need | Shape |
| --- | --- |
| Unfamiliar failure | One investigator maps reproduction/call path; primary agent implements. |
| Consequential local change | Primary agent drafts; one read-only reviewer critiques the diff or plan. |
| Independent questions | Two read-only investigators return evidence; primary agent reconciles and writes. |

## Do not add

- parallel writers or worktrees;
- a coordinator process, lane registry, or persistent state;
- a review merely because a review skill exists; or
- a second investigation after the first result is already decisive.

If the writer needs to be split, reassess at Level 3 rather than quietly adding a
second writer to Level 2.
