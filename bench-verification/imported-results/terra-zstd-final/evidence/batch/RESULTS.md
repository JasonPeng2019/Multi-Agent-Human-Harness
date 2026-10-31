# Two repaired workflow-1 trials — completed

Both trials used Terra 5.6 high/default for ROOT and every worker, unchanged workflow-1 prompts/skills, initially empty isolated memory, and the original five-hour absolute deadlines. Results are operator-assisted.

| Run | Final partial score | Public | Hidden | First integration matching final score | First-match revision | Total elapsed wall time | Operator resumes |
| --- | ---: | ---: | ---: | --- | --- | --- | ---: |
| w1-r01 | 58.1% (25/43) | 3/6 | 22/37 | 0h 18m 20.741s | `249a2c8652f9` | 4h 59m 49.741s | 3 |
| w1-r02 | 100.0% (43/43) | 6/6 | 37/37 | 3h 40m 36.590s | `1fd1f7ae87e5` | 4h 08m 03.590s | 2 |

Elapsed time starts at the initial collector/ROOT launch and includes every pause and continuation. Integration timestamps come from ROOT HEAD reflogs at one-second resolution, rather than worker commit dates. Native ROOT process creation clocks and their corresponding elapsed times are retained in the JSON report.

- w1-r01: first matching integration at **2026-10-15T12:44:16+00:00**; initial launch 2026-10-15T12:25:55.258878+00:00; final ROOT exit 2026-10-15T17:25:45+00:00; native ROOT created 2026-10-15T12:25:55.621970+00:00. First match from native ROOT creation: 0h 18m 20.378s.
- w1-r02: first matching integration at **2026-10-15T16:06:32+00:00**; initial launch 2026-10-15T12:25:55.409872+00:00; final ROOT exit 2026-10-15T16:33:59+00:00; native ROOT created 2026-10-15T12:25:55.731108+00:00. First match from native ROOT creation: 3h 40m 36.269s.

r01 remained incomplete. Independent module validation and both final checks failed. Its final benchmark score equals that of its first code integration, despite two later partial safety/empty-frame improvements. The intermediate partial source was not separately graded after the earliest match was already proven. ROOT overlapped the latest module and final checks before accepting the module. Its last continuation closed ten seconds before the original deadline because it could not fit another repair plus revalidation. Operator supervision was paused for part of the run; that delay is included in wall time.

r02 passed all 43 benchmark checks. Its final semantic review passed within decoder-source scope, while deterministic final validation retained FAIL for independently demonstrated fixed caller/API limitations: ambiguous zero-size error/empty returns and inadequate fallback allocation for valid high-expansion inputs without a declared content size. The benchmark score does not resolve those broader CLI limitations.

r02 first passed all six public cases at revision `efeef149b0be`, integrated at 14:07:30 UTC; that source scored 69.8% (30/43) on the full verifier. The review-driven repair `ad5b6ac55275` at 15:22:55 UTC scored 72.1% (31/43), and the later repair `1fd1f7ae87e5` at 16:06:32 UTC reached 100% (43/43). Public results stayed 6/6 throughout those repairs. Thus the later repair cycle produced measured hidden-test gains beyond the first public-suite pass.

Both ROOTs chose one whole-decoder module. The experiment therefore records their actual plans and partial-integration behavior, rather than implying that either performed a multi-module decomposition. Early finishes and operator resumes remain part of these results.

Known duplicate-dispatch, cleanup, observer-write and evaluation-image fixes were carried into the copies before launch. A Windows long-branch-path bootstrap failure and recovered working-directory mistakes occurred; they remain in the run evidence. No claim is made that all possible harness bugs are eliminated.

| Run | ROOT tokens | Worker tokens | Total input + output | Cached input (included in total) | Output (including reasoning) |
| --- | ---: | ---: | ---: | ---: | ---: |
| w1-r01 | 27,651,080 | 46,195,912 | 73,846,992 | 71,418,880 | 284,966 |
| w1-r02 | 64,312,987 | 43,375,182 | 107,688,169 | 104,673,792 | 432,022 |

Both strict ledgers reconcile with no missing/in-flight usage or accounting errors. These are recorded model-token counters, not invoices; cached input is already included in input totals.

Scoring used the pinned unchanged upstream verifier and corrected image calibrated at 43/43 by the upstream oracle. Scores were not rescaled. Every earlier distinct integrated source needed to prove the first match was graded, including non-building revisions that receive the official missing-decoder score. Identical full source trees reused matching evaluation evidence. Later integrations remain timestamped even when no further grade was needed.

Evidence: [score and timing JSON](FIRST_FINAL_SCORE_RESULTS.json), [all integrations](INTEGRATION_TIMELINE.md), [completion audit](COMPLETION_AUDIT.json), [archive verification](INTEGRATION_ARCHIVE_CHECK_FINAL.json), [stop/process proof](STOPPED_RUNS.json), [usage totals](FINAL_USAGE_SUMMARY.json). Per-arm workflow audits, immutable usage archives, checkpoint source snapshots and build/verifier logs remain under each arm’s `operator/` directory.
