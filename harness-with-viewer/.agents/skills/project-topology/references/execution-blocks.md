# Shipped execution blocks for Tier 3 and Tier 4

Use these blocks when the plan has expensive checks, stateful processes, external acceptance, or
repeated repair. They ship with this skill; do not copy their Python implementation into each plan.
Prefer an existing equivalent host facility. Record the selected implementation and its limitations
in the existing plan/card. A block is a helper inside a stage or M-module, not another agent, gate,
M-module, workflow database, or reason to invoke the formal compiler.

## Select and bind the blocks

| Block | Trigger and outcome | Shipped implementation | Project adapter responsibility |
| --- | --- | --- | --- |
| Readiness | Check prerequisites early; block only consuming operations | `ready` checks declared files/digests and named attestation receipts | Discover actual prerequisites; an owner accepts authority, provenance, target identity, and receipt meaning |
| Isolated environment | Prepare consistent writable paths before startup/import | `env` resolves environment paths beneath an existing owned run root; rejects traversal/escape | Create directories; apply patch to every child; prove effective application paths; use existing supervisor |
| Write footprint | Detect contamination of a named external store | `snapshot` and `compare` detect file/directory additions, removals, and byte changes | Name all relevant stores from source inspection; stop known writers while snapshotting; retain before/after snapshots outside watched roots |
| Rehearsal | Prove one costly public workflow before resource allocation | Reusable adapter contract below; project runs its actual transport with a deterministic backend | Supply application entrypoint, backend injection, public calls, independent expected responses, and cleanup |
| Repair selection | Preserve valid checks and rerun affected consumers | `select` propagates changed input labels and missing credit through a check dependency graph | Map input changes conservatively; check actual source/configuration/external state; supply only valid PASS credit |
| Evidence/progress | Record one result for a named consumer | `record` writes a versioned JSON result with status, elapsed seconds, evidence paths, and basis | Measure real elapsed time, capture exit/results, and make semantic decisions; reuse existing handoff/result location |

This is an executable utility kit with explicit adapter gaps. It is not an OS sandbox or command
supervisor. It does not launch children, set the caller's environment, fetch artifacts, operate hardware,
grant permissions, accept products, stop processes, delete files, or automate cleanup. Snapshot coverage
is limited to named roots and the sampling interval; temporary writes between samples may escape
detection. Use OS enforcement or application instrumentation when a stronger claim is required.
Links/junctions and unreadable paths cause errors rather than incomplete success.

## Planning rules learned from recorded failures

1. **Discover before committing the schedule.** Check document/pack availability and human-action
   dependencies during initial inspection. Defer only facts that actually require a later live state.
   Give each unresolved fact an owner, consuming operation, next action, and retry trigger. A 403 or
   missing authorization blocks that case; retry only with new evidence/access/state. Independent work
   continues. Provenance-checked immutable packs may be reused from a cache and copied into fresh roots;
   live bindings, permissions, and board state may not be cached as reusable authority.
2. **Prove isolation once at its owner.** A temporary directory is not evidence of containment. Name
   the server's effective storage settings and child inheritance; smoke startup and shutdown before
   a broad gate. Watch the known shared store. Recheck after environment/import/lifecycle changes.
3. **Exercise an early complete path.** For coupled state transitions, identify the cheapest decisive
   path from fresh state through commit, reconnect, and first protected use. Run it before broad feature
   expansion when its inputs become executable. Do not wait for live hardware to discover a circular
   dependency on already-committed state or an assignment-token representation mismatch. Include
   existing public argument order and accepted identifier forms in the compatibility proof; the
   recorded run also discovered legacy hyphenated IDs and positional setup calls only at the full gate.
4. **Rehearse actual transport.** A mock reproducing the runner author's assumptions is insufficient
   proof of the real entrypoint, serialization, error flags, protected-text responses, continuation
   tokens, and reconnect order. Share neutral transport/fixture mechanics; keep test judgments and
   expected behavior independent of production implementations.
5. **Scope repairs and review.** Every follow-up names the changed input and invalidated claim. Keep
   focused checks inside repairs, batch compatible findings, and run broad verification at a stable
   boundary when shared inputs justify it. A report-only correction cannot reopen code review. Review
   findings remain open; do not use a fixed review quota to waive required independent evidence.
6. **Price supporting infrastructure.** Compare the host tool, shipped block plus thin adapter, narrow
   script, and new framework before commissioning a runner. Name the missing behavior and consumer.
   Choose one owner for common mechanics. File size is a prompt to inspect, not proof of waste. On a
   paused project reuse accepted infrastructure; do not rewrite it for elegance or sunk-cost savings.
7. **Track real progress cheaply.** Name the critical path, expected stage ranges and their basis,
   concurrent branches, and a reassessment trigger. Elapsed time alone is not a timeout or evidence of
   failure. An overrun plus another proposed cycle prompts scope/fixture/review reassessment. Record
   start/end or elapsed in existing results; never sum overlapping agent durations as project wall time.
   Do not retrospectively turn unmeasured activity into precise saved-time estimates.
8. **Keep one evidence owner.** Store factual results once; handoffs summarize and link. Document-only
   changes do not create another assurance campaign. Consumer-specific private transcripts remain
   private; this utility prints paths and configured reasons, so do not put tokens/secrets in profiles.
9. **Schedule by dependencies.** Serial integration does not serialize independent local checks. After
   parallel delivery, retire terminal lanes and dispatch only needed repair/review roles. Preserve user
   model/effort choices; do not label an explicit allocation an optimization defect or silently replace it.

## Profile and command contract

For substantial matrices, use [Matrix execution](matrix-execution.md) and its
[binding template](../assets/matrix-execution-binding.md) alongside these blocks.
The host runner/adapter owns concurrent dispatch, terminal-state detection,
failure collection and bounded cleanup. The shipped selector and recorder do not
implement those controls. Reference the binding from the existing block/card;
do not add its scheduling fields to the helper's strict JSON profile schema.

Requires Python 3.11+ and the standard library. Start from
[`assets/execution-profile.example.json`](../assets/execution-profile.example.json). The profile is a
mechanical projection of an existing plan's inputs/dependencies, not a second policy source. Keep it
small and update it when those interfaces change. `validate` checks structure and dependencies only.

Required top-level fields: `version` (integer 1), `inputs` (unique labels), `environment` (environment
name to relative subdirectory), `checks` (nonempty rows), and `resources` (possibly empty rows).
Each check has `id`, nonempty `inputs`, and `prerequisites` referencing check IDs. Cycles, duplicate IDs,
unknown prerequisites/inputs/consumers, and unexpected fields fail validation. The declared list gives
stable ordering among independent checks; the selector does not prescribe serial execution.

Each resource has `id`, `owner`, `consumers` (check IDs), and `kind`:

- `file`: `path`, optionally `sha256` when byte provenance matters. Relative paths resolve from `--root`.
- `attestation`: `status` is READY, PENDING, or BLOCKED. `evidence` is a reason when unresolved, or a
  receipt path when READY. Existence of a receipt is mechanically checked; its truth, freshness, and
  authorization are the decision owner's responsibility. A prior narrative PASS is not a current
  authority receipt. Resource blocks propagate through prerequisite consumers.

From the project root (replace the sample profile and private paths with the plan's bindings):

```powershell
python .codex/skills/project-topology/scripts/execution_blocks.py validate path/to/profile.json
python .codex/skills/project-topology/scripts/execution_blocks.py ready path/to/profile.json --root . --consumer live
python .codex/skills/project-topology/scripts/execution_blocks.py env path/to/profile.json --run-root path/to/owned-existing-run
python .codex/skills/project-topology/scripts/execution_blocks.py snapshot --path path/to/watched-store --output path/to/private-before.json
python .codex/skills/project-topology/scripts/execution_blocks.py compare path/to/private-before.json path/to/private-after.json
python .codex/skills/project-topology/scripts/execution_blocks.py select path/to/profile.json --changed runner --credited unit --credited rehearsal --credited live
python .codex/skills/project-topology/scripts/execution_blocks.py record --claim rehearsal --status FAIL --elapsed-seconds 12.4 --evidence path/to/private-log.txt --note 'parser rejected protected text' --output path/to/new-result.json
```

CLI returns 0 for successful mechanical operations, 1 for invalid input/I/O, and 2 for blocked
readiness or a changed footprint. `record` retains the supplied status; a successful write is not a
test pass. PASS/FAIL records require existing evidence files. Elapsed seconds must be finite and
nonnegative. Output parents must exist, new output paths must be unused, and nothing is overwritten.
Use private result directories outside the watched store. No cleanup is attempted after any error.

`select` treats all uncredited checks as requiring execution. An unknown changed label invalidates all
checks conservatively. Dependencies propagate invalidation; no changed labels plus explicitly valid
credit permits reuse. An omitted source/environment dependency can make selection unsound: ROOT must
review the input map and external state before supplying credit. It is not automatic dependency analysis.

## Project rehearsal adapter contract

Use the host's existing tests and launcher. Specify one adapter with these inputs and outputs:

| Field | Required binding |
| --- | --- |
| Entry | Actual executable/module, arguments, cwd, environment patch, and runtime version |
| Isolation | Effective writable roots from application inspection; subprocess inheritance and known watched stores |
| Scenario | Smallest public path through fresh state, transition, reconnect, operation, refusal, and cleanup relevant to the claim |
| Backend | Deterministic substitute below the public transport/authorization boundary; no real device or service allocation |
| Oracles | Independent contract for token forms, continuation, supported operations, structured/text results and error flags |
| Output | Public transcript or focused test evidence, actual exit, elapsed time, cleanup outcome and external footprint comparison |
| Credit | Exact source, runner, environment, protocol and external inputs that invalidate the rehearsal |
| Missing adapter | Named owner, smallest implementation, blocked consumer and retained independent progress |

No generic built-in simulator claims to implement an arbitrary project's protocol. Where backend
injection cannot safely support a real public rehearsal, record the limitation and bind a narrowly
authorized next proof. Never turn schema-valid canned responses into live acceptance.

## Tier 3 and Tier 4 integration

Tier 3 puts selected blocks in its existing stage/task-card inputs, acceptance, and repair fields.
Use [`assets/execution-block-binding.md`](../assets/execution-block-binding.md) as a small drafting aid;
inline its filled content into the existing plan rather than creating a second coordinator.

Compact Tier 4 uses the same binding within its durable stages. Formal Tier 4 retains its exact package,
M01-M10 catalog, 20-field cards, three STEP entry flows, and P01-P15 ownership. Helpers are implementation
entrypoints within the existing modules, not new module instances or exemptions:

| Existing formal owner | Shared block use / existing policy |
| --- | --- |
| M01 | Resolve failed resource/adapter prerequisites; only their consumers wait |
| M03 | Thin independent rehearsal/oracle adapter; reuse common mechanics |
| M04/M07 | Scoped check selection and evidence; R14-R19, S7-S10 govern review and reuse |
| M05 | Semantic classification and retained credit; helper output does not accept work |
| M08 | Env/footprint and actual transport rehearsal under R20/R22 |
| M09 | Recheck live binding/authority, record real attempt and cleanup; fakes cannot pass live coverage |
| R3 / S12 / Pass 15 | Supporting-artifact payoff, stage ranges, actual progress and reassessment |

Formal bindings live in existing MI Inputs, Outputs, Isolation and lifecycle, Critical-path effect,
and Local instructions fields. A profile is a referenced target-tool input only when used. It adds no
fixed package file or schema field. Keep shared policy in global-rules; the existing structural
validator still checks the formal schema, while helper tests/profile validation check these mechanics.
