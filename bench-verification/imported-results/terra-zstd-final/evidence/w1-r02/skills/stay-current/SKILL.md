---
name: stay-current
description: Call this after every subagent finishes or returns. ROOT assesses the progress and decides whether the plan needs updating. If it does, ROOT makes the necessary plan changes, consistent with the $plan skill, and then updates the workflow on the new plan, consistent with the $workflow skill.
---

# Stay current

ROOT uses this after every subagent finishes or returns, to keep the plan and the workflow current with the progress.

## 1. Assess the progress

Look at what the subagent returned and where the work stands, and compare it with the current plan. Then decide whether the plan needs to change. It does when the progress shows the plan no longer fits the work, for example when:

- a requirement or expectation turns out to be wrong
- a task turns out bigger than planned and needs splitting
- the minimal working product needs something the plan missed

If the plan still fits the work, leave the plan and the workflow as they are.

## 2. Update the plan

If the plan needs to change, make the necessary changes, consistent with the $plan skill, so the updated plan follows the same rules and format. Change only what the progress calls for.

## 3. Update the workflow

Then update the workflow on the new plan, consistent with the $workflow skill. Change the parts of the workflow that the plan changes affect, so its modules and agents match the new plan.
