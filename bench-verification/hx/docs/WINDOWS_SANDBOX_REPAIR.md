# Windows sandbox repair and launch gate

The October 9 failure was `helper_sandbox_lock_failed` while applying a DACL
to `C:/Users/Jason/.codex/.sandbox-bin`: Windows error 5, Access denied. That
directory was owned by Jason and protected from inheritance. Administrators
and SYSTEM had Modify but lacked WRITE_DAC; the approved administrator shell
ran as another account. Failed provisioning left the setup marker empty,
allowing subsequent callers to request setup again. Shared logs do not prove
which run caused every popup.

The successful operator repair is retained at
`root_runs/zstd-sandbox-repair-20261009-explicit-2/runtime/`:

1. Preserve the exact directory owner and SDDL. Validate the three explicitly
   named sandbox directories are ordinary directories inside the intended
   Codex home. Do not recursively change unrelated files or workspaces.
2. As the binary directory owner, grant only ChangePermissions to SYSTEM and
   Administrators. Use a DirectorySecurity descriptor containing only its
   Access section with Directory.SetAccessControl. Set-Acl attempted a broader
   descriptor write and required SeSecurityPrivilege on this machine.
3. Make one administrator request for the reviewed bounded script. From that
   already elevated shell, invoke the installed CLI 0.162.0 exactly once:

   ```text
   codex sandbox setup --elevated --user Jason --codex-home C:/Users/Jason/.codex
   ```

   This explicit ProvisionOnly operation provisions accounts and shared
   sandbox directories. It does not replace the worker's workspace restrictions
   or ask for another elevation. The script snapshots ACLs, records the child
   PID/creation identity, has a 90-second bound and refuses repeat execution.
4. Require native exit 0 and a real, nonempty v5 setup marker. Never synthesize
   the marker or treat an approved popup as evidence of successful setup.
5. Run one isolated probe using the generated worker profile and exact native
   executable/home/cache. Require denied-path checks, successful sandboxed
   execution, real public-tool feedback and proven process/container cleanup.
   Only then issue the hash-bound operator health receipt.

The repair succeeded with one administrator request and one setup invocation.
The subsequent native sandbox probe passed without another administrator
request. It ran as CodexSandboxOffline and obtained compiler failure, committed
repair, successful rebuild, focused-test success, public-case failure feedback,
and both output streams with exact exit status. Protected harness, operator and
Codex-home files remained denied. Evidence:
`root_runs/zstd-sandbox-direct-feedback-proof-20261009/runtime/HEALTH_GATE.json`.

The prepared source now blocks ROOT setup and worker spawn when its marker,
CLI/home/cache, retained proof or run-wide sandbox state fails verification.
Automatic worker RESULT-correction launches are removed. A provider startup
setup failure invalidates the run and stops only that exact owned process
boundary. Each launcher gets one attempt: preserve, diagnose and fix failures
before any separate launch. Never request setup repeatedly, switch sandbox
implementations or bypass the gate.

Receipts are specific to their tested environment. New run copies using a
different cache must verify it; copying a receipt does not establish health.
Do not use speculative sandbox help commands: syntax differs by CLI version
and an unrecognized command can initiate setup. Frozen harness directories
must remain untouched. Unrelated agents and processes are outside this repair.
