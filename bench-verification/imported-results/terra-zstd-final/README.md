# Imported final Terra Zstd batch

Imported saved results from `zstd-w1-fixed-two-20261015`, the latest historical supervised Terra/high workflow-1 batch found in the original benchmark repository. Both arms are included. Original sources remain unchanged; no model or grader was launched.

| Run | Saved partial | Public | Hidden | Output tokens | Recorded workflow outcome |
| --- | ---: | ---: | ---: | ---: | --- |
| w1-r01 | 58.1% (25/43) | 3/6 | 22/37 | 284,966 | deadline_expired |
| w1-r02 | 100% (43/43) | 6/6 | 37/37 | 432,022 | genuine_blocker |

Mean of the saved rounded partial scores: **79.05%**. Best: **100%**. Both used GPT-5.6-terra, high ROOT/worker effort, a five-hour absolute allowance, and operator-assisted same-session continuations.

The workflow audits retain failed checks: r01 exhausted its deadline; r02's final deterministic validator retained fixed caller/API limitations despite its 43/43 benchmark score. These results do not assert full workflow success. The earlier three selected 100% scores span multiple batches and remain a separate script mode.

The authenticated official SWE-Marathon v1.1 run logs and verifier metrics confirm eight Codex/Terra high Zstd trials: **47.4% average, 58.1% best**. This is not the model's average across all tasks.

From the repository root:

```powershell
.\harness-single-run-version\.venv\Scripts\python.exe .\bench-verification\tools\show_terra_zstd_scores.py --final-batch
.\harness-single-run-version\.venv\Scripts\python.exe .\bench-verification\tools\show_terra_zstd_scores.py --swe-only
.\harness-single-run-version\.venv\Scripts\python.exe .\bench-verification\tools\score_run.py .\bench-verification\imported-results\terra-zstd-final\w1-r02
```

The script defaults to the complete imported final batch; `--final-batch` selects it explicitly. `--selected-successes` shows the earlier three selected 100% runs. `--swe-only` shows the official reference alone. All modes display scores only, including in `--json` output. Imported evidence hashes are verified before display.

[RESULTS.json](RESULTS.json) contains the summary and source identities. [IMPORT_MANIFEST.json](IMPORT_MANIFEST.json) records SHA-256 hashes for copied evidence. `evidence/` contains byte-identical original grades, workflow audits, prompts/skills, usage totals, calibration and batch completion records. Per-run normalized grades clearly identify themselves as imported historical evaluations.
