# ZSTD build/test adapter

The prepared run source now uses the reviewed v2 service. Its active
`local-config/public-check-policy.json` matches `public-check-policy.v2.json`
here and binds `zstd_check_adapter.py` by absolute path and SHA-256. Task image,
commands, public input selections and immutable fixtures remain run-specific.

For a fresh run copy, update the adapter path and hash for the final location,
keep it outside the worker-editable ROOT workspace, and prepare a fresh ROOT
workspace and setup receipt. Old v1 execution evidence and setup receipts are
historical; do not rewrite them or adopt an existing run's runtime. Previous
prepared source/config bytes are preserved in the carry-over evidence directory.

Adapter preflight checks an already-installed exact pinned offline image. It
never pulls an image, starts Docker, initializes a sandbox or retries a launcher.
Workers use their staged `.agent-workspace/public-check.py` client for direct
feedback; ROOT continues to test integrated code and supply validator evidence.

The run-only ROOT prompt, PowerShell launcher and legacy ROOT-side
`tools/public_task_check.py` remain. Vendored evaluation sources/fixtures and
the `benchmark-support/` archive are unchanged. Task-completion enforcement is
still deferred; runtime CLOSED proves cleanup.
