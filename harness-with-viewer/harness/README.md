# Portable Coding Orchestrator Harness (v2)

The Harness v2 coordinates ordinary software work across Git branches and worktrees. One public
launcher exposes the entire operator surface. `harness-single/` is the canonical product root and
launch directory; run all commands from there:

```powershell
python -m orchestrator_harness.operator_launch [--json] {harness,lane,resume-lane,manager,lease,send-lane-notification,scan,watch,view,health}
```

Every public command returns the small structured result `{ ok, code, summary, evidence_paths,
next_action }`; `--json` emits it as the machine-readable result object. Success prints a short
status line and exits 0; failure prints one stable failure code on stderr and exits non-zero.

## What the harness does and does not do

- Does: prepare and launch one coding worker per lane, publish durable lane/event records,
  serialize declared exclusive resources, deliver manager events, and record ROOT's review and
  acceptance.
- Does not: schedule work, choose providers, decide outcomes, accept results, operate hardware,
  or replace the root orchestrator. The persistent manager owns planning, launches, decisions,
  integration, acceptance, promotion, and final cleanup. The optional watcher is diagnostic-only
  with `evaluator_enabled: false`.

## Public CLI surface

The sole public CLI is `operator_launch`. Its groups and subcommands:

- `harness setup [--overwrite]` — one-time idempotent integration; `harness shutdown` — end the
  whole runtime.
- `lane bootstrap --lane-id --provider --model [--provider-option NAME=VALUE]
  [--exclusive-resource] --task-card` — prepare one lane; `lane launch --lane-id` — start one
  prepared lane.
- `lane completion-review (--event-id|--lane-id) --review-outcome {PASS,FAIL,BLOCKED} --approval
  {ACCEPTED,REJECTED} --review-summary [--evidence] [--force-accept] [--force-reason]` — record
  ROOT's review and acceptance.
- `lane force-stop --lane-id` — hard-stop one stuck lane; `lane retire --acceptance-ref` —
  gracefully retire one accepted lane.
- `resume-lane --lane-id --resume-task-card [--rationale]` — re-run a stopped, unaccepted lane.
- `manager acknowledge --event-id <top-level-event-id>` — move one event PENDING -> ACKNOWLEDGED; `manager close
  --event-id --outcome {COMPLETE,BLOCKED} --summary <text>` — close an acknowledged event (managed only).
- `lease force-release --resource-id <id>` — recover one declared orphaned resource lease. The
  command refuses an exact live holder and fails closed unless current process and lane/run evidence
  proves release is safe; follow its returned `next_action` instead of hand-editing lease records.
- `send-lane-notification --lane-id --prompt` — append one assignment to a running managed lane.
- `scan --no-write` — read-only lane-status snapshot; `watch --until-actionable [--timeout]
  [--until-event]` — block until an actionable condition exists.
- `view [--once] [--ascii] [--no-color]` — read-only terminal view of every lane's seven steps
  (Recall, Vet, Plan, Pack, Work, Review, Learn) and what needs ROOT; `--once` prints one snapshot.
- `health reconcile` — rebuild active-lanes and re-derive status.

## One-time ROOT sequence

1. Copy `examples/harness-config.example.json` to the ignored
   `local-config/harness-config.json`, replace the example value with the absolute path to the
   target Git repository, and choose `managed_coordination` (`enabled` or `disabled`; default
   `enabled`). This is the closed two-key `harness-config/v1` shape; no other keys are legal.
2. Copy `examples/resource-manifest.example.json` to the ignored
   `local-config/resource-manifest.json`. This is the closed `resource-manifest/v1` shape with a
   literal `schema` field and a `resources` list. Every nonempty entry declares a nonempty `id`
   and `exclusive: true`; duplicate IDs and unknown fields are invalid.
3. Run `harness setup` (repeat with `--overwrite` to re-integrate). Setup validates the config and
   manifest, preflights the entire catalog before writing anything, stages and byte-verifies the
   active super-cache, installs the ROOT payloads, writes the active resource manifest and lease
   directory, and starts the persistent monitor. It starts no lane or provider and never creates
   an epoch or worktree.

Setup preserves existing `.codex/` and `.claude/` directories. It adds the harness-owned skills,
hook scripts, and binding files, while structurally merging harness hook registrations into an
existing `.codex/hooks.json` or `.claude/settings.json`. Existing fields, permissions, and hook
groups remain in place. An existing `.codex/config.toml` is preserved byte-for-byte and must already
set `[features] hooks = true`. `--overwrite` replaces only harness-owned payload files; it does not
replace these shared provider configuration files.

The local pair takes precedence over the legacy same-root pair, which remains readable only for
backwards compatibility. The two locations are never mixed. Harness-root discovery is based on
the product source markers and stops at `harness-single/`, even when local configuration is
missing; it therefore cannot capture an unrelated parent checkout's configuration.

### Managed vs plain

`managed_coordination: "enabled"` (managed) stages a manager queue for the epoch: ROOT uses
`manager acknowledge`/`manager close` and `send-lane-notification`, and the monitor promotes
worker notices into the queue. Managed watch wakes from an unresolved queue event or an
actionable lane/resource state and records a durable per-session/queue delivery receipt for
queue events. `disabled` (plain) omits the manager
queue; lanes run without ROOT-to-worker assignments and plain scan/watch never reads it.

## Providers and the adapter catalog

Three provider IDs ship: `codex`, `claude-code`, and `qwen-code`. Each has one tree under
`adapters/<provider-id>/` with `root/` (ROOT payload), `super-cache/` (worker payload), and
`harness/launcher_binding.py` (registered under
`orchestrator_harness/provider_adapters/<provider-id>/` by setup). `super-cache/custom/` is the
custom file-only adapter tree: reserved for local, non-shipped payload files. The shipped tree
keeps only a marker README, and runtime staging never reads it unless an operator explicitly
places payloads there.

Provider launch preferences are explicit and closed: Codex requires `reasoning_effort` and
`service_tier` and optionally accepts `launcher=ollama`; Claude Code requires `effort`; Qwen Code
accepts no launch preferences. Pass each value with a repeated `--provider-option NAME=VALUE`.

## Super-cache and bootstrap

`super-cache/workspace/` is the provider-neutral base staged into every managed worktree by
`lane bootstrap`: the shared `.agent-workspace/` skeleton plus the three provider-neutral helpers
(`result-stop-check.py`, `lane-queue.py`, `manager-notify.py`). Bootstrap also materializes the
selected provider's worker payload, writes the authoritative worker binding with runtime paths,
and creates the lane's inbox/outbox. Bootstrap opens the epoch on first use and reuses it while
the immutable configuration is unchanged.

## Worker RESULT vs ROOT review/acceptance

The worker writes `RESULT.json` at the worktree root (`result/v1`). A result is merge-ready only
after schema, lane/run identity, outcome, summary, evidence, and content-hash validation succeed
against the current branch tip in a clean worktree. ROOT then records the factual finding and the
separate accept/reject decision with `lane completion-review`, which writes the linked
`COMPLETION_REVIEW.json` and `ORCHESTRATOR_ACCEPTANCE.json` pair outside the worktree and closes
its own managed review event. Lifecycle: task card -> RESULT.json -> COMPLETION_REVIEW.json ->
ORCHESTRATOR_ACCEPTANCE.json.

An invalid result may receive at most five corrective prompts in the same native provider
session, with per-attempt transcript, stderr, cleanup, and validation evidence. A sixth invalid
attempt, a missing native resume session, or a provider startup/auth/process failure ends as
`provider_exited_no_result`; it never starts a fresh context.

## Optional memory and accepted-plan handoff

The integrated `memory_harness` package supplies deterministic task/plan contracts, bounded local
and optional Atlas/EverOS search, reviewed template reuse, privacy filtering, durable dispatch
operations, usage evidence, and SQLite snapshot/restore. Ordinary task cards remain on the
inherited path with no memory store or optional call. Enhanced cards add a validated
`memory_handoff`; `absent` and `candidate_review` remain fail-closed planning states, while only an
exact ROOT `execution_accepted` plan is finalized into worker context and may launch.

Every task card, ordinary or enhanced, must include nonempty `acceptance_criteria`, `deliverables`,
and `reason_for_acceptance_and_deliverables` fields. Enhanced scrubbed lanes isolate provider
configuration under the worktree (`.codex`, `.claude`, or `.qwen`) and retain that boundary across
resume. See `examples/project-task-card.example.json` and `memory_harness/README.md` for the full
contracts and optional dependency setup.

## Resume, force-stop, retire, shutdown

- `resume-lane` re-runs a stopped, unaccepted lane in its same worktree and provider session with
  a fresh `run_id`; it never reconstructs a session, PID, or worktree.
- `lane force-stop` hard-stops one stuck lane by exact recorded identity.
- `lane retire` gracefully retires one accepted lane (by acceptance reference) with
  cleanup-proof-first and archive-first semantics.
- `harness shutdown` ends the whole runtime: OPEN -> SHUTTING_DOWN, each lane's controller cleans
  its own processes, the monitor stops, the active-epoch marker clears, and the runtime closes.
  It never kills by broad process name.

## Read-only shipped source

The shipped source (`adapters/`, `super-cache/`, `orchestrator_harness/`) is read-only product
material. Launcher bindings are shipped/read-only: setup validates catalog binding bytes against
the registered binding and never copies a binding into product source. Local configuration
belongs under `local-config/`; runtime state lives under the configured root workspace's
`.harness-runtime` with a fresh epoch per live run. Keep source directories free of runtime
output.

## Evidence and provider proof

Reported checks are evidence; the harness does not execute them. Static examples and fixtures are
never live provider proof: only a real recorded live run with exact identity evidence (provider,
session, command provenance, delivery receipts) can claim provider proof.
`orchestrator_harness.release_checks` is the one stable-ID registry/selector owning fast,
affected, full, and release checks; credit requires declared-input fingerprints plus exact source
root, Git common directory, and branch identity, with the recorded origin tip still an ancestor
of the current tip.

## Documentation

- `QUICK_START.md` — shortest live run.
- `QUICK_RULES.md` — authority and safety rules.
- `orchestrator_harness/README.md` — command and contract reference.
- `orchestrator_harness/SPEC.md` — harness contracts.
- `docs/HARNESS_WATCHER_GUIDE.md` — optional diagnostic watcher.
- `adapters/README.md` — provider adapter catalog and binding contract.

## Hermetic macOS product demonstration

Run `python -m unittest orchestrator_harness.tests.test_macos_product_smoke -v` from
`harness-single/` to exercise the public setup, bootstrap, launch, result, review, retirement, and
shutdown path in a disposable Git repository. The test sanitizes ambient Git routing and config,
uses empty template/hook directories, and places a controlled fake `codex` executable on `PATH`;
all result and transcript evidence is explicitly synthetic and is never live-provider proof. This
dedicated macOS demonstration skips on every non-macOS host rather than reporting a cross-platform
pass.

## Inspect agents

Run `python3 -m orchestrator_harness.operator_launch view`. Use
`--runtime-root /absolute/path/to/.harness-runtime` to inspect an existing run
without changing configuration or starting agents. Automatically opened viewer
windows enable color explicitly. For manual launches, use `--color` to override
an inherited `NO_COLOR` setting, or `--no-color` for monochrome.

The overview shows all agents with their task, model, status, and a prominent
seven-stage light strip. Working stages pulse once per second; completed stages
stay green, waiting stages stay amber, and unused memory stages are dim. Select an agent
with up/down and press Enter to open it. Left/right (or Tab) switches between:

- **Prompt:** the initial worker prompt and any correction prompts, verbatim.
- **Output:** agent messages, commands and their output/exit status, file edits,
  and provider diagnostics. Codex item updates are combined so each command appears
  once. Transport metadata, hook events and usage envelopes are omitted.
- **Result:** the verified root review, verdict, decision and saved check output,
  followed by the worker’s summary, evidence and final response. Pending reviews
  are explicitly identified.

**Events** shows an Inbox (ROOT → agent assignments) and Outbox (agent → ROOT
notifications and labeled harness status events). It includes processed messages,
current states, timestamps, event/signal IDs, payloads and state history for the
selected run. Forwarded notifications appear once. Events start collapsed: Up/Down selects an
event, Enter expands/collapses its complete record, and Page Up/Page Down scrolls
long contents. Selection and expanded records persist through live refreshes.
ROOT also appears in the overview with the same tabs: its Inbox contains forwarded
agent events and its Outbox contains assignments sent to agents. ROOT’s Result
shows recorded reviews; its Prompt and Output explain that the harness does not
capture ROOT’s conversation or terminal transcript. This read-only view refreshes
every two seconds and does not acknowledge or send messages.

Up/down scrolls; Page Up/Page Down scrolls a page; Home goes to the beginning;
End follows the latest output. Live agents open at the latest output, while
completed agents open at the beginning. Escape returns to all agents; q quits.
All new output—messages, commands, code and tool output—is revealed line by line
at 12 lines per second between the two-second data refreshes. Updates append in
arrival order without expanding earlier command records above the reader.
Press End to skip the reveal queue. Existing history loads immediately when an
agent or section is opened. This is a display effect over received text, not a
change to provider streaming or agent execution.

Scrolling up holds the displayed output steady, including when earlier command
records grow. A “New activity ↓” indicator appears as more output arrives. Press
End to return to live output. The agent name and the four sections stay visible
while scrolling. Output is
refreshed every two seconds. Files larger than 512 KB have an explicit preview
limit; the full original files remain on disk. All attempts are included.
Terminal control sequences are neutralized, so provider output cannot control
the viewer terminal.

Replay a run without invoking models or executing any saved commands:

```sh
python3 -m orchestrator_harness.operator_launch view --replay --speed 1.5
python3 -m orchestrator_harness.operator_launch view --list-replays
```

Add `--runtime-root /absolute/path/to/.harness-runtime` to select another saved
workspace. Only the latest run is retained for replay. In the live viewer, **r** starts replay of the selected runtime's latest
run. During replay, **Space** pauses/resumes, **r** restarts, **[ / ]** seeks backward
or forward ten seconds, **+ / -** changes speed, and **l** returns to live view.
Agent navigation, tabs and expandable events work normally. A persistent banner
shows REPLAY, speed, play/pause state and timeline position. Playback defaults to
1.5×: 15 recorded seconds take 10 real seconds.

When the CLI starts a newer run, replay stops automatically and the viewer switches
to that run’s live overview, even if playback is paused or the workspace changed.
The viewer checks run identity every quarter-second using the harness’s latest-run
registry. It clears old output, event selections and playback caches on switching.
Only the newest replay journal is retained; older replay databases are deleted
when the next run is registered, while original agent logs and workspaces remain.
Playback keeps a compact frame index and loads only the current snapshot into
memory. `--list-replays` reports the newest run; `--epoch` accepts only that epoch.

New managed runs record immutable TUI observations once per second through the
native monitor, plus snapshots after successful mutating launcher commands.
The journal is stored under `.harness-runtime/replay/<epoch-id>.sqlite3` and includes
worker prompts, visible output, event payloads/history, statuses and root reviews.
Recording is independent of whether a viewer window is open. It captures observed
arrival timing at one-second resolution, not provider token timings. Existing
512 KB artifact-preview limits still apply; original transcripts remain on disk.
ROOT's external CLI conversation is not captured. Plain runs without a monitor
have command-boundary snapshots only.

Playback reads frozen snapshots, so it never reads later worktree contents or
publishes messages, acknowledgements, reviews or work. Seeking backward hides
later output and reviews. Partial recordings and recording failures are labeled;
recording errors are retained in `replay/recording-errors.log` and do not interrupt
agent execution. The latest-run pointer is stored in `local-config/latest-replay.json`.

The latest completed run from before recording was introduced can be replayed
with **Approximate timing**: saved output is paced across agents, and events and
reviews appear at the end. Its original interleaving cannot be recovered. Older
runs are no longer offered for replay after a newer run starts.


“Awaiting orchestrator review” means the root orchestrator has not yet recorded
completion-review. This viewer does not submit reviews or launch reviewers.

## One-command live visualizer demo

From this directory run:

```bash
python3 run_visualizer_demo.py
```

This runs the local visualizer tests, creates a fresh disposable calculator Git
repository, opens the visualizer, and launches two real Codex workers. It uses
your logged-in Codex account and configured model (`--model NAME` overrides it).
Every invocation starts from the same buggy baseline in a new directory under
`../runtime/visualizer-demos/` (outside the harness source); previous runs, logs, and your original test workspace
are preserved. Local harness configuration is pointed at the new run; its previous
contents are backed up in that run's `.demo/` directory. An already-open harness
runtime must be closed first.

After execution, the script runs each worker's unittest suite and independent
calculator assertions, checks committed file scope and whitespace, and records
acceptance only after those fixed demo checks pass. This is automated fixture
validation, not an independent AI code review. It then shuts down the runtime,
leaving the worktrees, logs, test reports, and viewer available for inspection.
Failures/interrupts stop only this run's workers and preserve their evidence.

Use `python3 run_visualizer_demo.py --check-only` for local tests without any
agent launches or configuration changes. The lights and gradual text reveal are
visible during a live run; old completed messages are shown immediately.
