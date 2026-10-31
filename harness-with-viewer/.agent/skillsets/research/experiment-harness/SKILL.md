---
name: experiment-harness
description: Structure research experiments so results are comparable, reproducible, and honestly reported. Use for experiments, training, evaluation, sweeps, ablations, or metrics.
---

# Experiment harness

Define the hypothesis, baseline, success criterion, dataset/split, metric, and
failure condition before running an experiment. Keep a tracked base config and
save an immutable resolved config with each run.

For every result, record the source revision, seed, data version or hash,
environment/hardware facts that affect it, command, metrics, and artifact path.
Run a cheap smoke path before an expensive run. Do not overwrite prior run
artifacts or describe an unlogged result as established.

Compare a claimed improvement against a baseline under identical conditions.
Report variance, limitations, negative results, and missing evidence. Route a
claim through `research-claim-review` before presenting it as supported.
