---
name: module-planning
description: Break an assigned task into bounded implementation modules for ROOT, or decompose an oversized module when ROOT requests it.
---

# Module planning

Inspect the assigned task, current source, and visible requirements. Produce
one plan in MODULES.md; do not implement.

Each package must make substantial progress on one feature or aspect and contain:

- Objective: one specific outcome.
- Inputs: starting revision, relevant requirements, dependency outputs, and required interfaces.
- Deliverable: one concrete committed result.
- Acceptance criteria: observable checks for this module's completion and compatibility with completed modules.

Order modules by dependency and identify shared interfaces. Keep each module
manageable within its worker's execution budget. Specify required behavior and
interfaces; leave the implementation approach to the module worker.

Module acceptance uses its own criteria; full-task completion is a final gate.
Subdivide a module only when ROOT requests it after a worker reports several
independently testable deliverables or work that cannot reasonably fit its budget.
Reference MODULES.md in the native RESULT.json.
