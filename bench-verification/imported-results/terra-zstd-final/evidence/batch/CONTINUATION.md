# Operator-assisted completion

Do not launch or resume either benchmark without authorization. These setups
declare operator assistance before launch and retain the existing continuation
mechanism. They do not add a deterministic workflow scheduler or completion gate.

After every reported finish, preserve that checkpoint and audit the arm's
`PLAN.md`, `WORKFLOW.md`, installed skills, committed revisions, actual worker
identities, checks, and reports. Check that every planned module has its required
work and that ROOT used stay-current after each worker return. For workflow-1,
check each module's independent deterministic validation. Workflow-2 omits that
intervening stage. Both require the final independent semantic reviewer and
deterministic test validator, launched in parallel, on the integrated revision.
There is no extra final implementer. Check actual coverage and behavior evidence;
a PASS label, source presence, or clean shutdown alone does not prove completion.
Changes after final checks require fresh final checks on the resulting revision.

Compare useful committed worker contributions with ROOT's integrated checkpoint.
A FAIL/BLOCKED module can still contain a buildable, verified improvement that
should be integrated without known regressions. Keep its remaining gaps and
required validation outstanding. Check that repair handoffs retain prior
findings and that validation covers relevant criteria and compatibility, with
revision-matched commands/results rather than a bare PASS or passing build.
The total collector allowance is five hours (300 minutes), including pauses.

If steps are missing and time remains, write a short continuation prompt stating
the missing steps and evidence. Leave task diagnosis, implementation, and
delegation to ROOT. Do not supply hidden test results or solution hints. From
the applicable arm directory, use its existing continuation entry point:

```powershell
.\Launch.ps1 -ResumePromptFile <absolute-continuation-prompt> -PrepareOnly
.\Launch.ps1 -ResumePromptFile <absolute-continuation-prompt>
```

Preparation and continuation are distinct invocations with preserved receipts;
never loop these commands after failure. They resume the same ROOT session and
run identity, keep the original absolute deadline including pauses, preserve
attempt limits and isolated memory, and account for every ROOT segment and
worker. A proven clean CLOSED runtime may reopen its services once through
native preparation before continuation. Failed launches, live workers, expired
deadlines, and unsealed usage must be diagnosed rather than bypassed.

Audit again after each return. Stop at workflow completion, deadline,
cancellation, or a documented genuine blocker. Score only after all
continuations have ended, and label any results operator-assisted.

The underlying continuation mechanism's earlier live proof remains at
`../zstd-setup-repair-20261012/health/continuation-v3/runtime/HEALTH_GATE.json`.
It is historical verification of that mechanism, not a launch of either arm.
