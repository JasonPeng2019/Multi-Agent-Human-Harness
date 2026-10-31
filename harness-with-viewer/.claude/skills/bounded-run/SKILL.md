---
name: bounded-run
description: Run a finite command with visible heartbeats, an evidence-based deadline, captured output, exit-code propagation, and process-tree cleanup. Use only for long-running tests, builds, servers, watchers, or scripts explicitly selected in the repository's bounded-command policy; never wrap agent or subagent sessions.
---

# Run a bounded process

Use the platform launcher from the repository root:

- Windows: `.agent/run-bounded.ps1`
- Unix-like: `.agent/run-bounded.sh`

This launcher is only for finite non-agent commands. Agent and subagent sessions,
including `codex exec`, `claude -p`, and repository agent-launch wrappers, remain
unbounded even when their task contains finite checks. Use
`.agent/bounded-commands.txt` to opt individual tests, scripts, builds, or other
finite command fragments into this launcher; do not add agent-session fragments.

Before launch, choose:

- exact command and working directory;
- expected upper-bound seconds based on measured history, a protocol/resource
  bound, or a concrete accepted task estimate with stated headroom;
- cleanup allowance of 1–120 seconds, capped at the smaller of 120 seconds or
  25% of the expected runtime (with a 5-second allowance for short commands);
- optional explicit maximum lifetime, which must equal expected runtime plus
  cleanup allowance;
- heartbeat interval of 1–60 seconds;
- optional unique result path (otherwise the launcher creates one);
- a short timeout-basis explanation.

Do not invent a tiny deadline merely to satisfy the interface. Do not pad a retry
after timeout without new evidence.

Windows example:

```powershell
& .agent/run-bounded.ps1 -Command 'pytest -q' -WorkingDirectory . `
  -ExpectedUpperBoundSeconds 120 -CleanupAllowanceSeconds 20 `
  -HeartbeatIntervalSeconds 30 `
  -TimeoutBasis 'The relevant CI job normally finishes under 90 seconds.'
```

Unix example:

```bash
bash .agent/run-bounded.sh --command 'pytest -q' --working-directory . \
  --expected-upper-bound-seconds 120 --cleanup-allowance-seconds 20 \
  --heartbeat-interval-seconds 30 \
  --timeout-basis 'The relevant CI job normally finishes under 90 seconds.'
```

Interpret results exactly:

- `PASSED`: command exited zero.
- `FAILED`: command completed nonzero.
- `TIMED_OUT`: expected runtime expired; the launcher attempted and checked
  process-tree cleanup. This is not a product pass or product failure by itself.

Preserve stdout/stderr and terminal JSON until the result has been consumed. On a
timeout or launcher failure, inspect those files and change a relevant condition
before retrying. Never bypass the launcher silently for a command the hook routes
here.

## Optional strict script routing

Most repositories should use only the explicitly listed command guard. If direct
Python scripts, PowerShell files, shell scripts, Python `-m`/`-c`, or POSIX-shell
`-c` forms have repeatedly caused hangs or orphaned processes, read
[the optional script-routing policy](../../../../.agent/bounded-script-policy.md).
It provides Git-ignore-style exclusions and mechanically routes only those direct
script forms after a repository explicitly enables it. It is not enabled by
default, does not scan the repository, and must not become a reason to wrap quick
read-only commands or any agent/subagent session.
