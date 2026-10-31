# Benchmark terminal viewer

Run from `harness-single-run-version/` in a separate terminal:

```powershell
python -m orchestrator_harness.operator_launch view --runtime-root 'C:\path\to\workspace\.harness-runtime'
```

Use the benchmark workspace's `.harness-runtime` directory. Omitting
`--runtime-root` uses the workspace in `harness-config.json`. The inherited
configuration currently points to a removed run; select an existing runtime
explicitly until a new benchmark workspace is prepared.

The first screen lists epochs, newest first, with the active epoch highlighted
and recorded replays marked.
Choose one with Up/Down and Enter. The viewer stays on that epoch as the run
progresses, even if another epoch becomes current. It reads every retained
`epochs/<epoch-id>/lanes/*/lane.json`, including retired agents from earlier
steps. Each benchmark run is one epoch; separate runs remain separate choices.

In the agent overview, Up/Down selects an agent and Enter opens it. Left/Right
or Tab changes between Prompt, Output, Result and Events. Up/Down and PageUp/
PageDown scroll text; End follows the latest output. In Events, Up/Down selects
an event and Enter expands its complete record, including original event and
signal IDs. Esc returns to the overview; Esc again returns to epoch selection.
Press q to quit.

The screen refreshes every two seconds. New and retired agents remain visible,
and the selected agent stays selected when another lane is added. Output
supports Claude Code and Codex transcripts, provider diagnostics and correction
attempts. Result includes the worker report and verified ROOT review, including
retained retirement archives. ROOT's row aggregates recorded communications and
reviews; the viewer does not import the benchmark collector's separate ROOT
terminal log.

For explicit selection or a noninteractive snapshot:

```powershell
python -m orchestrator_harness.operator_launch view --runtime-root 'C:\path\to\workspace\.harness-runtime' --list-epochs
python -m orchestrator_harness.operator_launch view --runtime-root 'C:\path\to\workspace\.harness-runtime' --epoch <epoch-id>
python -m orchestrator_harness.operator_launch --json view --runtime-root 'C:\path\to\workspace\.harness-runtime' --epoch <epoch-id> --once
```

`--once` and redirected output default to the active epoch, or the newest stored
epoch when none is active. `--json` also produces a snapshot rather than opening
the interactive screen. `--color` restores terminal colors when the shell inherits
`NO_COLOR`. An explicit `--no-color` still wins, and redirected output has no ANSI
colors. `--ascii --no-color` gives plain terminal output.

## Replay

Press r in the agent overview to replay the selected epoch. To open replay
directly or list recording availability:

```powershell
python -m orchestrator_harness.operator_launch view --runtime-root 'C:\path\to\workspace\.harness-runtime' --replay --epoch <epoch-id> --speed 1.5 --color
python -m orchestrator_harness.operator_launch view --runtime-root 'C:\path\to\workspace\.harness-runtime' --list-replays
```

Without `--epoch`, interactive replay opens the epoch selector first. The REPLAY
banner shows speed, play/pause state, timeline position and recording warnings.
Space pauses/resumes, r restarts, [ and ] seek backward/forward ten seconds,
and + and - adjust speed within 0.25x to 40x. Default speed is 1.5x. Agent tabs,
scrolling and expandable events work during playback. Press l to return to the
selected epoch's current retained state, or Esc twice to choose another epoch.
Starting another run leaves your selected epoch and replay in place.

New managed runs record observations through a background thread in the native
monitor, about once per second. Successful mutating launcher commands also
capture snapshots, including bootstrap and retirement boundaries. Recording
works without an open viewer. Plain runs without a monitor have command-boundary
snapshots. Each epoch has its own journal at
`.harness-runtime/replay/<epoch-id>.sqlite3`; earlier recordings are retained.

Snapshots freeze visible prompts, output, results, event payloads/history and
ROOT reviews. Playback reads those snapshots without consulting later worker
files or executing saved commands. Seeking backward hides later output, events
and reviews. Timing represents sampled observations rather than exact provider
token or event timestamps. Original 512 KB preview limits apply to recordings.
Partial recordings are labeled; capture failures are retained in
`replay/recording-errors.log` and do not change native command outcomes. Completed
recordings are sealed against later workspace changes.

Replay startup reads the frame index and validates the first and last snapshots.
Other snapshots are decoded and validated immediately before display, keeping
startup fast for large recordings without showing unvalidated content.

Closed epochs without a journal support **Approximate timing** playback using
their retained artifacts: output is paced and events/reviews appear at the end.
Original interleaving cannot be recovered. An active epoch without a journal
cannot replay until recording starts.

Opening the viewer or replay only reads files and process status. It starts no
provider, monitor, setup, benchmark or service, and writes no runtime records.
Native capture writes replay sidecars independently. Existing Claude launch
preferences, hooks, receipts and token accounting are unchanged.

History requires retained epoch records and either replay journals or worker
worktrees/logs. A deleted run cannot be reconstructed by this viewer. The harness replaces its global
manager queue on a new epoch; older epochs can show retained worker notification
files or frozen recorded events but cannot recover unrecorded queue events that
were overwritten. Large transcripts
are displayed as a bounded 512 KB tail, with the full file path shown.
