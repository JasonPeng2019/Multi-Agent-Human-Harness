# Restore worker build/test feedback

The benchmark explicitly provides Make, GCC and six public cases for iteration.
The run's worker profile protects the entire harness directory, but the public
Docker helper is inside that directory. Workers fail before entering Docker.
Windows has no substitute C toolchain. This is a run integration defect.

Options considered:

- Make the helper readable and give workers Docker access. A readable helper
  does not constrain other uses of the Docker daemon. Moving the file alone is
  insufficient.
- Ask ROOT to run each check through native escalation. This preserves isolation
  but depends on ROOT correctly servicing every request during implementation.
- Provide a deterministic, restricted public-test service. Workers invoke a
  lane-local client; the operator-owned service runs only the selected lane's
  committed task files in the pinned offline image. This is the chosen route.

Implementation plan:

1. Start and verify the service during pre-launch preparation. Keep its state,
   native process identity, registrations and authoritative results under the
   existing denied operator-only runtime directory.
2. Bootstrap a standalone client and lane/run-bound route into each applicable
   managed lane. Preserve the existing worker filesystem restrictions. Use
   request/result files in that lane so no host-network permission change is
   needed. These are task-tool calls, not a second manager queue or agent runner.
3. Validate requests against operator registrations and native lane identity.
   Snapshot the requested full Git revision using Git archive, copying only
   task-visible inputs and committed scratch files. Reject links, foreign lanes,
   stale invocations and changes to fixed public inputs. Do not mount host paths.
4. Run public compilation, public tests or a focused container command with a
   bounded timeout. Return command, revision, stdout, stderr and exit status.
   Save an authoritative operator result and a correlated worker copy. A failed
   check is feedback, not worker completion or a new provider invocation.
5. Stop service work and prove its exact process is gone during native shutdown.
   Teach ROOT and workers the client workflow. No ROOT model action is needed
   between a worker's request and its returned feedback.
6. Test revision accuracy, boundaries, errors, duplicate delivery, timeouts,
   startup and cleanup. Then use a fresh diagnostic native workspace to prove a
   sandboxed worker can obtain a compile failure, repair and retest, and receive
   public-case feedback without broadening harness or Docker access.

All implementation belongs in this prepared run source and fresh diagnostics.
Frozen reusable directories and completed benchmark snapshots remain untouched.

Verification status (2026-10-09): implemented and verified. The latest focused
regression suite passed 85 checks. Five real service/client/Docker checks first
passed without the sandbox; a subsequent single native Codex sandbox invocation
then passed the same feedback loop using the production bootstrap's exact
`worker-isolated` profile, running as `CodexSandboxOffline`:

- Compiler failure returned real GCC diagnostics and exit 2.
- The isolated process repaired and committed code, then obtained build exit 0
  on the new revision.
- A focused GCC compile/run test passed.
- Public-test feedback returned exit 1 and all six expected failures from the
  deliberately incomplete diagnostic decoder.
- Both output streams and exact exit 7 were preserved.

Each result matched the lane/run/request/revision. Harness, operator-only and
Codex-home reads remained denied; ROOT Git writes outside explicit grants
remained denied. No ROOT model serviced requests. No model agents were launched.
All containers and the exact sandbox/service processes were cleaned up.
Evidence: `root_runs/zstd-sandbox-direct-feedback-proof-20261009/runtime/PROOF.json`
and `runtime/HEALTH_GATE.json`. This verifies tool access and feedback under the
real sandbox; it does not measure model instruction following or decoder quality.

The original diagnostic and canceled administrator attempt remain historical.
A separate repair authorized by a new user request succeeded with one
administrator request and one explicit provisioning invocation. The sandbox
binary directory's protected ACL lacked privileged WRITE_DAC; its owner granted
that narrowly scoped permission before provisioning. Use a DACL-only API and
preserve the original descriptor. See `WINDOWS_SANDBOX_REPAIR.md` and
`root_runs/zstd-sandbox-repair-20261009-explicit-2/runtime/RESULT.json`.

The genuine `local-config/windows-sandbox-health.json` receipt records the
successful probe, native executable/home/cache, hashes of executable/marker,
and retained evidence path/hash. The read-only preflight now passes for that
exact environment. Different run caches or CLI/home/marker identities require
their own one-attempt verification; never fabricate or blindly copy receipts.
No automatic launcher retry, sandbox re-provisioning, fallback or mode switch
is allowed after a failed health gate. Ordinary permission refresh for a new
workspace succeeded without elevation; it is distinct from repeating a failed
setup. Future benchmark ROOTs still need their own native pre-launch setup,
healthy public-check service and valid sandbox receipt before model launch.
