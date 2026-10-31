# Display a run's hidden score

From the repository root:

```powershell
.\harness-single-run-version\.venv\Scripts\python.exe .\bench-verification\tools\score_run.py .\bench-verification\root_runs\b1
```

Replace `b1` with another run folder such as `b0`. Pass the run folder, not its `w` workspace. Add `--json` for the saved grading record. The script displays the saved hidden partial score, binary reward, candidate revision, and any scoring variation. It exits with code 2 while no verified score is available.

Latest scope: only `b1` is continuing grading, with all four Docker CPUs and an extended grading timeout authorized by the user. Its completed 129 tests (92 passed, 37 failed) are reused from the saved transcript bound to the identical candidate archive, pinned image, and official verifier hash. Only the unfinished suites are executed again. The original timed-out attempt is preserved under `b1/hidden-evaluation-attempt-0001-timeout/`. The official verifier, test assertions, golden data, and count-based score formula remain unchanged; the result is explicitly labeled continued grading with extra time, rather than official time-limit parity. The continuation also validates that every workspace target is covered exactly once. Its operator-only command is `tools/continue_biofabric_grade.py`; it is a one-shot operation and will refuse to overwrite existing attempt evidence.

The native `b0` result is complete: 308/418 tests, **73.684%** partial. The user cancelled further grading of `b2`; its interrupted attempt remains preserved and unscored. Excel `e1` is unfinished and unscored. No further benchmark model continuations are authorized.

The evaluation command, used after the run and all workers have stopped, is:

```powershell
.\harness-single-run-version\.venv\Scripts\python.exe .\bench-verification\tools\grade_run.py .\bench-verification\root_runs\b1
```

Evaluation requires a sealed collector, a process-stop audit, a clean committed candidate, and CLOSED harness runtime for harness trials. It preserves its evaluation directory instead of overwriting an earlier evaluation. Hidden test results must not be supplied to active model sessions.

BioFabric's grading engine passed the official oracle: 450/450 tests, partial score 100%, binary reward 1. Evidence: `biofabric/CALIBRATION.json`.

Excel `e1` was stopped unfinished after the usage limit and the user's instruction to grade only completed trials. It is unscored; no further model continuation or visual-grader calls are authorized for these trials.

Excel's unchanged official oracle failed two performance budgets on this host. The separately authorized local timing/Claude CLI grading variant passed all 18 correctness gates (136/136 tests), but its visual calibration was interrupted and failed. It is not fully calibrated and is not official benchmark parity. Original and variant evidence remain under `excel/CALIBRATION.json` and `excel/operator-only/cli-oracle-20261031T120716Z/hidden-evaluation/`. A correctness component check is not the blended hidden partial score.
