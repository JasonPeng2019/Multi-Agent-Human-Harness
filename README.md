# Harness benchmark results

All model runs and graders are stopped following user cancellation. The latest historical supervised Terra/high Zstd batch is available in [imported results](bench-verification/imported-results/terra-zstd-final/README.md). Read [CURRENT_HARNESS.md](CURRENT_HARNESS.md) and [the final audit](bench-verification/FINALIZATION_AUDIT.json) for retained grades and cancelled trials. The reusable harness remains in `harness-single-run-version/`; benchmark support is under `bench-verification/`. Stopped Zstd tasks and candidate repos remain in [the verified archive](archive/zstd-cancelled-20261031/README.md).

This source checkout includes both harness versions, their skills and tests, the
viewer, and benchmark support code. Run workspaces and transcripts, archives,
downloaded reference distributions, and large generated datasets are ignored and
remain in the original local checkout. Historical links to those artifacts need
that local evidence; a fresh clone cannot reproduce full benchmark grading until
the omitted fixtures are supplied separately.

Clone with `git clone --recurse-submodules` to fetch the pinned harness vendors.
The existing Windows file-locking fix for both EverOS checkouts is preserved in
[vendor-patches/everos-windows-locking.patch](vendor-patches/everos-windows-locking.patch).
After initializing submodules, apply it to each checkout and install `portalocker`
in the Python environment used by the harness:

```powershell
git -C harness-single-run-version/vendor/everos apply ../../../vendor-patches/everos-windows-locking.patch
git -C harness-with-viewer/harness/vendor/everos apply ../../../../vendor-patches/everos-windows-locking.patch
python -m pip install portalocker
```
