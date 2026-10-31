---
name: workflow-1
description: Make a workflow topology from a plan. Gives each module in the plan its own independent implementer and independent deterministic test validator, adds a final test validator and a semantic reviewer that cover all the modules, and makes ROOT the only agent that can block progress, with validators and reviewers reporting only to ROOT. Use this to turn a plan into a workflow.
---

# Workflow

Make a workflow topology based on the plan. In the plan, each task is a module with its own file and one deliverable. The topology names every agent in the workflow, what each one works on, and how work and reports move between them.

## Agents

**ROOT** receives every report from the validators and the reviewer and decides whether each one is valid. It's the only agent that can block progress.

**Each module** gets two agents of its own:

- **Implementer:** builds the module's deliverable in the module's file.
- **Deterministic test validator:** tests the module and reports the results to ROOT. Deterministic means the tests give the same pass or fail result every time they run on the same code: nothing random, nothing time-dependent, and no judgment involved.

The implementer and the validator are independent: separate agents, each working only on its own module. The validator writes its tests from the plan, not from the implementer's code, so the tests check what the module is supposed to do.

**All the modules together** get two more agents:

- **Final test validator:** tests all the modules together against the plan's expectations, with deterministic tests, and reports the results to ROOT.
- **Semantic reviewer:** reads all the modules and finds issues in what the code actually does, such as logic that doesn't do what the plan requires. These are the problems tests can miss. It reports them to ROOT.

## Reports and progress

ROOT is the only agent that can block progress. Validators and reviewers can only report back to ROOT, and ROOT determines whether each criticism or objection is valid:

- **Valid:** ROOT blocks progress and sends the issue to the implementer of the module it affects. The fix goes back through that module's validator to ROOT.
- **Not valid:** ROOT dismisses it, and progress continues.

The final test validator and the semantic reviewer are launched in parallel to check the modules once ROOT has accepted all of them.

## Topology format

```markdown
## Workflow topology

**ROOT**
- Receives all reports and decides whether each criticism or objection is valid
- The only agent that can block progress

**Module: `<module file>`** (one block per module)
- Implementer: builds <the module's deliverable>
- Deterministic test validator: tests the deliverable against the plan and reports to ROOT

**All modules**
- Final test validator: tests all modules together against the expectations and reports to ROOT
- Semantic reviewer: reviews all modules for issues and reports to ROOT

**Flow**
1. Each module: implementer → deterministic test validator → ROOT
2. ROOT judges each report. Valid: ROOT blocks progress and sends the issue to the module's implementer, and the fix goes back through step 1. Not valid: dismissed.
3. Once ROOT has accepted every module: final test validator and semantic reviewer (launched in parallel) → ROOT
4. ROOT judges each report. Valid: ROOT blocks progress and sends the issue to the affected module's implementer, and the fix goes back through step 1. None valid: the workflow is done.
```

## Example

For the plan of a tool that checks which URLs in a text file are down, the module blocks are:

```markdown
**Module: `url_list.py`**
- Implementer: builds a function that returns the URLs in a file
- Deterministic test validator: tests that function against the plan and reports to ROOT

**Module: `checker.py`**
- Implementer: builds a function that returns whether a URL responds
- Deterministic test validator: tests that function against the plan and reports to ROOT

**Module: `main.py`**
- Implementer: builds a command that reads the file, checks each URL, and prints the results
- Deterministic test validator: tests that command against the plan and reports to ROOT
```

The ROOT, All modules, and Flow sections stay exactly as in the format.
