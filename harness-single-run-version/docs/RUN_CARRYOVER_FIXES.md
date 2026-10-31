# Prepared benchmark source carry-over

The runtime fixes reviewed at memory/working-v1 commit
`bccf627d237e4f66596bc346bf63891e5192ad08` are carried into this prepared source.

- ROOT launch and resume validate the same setup receipt, hook/config hashes,
  sandbox proof and public-service identity. CLOSED resumes require the original
  service stopped with cleanup proven; validation never repeats setup.
- Windows sandbox health is required even without a local policy. A setup error
  is recorded and blocks later lanes even if the provider exits before polling.
- Public checks use the general v2 service with this run's pinned ZSTD adapter.
  Resumed or historical routes cannot overwrite a different invocation's result.
- Completed backend exit 75 is preserved in feedback but maps to client exit 2.
  Client exit 75 exclusively means the original request is still pending. Native
  crash codes and compiler/test diagnostics are also retained.
- Adapter imports register verified modules, support dataclasses/postponed
  annotations, serialize concurrent imports and remove failed partial modules.

The active local policy selects the same task inputs, immutable public files,
Makefile/harness, build/public commands, timeout and parallelism. The adapter,
benchmark worker sandbox profile, ROOT prompt, run-only PowerShell launcher,
memory backend, vendor sources and original execution evidence are preserved.
The collector retains the benchmark's SWE_TOKEN environment names.

Use fresh workspaces and ROOT setup receipts for future runs. Existing v1 source
and policy backups are in the outer carry-over evidence directory; no old run
receipt has been rewritten to claim a newer service was tested. Sandbox setup
and provider launch never retry automatically.

Task-ID/overview and harness-owned final task-completion validation remain
deferred. The existing Stop hook still requires runtime CLOSED for cleanup;
CLOSED is not a task-success receipt. Prompt requirements for incremental
integration, fresh repairs and independent validation remain in force.

Source, regression and deterministic integration evidence:
`root_runs/harness-run-carryover-20261010/runtime/` in the outer repository.

Verification on 2026-10-10: 132 affected runtime regressions and four ZSTD
adapter checks pass. The existing Windows health receipt also passes a read-only
hash/identity check; no Codex executable or sandbox setup was invoked. One fresh
Docker integration attempt stopped at adapter preflight because Docker Desktop's
Linux engine was unavailable. No service or container launched, and that attempt
was not retried. A new live v2 Docker proof remains unverified; the earlier live
proofs remain historical evidence. Future execution requires Docker to be running
with the pinned image, plus the normal fresh workspace/setup receipt.
