from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

HEADINGS = [
    "## 0. Plan contract and status",
    "## 1. Inputs, authority, and directive hierarchy",
    "## 2. Goal, exclusions, and acceptance outcomes",
    "## 3. Requirement coverage map",
    "## 4. Runtime and repository truth",
    "## 5. Deliverable, dependency, risk, and cost model",
    "## 6. Step and M-module library index",
    "## 7. Roles and role-agent mapping boundary",
    "## 8. Composed execution graph and critical path",
    "## 9. Global workflow policies and exceptions",
    "## 10. Lane, resource, result, and handoff manifest",
    "__AGGREGATED_MODULE_INSTANCES_FOR_VALIDATION__",
    "## 12. External and practical validation",
    "## 13. Integration, safeguard, promotion, rollback, and retirement",
    "## 14. Tolerances, unresolved decisions, and out-of-scope ledger",
    "## 15. Rule application matrix",
    "## 16. Structural validation result",
]

AUDIT_META_TABLE = ("Audit field", "Value")
AUDIT_GROUP_TABLE = (
    "Review group", "Reviewer", "Plan revision", "Review evidence",
    "Findings and dispositions", "Verdict",
)
AUDIT_GROUPS = (
    "SCOPE_AUTHORITY", "TOPOLOGY_SIMPLICITY", "VERIFICATION", "EXECUTION_RESOURCES",
)
ACCEPTANCE_ASSESSMENT_FIELDS = (
    "Necessity assessment", "Multiplicity assessment", "Proportionality assessment",
)
AUDIT_SCOPE_TABLE = (
    "Step", "Evidence scope", "Requirement and oracle", "Dimension rationale",
    "Cost basis", *ACCEPTANCE_ASSESSMENT_FIELDS,
    "Review findings", "Writer disposition", "Final status",
)
AUDIT_FIELDS = (
    "Plan writer", "Review panel", "Plan revision", "Review evidence",
    "Requested outcome and non-goals", "Scope and authority review",
    "Topology and simplicity review", "Verification and budget review",
    "Execution authorization boundary", "Plan review verdict",
    "ROOT acceptance", "Audit status",
)

POLICY_HEADINGS = [
    "### P01 Ownership and decisions",
    "### P02 Context and thread lifetime",
    "### P03 Failure-case selection",
    "### P04 Check selection and green credit",
    "### P05 Review classes and invalidation",
    "### P06 Parallel checks and results",
    "### P07 Finding pooling and material repair",
    "### P08 Test-only correction",
    "### P09 Administrative recovery",
    "### P10 Semantic acceptance",
    "### P11 Full-safeguard scope",
    "### P12 External authorization and rehearsal",
    "### P13 Gate/loop sizing, health, and topology reassessment",
    "### P14 Exception classes",
    "### P15 Stop and live-harm containment",
]

INSTANCE_FIELDS = [
    "Purpose",
    "Coverage",
    "Selection basis",
    "Owner and roles",
    "Preconditions",
    "Inputs",
    "Local instructions",
    "Outputs and results",
    "Concurrency and isolation",
    "Resources and side effects",
    "Checks and acceptance",
    "Failure and exception routes",
    "Prior results and change effects",
    "Repeat, join, and terminal behavior",
    "Cost and critical-path effect",
]

TASK_FIELDS = [
    "schema/card_id/module_instance_id/deliverable_id/stage_cohort_id/gate_id/loop_id",
    "workflow_role",
    "objective",
    "why_now",
    "starting_state",
    "dependencies_and_predecessor_outputs",
    "working_scope",
    "required_behavior",
    "initial_entrypoints",
    "failure_case_brief",
    "ordered_actions",
    "allowed_tools_capabilities_resources",
    "forbidden_actions_and_boundaries",
    "verification",
    "deliverables_and_result_paths",
    "acceptance_criteria_and_tolerances",
    "completion_review_owner_and_handoff",
    "failure_classification_and_routes",
    "thread_resume_and_terminal_rule",
    "cited_global_policy_ids_and_exception_ids",
]

UNDISPATCHABLE_BARE_TASK_VALUES = {"", "N/A", "TBD", "TODO", "UNKNOWN"}
UNDISPATCHABLE_EXECUTABLE_VALUES = UNDISPATCHABLE_BARE_TASK_VALUES | {
    "NONE", "DISABLED", "SKIPPED", "OMITTED", "INELIGIBLE", "UNAVAILABLE",
    "NOT NEEDED", "NOT REQUIRED", "NO ACTION",
}

MODULE_IDS = [f"M{number:02d}" for number in range(1, 11)]
MODULE_ACTION_COUNTS = {
    "M01": 7,
    "M02": 8,
    "M03": 7,
    "M04": 8,
    "M05": 10,
    "M06": 8,
    "M07": 7,
    "M08": 6,
    "M09": 9,
    "M10": 5,
}
MODULE_ACTIONS = {
    module_id: [f"{module_id}-A{number}" for number in range(1, count + 1)]
    for module_id, count in MODULE_ACTION_COUNTS.items()
}
RULE_IDS = [f"R{number}" for number in range(1, 31)] + [f"S{number}" for number in range(1, 18)]
CHECK_IDS = [f"V{number:02d}" for number in range(1, 31)]
ALLOWED_CAPABILITY_STATES = {
    "RUNTIME_ENFORCED",
    "ORCHESTRATOR_ENFORCED",
    "TARGET_TOOL_INVOKED",
    "UNAVAILABLE",
}
ALLOWED_MODULE_DECISIONS = {"SELECTED", "OMITTED"}
ALLOWED_GATE_CLASSES = {"PRODUCT", "OPERATION_BOUNDARY"}
PLAN_CONTRACT_FIELDS = [
    "Plan ID",
    "Plan version",
    "Status",
    "Decision owner",
    "Orchestration topology",
    "Verification protocol",
    "Operative document boundary",
    "Change procedure",
    "Definition of valid",
]
PACKAGE_DEPENDENCY_TABLE = (
    "Dependency",
    "Authoritative path",
    "Owns",
    "Referenced by",
    "Compatible edit boundary",
)
PACKAGE_DEPENDENCIES = ["Global rules", "Gated steps", "M-module library", "Agent mapping", "Validation"]
ROLE_TABLE = (
    "Workflow role",
    "Authority class",
    "Reports to",
    "Directs",
    "Responsibilities",
    "Pool capacity",
    "Context class",
    "Write authority",
    "Resources",
    "Activation",
    "Lifetime",
)

REQUIRED_TABLES: dict[str, list[tuple[str, ...]]] = {
    HEADINGS[0]: [("Field", "Value"), PACKAGE_DEPENDENCY_TABLE],
    HEADINGS[1]: [
        (
            "Source",
            "Authority",
            "Path/reference",
            "Supplies",
            "Conflict rule",
        ),
        ("Layer", "Authority", "May define", "Must not override"),
    ],
    HEADINGS[2]: [
        (
            "Outcome ID",
            "Required behavior",
            "Acceptance method",
            "Decision owner",
            "Status",
        ),
        (
            "Boundary ID",
            "Type",
            "Included/excluded/authorization condition",
            "Reason",
            "Owner",
        ),
    ],
    HEADINGS[3]: [
        (
            "Requirement ID",
            "Source",
            "Deliverable ID",
            "Implementation owner",
            "Verification",
            "Acceptance owner",
            "Status",
        )
    ],
    HEADINGS[4]: [
        (
            "Capability/action",
            "State",
            "Source of truth",
            "Invocation owner",
            "Preconditions",
            "How confirmed",
            "Fallback",
        )
    ],
    HEADINGS[5]: [
        (
            "Deliverable ID",
            "Behavioral output",
            "Requirement IDs",
            "Dependencies",
            "Shared seams",
            "Release unit",
        ),
        (
            "Deliverable ID",
            "Realistic failure",
            "Impact",
            "Coupling",
            "Expected range",
            "Expensive operations",
            "Cheapest adequate topology",
            "Why",
        ),
    ],
    HEADINGS[6]: [
        (
            "Step ID",
            "Step file",
            "Public input",
            "Public output",
            "Gate/decision ID",
            "Acceptance owner",
        ),
        ("Module type", "Authoritative module file"),
    ],
    HEADINGS[7]: [
        ROLE_TABLE,
        ("Resolution rule", "Unknown-role behavior", "Mapping-update behavior"),
    ],
    HEADINGS[8]: [
        (
            "Edge ID",
            "From step/output",
            "To step/input",
            "Condition",
            "Serial/parallel",
            "Join ID",
            "Failure branch",
        ),
        (
            "Parallel group",
            "Shared input",
            "Member step IDs",
            "Writable-root isolation",
            "Launch rule",
            "Join ID",
            "Serial exception",
        ),
        (
            "Path ID",
            "Ordered step/edge IDs",
            "Expected range",
            "Overlap",
            "Expensive operations",
            "Why critical",
        ),
        (
            "Gate/loop ID",
            "Owning step",
            "Step file",
            "Gate class",
            "Public outcome/operation",
            "Default-forward edge",
            "Failure/return reference",
        ),
    ],
    HEADINGS[10]: [
        (
            "Lane ID",
            "Module instance",
            "Role",
            "Activation",
            "Mutable root",
            "Consumer",
            "Completion condition",
            "Failure route",
        ),
        (
            "Claim/lock ID",
            "Resource",
            "Owner",
            "Activation",
            "Mutable root",
            "Consumer",
            "Completion condition",
            "Failure route",
        ),
        (
            "Check",
            "Proves",
            "Dependencies",
            "Result owner",
            "Reuse condition",
            "Rerun route",
            "Result path if needed",
            "Failure route",
        ),
        (
            "Result/handoff ID",
            "Producer",
            "Consumer",
            "Path if durable",
            "Correlation needed",
            "Publication rule",
            "Completion condition",
            "Failure route",
        ),
        (
            "Source allocation ID",
            "Mode",
            "Source/worktree",
            "Writer",
            "Mutable root",
            "Consumer",
            "Completion condition",
            "Failure route",
        ),
        (
            "Retirement ID",
            "Target",
            "Owner",
            "Activation",
            "What must be retained",
            "Completion condition",
            "Recovery visibility",
            "Failure route",
        ),
    ],
    HEADINGS[12]: [
        (
            "Decision ID",
            "Module type",
            "Decision",
            "Authority/resource",
            "Synthetic proof",
            "Real proof",
            "Owner",
            "Failure route",
        )
    ],
    HEADINGS[13]: [
        (
            "Decision ID",
            "Module type",
            "Decision",
            "Accepted input",
            "Action/order",
            "Checks",
            "Promotion/rollback/retirement",
            "Owner",
        )
    ],
    HEADINGS[14]: [
        (
            "Item ID",
            "Type",
            "Exact condition",
            "Consequence",
            "Owner",
            "Resolution boundary",
        )
    ],
    HEADINGS[15]: [("Rule ID", "Plan location", "Concrete applied behavior")],
    HEADINGS[16]: [("Check ID", "Result", "Basis"), AUDIT_META_TABLE, AUDIT_GROUP_TABLE, AUDIT_SCOPE_TABLE],
}

POLICY_TABLE = (
    "Owner",
    "Trigger",
    "Required action",
    "Exit",
    "Result/record if needed",
    "Module IDs",
)
EXCEPTION_TABLE = (
    "Exception ID",
    "Affected policy",
    "Exact trigger",
    "Decision owner",
    "Allowed alternate action",
    "Required confirmation",
    "Preserved results",
    "Invalidated results",
    "Scope",
    "Expiry",
)
STEP_HEADINGS = [
    "## Step contract",
    "## Activation, inputs, and protected boundaries",
    "## Normal and FAST_LANE_V2 entry flows",
    "## Ordered M-module composition",
    "## Public outputs and successors",
    "## Gate, completion, and return boundary",
    "## Failure, continuation, and preserved results",
    "## Concurrency, isolation, resources, and lifecycle",
    "## Cost and critical-path effect",
]
STEP_ENTRY_TABLE = (
    "Entry flow",
    "Status and activation",
    "Consumes",
    "Ordered distinct MI-* path",
    "Produces and exit",
    "Destination or continuation",
    "Checkpoint and invalidation rule",
    "Concrete saved work",
    "Failure/fallback route",
)
STEP_ENTRY_NAMES = ["NORMAL", "FAST_LANE_V2_SERIES_1", "FAST_LANE_V2_SERIES_2"]
STEP_ENTRY_PREFIXES = {
    "NORMAL": "MI-NORMAL-",
    "FAST_LANE_V2_SERIES_1": "MI-FL2-S1-",
    "FAST_LANE_V2_SERIES_2": "MI-FL2-S2-",
}
STEP_FAST_LANE_CANONICAL_BLOCK = """### FAST_LANE_V2 — canonical usage

Every STEP MUST contain both complete FAST_LANE_V2 rows and their configured, disjoint MI paths. This
is an unconditional plan-construction requirement. The runtime activation conditions below govern
only which configured path executes for a particular event; they can never remove, weaken, relabel,
reason away, or replace required plan content.

Activate `FAST_LANE_V2` only for a compatible set of small, scoped edits with deterministic impact and a
known motivating test. In an affected earlier step, `FAST_LANE_V2_SERIES_1` takes the distinct
`MI-FL2-S1-*` outbound-patch path to make the scoped repair, run only changed-source compile and
motivating tests, independently review and integrate the repaired output, and exit forward to the
current progress-bound step. At that current progress-bound step, `FAST_LANE_V2_SERIES_2` takes the
distinct `MI-FL2-S2-*` inbound-reconcile path to receive all accepted repairs, calculate invalidation,
preserve unaffected PASS credit, run only failed, unresolved, affected, uncertain, or uncredited
checks from the earliest required unit, and then continue normal forward progress. Use these paths to
avoid redoing heavy computations, broad review/test campaigns, or full restarts when their inputs and
PASS credit remain valid; if the activation predicate, deterministic impact, or safe credit reuse cannot be proven,
use R15's normal material classification for that event. That event-level route does not change either
required FAST_LANE_V2 row or its configured contract."""
STEP_CONTRACT_FIELDS = [
    "Step ID",
    "Objective and independently decidable outcome",
    "Acceptance owner",
    "Deliverable and requirement coverage",
    "Global policy and exception references",
    "Public compatibility boundary",
]
STEP_COMPOSITION_TABLE = (
    "Order",
    "Instance ID",
    "Module type",
    "Consumes",
    "Produces",
    "Activation/condition",
)
STEP_GATE_TABLE = (
    "Gate/loop ID",
    "Gate class",
    "Shared input",
    "Decided behavioral outcome",
    "Checking module instances",
    "Shared failure family/invariants",
    "Blocking scope",
    "Continuation/loop eligibility",
    "Default-forward edge",
    "Failure return target",
    "Aggregation payoff",
    "Manageability proof",
    "Prior-result boundary",
    "Split/merge trigger",
)
MODULE_HEADINGS = [
    "## Module contract and selection",
    "## Public interface and compatibility boundary",
    "## Rules, process, recipe actions, and allowed variations",
    "## Configured module instances",
]
MODULE_SELECTION_TABLE = (
    "Module type",
    "Decision",
    "Instance IDs",
    "Reason",
)
MODULE_ACTION_TABLE = (
    "Order",
    "Recipe action ID",
    "Project-specific action/process",
    "Allowed parameterization",
    "Decision owner",
)
INSTANCE_RE = re.compile(r"(?m)^###\s+(MI-[A-Z0-9][A-Z0-9_-]*)\s+-\s+(M\d{2}):\s+(.+?)\s*$")
MI_RE = re.compile(r"\bMI-[A-Z0-9][A-Z0-9_-]*\b")
STEP_RE = re.compile(r"\bSTEP-[A-Z0-9][A-Z0-9_-]*\b")
REQ_RE = re.compile(r"\bREQ-[A-Z0-9][A-Z0-9._-]*\b")
DEL_RE = re.compile(r"\bDEL-[A-Z0-9][A-Z0-9._-]*\b")
OUT_RE = re.compile(r"\bOUT-[A-Z0-9][A-Z0-9._-]*\b")
LANE_RE = re.compile(r"\bLANE-[A-Z0-9][A-Z0-9._-]*\b")
HANDOFF_RE = re.compile(r"\bHANDOFF-[A-Z0-9][A-Z0-9._-]*\b")
RESULT_RE = re.compile(r"\bRESULT-[A-Z0-9][A-Z0-9._-]*\b")
PROCESS_RE = re.compile(r"\bPROCESS-[A-Z0-9][A-Z0-9._-]*\b")
INVOCATION_RE = re.compile(r"\bINVOCATION-[A-Z0-9][A-Z0-9._-]*\b")
FAST_LANE_OPT_OUT_RE = re.compile(
    r"\b(?:ineligible|disabled|unsupported|unavailable|optional|not\s+required|not\s+applicable|"
    r"omit(?:ted)?|skip(?:ped)?|normal[- ]only|never\s+execute|must\s+not\s+execute|"
    r"do\s+not\s+execute|cannot\s+execute|waiv(?:e|ed|er)|exempt(?:ed|ion)?|"
    r"prohibit(?:ed|ion)?|never\s+activates?|"
    r"always\s+false|literal\s+false|false\s+condition|impossible\s+predicate|cannot\s+activate)\b|\bN/?A\b",
    re.IGNORECASE,
)
ORDERED_MI_PATH_RE = re.compile(
    r"^\s*MI-[A-Z0-9][A-Z0-9_-]*(?:\s*(?:->|\u2192|,|;)\s*MI-[A-Z0-9][A-Z0-9_-]*)*\s*$"
)
VAGUE_EXECUTION_RE = re.compile(
    r"\b(?:as needed|if useful|when useful|where useful|as appropriate|if appropriate|"
    r"when appropriate|where appropriate|best practice|standard procedure)\b",
    re.IGNORECASE,
)
HARD_VALUE_BYPASS_RE = re.compile(
    r"\b(?:TBD|TODO|UNKNOWN|DEFERRED|INELIGIBLE|waiv(?:e|ed|er)|exempt(?:ed|ion)?|"
    r"not\s+required|no\s+verification|"
    r"later\s+by|after\s+dispatch|self[- ]certif(?:y|ies|ied|ication)|author\s+(?:says|claims))\b",
    re.IGNORECASE,
)
REQUIRED_TABLE_BYPASS_RE = re.compile(
    r"\b(?:TBD|TODO|UNKNOWN|DEFERRED|INELIGIBLE|waiv(?:e|ed|er)|exempt(?:ed|ion)?|"
    r"self[- ]certif(?:y|ies|ied|ication)|author\s+(?:says|claims))\b",
    re.IGNORECASE,
)
FAST_LANE_CONTRACT_BYPASS_RE = re.compile(
    r"\b(?:never\s+activates?|always\s+false|literal\s+false|false\s+condition|"
    r"impossible\s+predicate|cannot\s+activate)\b|"
    r"\b(?:FAST_LANE_V2|fast[-_ ]lane|series\s*[12])\b(?:\s+\S+){0,12}\s+"
    r"(?:is|are|may\s+be|can\s+be|remains?|was|were)\s+"
    r"(?:ineligible|disabled|optional|not\s+required|not\s+applicable|omitted|skipped|"
    r"waived|exempt|prohibited)\b|"
    r"\b(?:FAST_LANE_V2|fast[-_ ]lane|series\s*[12])\b(?:\s+\S+){0,12}\s+"
    r"(?:execution|entry|path|contract)?\s*(?:ineligible|disabled|omitted|waived|exempt|prohibited)\b",
    re.IGNORECASE,
)
TASK_CARD_RE = re.compile(
    r"(?m)^#####\s+(Governing|Member) task card:\s+(CARD-[A-Z0-9][A-Z0-9_-]*)\s*$"
)


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().strip("`"))


def is_bare(value: str) -> bool:
    return normalize(value).upper() in UNDISPATCHABLE_BARE_TASK_VALUES


def is_bare_executable(value: str) -> bool:
    return normalize(value).upper() in UNDISPATCHABLE_EXECUTABLE_VALUES


def contains_na(value: str) -> bool:
    return bool(re.search(r"\bN/?A\b|\bnot applicable\b", normalize(value), re.IGNORECASE))


def invalid_hard_value(value: str) -> bool:
    return is_bare(value) or contains_na(value) or bool(HARD_VALUE_BYPASS_RE.search(normalize(value)))


def invalid_obligation_value(value: str) -> bool:
    normalized = normalize(value)
    return invalid_hard_value(normalized) or bool(
        re.match(r"^(?:SKIPPED|OMITTED|OPTIONAL|PROHIBITED)(?:\b|\s*[:;-])", normalized, re.IGNORECASE)
    )


def invalid_executable_value(value: str) -> bool:
    """Reject empty/N/A-equivalent values in selected executable contracts."""
    normalized = normalize(value)
    return is_bare_executable(normalized) or invalid_obligation_value(normalized)


def invalid_required_table_value(value: str) -> bool:
    normalized = normalize(value)
    return is_bare(normalized) or contains_na(normalized) or bool(REQUIRED_TABLE_BYPASS_RE.search(normalized))


def table_cells(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return [normalize(cell) for cell in stripped[1:-1].split("|")]


def is_separator(cells: list[str] | None) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def extract_table(body: str, header: tuple[str, ...]) -> list[list[str]] | None:
    lines = body.splitlines()
    expected = list(header)
    for index, line in enumerate(lines):
        if table_cells(line) != expected:
            continue
        if index + 1 >= len(lines) or not is_separator(table_cells(lines[index + 1])):
            return []
        rows: list[list[str]] = []
        for row_line in lines[index + 2 :]:
            cells = table_cells(row_line)
            if cells is None:
                if rows or row_line.strip():
                    break
                continue
            if len(cells) != len(expected):
                rows.append(cells)
                continue
            rows.append(cells)
        return rows
    return None


def table_header_count(body: str, header: tuple[str, ...]) -> int:
    expected = list(header)
    return sum(1 for line in body.splitlines() if table_cells(line) == expected)


def validate_pipe_table_groups(text: str, filename: str) -> list[str]:
    """Reject detached/unknown pipe rows that extract_table would otherwise ignore."""
    known_headers = {
        header for headers in REQUIRED_TABLES.values() for header in headers
    } | {
        PACKAGE_DEPENDENCY_TABLE, ROLE_TABLE, POLICY_TABLE, EXCEPTION_TABLE,
        STEP_ENTRY_TABLE, STEP_COMPOSITION_TABLE, STEP_GATE_TABLE,
        MODULE_SELECTION_TABLE, MODULE_ACTION_TABLE, ("Field", "Value"),
    }
    if filename == "plan-workflow.md":
        root_headings = HEADINGS[:9] + [HEADINGS[10], HEADINGS[12], HEADINGS[13], HEADINGS[14]]
        allowed_headers = {header for heading in root_headings for header in REQUIRED_TABLES[heading]}
    elif filename == "global-rules.md":
        allowed_headers = {POLICY_TABLE, EXCEPTION_TABLE}
    elif filename == "validation.md":
        allowed_headers = set(REQUIRED_TABLES[HEADINGS[15]] + REQUIRED_TABLES[HEADINGS[16]])
    elif filename.startswith("steps/"):
        allowed_headers = {("Field", "Value"), STEP_ENTRY_TABLE, STEP_COMPOSITION_TABLE, STEP_GATE_TABLE}
    elif filename.startswith("modules/"):
        allowed_headers = {MODULE_SELECTION_TABLE, MODULE_ACTION_TABLE, ("Field", "Value")}
    else:
        allowed_headers = known_headers
    errors: list[str] = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        if table_cells(lines[index]) is None:
            index += 1
            continue
        start = index
        group: list[list[str]] = []
        while index < len(lines) and table_cells(lines[index]) is not None:
            group.append(table_cells(lines[index]) or [])
            index += 1
        first = tuple(group[0])
        if first not in known_headers:
            errors.append(
                f"{filename} has a detached or unknown pipe-table group at line {start + 1}; "
                "every pipe row must remain under a declared schema header"
            )
        elif first not in allowed_headers:
            errors.append(
                f"{filename} contains table {' | '.join(first)} at line {start + 1}, "
                "but that schema belongs to a different artifact"
            )
    return errors


def task_card_blocks(body: str) -> list[tuple[str, str, str]]:
    matches = list(TASK_CARD_RE.finditer(body))
    return [
        (
            match.group(1),
            match.group(2),
            body[match.end() : matches[index + 1].start() if index + 1 < len(matches) else len(body)],
        )
        for index, match in enumerate(matches)
    ]


def section(text: str, heading: str, next_heading: str | None) -> str:
    start = text.index(heading) + len(heading)
    end = text.index(next_heading, start) if next_heading else len(text)
    return text[start:end]


def sections(text: str) -> dict[str, str]:
    return {
        heading: section(text, heading, HEADINGS[index + 1] if index + 1 < len(HEADINGS) else None)
        for index, heading in enumerate(HEADINGS)
    }


def duplicates(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def id_column(rows: list[list[str]], pattern: str) -> list[str]:
    return [row[0] for row in rows if row and re.fullmatch(pattern, row[0])]


def validate_required_tables(by_section: dict[str, str]) -> list[str]:
    errors: list[str] = []
    optional_na_headers = {
        REQUIRED_TABLES[HEADINGS[8]][1],
        REQUIRED_TABLES[HEADINGS[10]][1],
        REQUIRED_TABLES[HEADINGS[10]][2],
        REQUIRED_TABLES[HEADINGS[10]][4],
        REQUIRED_TABLES[HEADINGS[10]][5],
        REQUIRED_TABLES[HEADINGS[12]][0],
        REQUIRED_TABLES[HEADINGS[13]][0],
        REQUIRED_TABLES[HEADINGS[14]][0],
    }
    allowed_na_cells = {
        ROLE_TABLE: {2, 3},
        REQUIRED_TABLES[HEADINGS[8]][0]: {5},
        REQUIRED_TABLES[HEADINGS[8]][1]: {6},
        REQUIRED_TABLES[HEADINGS[10]][1]: {4},
        REQUIRED_TABLES[HEADINGS[10]][2]: {6},
        REQUIRED_TABLES[HEADINGS[10]][3]: {3},
        REQUIRED_TABLES[HEADINGS[12]][0]: {3, 4, 5},
        REQUIRED_TABLES[HEADINGS[13]][0]: {3, 4, 5, 6},
    }
    known_required_headers = {
        header for headers in REQUIRED_TABLES.values() for header in headers
    }
    for heading, headers in REQUIRED_TABLES.items():
        body = by_section[heading]
        allowed_headers = set(headers)
        for line_number, line in enumerate(body.splitlines(), 1):
            cells = table_cells(line)
            if cells and tuple(cells) in known_required_headers and tuple(cells) not in allowed_headers:
                errors.append(
                    f"{heading} contains a known schema table in the wrong owning section at line {line_number}"
                )
        for header in headers:
            occurrence_count = table_header_count(body, header)
            if occurrence_count != 1:
                errors.append(
                    f"{heading} must contain table {' | '.join(header)} exactly once; found {occurrence_count}"
                )
            rows = extract_table(body, header)
            if rows is None:
                errors.append(f"{heading} is missing table: {' | '.join(header)}")
            elif not rows:
                errors.append(f"{heading} table has no data rows: {' | '.join(header)}")
            elif any(len(row) != len(header) for row in rows):
                errors.append(f"{heading} table has a row with the wrong column count: {' | '.join(header)}")
            else:
                for row in rows:
                    if normalize(row[0]).upper() == "N/A":
                        if header not in optional_na_headers:
                            errors.append(
                                f"{heading} table {' | '.join(header)} is mandatory and may not use an N/A sentinel"
                            )
                            continue
                        if len(rows) != 1:
                            errors.append(
                                f"{heading} table {' | '.join(header)} may use only one sole N/A sentinel row"
                            )
                        reason = normalize(" ".join(row[1:]))
                        if len(reason) < 40 or not re.search(
                            r"\b(?:because|no |none |not required|does not|without)\b", reason, re.IGNORECASE
                        ):
                            errors.append(
                                f"{heading} table {' | '.join(header)} uses an N/A sentinel without a concrete reason"
                            )
                        continue
                    for index, value in enumerate(row):
                        if index in allowed_na_cells.get(header, set()):
                            continue
                        if invalid_required_table_value(value):
                            errors.append(
                                f"{heading} table {' | '.join(header)} field {header[index]} "
                                "contains an N/A, placeholder, or waiver"
                            )
    return errors


def optional_decision_error(value: str, selected_requires_detail: bool = False) -> str | None:
    normalized = normalize(value)
    if normalized == "SELECTED" and not selected_requires_detail:
        return None
    if selected_requires_detail and re.fullmatch(r"SELECTED:\s+.{16,}", normalized):
        return None
    omitted = re.fullmatch(r"OMITTED:\s+(.+)", normalized)
    if omitted:
        reason = normalize(omitted.group(1))
        if len(reason) >= 24 and not invalid_required_table_value(reason) and not VAGUE_EXECUTION_RE.search(reason):
            return None
        return "OMITTED requires a substantive free-form project justification"
    selected_form = "SELECTED: <concrete action>" if selected_requires_detail else "SELECTED"
    return f"use exactly {selected_form} or OMITTED: <free-form project justification>"


def validate_optional_profile_decisions(
    by_section: dict[str, str],
    module_texts: dict[str, str],
    instance_types: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    selected_types = set(instance_types.values())
    section_specs = (
        (HEADINGS[12], REQUIRED_TABLES[HEADINGS[12]][0], r"EXT-[A-Z0-9][A-Z0-9._-]*", {"M08", "M09"}),
        (HEADINGS[13], REQUIRED_TABLES[HEADINGS[13]][0], r"REL-[A-Z0-9][A-Z0-9._-]*", {"M06", "M07"}),
    )
    rows_by_module: dict[str, list[list[str]]] = {}
    decision_ids: list[str] = []
    for heading, header, id_pattern, allowed_modules in section_specs:
        rows = extract_table(by_section[heading], header) or []
        for row in rows:
            if len(row) != len(header) or row[0] == "N/A":
                continue
            decision_ids.append(row[0])
            if not re.fullmatch(id_pattern, row[0]):
                errors.append(f"{heading} has invalid decision ID {row[0]!r}")
            if row[1] not in allowed_modules:
                errors.append(f"{row[0]} must name one of {', '.join(sorted(allowed_modules))}")
                continue
            if row[1] not in selected_types:
                errors.append(f"{row[0]} names {row[1]}, but that optional module is not SELECTED")
            if decision_error := optional_decision_error(row[2]):
                errors.append(f"{row[0]} Decision must {decision_error}")
            if normalize(row[2]) == "SELECTED":
                required_selected_fields = {
                    "M08": (3, 4),
                    "M09": (3, 5),
                    "M06": (3, 4, 5),
                    "M07": (3, 4, 5),
                }[row[1]]
                for field_index in required_selected_fields:
                    if invalid_executable_value(row[field_index]):
                        errors.append(
                            f"{row[0]} SELECTED {header[field_index]} must be concrete; "
                            "N/A-equivalents and omission/waiver language are forbidden"
                        )
            rows_by_module.setdefault(row[1], []).append(row)

    if duplicates(decision_ids):
        errors.append(f"optional profile/manifest decision IDs are duplicated: {', '.join(duplicates(decision_ids))}")

    for module_type in selected_types & {"M08", "M09"}:
        if not rows_by_module.get(module_type):
            errors.append(f"selected {module_type} requires a concrete Section 12 decision row")
    for module_type in selected_types & {"M06", "M07"}:
        if not rows_by_module.get(module_type):
            errors.append(f"selected {module_type} requires a concrete Section 13 decision row")
    for module_type in selected_types & {"M06", "M07", "M08", "M09"}:
        if rows_by_module.get(module_type) and not any(
            normalize(row[2]) == "SELECTED" for row in rows_by_module[module_type]
        ):
            errors.append(
                f"selected {module_type} requires at least one SELECTED Section "
                f"{'12' if module_type in {'M08', 'M09'} else '13'} behavior row; "
                "OMITTED rows may describe only additional optional profiles"
            )

    if "M08" in selected_types:
        action_rows = extract_table(module_texts.get("M08.md", ""), MODULE_ACTION_TABLE) or []
        actions = {row[1]: row[2] for row in action_rows if len(row) == len(MODULE_ACTION_TABLE)}
        for action_id, profile in (("M08-A2", "recordability preflight"), ("M08-A3", "external rehearsal")):
            if decision_error := optional_decision_error(actions.get(action_id, ""), selected_requires_detail=True):
                errors.append(f"{action_id} {profile} decision must {decision_error}")
    return errors


def validate_instances(body: str, instance_types: dict[str, str]) -> list[str]:
    errors: list[str] = []
    card_ids: list[str] = []
    matches = list(INSTANCE_RE.finditer(body))
    found_ids = [match.group(1) for match in matches]
    if duplicates(found_ids):
        errors.append(f"module files contain duplicate instance blocks: {', '.join(duplicates(found_ids))}")
    missing = sorted(set(instance_types) - set(found_ids))
    extra = sorted(set(found_ids) - set(instance_types))
    if missing:
        errors.append(f"selected module instances missing from their owning M files: {', '.join(missing)}")
    if extra:
        errors.append(f"M files contain undeclared module instances: {', '.join(extra)}")

    for index, match in enumerate(matches):
        instance_id, module_type = match.group(1), match.group(2)
        block_end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        block = body[match.end() : block_end]
        if instance_types.get(instance_id) != module_type:
            errors.append(
                f"{instance_id} block type {module_type} does not match its M-file selection type "
                f"{instance_types.get(instance_id, 'UNDECLARED')}"
            )
        fields = re.findall(r"(?m)^####\s+(.+?)\s*$", block)
        if fields != INSTANCE_FIELDS:
            errors.append(
                f"{instance_id} does not use the exact 15 H4 subheadings in order "
                "(16 required schema headings including its MI H3)"
            )
        field_matches = list(re.finditer(r"(?m)^####\s+(.+?)\s*$", block))
        instance_field_values: dict[str, str] = {}
        for field_index, field_match in enumerate(field_matches):
            field_name = field_match.group(1)
            field_end = field_matches[field_index + 1].start() if field_index + 1 < len(field_matches) else len(block)
            field_value = normalize(block[field_match.end() : field_end])
            instance_field_values[field_name] = field_value
            if field_name == "Local instructions":
                continue
            if invalid_executable_value(field_value):
                errors.append(f"{instance_id} instance field {field_name} is empty or a non-executable placeholder/waiver")
            elif re.search(r"\bN/?A\b|\bnot applicable\b", field_value, re.IGNORECASE):
                errors.append(f"{instance_id} executable instance field {field_name} may not use N/A")
            if VAGUE_EXECUTION_RE.search(field_value):
                errors.append(f"{instance_id} instance field {field_name} contains vague executable language")
        local_start = block.find("#### Local instructions")
        local_end = block.find("#### Outputs and results", local_start + 1)
        local_body = block[local_start:local_end] if local_start >= 0 and local_end >= 0 else ""
        cards = task_card_blocks(local_body)
        h5_headings = re.findall(r"(?m)^#####\s+.+?$", local_body)
        if len(h5_headings) != len(cards):
            errors.append(f"{instance_id} has an H5 that is not an exact governing/member task-card label")
        governing_cards = [card for card in cards if card[0] == "Governing"]
        if len(governing_cards) != 1:
            errors.append(f"{instance_id} must contain exactly one governing task card")
        member_cards = [card for card in cards if card[0] == "Member"]
        if not member_cards:
            errors.append(f"{instance_id} must contain at least one member task card for executable worker dispatch")
        dispatch_inventory = re.findall(
            r"\b(CARD-[A-Z0-9][A-Z0-9_-]*)\s*=\s*([A-Za-z][A-Za-z0-9._-]*)\b",
            instance_field_values.get("Owner and roles", ""),
        )
        inventory_card_ids = [card_id for card_id, _role in dispatch_inventory]
        expected_member_ids = [card_id for _kind, card_id, _body in member_cards]
        if inventory_card_ids != expected_member_ids or duplicates(inventory_card_ids):
            errors.append(
                f"{instance_id} Owner and roles must inventory every member dispatch exactly once as CARD-ID=workflow_role"
            )
        inventoried_roles = dict(dispatch_inventory)
        for card_kind, card_id, card_body in cards:
            card_ids.append(card_id)
            task_rows = extract_table(card_body, ("Field", "Value"))
            if table_header_count(card_body, ("Field", "Value")) != 1:
                errors.append(f"{instance_id} {card_id} must contain exactly one Field | Value table")
            if task_rows is None:
                errors.append(f"{instance_id} {card_id} has no Field | Value task-card table")
                continue
            valid_task_rows = [row for row in task_rows if len(row) == 2]
            if len(valid_task_rows) != len(task_rows):
                errors.append(f"{instance_id} {card_id} has a malformed task-card row")
            if [row[0] for row in valid_task_rows] != TASK_FIELDS:
                errors.append(f"{instance_id} {card_id} does not use all 20 task-card fields in order")
            task_values = {row[0]: row[1] for row in valid_task_rows}
            identity_value = task_values.get(TASK_FIELDS[0], "")
            assignments = dict(re.findall(r"\b([a-z_]+)=([A-Za-z0-9][A-Za-z0-9._-]*)\b", identity_value))
            expected_identity_keys = {
                "schema", "card_id", "module_instance_id", "deliverable_id",
                "stage_cohort_id", "gate_id", "loop_id",
            }
            identity_valid = (
                set(assignments) == expected_identity_keys
                and assignments.get("card_id") == card_id
                and assignments.get("module_instance_id") == instance_id
                and bool(re.fullmatch(r"DEL-[A-Z0-9][A-Z0-9._-]*", assignments.get("deliverable_id", "")))
                and bool(re.fullmatch(r"COHORT-[A-Z0-9][A-Z0-9._-]*", assignments.get("stage_cohort_id", "")))
                and bool(re.fullmatch(r"GATE-[A-Z0-9][A-Z0-9._-]*", assignments.get("gate_id", "")))
                and bool(re.fullmatch(r"LOOP-[A-Z0-9][A-Z0-9._-]*", assignments.get("loop_id", "")))
            )
            if not identity_valid:
                errors.append(
                    f"{instance_id} {card_id} identity row must assign exactly seven nonempty, well-formed "
                    "schema/card/module-instance/deliverable/cohort/gate/loop values"
                )
            for task_field in TASK_FIELDS:
                raw_task_value = normalize(task_values.get(task_field, ""))
                if invalid_executable_value(raw_task_value):
                    errors.append(
                        f"{instance_id} {card_id} task field {task_field} has a placeholder or waiver; "
                        "the owning authorized orchestration authority must supply a concrete "
                        "dispatch-contract value; N/A and justification-based waivers are forbidden"
                    )
                elif re.search(r"\bN/?A\b|\bnot applicable\b", raw_task_value, re.IGNORECASE):
                    errors.append(f"{instance_id} {card_id} executable task field {task_field} may not use N/A")
                if VAGUE_EXECUTION_RE.search(raw_task_value):
                    errors.append(f"{instance_id} {card_id} task field {task_field} contains vague executable language")
                if task_field in {
                    "objective", "required_behavior", "verification",
                    "acceptance_criteria_and_tolerances", "completion_review_owner_and_handoff",
                } and invalid_obligation_value(raw_task_value):
                    errors.append(f"{instance_id} {card_id} hard obligation field {task_field} uses waiver language")
            cited_policy_value = task_values.get("cited_global_policy_ids_and_exception_ids", "")
            if not re.search(r"\bP(?:0[1-9]|1[0-5])\b", cited_policy_value):
                errors.append(f"{instance_id} {card_id} must cite at least one applicable global policy ID")
            if card_kind == "Member" and inventoried_roles.get(card_id) != task_values.get("workflow_role"):
                errors.append(f"{instance_id} {card_id} workflow role disagrees with the Owner and roles dispatch inventory")
            found_actions = re.findall(r"\bM\d{2}-A\d+\b", task_values.get("ordered_actions", ""))
            expected_actions = MODULE_ACTIONS.get(module_type, [])
            if card_kind == "Governing" and found_actions != expected_actions:
                errors.append(
                    f"{instance_id} governing card {card_id} ordered_actions must contain "
                    f"{', '.join(MODULE_ACTIONS.get(module_type, []))} exactly once and in order"
                )
            if card_kind == "Member":
                positions = [expected_actions.index(action) for action in found_actions if action in expected_actions]
                if (
                    not found_actions
                    or len(positions) != len(found_actions)
                    or duplicates(found_actions)
                    or positions != sorted(positions)
                ):
                    errors.append(
                        f"{instance_id} member card {card_id} ordered_actions must be a nonempty, "
                        f"duplicate-free ordered subsequence of {', '.join(expected_actions)}"
                    )
    if duplicates(card_ids):
        errors.append(f"task-card IDs are declared more than once: {', '.join(duplicates(card_ids))}")
    return errors


def validate_policies(
    body: str,
    instance_types: dict[str, str],
    mapping_roles: set[str],
    root_role: str,
) -> list[str]:
    errors: list[str] = []
    if table_header_count(body, POLICY_TABLE) != len(POLICY_HEADINGS):
        errors.append("Section 9 must contain exactly one policy table under each P01-P15 heading")
    if table_header_count(body, EXCEPTION_TABLE) != 1:
        errors.append("Section 9 must contain exactly one exception-class table, owned by P14")
    found = re.findall(r"(?m)^###\s+P\d{2}.+?$", body)
    if found != POLICY_HEADINGS:
        errors.append("Section 9 does not contain exact P01-P15 policy headings in order")
        return errors
    for index, heading in enumerate(POLICY_HEADINGS):
        start = body.index(heading) + len(heading)
        end = body.index(POLICY_HEADINGS[index + 1], start) if index + 1 < len(POLICY_HEADINGS) else len(body)
        policy_body = body[start:end]
        if table_header_count(policy_body, POLICY_TABLE) != 1:
            errors.append(f"{heading} must contain exactly one policy table")
        rows = extract_table(policy_body, POLICY_TABLE)
        if rows is None or not rows:
            errors.append(f"{heading} has no populated policy table")
        else:
            if heading.startswith("### P01") and not any(
                len(row) == len(POLICY_TABLE) and row[0] == root_role for row in rows
            ):
                errors.append("P01 must contain a concrete ROOT-owned ownership/decision policy row")
            for row in rows:
                if len(row) != len(POLICY_TABLE):
                    errors.append(f"{heading} has a malformed policy row")
                    continue
                for field_name, value in zip(POLICY_TABLE[:4], row[:4]):
                    if invalid_executable_value(value):
                        errors.append(f"{heading} policy field {field_name} is empty or a non-executable placeholder/waiver")
                    if VAGUE_EXECUTION_RE.search(value):
                        errors.append(f"{heading} policy field {field_name} contains vague executable language")
                if row[0] not in mapping_roles:
                    errors.append(f"{heading} policy owner {row[0]!r} is absent from the role mapping")
                policy_instance_ids = MI_RE.findall(row[5])
                if normalize(row[5]).upper() != "N/A" and not policy_instance_ids:
                    errors.append(f"{heading} Module IDs must name configured MI-* IDs or N/A")
                unknown_instances = sorted(set(policy_instance_ids) - set(instance_types))
                if unknown_instances:
                    errors.append(f"{heading} references undeclared module instances: {', '.join(unknown_instances)}")
        if heading.startswith("### P14"):
            if table_header_count(policy_body, EXCEPTION_TABLE) != 1:
                errors.append("P14 must contain exactly one exception-class table")
            exception_rows = extract_table(policy_body, EXCEPTION_TABLE)
            if exception_rows is None or not exception_rows:
                errors.append("P14 has no exception-class table or explained no-exception sentinel row")
            else:
                valid_exception_rows = [row for row in exception_rows if len(row) == len(EXCEPTION_TABLE)]
                if len(valid_exception_rows) != len(exception_rows):
                    errors.append("P14 has a malformed exception row")
                na_rows = [row for row in valid_exception_rows if normalize(row[0]).upper() == "N/A"]
                if na_rows:
                    if len(valid_exception_rows) != 1 or len(normalize(" ".join(na_rows[0][1:]))) < 40 or not re.search(
                        r"\b(?:no exception|none declared|without exception)\b",
                        " ".join(na_rows[0][1:]),
                        re.IGNORECASE,
                    ):
                        errors.append("P14 N/A row must be the sole row and explain concretely that no exception is declared")
                for row in valid_exception_rows:
                    if normalize(row[0]).upper() == "N/A":
                        continue
                    if not re.fullmatch(r"EXC-[A-Z0-9][A-Z0-9._-]*", row[0]):
                        errors.append(f"P14 has invalid exception ID {row[0]!r}")
                    if row[1] not in {policy.split()[1] for policy in POLICY_HEADINGS}:
                        errors.append(f"{row[0]} affects unknown policy {row[1]!r}")
                    if row[3] not in mapping_roles:
                        errors.append(f"{row[0]} decision owner {row[3]!r} is absent from the role mapping")
                    for field_name, value in zip(EXCEPTION_TABLE[1:], row[1:]):
                        if invalid_hard_value(value):
                            errors.append(
                                f"{row[0]} exception field {field_name} contains an N/A, placeholder, or waiver"
                            )
                    if invalid_obligation_value(row[5]):
                        errors.append(f"{row[0]} Required confirmation uses waiver language")
    return errors


def validate_verification_economy(
    plan_contract: str,
    global_policies: str,
    text: str,
) -> list[str]:
    """Validate the required checkpointed and three-entry fast-lane protocol."""

    checkpointed = "checkpointed_verification_v1" in plan_contract.lower()
    if not checkpointed:
        return ["formal modular plans require CHECKPOINTED_VERIFICATION_V1 in Section 0"]

    errors: list[str] = []
    policy_text = global_policies.lower()
    for term in ("checkpoint", "input map", "first unresolved", "earliest required", "ordinary failure"):
        if term not in policy_text:
            errors.append(f"CHECKPOINTED_VERIFICATION_V1 requires policy text for {term!r}")
    for term in (
        "complete pool",
        "motivating test",
        "compile",
        "review",
        "integration",
        "smoke credit",
        "series 1",
        "series 2",
        "progress bound",
        "saved work",
    ):
        if term not in policy_text:
            errors.append(f"FAST_LANE_V2 requires policy text for {term!r}")
    policy_bodies: dict[str, str] = {}
    for index, heading in enumerate(POLICY_HEADINGS):
        start = global_policies.find(heading)
        if start < 0:
            continue
        start += len(heading)
        end = global_policies.find(POLICY_HEADINGS[index + 1], start) if index + 1 < len(POLICY_HEADINGS) else len(global_policies)
        policy_bodies[heading.split()[1]] = global_policies[start:end].lower()
    for policy_id, terms in {
        "P04": ("checkpoint", "input map", "first unresolved", "earliest required", "ordinary failure",
                "complete pool", "motivating test", "compile", "review", "integration", "smoke credit",
                "series 1", "series 2", "progress bound", "saved work"),
        "P07": ("complete pool", "series 1", "progress bound", "series 2", "join"),
    }.items():
        policy_body = policy_bodies.get(policy_id, "")
        if FAST_LANE_OPT_OUT_RE.search(policy_body):
            errors.append(f"{policy_id} contains forbidden opt-out language for required verification behavior")
        for term in terms:
            if term not in policy_body:
                errors.append(f"{policy_id} must own its required verification-economy behavior for {term!r}")
    return errors


def validate_gates(body: str) -> list[str]:
    errors: list[str] = []
    header = STEP_GATE_TABLE
    rows = extract_table(body, header) or []
    gate_ids = [row[0] for row in rows if len(row) == len(header) and row[0] != "N/A"]
    if duplicates(gate_ids):
        errors.append(f"gate manifest contains duplicates: {', '.join(duplicates(gate_ids))}")

    for row in rows:
        if len(row) != len(header):
            continue
        if row[0] == "N/A":
            errors.append("STEP gate/completion rows may not use N/A")
            continue
        gate_id, gate_class = row[0], row[1]
        for field_name, value in zip(header, row):
            if invalid_executable_value(value):
                errors.append(f"{gate_id} gate field {field_name} is empty or a non-executable placeholder/waiver")
        if not gate_id.startswith("GATE-"):
            errors.append(f"gate row has invalid ID {gate_id!r}")
        if gate_class not in ALLOWED_GATE_CLASSES:
            errors.append(f"{gate_id} has invalid gate class {gate_class!r}")
        required_fields = (
            (6, "blocking scope"),
            (7, "continuation/loop eligibility"),
            (8, "default-forward edge"),
            (9, "failure return target"),
        )
        for index, label in required_fields:
            if row[index].lower() in {"", "n/a", "none", "not applicable"}:
                errors.append(f"{gate_id} has no {label}")
        blocking_scope = row[6].lower()
        continuation = row[7].lower()
        default_forward = row[8].lower()
        failure_target = row[9].lower()

        if not any(
            token in default_forward
            for token in (
                "edge",
                "advance",
                "continue",
                "accept",
                "success",
                "terminal",
            )
        ):
            errors.append(f"{gate_id} default-forward edge must name an advancing successor or terminal action")

        if gate_class == "PRODUCT":
            decided_outcome = row[3].lower()
            strong_product_terms = (
                "behavior",
                "contract",
                "satisf",
                "capability",
                "agree",
                "prove",
            )
            operation_terms = (
                "allocat",
                "integrat",
                "join",
                "deploy",
                "promot",
                "read back",
                "readback",
                "cleanup",
                "retire",
            )
            names_product_outcome = any(token in decided_outcome for token in strong_product_terms) or (
                "correct" in decided_outcome and not any(token in decided_outcome for token in operation_terms)
            )
            if not names_product_outcome:
                errors.append(
                    f"{gate_id} PRODUCT decided outcome must name observable behavior, "
                    "contract, capability, correctness, satisfaction, agreement, or proof; "
                    "a pure required operation belongs to OPERATION_BOUNDARY"
                )
            required_terms = ("only", "required", "product")
            if not all(term in continuation for term in required_terms) or not any(
                term in continuation for term in ("fail", "undecidable")
            ):
                errors.append(
                    f"{gate_id} PRODUCT continuation eligibility must say that only a failed/"
                    "undecidable required product criterion permits continuation"
                )
            if "only" not in blocking_scope:
                errors.append(f"{gate_id} PRODUCT blocking scope must be explicitly limited with 'only'")

        if gate_class == "OPERATION_BOUNDARY":
            if "only" not in blocking_scope or "never product" not in blocking_scope:
                errors.append(
                    f"{gate_id} OPERATION_BOUNDARY blocking scope must say it holds only the "
                    "exact operation and never product work/credit"
                )
            if "no product loop" not in continuation:
                errors.append(f"{gate_id} OPERATION_BOUNDARY continuation must explicitly say 'No product loop'")
            if any(
                token in failure_target
                for token in (
                    "m02",
                    "material repair",
                    "material return",
                    "product repair",
                )
            ):
                errors.append(f"{gate_id} OPERATION_BOUNDARY failure target must not enter product repair")
    return errors


def validate_cross_references(
    by_section: dict[str, str],
    instance_types: dict[str, str],
    step_texts: dict[str, str],
    mapping_roles: set[str],
) -> list[str]:
    errors: list[str] = []
    source_rows = extract_table(by_section[HEADINGS[1]], REQUIRED_TABLES[HEADINGS[1]][0]) or []
    source_ids = [row[0] for row in source_rows if len(row) == 5]
    invalid_source_ids = [item for item in source_ids if not re.fullmatch(r"SRC-[A-Z0-9][A-Z0-9._-]*", item)]
    if invalid_source_ids:
        errors.append(f"authority/source table has invalid SRC-* IDs: {', '.join(invalid_source_ids)}")
    if duplicates(source_ids):
        errors.append(f"authority/source table has duplicate IDs: {', '.join(duplicates(source_ids))}")
    hierarchy_rows = extract_table(by_section[HEADINGS[1]], REQUIRED_TABLES[HEADINGS[1]][1]) or []
    if [row[0] for row in hierarchy_rows if len(row) == 4] != [str(number) for number in range(1, 10)]:
        errors.append("directive hierarchy table must declare exact Layers 1 through 9 once and in order")
    req_header = REQUIRED_TABLES[HEADINGS[3]][0]
    deliverable_header = REQUIRED_TABLES[HEADINGS[5]][0]
    req_rows = extract_table(by_section[HEADINGS[3]], req_header) or []
    deliverable_rows = extract_table(by_section[HEADINGS[5]], deliverable_header) or []
    outcome_rows = extract_table(by_section[HEADINGS[2]], REQUIRED_TABLES[HEADINGS[2]][0]) or []
    risk_rows = extract_table(by_section[HEADINGS[5]], REQUIRED_TABLES[HEADINGS[5]][1]) or []
    outcome_ids = [row[0] for row in outcome_rows if len(row) == 5 and OUT_RE.fullmatch(row[0])]
    req_ids = id_column(req_rows, r"REQ-[A-Z0-9][A-Z0-9._-]*")
    deliverable_ids = id_column(deliverable_rows, r"DEL-[A-Z0-9][A-Z0-9._-]*")
    if not outcome_ids:
        errors.append("acceptance outcome table has no OUT-* rows")
    if not req_ids:
        errors.append("requirement coverage map has no REQ-* rows")
    if not deliverable_ids:
        errors.append("deliverable model has no DEL-* rows")
    if duplicates(req_ids):
        errors.append(f"duplicate requirement IDs: {', '.join(duplicates(req_ids))}")
    if duplicates(deliverable_ids):
        errors.append(f"duplicate deliverable IDs: {', '.join(duplicates(deliverable_ids))}")
    if duplicates(outcome_ids):
        errors.append(f"duplicate outcome IDs: {', '.join(duplicates(outcome_ids))}")
    for row in outcome_rows:
        if len(row) == 5 and row[0] != "N/A" and not OUT_RE.fullmatch(row[0]):
            errors.append(f"acceptance outcome table has invalid Outcome ID {row[0]!r}")
    boundary_rows = extract_table(by_section[HEADINGS[2]], REQUIRED_TABLES[HEADINGS[2]][1]) or []
    for row in boundary_rows:
        if len(row) == 5 and row[0] != "N/A" and not re.fullmatch(r"BOUND-[A-Z0-9][A-Z0-9._-]*", row[0]):
            errors.append(f"boundary table has invalid Boundary ID {row[0]!r}")
    for row in req_rows:
        if len(row) == len(req_header) and row[0] != "N/A" and not REQ_RE.fullmatch(row[0]):
            errors.append(f"requirement coverage map has invalid Requirement ID {row[0]!r}")
    for row in deliverable_rows:
        if len(row) == len(deliverable_header) and row[0] != "N/A" and not DEL_RE.fullmatch(row[0]):
            errors.append(f"deliverable model has invalid Deliverable ID {row[0]!r}")
    for row in outcome_rows:
        if len(row) == 5 and row[0] != "N/A" and any(invalid_hard_value(value) for value in row):
            errors.append(f"outcome {row[0]} has an empty or bare field")
        if len(row) == 5 and row[0] != "N/A" and normalize(row[4]).upper() != "COVERED":
            errors.append(f"outcome {row[0]} final status must be COVERED")
        if len(row) == 5 and row[0] != "N/A" and invalid_obligation_value(row[2]):
            errors.append(f"outcome {row[0]} Acceptance method uses waiver language")
        if len(row) == 5 and row[0] != "N/A" and invalid_obligation_value(row[1]):
            errors.append(f"outcome {row[0]} Required behavior uses omission/waiver language")
    for row in req_rows:
        if len(row) == len(req_header) and row[0] != "N/A" and any(invalid_hard_value(value) for value in row):
            errors.append(f"requirement {row[0]} has an empty or bare field")
        if len(row) == len(req_header) and row[0] != "N/A" and normalize(row[6]).upper() != "COVERED":
            errors.append(f"requirement {row[0]} final status must be COVERED")
        if len(row) == len(req_header) and row[0] != "N/A" and invalid_obligation_value(row[4]):
            errors.append(f"requirement {row[0]} Verification uses waiver language")
        if len(row) == len(req_header) and row[0] != "N/A" and row[3] not in mapping_roles:
            errors.append(f"requirement {row[0]} Implementation owner must be a mapped workflow role")
    known_deliverables = set(deliverable_ids)
    known_requirements = set(req_ids)
    for row in req_rows:
        if len(row) == len(req_header) and row[0].startswith("REQ-") and row[2] not in known_deliverables:
            errors.append(f"{row[0]} references unknown deliverable {row[2]}")
    requirements_by_deliverable: dict[str, set[str]] = {deliverable_id: set() for deliverable_id in deliverable_ids}
    for row in req_rows:
        if len(row) == len(req_header) and row[0] in known_requirements and row[2] in known_deliverables:
            requirements_by_deliverable[row[2]].add(row[0])
    for row in deliverable_rows:
        if len(row) != len(deliverable_header) or row[0] not in known_deliverables:
            continue
        if any(invalid_hard_value(value) for value in row):
            errors.append(f"deliverable {row[0]} has an empty or bare field")
        if invalid_obligation_value(row[1]):
            errors.append(f"deliverable {row[0]} Behavioral output uses omission/waiver language")
        listed_requirements = set(REQ_RE.findall(row[2]))
        if listed_requirements != requirements_by_deliverable[row[0]]:
            errors.append(
                f"deliverable {row[0]} Requirement IDs must exactly match its requirement-map rows"
            )
        unknown_dependencies = sorted(set(DEL_RE.findall(row[3])) - known_deliverables)
        if unknown_dependencies:
            errors.append(f"deliverable {row[0]} has unknown dependencies: {', '.join(unknown_dependencies)}")
    risk_ids = [row[0] for row in risk_rows if len(row) == 8 and DEL_RE.fullmatch(row[0])]
    for row in risk_rows:
        if len(row) == 8 and row[0] != "N/A" and not DEL_RE.fullmatch(row[0]):
            errors.append(f"deliverable risk/cost table has invalid Deliverable ID {row[0]!r}")
    if Counter(risk_ids) != Counter(deliverable_ids):
        errors.append("deliverable risk/cost rows must cover every DEL-* exactly once")
    for row in risk_rows:
        if len(row) == 8 and row[0] != "N/A" and any(invalid_hard_value(value) for value in row):
            errors.append(f"deliverable risk row {row[0]} has an empty or bare field")

    covered_requirements: set[str] = set()
    covered_deliverables: set[str] = set()
    for filename, text in step_texts.items():
        contract_rows = extract_table(text, ("Field", "Value")) or []
        contract = {row[0]: row[1] for row in contract_rows if len(row) == 2}
        coverage = contract.get("Deliverable and requirement coverage", "")
        step_requirements = set(REQ_RE.findall(coverage))
        step_deliverables = set(DEL_RE.findall(coverage))
        unknown_requirements = sorted(step_requirements - known_requirements)
        unknown_step_deliverables = sorted(step_deliverables - known_deliverables)
        if unknown_requirements:
            errors.append(f"{filename} covers unknown requirements: {', '.join(unknown_requirements)}")
        if unknown_step_deliverables:
            errors.append(f"{filename} covers unknown deliverables: {', '.join(unknown_step_deliverables)}")
        covered_requirements.update(step_requirements)
        covered_deliverables.update(step_deliverables)
    missing_requirement_coverage = sorted(known_requirements - covered_requirements)
    missing_deliverable_coverage = sorted(known_deliverables - covered_deliverables)
    if missing_requirement_coverage:
        errors.append(f"requirements are not covered by any STEP-* contract: {', '.join(missing_requirement_coverage)}")
    if missing_deliverable_coverage:
        errors.append(f"deliverables are not covered by any STEP-* contract: {', '.join(missing_deliverable_coverage)}")

    capability_rows = extract_table(by_section[HEADINGS[4]], REQUIRED_TABLES[HEADINGS[4]][0]) or []
    m01_instances = {instance_id for instance_id, module_type in instance_types.items() if module_type == "M01"}
    for row in capability_rows:
        if len(row) == 7 and row[0] != "N/A" and row[1] not in ALLOWED_CAPABILITY_STATES:
            errors.append(f"capability {row[0]!r} has invalid state {row[1]!r}")
        if len(row) == 7 and row[0] != "N/A" and any(invalid_hard_value(value) for value in row):
            errors.append(f"capability {row[0]!r} has an N/A or placeholder in a mandatory truth field")
        if len(row) == 7 and row[0] != "N/A" and row[1] == "UNAVAILABLE":
            referenced_recovery = set(MI_RE.findall(row[6])) & m01_instances
            if not m01_instances or not referenced_recovery:
                errors.append(
                    f"unavailable capability {row[0]!r} requires a selected M01 recovery instance "
                    "and a fallback that explicitly names that MI-* instance"
                )

    selected_ids = set(instance_types)
    for header in REQUIRED_TABLES[HEADINGS[8]]:
        rows = extract_table(by_section[HEADINGS[8]], header) or []
        for row in rows:
            for instance_id in MI_RE.findall(" ".join(row)):
                if instance_id not in selected_ids:
                    errors.append(f"Section 8 references undeclared module instance {instance_id}")
    return errors


def validate_member_lane_and_handoff_manifest(
    by_section: dict[str, str],
    joined_instances: str,
    instance_types: dict[str, str],
    mapping_roles: set[str],
) -> list[str]:
    errors: list[str] = []
    role_rows = extract_table(by_section[HEADINGS[7]], ROLE_TABLE) or []
    role_parent = {
        row[0]: normalize(row[2]) for row in role_rows
        if len(row) == len(ROLE_TABLE) and normalize(row[1]).upper() in {"WORKER", "LANE_SUB_ORCHESTRATOR"}
    }
    member_contracts: list[tuple[str, str, str, str, str, str, str]] = []
    instance_matches = list(INSTANCE_RE.finditer(joined_instances))
    for index, match in enumerate(instance_matches):
        instance_id = match.group(1)
        block_end = instance_matches[index + 1].start() if index + 1 < len(instance_matches) else len(joined_instances)
        block = joined_instances[match.end():block_end]
        for card_kind, card_id, card_body in task_card_blocks(block):
            if card_kind != "Member":
                continue
            rows = extract_table(card_body, ("Field", "Value")) or []
            values = {row[0]: row[1] for row in rows if len(row) == 2}
            role = values.get("workflow_role", "")
            lane_ids = sorted(set(LANE_RE.findall(" ".join(values.values()))))
            completion = values.get("completion_review_owner_and_handoff", "")
            handoff_ids = sorted(set(HANDOFF_RE.findall(completion)))
            runtime_text = " ".join(values.values())
            process_ids = sorted(set(PROCESS_RE.findall(runtime_text)))
            invocation_ids = sorted(set(INVOCATION_RE.findall(runtime_text)))
            if len(lane_ids) != 1:
                errors.append(f"{instance_id} {card_id} must name exactly one concrete LANE-* ID")
            if len(handoff_ids) != 1:
                errors.append(
                    f"{instance_id} {card_id} completion_review_owner_and_handoff must name exactly one HANDOFF-* ID"
                )
            if len(process_ids) != 1:
                errors.append(f"{instance_id} {card_id} must name exactly one launch-time PROCESS-* ID")
            if len(invocation_ids) != 1:
                errors.append(f"{instance_id} {card_id} must name exactly one preassigned INVOCATION-* ID")
            if len(lane_ids) == len(handoff_ids) == len(process_ids) == len(invocation_ids) == 1:
                member_contracts.append(
                    (card_id, instance_id, role, lane_ids[0], handoff_ids[0], process_ids[0], invocation_ids[0])
                )

    lane_header = REQUIRED_TABLES[HEADINGS[10]][0]
    lane_rows = [
        row for row in (extract_table(by_section[HEADINGS[10]], lane_header) or [])
        if len(row) == len(lane_header) and row[0] != "N/A"
    ]
    lane_ids = [row[0] for row in lane_rows]
    if duplicates(lane_ids):
        errors.append(f"Section 10 contains duplicate lane IDs: {', '.join(duplicates(lane_ids))}")
    lane_by_id = {row[0]: row for row in lane_rows}
    for row in lane_rows:
        if not LANE_RE.fullmatch(row[0]):
            errors.append(f"Section 10 has invalid lane ID {row[0]!r}")
        if row[1] not in instance_types:
            errors.append(f"Section 10 lane {row[0]} references undeclared module instance {row[1]!r}")
        if row[2] not in mapping_roles:
            errors.append(f"Section 10 lane {row[0]} references unmapped role {row[2]!r}")

    handoff_header = REQUIRED_TABLES[HEADINGS[10]][3]
    handoff_rows = [
        row for row in (extract_table(by_section[HEADINGS[10]], handoff_header) or [])
        if len(row) == len(handoff_header) and row[0] != "N/A"
    ]
    manifest_ids = [row[0] for row in handoff_rows]
    if duplicates(manifest_ids):
        errors.append(f"Section 10 contains duplicate result/handoff IDs: {', '.join(duplicates(manifest_ids))}")
    handoff_by_id = {row[0]: row for row in handoff_rows if HANDOFF_RE.fullmatch(row[0])}
    for row in handoff_rows:
        if not (HANDOFF_RE.fullmatch(row[0]) or RESULT_RE.fullmatch(row[0])):
            errors.append(f"Section 10 has invalid result/handoff ID {row[0]!r}")
        if row[1] not in mapping_roles or row[2] not in mapping_roles:
            errors.append(f"Section 10 result/handoff {row[0]} must name mapped producer and consumer roles")

    expected_lanes = [contract[3] for contract in member_contracts]
    expected_handoffs = [contract[4] for contract in member_contracts]
    expected_processes = [contract[5] for contract in member_contracts]
    expected_invocations = [contract[6] for contract in member_contracts]
    if duplicates(expected_lanes):
        errors.append(f"member cards reuse lane IDs: {', '.join(duplicates(expected_lanes))}")
    if duplicates(expected_handoffs):
        errors.append(f"member cards reuse handoff IDs: {', '.join(duplicates(expected_handoffs))}")
    if duplicates(expected_processes):
        errors.append(f"member cards reuse process IDs: {', '.join(duplicates(expected_processes))}")
    if duplicates(expected_invocations):
        errors.append(f"member cards reuse invocation IDs: {', '.join(duplicates(expected_invocations))}")
    for card_id, instance_id, role, lane_id, handoff_id, process_id, invocation_id in member_contracts:
        lane_row = lane_by_id.get(lane_id)
        if lane_row is None:
            errors.append(f"{instance_id} {card_id} lane {lane_id} has no reciprocal Section 10 row")
        elif lane_row[1] != instance_id or lane_row[2] != role:
            errors.append(f"{instance_id} {card_id} lane {lane_id} disagrees on module instance or role")
        elif role_parent.get(role) and lane_row[5] != role_parent[role]:
            errors.append(
                f"{instance_id} {card_id} lane {lane_id} Consumer must be its owning orchestration role "
                f"{role_parent[role]!r}"
            )
        handoff_row = handoff_by_id.get(handoff_id)
        if handoff_row is None:
            errors.append(f"{instance_id} {card_id} handoff {handoff_id} has no reciprocal Section 10 row")
        elif handoff_row[1] != role:
            errors.append(f"{instance_id} {card_id} handoff {handoff_id} disagrees on producer role")
        elif role_parent.get(role) and handoff_row[2] != role_parent[role]:
            errors.append(
                f"{instance_id} {card_id} handoff {handoff_id} Consumer must be its owning orchestration role "
                f"{role_parent[role]!r}"
            )
        elif process_id not in handoff_row[4] or invocation_id not in handoff_row[4]:
            errors.append(
                f"{instance_id} {card_id} handoff {handoff_id} Correlation needed must name "
                f"{process_id} and {invocation_id}"
            )
    return errors


def split_role_keys(value: str) -> list[str]:
    if normalize(value).upper() == "N/A":
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def validate_plan_contract(
    body: str,
    mapping_name: str,
    mapping_path: Path | None = None,
    plan_path: Path | None = None,
) -> tuple[list[str], str]:
    errors: list[str] = []
    contract_rows = extract_table(body, ("Field", "Value")) or []
    valid_contract_rows = [row for row in contract_rows if len(row) == 2]
    if len(valid_contract_rows) != len(contract_rows):
        errors.append("Section 0 plan-contract table contains a malformed extra row")
    if [row[0] for row in valid_contract_rows] != PLAN_CONTRACT_FIELDS:
        errors.append("Section 0 must contain the exact plan-contract fields once and in order")
    contract = {row[0]: normalize(row[1]) for row in valid_contract_rows}
    for field in PLAN_CONTRACT_FIELDS:
        if invalid_hard_value(contract.get(field, "")):
            errors.append(f"Section 0 plan-contract field {field} is empty or a bare placeholder")
    if contract.get("Status") != "VALIDATED":
        errors.append("Section 0 final Status must be exactly VALIDATED")
    if contract.get("Verification protocol") != "CHECKPOINTED_VERIFICATION_V1":
        errors.append("Section 0 Verification protocol must be exactly CHECKPOINTED_VERIFICATION_V1")
    topology = contract.get("Orchestration topology", "")
    if topology not in {"ROOT_DIRECT_WORKERS", "ROOT_WITH_LANE_SUB_ORCHESTRATORS"}:
        errors.append(
            "Multi-agent topology must declare ROOT_DIRECT_WORKERS or "
            "ROOT_WITH_LANE_SUB_ORCHESTRATORS"
        )

    dependency_rows = extract_table(body, PACKAGE_DEPENDENCY_TABLE) or []
    valid_dependencies = [row for row in dependency_rows if len(row) == len(PACKAGE_DEPENDENCY_TABLE)]
    if len(valid_dependencies) != len(dependency_rows):
        errors.append("Section 0 package-dependency table contains a malformed extra row")
    if [row[0] for row in valid_dependencies] != PACKAGE_DEPENDENCIES:
        errors.append("Section 0 package dependencies must list the five authoritative artifacts once and in order")
    else:
        expected_paths = {
            "Global rules": "global-rules.md",
            "Gated steps": "steps/",
            "M-module library": "modules/M01.md through modules/M10.md",
            "Validation": "validation.md",
        }
        for row in valid_dependencies:
            if row[0] == "Agent mapping":
                declared_path = Path(normalize(row[1]))
                if mapping_path is not None and plan_path is not None:
                    declared_target = declared_path if declared_path.is_absolute() else plan_path / declared_path
                    if declared_target.resolve() != mapping_path.resolve():
                        errors.append("Section 0 Agent mapping path does not resolve to the canonical --mapping path")
                elif declared_path.name != mapping_name:
                    errors.append(f"Section 0 Agent mapping path must name {mapping_name!r}")
            elif row[0] != "Agent mapping" and normalize(row[1]) != expected_paths[row[0]]:
                errors.append(f"Section 0 dependency {row[0]} must use authoritative path {expected_paths[row[0]]!r}")
            if any(invalid_hard_value(value) for value in row[2:]):
                errors.append(f"Section 0 dependency {row[0]} has an empty or bare ownership/edit-boundary value")
    return errors, topology


def validate_roles(
    body: str,
    mapping_roles: set[str],
    mapping_name: str,
    text: str,
    topology: str,
) -> list[str]:
    errors: list[str] = []
    role_rows = extract_table(body, ROLE_TABLE) or []
    valid_role_rows = [row for row in role_rows if len(row) == len(ROLE_TABLE) and row[0] != "N/A"]
    if len(valid_role_rows) != len(role_rows):
        errors.append("role table contains an N/A or malformed bypass row")
    plan_roles = [row[0] for row in valid_role_rows]
    if not plan_roles:
        errors.append("role table contains no workflow roles")
    if duplicates(plan_roles):
        errors.append(f"role table contains duplicate roles: {', '.join(duplicates(plan_roles))}")
    if set(plan_roles) != mapping_roles:
        missing = sorted(set(plan_roles) - mapping_roles)
        extra = sorted(mapping_roles - set(plan_roles))
        if missing:
            errors.append(f"mapping is missing plan roles: {', '.join(missing)}")
        if extra:
            errors.append(f"mapping has roles absent from the plan: {', '.join(extra)}")
    row_by_role = {row[0]: row for row in valid_role_rows}
    root_roles = [row[0] for row in valid_role_rows if normalize(row[1]).upper() == "ROOT"]
    if len(root_roles) != 1:
        errors.append("authority graph must declare exactly one ROOT role")
        root_role = ""
    else:
        root_role = root_roles[0]

    allowed_classes = {"ROOT", "LANE_SUB_ORCHESTRATOR", "WORKER"}
    sub_orchestrators: list[str] = []
    for row in valid_role_rows:
        role, authority_class, reports_to, directs = row[0], normalize(row[1]).upper(), normalize(row[2]), row[3]
        for field_index in (0, 1, 4, 6, 7, 8, 9, 10):
            if invalid_hard_value(row[field_index]):
                errors.append(f"role {role!r} has a bare or unjustified {ROLE_TABLE[field_index]} field")
            if VAGUE_EXECUTION_RE.search(row[field_index]):
                errors.append(f"role {role!r} has vague language in {ROLE_TABLE[field_index]}")
        if authority_class not in allowed_classes:
            errors.append(f"role {role} has invalid authority class {authority_class!r}")
        parent = "" if reports_to.upper() == "N/A" else reports_to
        children = split_role_keys(directs)
        if authority_class == "ROOT":
            if parent:
                errors.append(f"ROOT role {role} must report to N/A")
        elif authority_class == "LANE_SUB_ORCHESTRATOR":
            sub_orchestrators.append(role)
            if parent != root_role:
                errors.append(f"lane sub-orchestrator {role} must report directly to ROOT role {root_role!r}")
            if not children:
                errors.append(f"lane sub-orchestrator {role} must direct at least one worker role")
            lane_contract = " ".join(row[4:11]).lower()
            for term in (
                "payoff", "outcome", "input", "protected scope", "mutable resource",
                "worker", "local decision", "terminal handoff", "return condition",
            ):
                if term not in lane_contract:
                    errors.append(f"lane sub-orchestrator {role} contract must state {term!r}")
        elif authority_class == "WORKER":
            if parent not in row_by_role:
                errors.append(f"worker role {role} reports to unknown role {parent!r}")
            elif normalize(row_by_role[parent][1]).upper() not in {"ROOT", "LANE_SUB_ORCHESTRATOR"}:
                errors.append(f"worker role {role} must report to ROOT or a lane sub-orchestrator")
            if children:
                errors.append(f"worker role {role} may not direct another role")
        for child in children:
            if child not in row_by_role:
                errors.append(f"role {role} directs unknown role {child!r}")
            elif normalize(row_by_role[child][2]) != role:
                errors.append(f"role {role} directs {child}, but {child} does not report to {role}")
        pool_match = re.search(r"\b(\d+)\b", row[5])
        if pool_match is None or int(pool_match.group(1)) < 1:
            errors.append(f"role {row[0]} has no positive pool capacity")
    for role, row in row_by_role.items():
        parent = "" if normalize(row[2]).upper() == "N/A" else normalize(row[2])
        if parent and (parent not in row_by_role or role not in split_role_keys(row_by_role[parent][3])):
            errors.append(f"role {role} reports to {parent!r}, but that parent does not direct it")
    expected_topology = "ROOT_WITH_LANE_SUB_ORCHESTRATORS" if sub_orchestrators else "ROOT_DIRECT_WORKERS"
    if topology and topology != expected_topology:
        errors.append(
            f"Section 0 topology {topology!r} does not match the structured authority graph "
            f"({expected_topology})"
        )
    if text.lower().count(mapping_name.lower()) != 1:
        errors.append(f"plan must mention mapping filename {mapping_name!r} exactly once")
    return errors


def validate_root_acceptance_ownership(root_sections: dict[str, str]) -> list[str]:
    errors: list[str] = []
    role_rows = extract_table(root_sections[HEADINGS[7]], ROLE_TABLE) or []
    root_roles = [row[0] for row in role_rows if len(row) == len(ROLE_TABLE) and normalize(row[1]).upper() == "ROOT"]
    if len(root_roles) != 1:
        return errors
    root_role = root_roles[0]
    allowed_local_acceptors = {
        row[0] for row in role_rows
        if len(row) == len(ROLE_TABLE) and normalize(row[1]).upper() == "LANE_SUB_ORCHESTRATOR"
    }
    contract_rows = extract_table(root_sections[HEADINGS[0]], ("Field", "Value")) or []
    contract = {row[0]: normalize(row[1]) for row in contract_rows if len(row) == 2}
    if contract.get("Decision owner") != root_role:
        errors.append(f"Section 0 Decision owner must be the ROOT role {root_role!r}")
    outcome_rows = extract_table(root_sections[HEADINGS[2]], REQUIRED_TABLES[HEADINGS[2]][0]) or []
    for row in outcome_rows:
        if len(row) == 5 and row[0] != "N/A" and row[3] != root_role:
            errors.append(f"outcome {row[0]} Decision owner must be the ROOT role {root_role!r}")
    requirement_rows = extract_table(root_sections[HEADINGS[3]], REQUIRED_TABLES[HEADINGS[3]][0]) or []
    allowed_requirement_acceptors = {root_role} | allowed_local_acceptors
    role_by_name = {row[0]: row for row in role_rows if len(row) == len(ROLE_TABLE)}
    for row in requirement_rows:
        if len(row) == 7 and row[0] != "N/A" and row[5] not in allowed_requirement_acceptors:
            errors.append(
                f"requirement {row[0]} Acceptance owner must be ROOT or an authorized lane sub-orchestrator"
            )
        if len(row) == 7 and row[0] != "N/A" and row[5] in allowed_local_acceptors:
            lane_scope = " ".join(role_by_name[row[5]][4:])
            if row[0] not in set(REQ_RE.findall(lane_scope)):
                errors.append(
                    f"lane sub-orchestrator {row[5]} may accept {row[0]} only when its structured lane contract "
                    "explicitly scopes that exact requirement ID"
                )
    return errors


def validate_card_authority_and_graph_references(
    by_section: dict[str, str],
    step_texts: dict[str, str],
    joined_instances: str,
) -> list[str]:
    errors: list[str] = []
    role_rows = extract_table(by_section[HEADINGS[7]], ROLE_TABLE) or []
    role_classes = {
        row[0]: normalize(row[1]).upper() for row in role_rows if len(row) == len(ROLE_TABLE)
    }
    known_deliverables = set(id_column(
        extract_table(by_section[HEADINGS[5]], REQUIRED_TABLES[HEADINGS[5]][0]) or [],
        r"DEL-[A-Z0-9][A-Z0-9._-]*",
    ))
    known_gates: set[str] = set()
    known_loops: set[str] = set()
    for text in step_texts.values():
        for row in extract_table(text, STEP_GATE_TABLE) or []:
            if len(row) != len(STEP_GATE_TABLE):
                continue
            known_gates.update(re.findall(r"\bGATE-[A-Z0-9][A-Z0-9._-]*\b", row[0]))
            known_loops.update(re.findall(r"\bLOOP-[A-Z0-9][A-Z0-9._-]*\b", row[0]))
    for card_kind, card_id, card_body in task_card_blocks(joined_instances):
        rows = extract_table(card_body, ("Field", "Value")) or []
        values = {row[0]: row[1] for row in rows if len(row) == 2}
        role = values.get("workflow_role", "")
        authority_class = role_classes.get(role, "")
        if card_kind == "Governing" and authority_class not in {"ROOT", "LANE_SUB_ORCHESTRATOR"}:
            errors.append(
                f"governing task card {card_id} must use ROOT or an authorized LANE_SUB_ORCHESTRATOR role"
            )
        if card_kind == "Member" and authority_class != "WORKER":
            errors.append(f"member task card {card_id} must use a terminal WORKER role")
        identity = values.get(TASK_FIELDS[0], "")
        assignments = dict(re.findall(r"\b([a-z_]+)=([A-Za-z0-9][A-Za-z0-9._-]*)\b", identity))
        for key, known in (
            ("deliverable_id", known_deliverables),
            ("gate_id", known_gates),
            ("loop_id", known_loops),
        ):
            if assignments.get(key) not in known:
                errors.append(f"task card {card_id} references undeclared {key} {assignments.get(key)!r}")
    return errors


def validate_rule_and_check_matrices(by_section: dict[str, str]) -> list[str]:
    errors: list[str] = []
    rule_rows = extract_table(by_section[HEADINGS[15]], REQUIRED_TABLES[HEADINGS[15]][0]) or []
    rule_ids = [row[0] for row in rule_rows if len(row) == 3]
    if rule_ids != RULE_IDS:
        errors.append("Section 15 must map R1-R30 then S1-S17 exactly once and in order")
    for row in rule_rows:
        if len(row) != 3:
            continue
        if invalid_hard_value(row[1]):
            errors.append(f"{row[0]} has no concrete plan location")
        elif not re.search(r"(?:plan-workflow|global-rules|validation)\.md|(?:steps/STEP-[^\s|]+|modules/M\d{2})\.md", row[1]):
            errors.append(f"{row[0]} plan location must name a concrete owning package artifact")
        if invalid_hard_value(row[2]):
            errors.append(f"{row[0]} must name concrete applied behavior; normative rules may not use N/A")

    check_rows = extract_table(by_section[HEADINGS[16]], REQUIRED_TABLES[HEADINGS[16]][0]) or []
    check_ids = [row[0] for row in check_rows if len(row) == 3]
    if check_ids != CHECK_IDS:
        errors.append("Section 16 must contain V01-V30 exactly once and in order")
    for row in check_rows:
        if len(row) == 3 and row[1] != "PASS":
            errors.append(f"{row[0]} is not PASS")
        if len(row) == 3 and not row[2].strip():
            errors.append(f"{row[0]} has no basis")
        if len(row) == 3 and (invalid_hard_value(row[2]) or len(normalize(row[2])) < 24):
            errors.append(f"{row[0]} has no substantive artifact-specific validation basis")
        if len(row) == 3 and not re.search(
            r"(?:plan-workflow|global-rules|validation)\.md|(?:steps/STEP-[^\s|]+|modules/M\d{2})\.md", row[2]
        ):
            errors.append(f"{row[0]} validation basis must name a concrete package artifact")
    marker_count = by_section[HEADINGS[16]].count("PLAN_STRUCTURE=VALID")
    if marker_count != 1:
        errors.append(f"expected one PLAN_STRUCTURE=VALID marker, found {marker_count}")
    if "PLAN_STRUCTURE=INVALID" in by_section[HEADINGS[16]]:
        errors.append("Section 16 still contains PLAN_STRUCTURE=INVALID")
    return errors


def validate_test_scope_audit(body: str, step_texts: dict[str, str]) -> list[str]:
    """Check declared audit coverage, not reviewer authenticity or semantic sufficiency."""
    errors: list[str] = []
    absent_markers = {"PENDING", "NONE", "UNKNOWN", "UNAVAILABLE", "MISSING", "NOT REVIEWED", "NOT RUN"}

    def absent_declaration(value: str) -> bool:
        return invalid_hard_value(value) or normalize(value).upper() in absent_markers

    meta_rows = extract_table(body, AUDIT_META_TABLE) or []
    if [row[0] for row in meta_rows if len(row) == 2] != list(AUDIT_FIELDS):
        errors.append("test-scope audit must declare every audit field once in order")
    values = {row[0]: row[1] for row in meta_rows if len(row) == 2}
    for field in AUDIT_FIELDS:
        if absent_declaration(values.get(field, "")):
            errors.append(f"test-scope audit lacks concrete {field}")
    group_rows = extract_table(body, AUDIT_GROUP_TABLE) or []
    if [row[0] for row in group_rows if len(row) == len(AUDIT_GROUP_TABLE)] != list(AUDIT_GROUPS):
        errors.append("plan review requires every independent group exactly once in order")
    reviewer_ids: list[str] = []
    writer_id = normalize(values.get("Plan writer", "")).casefold()
    for row in group_rows:
        if len(row) != len(AUDIT_GROUP_TABLE):
            errors.append("plan review group row has the wrong number of columns")
            continue
        group, reviewer, revision, evidence, findings, verdict = row
        for field, value in zip(AUDIT_GROUP_TABLE, row):
            if absent_declaration(value):
                errors.append(f"plan review {group} lacks concrete {field}")
        reviewer_id = normalize(reviewer).casefold()
        reviewer_ids.append(reviewer_id)
        if reviewer_id == writer_id:
            errors.append(f"plan review {group} must be independent of the writer")
        if revision != values.get("Plan revision"):
            errors.append(f"plan review {group} approval is not for the final Plan revision")
        if verdict != "PASS":
            errors.append(f"plan review {group} verdict is not PASS")
    if duplicates(reviewer_ids):
        errors.append("plan review groups require four distinct independent reviewer identities")
    if values.get("Plan review verdict") != "PASS":
        errors.append("plan-conformance review verdict is not PASS")
    if values.get("Audit status") != "ACCEPTED":
        errors.append("test-scope audit is not ACCEPTED")

    scope_rows = extract_table(body, AUDIT_SCOPE_TABLE) or []
    ids = [row[0] for row in scope_rows if len(row) == len(AUDIT_SCOPE_TABLE)]
    if duplicates(ids) or set(ids) != {Path(name).stem for name in step_texts}:
        errors.append("test-scope audit must cover every STEP exactly once without unknown steps")
    for row in scope_rows:
        if len(row) != len(AUDIT_SCOPE_TABLE):
            errors.append("test-scope audit row has the wrong number of columns")
            continue
        for field, value in zip(AUDIT_SCOPE_TABLE, row):
            if absent_declaration(value):
                errors.append(f"test-scope audit {row[0]} lacks concrete {field}")
            elif field in ACCEPTANCE_ASSESSMENT_FIELDS and normalize(value).upper() in {
                "YES", "NO", "PASS", "ACCEPTED", "APPROVED", "SUFFICIENT", "COMPLETE",
                "BLOCK", "FAIL", "FAILED", "REJECTED",
            }:
                errors.append(f"test-scope audit {row[0]} requires reasoning or a reviewed reference for {field}")
        if row[-1] != "ACCEPTED":
            errors.append(f"test-scope audit {row[0]} has an unresolved final status")
    return errors


def validate_module_policy_and_role_references(
    global_body: str,
    step_texts: dict[str, str],
    module_texts: dict[str, str],
    mapping_roles: set[str],
) -> list[str]:
    errors: list[str] = []
    known_refs = {heading.split()[1] for heading in POLICY_HEADINGS}
    exception_rows = extract_table(global_body, EXCEPTION_TABLE) or []
    known_refs.update(
        row[0] for row in exception_rows
        if len(row) == len(EXCEPTION_TABLE) and re.fullmatch(r"EXC-[A-Z0-9][A-Z0-9._-]*", row[0])
    )
    reference_pattern = r"\bP\d{2}\b|\bEXC-[A-Z0-9][A-Z0-9._-]*"
    for filename, text in {**step_texts, **module_texts}.items():
        unknown = sorted(set(re.findall(reference_pattern, text)) - known_refs)
        if unknown:
            errors.append(f"{filename} cites unknown global policy/exception IDs: {', '.join(unknown)}")
    for filename, text in module_texts.items():
        action_rows = extract_table(text, MODULE_ACTION_TABLE) or []
        for row in action_rows:
            if len(row) == len(MODULE_ACTION_TABLE) and row[4] not in mapping_roles:
                errors.append(f"{filename} action {row[1]} uses decision owner absent from mapping: {row[4]}")
    return errors


def validate_unbounded_agent_sessions(text: str, mapping_roles: set[str]) -> list[str]:
    errors: list[str] = []
    named_roles = "|".join(
        sorted((re.escape(role) for role in mapping_roles if role.strip()), key=len, reverse=True)
    )
    role_prefix = (
        r"agent(?:\s+and\s+subagent)?|subagent|root|lane\s+sub-orchestrator|"
        r"workers?|reviewers?|testers?|observers?|auditors?|implementers?|planners?|researchers?"
    )
    if named_roles:
        role_prefix += f"|{named_roles}"
    session_pattern = re.compile(
        rf"\b(?:{role_prefix})\s+"
        r"(?:launch(?:es)?|session(?:s)?|invocation(?:s)?|launch wrappers?)\b|"
        r"\bcodex exec\b|\bclaude -p\b",
        re.IGNORECASE,
    )
    finite_bound_pattern = re.compile(
        r"\b(?:timeout|deadline|maximum\s+(?:lifetime|runtime)|"
        r"(?:time[- ]?)?bounded\s+(?:to|at)\s+\d+\s*(?:seconds?|minutes?|hours?)|"
        r"max(?:imum)?\s+of\s+\d+\s*(?:seconds?|minutes?|hours?)|"
        r"(?:must|shall|required\s+to)\s+(?:finish|terminate|end|complete|stop)\s+within|"
        r"within\s+\d+\s*(?:seconds?|minutes?|hours?))\b",
        re.IGNORECASE,
    )
    exemption_pattern = re.compile(
        r"\b(?:unbounded|exempt|no\s+(?:timeout|deadline|maximum)|not\s+(?:time-?)?bounded|"
        r"not\s+subject|outside.{0,30}(?:bound|supervis)|never.{0,20}(?:bound|wrap)|"
        r"must\s+not.{0,20}(?:bound|wrap|timeout))\b",
        re.IGNORECASE,
    )
    clause_split_pattern = re.compile(
        r"(?<=[.;!?])\s+|,\s*(?=(?:but|however|except|whereas)\b)|"
        r"\b(?:but|however|except|whereas)\b",
        re.IGNORECASE,
    )
    for line_number, line in enumerate(text.splitlines(), 1):
        for clause in clause_split_pattern.split(line):
            if (
                session_pattern.search(clause)
                and finite_bound_pattern.search(clause)
                and not exemption_pattern.search(clause)
            ):
                errors.append(
                    f"line {line_number} assigns a finite timeout/deadline to an agent session or launch; "
                    "agent and subagent sessions must remain unbounded"
                )
                break
    return errors


def split_owned_sections(text: str, headings: list[str], label: str) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    found = re.findall(r"(?m)^##\s+.+?$", text)
    if found != headings:
        errors.append(f"{label} does not contain its exact H2 headings once and in order")
        return {}, errors
    result: dict[str, str] = {}
    for index, heading in enumerate(headings):
        start = text.index(heading) + len(heading)
        end = text.index(headings[index + 1], start) if index + 1 < len(headings) else len(text)
        result[heading] = text[start:end]
    return result, errors


def validate_module_files(module_texts: dict[str, str]) -> tuple[list[str], dict[str, str], str]:
    errors: list[str] = []
    instance_types: dict[str, str] = {}
    instance_bodies: list[str] = []
    expected_files = {f"{module_id}.md" for module_id in MODULE_IDS}
    if set(module_texts) != expected_files:
        missing = sorted(expected_files - set(module_texts))
        extra = sorted(set(module_texts) - expected_files)
        if missing:
            errors.append(f"modules directory is missing: {', '.join(missing)}")
        if extra:
            errors.append(f"modules directory has unexpected files: {', '.join(extra)}")

    for module_id in MODULE_IDS:
        filename = f"{module_id}.md"
        text = module_texts.get(filename, "")
        if not text:
            continue
        titles = re.findall(r"(?m)^#\s+(.+?)\s*$", text)
        if len(titles) != 1 or not titles[0].startswith(f"{module_id} - "):
            errors.append(f"{filename} must have exactly one '# {module_id} - <name>' title")
        owned, heading_errors = split_owned_sections(text, MODULE_HEADINGS, filename)
        errors.extend(heading_errors)
        if heading_errors:
            continue
        if invalid_executable_value(owned[MODULE_HEADINGS[1]]) or len(normalize(owned[MODULE_HEADINGS[1]])) < 24:
            errors.append(f"{filename} must define a concrete stable public interface and compatibility boundary")

        selection_rows = extract_table(owned[MODULE_HEADINGS[0]], MODULE_SELECTION_TABLE) or []
        if table_header_count(text, MODULE_SELECTION_TABLE) != 1:
            errors.append(f"{filename} must contain the module selection table exactly once")
        if len(selection_rows) != 1 or len(selection_rows[0]) != len(MODULE_SELECTION_TABLE):
            errors.append(f"{filename} must contain exactly one valid module selection row")
            continue
        row = selection_rows[0]
        if row[0] != module_id:
            errors.append(f"{filename} selection row declares {row[0]!r}, expected {module_id}")
        decision = row[1].upper()
        declared_ids = MI_RE.findall(row[2])
        if decision not in ALLOWED_MODULE_DECISIONS:
            errors.append(f"{module_id} has invalid decision {row[1]!r}")
        if decision == "SELECTED" and not declared_ids:
            errors.append(f"{module_id} is SELECTED but has no MI-* instance ID")
        if decision == "SELECTED" and not ORDERED_MI_PATH_RE.fullmatch(row[2]):
            errors.append(f"{module_id} SELECTED Instance IDs must be an explicit MI-* list")
        if decision != "SELECTED" and declared_ids:
            errors.append(f"{module_id} is {decision} but declares instance IDs")
        if decision == "OMITTED" and normalize(row[2]).upper() != "N/A":
            errors.append(f"{module_id} OMITTED Instance IDs must be exactly N/A")
        if (
            invalid_required_table_value(row[3])
            or len(normalize(row[3])) < 24
            or VAGUE_EXECUTION_RE.search(row[3])
        ):
            errors.append(f"{module_id} selection has no substantive project-specific decision justification")
        if module_id == "M05" and decision != "SELECTED":
            errors.append("M05 must be SELECTED because every formal package defines DEL/REQ acceptance and a product gate")

        action_rows = extract_table(owned[MODULE_HEADINGS[2]], MODULE_ACTION_TABLE) or []
        if table_header_count(text, MODULE_ACTION_TABLE) != 1:
            errors.append(f"{filename} must contain the module action table exactly once")
        valid_action_rows = [item for item in action_rows if len(item) == len(MODULE_ACTION_TABLE)]
        if len(valid_action_rows) != len(action_rows):
            errors.append(f"{filename} action table contains a malformed extra row")
        action_ids = [item[1] for item in valid_action_rows]
        if action_ids != MODULE_ACTIONS[module_id]:
            errors.append(
                f"{filename} action table must contain {', '.join(MODULE_ACTIONS[module_id])} "
                "exactly once and in order"
            )
        expected_order = [str(index) for index in range(1, len(valid_action_rows) + 1)]
        if [item[0] for item in valid_action_rows] != expected_order:
            errors.append(f"{filename} action-table Order values must be consecutive from 1")
        for item in valid_action_rows:
            if any(invalid_hard_value(value) for value in item[2:]):
                errors.append(f"{filename} action {item[1]} has an empty or bare process/parameter/owner value")

        configured = owned[MODULE_HEADINGS[3]]
        matches = list(INSTANCE_RE.finditer(configured))
        found_ids = [match.group(1) for match in matches]
        all_h3 = re.findall(r"(?m)^###\s+.+?$", configured)
        if len(all_h3) != len(matches):
            errors.append(f"{filename} contains a malformed or non-instance H3 heading")
        if found_ids != declared_ids:
            errors.append(
                f"{filename} declared instance IDs do not exactly match configured instance blocks in order"
            )
        for match in matches:
            instance_id, declared_type = match.group(1), match.group(2)
            if declared_type != module_id:
                errors.append(f"{instance_id} is in {filename} but declares type {declared_type}")
            if instance_id in instance_types:
                errors.append(f"module instance ID is declared more than once: {instance_id}")
            instance_types[instance_id] = module_id
        instance_bodies.append(configured)
        expected_card_tables = len(TASK_CARD_RE.findall(configured))
        if table_header_count(text, ("Field", "Value")) != expected_card_tables:
            errors.append(
                f"{filename} must contain exactly one Field | Value table for each governing/member card"
            )

    joined_instances = "\n\n".join(instance_bodies)
    errors.extend(validate_instances(joined_instances, instance_types))
    return errors, instance_types, joined_instances


def validate_step_files(
    root_sections: dict[str, str],
    step_texts: dict[str, str],
    instance_types: dict[str, str],
    joined_instances: str,
) -> list[str]:
    errors: list[str] = []
    index_body = root_sections[HEADINGS[6]]
    role_rows = extract_table(root_sections[HEADINGS[7]], ROLE_TABLE) or []
    root_roles = [
        row[0] for row in role_rows
        if len(row) == len(ROLE_TABLE) and normalize(row[1]).upper() == "ROOT"
    ]
    root_role = root_roles[0] if len(root_roles) == 1 else ""
    lane_role_rows = {
        row[0]: row for row in role_rows
        if len(row) == len(ROLE_TABLE) and normalize(row[1]).upper() == "LANE_SUB_ORCHESTRATOR"
    }
    allowed_step_acceptors = ({root_role} if root_role else set()) | set(lane_role_rows)
    graph_body = root_sections[HEADINGS[8]]
    edge_rows = extract_table(graph_body, REQUIRED_TABLES[HEADINGS[8]][0]) or []
    edge_ids = [row[0] for row in edge_rows if len(row) == 7]
    invalid_edge_ids = [item for item in edge_ids if not re.fullmatch(r"EDGE-[A-Z0-9][A-Z0-9._-]*", item)]
    if invalid_edge_ids:
        errors.append(f"Section 8 has invalid EDGE-* IDs: {', '.join(invalid_edge_ids)}")
    if duplicates(edge_ids):
        errors.append(f"Section 8 has duplicate edge IDs: {', '.join(duplicates(edge_ids))}")
    known_edge_ids = set(edge_ids)
    step_rows = extract_table(index_body, REQUIRED_TABLES[HEADINGS[6]][0]) or []
    module_rows = extract_table(index_body, REQUIRED_TABLES[HEADINGS[6]][1]) or []
    instance_matches = list(INSTANCE_RE.finditer(joined_instances))
    instance_bodies = {
        match.group(1): joined_instances[match.start():instance_matches[index + 1].start() if index + 1 < len(instance_matches) else len(joined_instances)]
        for index, match in enumerate(instance_matches)
    }

    indexed_steps: dict[str, str] = {}
    indexed_step_rows: dict[str, list[str]] = {}
    for row in step_rows:
        if len(row) != 6 or row[0] == "N/A":
            continue
        step_id, step_file = row[0], row[1]
        if not re.fullmatch(r"STEP-[A-Z0-9][A-Z0-9_-]*", step_id):
            errors.append(f"step index has invalid ID {step_id!r}")
        if step_id in indexed_steps:
            errors.append(f"step index contains duplicate ID {step_id}")
        indexed_steps[step_id] = step_file
        indexed_step_rows[step_id] = row
        if step_file != f"steps/{step_id}.md":
            errors.append(f"{step_id} must use step file steps/{step_id}.md")
        if any(is_bare(value) for value in row):
            errors.append(f"{step_id} index row has an empty or bare field")
        if row[5] not in allowed_step_acceptors:
            errors.append(
                f"{step_id} Acceptance owner must be ROOT or an explicitly authorized lane sub-orchestrator"
            )
    if not indexed_steps:
        errors.append("step index contains no STEP-* rows")

    expected_module_rows = [[module_id, f"modules/{module_id}.md"] for module_id in MODULE_IDS]
    if module_rows != expected_module_rows:
        errors.append("Section 6 module index must list M01.md through M10.md exactly once and in order")

    expected_step_files = {f"{step_id}.md" for step_id in indexed_steps}
    if set(step_texts) != expected_step_files:
        missing = sorted(expected_step_files - set(step_texts))
        extra = sorted(set(step_texts) - expected_step_files)
        if missing:
            errors.append(f"steps directory is missing indexed files: {', '.join(missing)}")
        if extra:
            errors.append(f"steps directory has unindexed files: {', '.join(extra)}")

    consumed_instances: list[str] = []
    gate_owners: dict[str, tuple[str, str]] = {}
    for step_id, indexed_path in indexed_steps.items():
        filename = f"{step_id}.md"
        text = step_texts.get(filename, "")
        if not text:
            continue
        titles = re.findall(r"(?m)^#\s+(.+?)\s*$", text)
        if len(titles) != 1 or not titles[0].startswith(f"{step_id} - "):
            errors.append(f"{filename} must have exactly one '# {step_id} - <name>' title")
        owned, heading_errors = split_owned_sections(text, STEP_HEADINGS, filename)
        errors.extend(heading_errors)
        if heading_errors:
            continue
        for prose_heading in (
            STEP_HEADINGS[1], STEP_HEADINGS[4], STEP_HEADINGS[6], STEP_HEADINGS[7], STEP_HEADINGS[8],
        ):
            if invalid_executable_value(owned[prose_heading]) or len(normalize(owned[prose_heading])) < 24:
                errors.append(f"{filename} {prose_heading} must contain a concrete executable contract")
        successor_edges = set(re.findall(r"\bEDGE-[A-Z0-9][A-Z0-9._-]*\b", owned[STEP_HEADINGS[4]]))
        if not successor_edges:
            errors.append(f"{filename} Public outputs and successors must name at least one EDGE-* route")
        unknown_successor_edges = sorted(successor_edges - known_edge_ids)
        if unknown_successor_edges:
            errors.append(
                f"{filename} Public outputs and successors reference unknown edges: "
                + ", ".join(unknown_successor_edges)
            )

        contract_rows = extract_table(owned[STEP_HEADINGS[0]], ("Field", "Value")) or []
        if table_header_count(text, ("Field", "Value")) != 1:
            errors.append(f"{filename} must contain exactly one step-contract Field | Value table")
        valid_contract_rows = [row for row in contract_rows if len(row) == 2]
        if len(valid_contract_rows) != len(contract_rows):
            errors.append(f"{filename} step-contract table contains a malformed extra row")
        if [row[0] for row in valid_contract_rows] != STEP_CONTRACT_FIELDS:
            errors.append(f"{filename} does not use the exact step-contract fields in order")
        contract_values = {row[0]: row[1] for row in valid_contract_rows}
        if contract_values.get("Step ID") != step_id:
            errors.append(f"{filename} Step ID field does not match its filename")
        indexed_row = indexed_step_rows.get(step_id, [])
        if indexed_row and contract_values.get("Acceptance owner") != indexed_row[5]:
            errors.append(f"{filename} Acceptance owner does not match the Section 6 step index")
        acceptance_owner = contract_values.get("Acceptance owner", "")
        if acceptance_owner not in allowed_step_acceptors:
            errors.append(
                f"{filename} Acceptance owner must be ROOT or an explicitly authorized lane sub-orchestrator"
            )
        elif acceptance_owner in lane_role_rows:
            covered_requirements = set(REQ_RE.findall(contract_values.get("Deliverable and requirement coverage", "")))
            lane_requirement_scope = set(REQ_RE.findall(" ".join(lane_role_rows[acceptance_owner][4:])))
            if not covered_requirements or not covered_requirements.issubset(lane_requirement_scope):
                errors.append(
                    f"{filename} lane acceptance owner {acceptance_owner!r} must explicitly scope every "
                    "covered REQ-* ID in its structured role contract"
                )
        for field in STEP_CONTRACT_FIELDS:
            if invalid_executable_value(contract_values.get(field, "")):
                errors.append(f"{filename} step-contract field {field} is empty or a non-executable placeholder/waiver")

        entry_body = owned[STEP_HEADINGS[2]]
        expected_entry_prefix = (
            "\n\n" + STEP_FAST_LANE_CANONICAL_BLOCK + "\n\n| " + " | ".join(STEP_ENTRY_TABLE) + " |"
        )
        if not entry_body.startswith(expected_entry_prefix):
            errors.append(
                f"{filename} must copy the exact canonical FAST_LANE_V2 usage block once directly "
                "beneath the entry-flow heading and immediately before the entry table"
            )
        if entry_body.count(STEP_FAST_LANE_CANONICAL_BLOCK) != 1:
            errors.append(f"{filename} must contain the canonical FAST_LANE_V2 usage block exactly once")
        entry_rows = extract_table(entry_body, STEP_ENTRY_TABLE) or []
        if table_header_count(text, STEP_ENTRY_TABLE) != 1:
            errors.append(f"{filename} must contain the entry-flow table exactly once")
        valid_entries = [row for row in entry_rows if len(row) == len(STEP_ENTRY_TABLE)]
        if len(valid_entries) != len(entry_rows):
            errors.append(f"{filename} entry table contains a malformed extra row")
        if [row[0] for row in valid_entries] != STEP_ENTRY_NAMES:
            errors.append(
                f"{filename} must define exactly NORMAL, FAST_LANE_V2_SERIES_1, "
                "and FAST_LANE_V2_SERIES_2 entry rows in order"
            )
        entry_instance_ids: list[str] = []
        for row in valid_entries:
            entry_name = row[0]
            if any(invalid_executable_value(value) for value in row[1:]):
                errors.append(f"{filename} {entry_name} entry has an empty or non-executable placeholder/waiver field")
            path_ids = MI_RE.findall(row[3])
            row_text = " ".join(row).lower()
            if entry_name != "NORMAL" and FAST_LANE_OPT_OUT_RE.search(" ".join(row)):
                errors.append(
                    f"{filename} {entry_name} entry uses forbidden fast-lane opt-out text; "
                    "every entry requires a configured MI-* path"
                )
            if not ORDERED_MI_PATH_RE.fullmatch(row[3]):
                errors.append(
                    f"{filename} {entry_name} path must be an explicit ordered MI-* list, not prose or a disguised opt-out"
                )
            if not path_ids:
                errors.append(f"{filename} {entry_name} entry has no configured MI-* path")
            expected_prefix = STEP_ENTRY_PREFIXES.get(entry_name)
            wrong_prefix_ids = [
                instance_id for instance_id in path_ids
                if expected_prefix is not None
                and (not instance_id.startswith(expected_prefix) or len(instance_id) == len(expected_prefix))
            ]
            if expected_prefix is not None and wrong_prefix_ids:
                errors.append(
                    f"{filename} {entry_name} entry must use only {expected_prefix}* IDs; found: "
                    + ", ".join(wrong_prefix_ids)
                )
            entry_instance_ids.extend(path_ids)
            if entry_name == "FAST_LANE_V2_SERIES_1":
                for term in ("complete pool", "correction", "motivating test", "compile", "review", "integration", "progress bound"):
                    if term not in row_text:
                        errors.append(f"{filename} Series 1 entry requires {term!r}")
                if not any(term in row[7].lower() for term in ("broad", "saved", "avoid")):
                    errors.append(f"{filename} Series 1 entry must state concrete normal broad work saved")
                if not all(term in row[1].lower() for term in ("complete pool", "correction")):
                    errors.append(f"{filename} Series 1 activation must require a complete pool and correction objective")
                if not all(term in row[2].lower() for term in ("complete pool", "motivating test")):
                    errors.append(f"{filename} Series 1 inputs must name the complete pool and motivating test")
                if not all(term in row[4].lower() for term in ("accepted", "repaired", "review", "integration")):
                    errors.append(f"{filename} Series 1 output must be accepted and repaired after review and integration")
                if "progress bound" not in row[5].lower():
                    errors.append(f"{filename} Series 1 destination must name the later progress bound")
                if not all(term in row[6].lower() for term in ("compile", "motivating test", "smoke")):
                    errors.append(f"{filename} Series 1 checkpoint rule must name compile and motivating-test smoke credit")
                path_contract = " ".join(instance_bodies.get(instance_id, "") for instance_id in path_ids).lower()
                if FAST_LANE_CONTRACT_BYPASS_RE.search(path_contract):
                    errors.append(f"{filename} Series 1 MI-* contracts contain forbidden fast-lane bypass language")
                for term in ("correction", "compile", "motivating test", "review", "integration", "progress bound"):
                    if term not in path_contract:
                        errors.append(f"{filename} Series 1 MI-* public contracts do not implement {term!r}")
            if entry_name == "FAST_LANE_V2_SERIES_2":
                for term in ("progress bound", "series 1", "invalidation", "unaffected pass", "earliest required", "remaining"):
                    if term not in row_text:
                        errors.append(f"{filename} Series 2 entry requires {term!r}")
                if not any(term in row[7].lower() for term in ("restart", "saved", "avoid")):
                    errors.append(f"{filename} Series 2 entry must state concrete restart work saved")
                if "progress bound" not in row[1].lower():
                    errors.append(f"{filename} Series 2 activation must require this step to be the progress bound")
                if not all(term in row[2].lower() for term in ("accepted", "series 1")):
                    errors.append(f"{filename} Series 2 inputs must name accepted Series 1 exits")
                if not all(term in row[5].lower() for term in ("normal", "successor")):
                    errors.append(f"{filename} Series 2 destination must return to the normal successor")
                if not all(term in row[6].lower() for term in ("invalidation", "unaffected pass", "earliest required", "remaining")):
                    errors.append(f"{filename} Series 2 checkpoint rule must define invalidation and remaining-check reuse")
                path_contract = " ".join(instance_bodies.get(instance_id, "") for instance_id in path_ids).lower()
                if FAST_LANE_CONTRACT_BYPASS_RE.search(path_contract):
                    errors.append(f"{filename} Series 2 MI-* contracts contain forbidden fast-lane bypass language")
                for term in ("series 1", "invalidation", "unaffected pass", "earliest required", "remaining", "normal successor"):
                    if term not in path_contract:
                        errors.append(f"{filename} Series 2 MI-* public contracts do not implement {term!r}")
        if duplicates(entry_instance_ids):
            errors.append(
                f"{filename} entry paths must use disjoint MI-* IDs; duplicates: "
                + ", ".join(duplicates(entry_instance_ids))
            )

        composition_rows = extract_table(owned[STEP_HEADINGS[3]], STEP_COMPOSITION_TABLE) or []
        if table_header_count(text, STEP_COMPOSITION_TABLE) != 1:
            errors.append(f"{filename} must contain the composition table exactly once")
        valid_composition = [row for row in composition_rows if len(row) == len(STEP_COMPOSITION_TABLE)]
        if len(valid_composition) != len(composition_rows):
            errors.append(f"{filename} composition table contains a malformed extra row")
        if not valid_composition:
            errors.append(f"{filename} has no configured M-module composition rows")
        if [row[0] for row in valid_composition] != [str(i) for i in range(1, len(valid_composition) + 1)]:
            errors.append(f"{filename} composition Order values must be consecutive from 1")
        for row in valid_composition:
            instance_id, module_type = row[1], row[2]
            if instance_id not in instance_types:
                errors.append(f"{filename} composes undeclared instance {instance_id}")
            elif instance_types[instance_id] != module_type:
                errors.append(
                    f"{filename} composes {instance_id} as {module_type}, expected {instance_types[instance_id]}"
                )
            consumed_instances.append(instance_id)
            if any(invalid_executable_value(value) for value in row[3:]):
                errors.append(f"{filename} composition for {instance_id} has a non-executable interface/activation value")

        inventory_ids = [row[1] for row in valid_composition]
        if sorted(entry_instance_ids) != sorted(inventory_ids):
            missing_from_entries = sorted(set(inventory_ids) - set(entry_instance_ids))
            missing_from_inventory = sorted(set(entry_instance_ids) - set(inventory_ids))
            if missing_from_entries:
                errors.append(
                    f"{filename} composition instances are not assigned to one entry path: "
                    + ", ".join(missing_from_entries)
                )
            if missing_from_inventory:
                errors.append(
                    f"{filename} entry paths reference instances absent from composition inventory: "
                    + ", ".join(missing_from_inventory)
                )

        gate_rows = extract_table(owned[STEP_HEADINGS[5]], STEP_GATE_TABLE) or []
        if table_header_count(text, STEP_GATE_TABLE) != 1:
            errors.append(f"{filename} must contain the gate/completion table exactly once")
        concrete_gate_rows = [row for row in gate_rows if len(row) == len(STEP_GATE_TABLE) and row[0] != "N/A"]
        if len(concrete_gate_rows) != 1:
            errors.append(f"{filename} must define exactly one concrete gate/completion row; N/A is forbidden")
        if len(gate_rows) != len(concrete_gate_rows):
            errors.append(f"{filename} gate/completion table contains an N/A or malformed bypass row")
        errors.extend(validate_gates(owned[STEP_HEADINGS[5]]))
        for row in gate_rows:
            if len(row) != len(STEP_GATE_TABLE) or row[0] == "N/A":
                continue
            gate_match = re.search(r"\bGATE-[A-Z0-9][A-Z0-9_-]*\b", row[0])
            if not gate_match:
                continue
            gate_id = gate_match.group(0)
            checking_ids = MI_RE.findall(row[4])
            if not checking_ids:
                errors.append(f"{filename} gate {gate_id} must name at least one checking MI-* instance")
            unknown_checking_ids = sorted(set(checking_ids) - set(instance_types))
            if unknown_checking_ids:
                errors.append(
                    f"{filename} gate {gate_id} references undeclared checking instances: "
                    + ", ".join(unknown_checking_ids)
                )
            if indexed_row and indexed_row[4] != gate_id:
                errors.append(f"{filename} gate {gate_id} does not match Section 6 value {indexed_row[4]!r}")
            if gate_id in gate_owners:
                errors.append(f"gate ID is defined by more than one step: {gate_id}")
            gate_owners[gate_id] = (step_id, row[1])

        if re.search(r"\bM\d{2}-A\d+\b", text):
            errors.append(f"{filename} copies M-module recipe actions instead of referencing MI-* interfaces")
        if re.search(r"(?m)^\|\s*workflow_role\s*\|", text):
            errors.append(f"{filename} contains a copied task card")
        if re.search(r"(?m)^###\s+P\d{2}", text):
            errors.append(f"{filename} contains copied global policy definitions")

    if duplicates(consumed_instances):
        errors.append(
            "configured module instances must belong to exactly one step; duplicates: "
            + ", ".join(duplicates(consumed_instances))
        )
    missing_instances = sorted(set(instance_types) - set(consumed_instances))
    extra_instances = sorted(set(consumed_instances) - set(instance_types))
    if missing_instances:
        errors.append(f"selected module instances are not composed by a step: {', '.join(missing_instances)}")
    if extra_instances:
        errors.append(f"steps compose unknown module instances: {', '.join(extra_instances)}")

    known_steps = set(indexed_steps)
    for header in REQUIRED_TABLES[HEADINGS[8]]:
        for row in extract_table(graph_body, header) or []:
            for referenced_step in STEP_RE.findall(" ".join(row)):
                if referenced_step not in known_steps:
                    errors.append(f"Section 8 references unknown step {referenced_step}")

    gate_index_rows = extract_table(graph_body, REQUIRED_TABLES[HEADINGS[8]][3]) or []
    gate_index_ids = [row[0] for row in gate_index_rows if len(row) == 7 and row[0] != "N/A"]
    if duplicates(gate_index_ids):
        errors.append(f"Section 8 gate index has duplicate IDs: {', '.join(duplicates(gate_index_ids))}")
    indexed_gates: dict[str, tuple[str, str, str]] = {}
    for row in gate_index_rows:
        if len(row) != 7 or row[0] == "N/A":
            continue
        indexed_gates[row[0]] = (row[1], row[2], row[3])
    if set(indexed_gates) != set(gate_owners):
        errors.append("Section 8 gate index must match the gates defined in STEP-* files exactly")
    for gate_id, (step_id, gate_class) in gate_owners.items():
        indexed = indexed_gates.get(gate_id)
        if indexed and indexed != (step_id, f"steps/{step_id}.md", gate_class):
            errors.append(f"Section 8 gate index disagrees with {step_id} for {gate_id}")
    return errors


def validate_package_texts(
    root_text: str,
    global_text: str,
    validation_text: str,
    step_texts: dict[str, str],
    module_texts: dict[str, str],
    mapping_roles: set[str],
    mapping_name: str,
    mapping_path: Path | None = None,
    plan_path: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    root_headings = HEADINGS[:9] + [HEADINGS[10], HEADINGS[12], HEADINGS[13], HEADINGS[14]]
    root_sections, root_heading_errors = split_owned_sections(root_text, root_headings, "plan-workflow.md")
    global_sections, global_heading_errors = split_owned_sections(global_text, [HEADINGS[9]], "global-rules.md")
    validation_sections, validation_heading_errors = split_owned_sections(
        validation_text, [HEADINGS[15], HEADINGS[16]], "validation.md"
    )
    errors.extend(root_heading_errors + global_heading_errors + validation_heading_errors)

    if len(re.findall(r"(?m)^#\s+.+\s+-\s+Modular Execution Plan\s*$", root_text)) != 1:
        errors.append("plan-workflow.md must have exactly one modular execution plan title")
    if len(re.findall(r"(?m)^#\s+.+\s+-\s+Global Workflow Rules\s*$", global_text)) != 1:
        errors.append("global-rules.md must have exactly one global workflow rules title")
    if len(re.findall(r"(?m)^#\s+.+\s+-\s+Plan Validation\s*$", validation_text)) != 1:
        errors.append("validation.md must have exactly one plan validation title")
    if errors:
        return errors

    combined_markdown = "\n\n".join(
        [root_text, global_text, validation_text, *step_texts.values(), *module_texts.values()]
    )
    for filename, text in {
        "plan-workflow.md": root_text,
        "global-rules.md": global_text,
        "validation.md": validation_text,
        **{f"steps/{name}": value for name, value in step_texts.items()},
        **{f"modules/{name}": value for name, value in module_texts.items()},
    }.items():
        errors.extend(validate_pipe_table_groups(text, filename))
    unresolved = sorted(set(re.findall(r"\{\{[^}\n]+\}\}", combined_markdown)))
    if unresolved:
        errors.append(f"unresolved template tokens remain: {', '.join(unresolved[:5])}")
    if "TEMPLATE NOTE:" in combined_markdown:
        errors.append("TEMPLATE NOTE lines remain in the execution package")
    angle_placeholders = sorted(set(re.findall(r"<[^>\n]+>", combined_markdown)))
    if angle_placeholders:
        errors.append(f"angle-bracket placeholders remain: {', '.join(angle_placeholders[:5])}")

    by_section = {**root_sections, **global_sections, **validation_sections, HEADINGS[11]: ""}
    errors.extend(validate_required_tables(by_section))
    ledger_rows = extract_table(root_sections[HEADINGS[14]], REQUIRED_TABLES[HEADINGS[14]][0]) or []
    for row in ledger_rows:
        if len(row) == 6 and row[0] != "N/A" and normalize(row[1]).upper() not in {"TOLERANCE", "OUT_OF_SCOPE"}:
            errors.append(
                f"final ledger item {row[0]} must be TOLERANCE or OUT_OF_SCOPE; "
                "an unresolved or differently labeled blocking item cannot validate"
            )
    contract_errors, topology = validate_plan_contract(
        root_sections[HEADINGS[0]], mapping_name, mapping_path, plan_path
    )
    errors.extend(contract_errors)
    module_errors, instance_types, joined_instances = validate_module_files(module_texts)
    errors.extend(module_errors)
    by_section[HEADINGS[11]] = joined_instances
    errors.extend(validate_optional_profile_decisions(by_section, module_texts, instance_types))
    errors.extend(validate_step_files(root_sections, step_texts, instance_types, joined_instances))
    role_rows = extract_table(root_sections[HEADINGS[7]], ROLE_TABLE) or []
    root_roles = [
        row[0] for row in role_rows
        if len(row) == len(ROLE_TABLE) and normalize(row[1]).upper() == "ROOT"
    ]
    root_role = root_roles[0] if len(root_roles) == 1 else ""
    errors.extend(validate_policies(global_sections[HEADINGS[9]], instance_types, mapping_roles, root_role))
    errors.extend(validate_verification_economy(
        root_sections[HEADINGS[0]], global_sections[HEADINGS[9]], combined_markdown
    ))
    errors.extend(validate_cross_references(by_section, instance_types, step_texts, mapping_roles))
    errors.extend(validate_member_lane_and_handoff_manifest(
        by_section, joined_instances, instance_types, mapping_roles
    ))
    errors.extend(validate_roles(root_sections[HEADINGS[7]], mapping_roles, mapping_name, combined_markdown, topology))
    errors.extend(validate_root_acceptance_ownership(root_sections))
    errors.extend(validate_card_authority_and_graph_references(by_section, step_texts, joined_instances))
    errors.extend(validate_module_policy_and_role_references(
        global_sections[HEADINGS[9]], step_texts, module_texts, mapping_roles
    ))
    errors.extend(validate_unbounded_agent_sessions(combined_markdown, mapping_roles))
    errors.extend(validate_rule_and_check_matrices(by_section))
    errors.extend(validate_test_scope_audit(validation_sections[HEADINGS[16]], step_texts))

    task_roles: set[str] = set()
    for _, _, card_body in task_card_blocks(joined_instances):
        rows = extract_table(card_body, ("Field", "Value")) or []
        values = {row[0]: row[1] for row in rows if len(row) == 2}
        if role := values.get("workflow_role"):
            task_roles.add(role)
    unknown_task_roles = sorted(task_roles - mapping_roles)
    if unknown_task_roles:
        errors.append(f"module cards use roles absent from the mapping: {', '.join(unknown_task_roles)}")

    if vague_match := VAGUE_EXECUTION_RE.search(joined_instances):
        errors.append(f"module local instructions contain banned vague phrase: {vague_match.group(0)!r}")
    if re.search(r"(?m)^###\s+P\d{2}", root_text + "\n" + validation_text + "\n" + "\n".join(step_texts.values())):
        errors.append("global policy definitions appear outside global-rules.md")
    if re.search(r"\bM\d{2}-A\d+\b", root_text + "\n" + global_text + "\n" + validation_text):
        errors.append("M-module recipe action definitions appear outside modules/Mxx.md")
    return errors


def markdown_table(header: tuple[str, ...], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(header) + " |",
        "|" + "|".join("---" for _ in header) + "|",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def build_self_test_package() -> tuple[str, str, str, dict[str, str], dict[str, str]]:
    root_parts = ["# Validator Self Test - Modular Execution Plan"]
    root_parts += [
        HEADINGS[0],
        markdown_table(("Field", "Value"), [
            ["Plan ID", "SELF-TEST"],
            ["Plan version", "1"],
            ["Status", "VALIDATED"],
            ["Decision owner", "orchestrator"],
            ["Orchestration topology", "ROOT_DIRECT_WORKERS"],
            ["Verification protocol", "CHECKPOINTED_VERIFICATION_V1"],
            ["Operative document boundary", "self-test package"],
            ["Change procedure", "edit the owning artifact"],
            ["Definition of valid", "semantic and deterministic checks pass"],
        ]),
        markdown_table(PACKAGE_DEPENDENCY_TABLE, [
            ["Global rules", "global-rules.md", "policies", "steps and modules", "compatible policy edits"],
            ["Gated steps", "steps/", "step composition", "composition root", "compatible step edits"],
            ["M-module library", "modules/M01.md through modules/M10.md", "module process", "steps", "compatible module edits"],
            ["Agent mapping", "mapping.json", "agent selection", "runtime resolver", "mapping-only edits"],
            ["Validation", "validation.md", "validation results", "delivery", "observes only"],
        ]),
    ]
    root_parts += [
        HEADINGS[1],
        markdown_table(REQUIRED_TABLES[HEADINGS[1]][0], [["SRC-001", "goal", "goal.md", "requirements", "user wins"]]),
        markdown_table(REQUIRED_TABLES[HEADINGS[1]][1], [[
            str(number), f"authority layer {number}", f"layer {number} owned behavior",
            f"layers above {number}",
        ] for number in range(1, 10)]),
        HEADINGS[2],
        "Goal: validate the modular package validator.",
        markdown_table(REQUIRED_TABLES[HEADINGS[2]][0], [["OUT-001", "valid plan behavior", "validator pass", "orchestrator", "covered"]]),
        markdown_table(REQUIRED_TABLES[HEADINGS[2]][1], [["BOUND-001", "in scope", "validation", "self test", "orchestrator"]]),
        HEADINGS[3],
        markdown_table(REQUIRED_TABLES[HEADINGS[3]][0], [["REQ-001", "SRC-001", "DEL-001", "orchestrator", "CHECK-001", "orchestrator", "covered"]]),
        HEADINGS[4],
        markdown_table(REQUIRED_TABLES[HEADINGS[4]][0], [["validation", "ORCHESTRATOR_ENFORCED", "script", "orchestrator", "plan", "exit 0", "fix"]]),
        HEADINGS[5],
        markdown_table(REQUIRED_TABLES[HEADINGS[5]][0], [["DEL-001", "valid plan", "REQ-001", "none", "schema", "plan"]]),
        markdown_table(REQUIRED_TABLES[HEADINGS[5]][1], [["DEL-001", "shape error", "invalid", "low", "short", "none", "M05", "accept"]]),
        HEADINGS[6],
        markdown_table(REQUIRED_TABLES[HEADINGS[6]][0], [["STEP-001", "steps/STEP-001.md", "candidate", "accepted result", "GATE-001", "orchestrator"]]),
        markdown_table(REQUIRED_TABLES[HEADINGS[6]][1], [[module_id, f"modules/{module_id}.md"] for module_id in MODULE_IDS]),
        HEADINGS[7],
        markdown_table(ROLE_TABLE, [
            ["orchestrator", "ROOT", "N/A", "worker", "accept", "1", "bounded", "none", "none", "plan ready", "plan"],
            ["worker", "WORKER", "orchestrator", "N/A", "execute", "1", "bounded", "source", "workspace", "dispatched", "task"],
        ]),
        markdown_table(REQUIRED_TABLES[HEADINGS[7]][1], [["resolve at launch", "reject", "no plan edit"]]),
        HEADINGS[8],
        markdown_table(REQUIRED_TABLES[HEADINGS[8]][0], [["EDGE-001", "STEP-001.accepted result", "terminal", "accepted", "serial", "N/A", "incomplete"]]),
        markdown_table(REQUIRED_TABLES[HEADINGS[8]][1], [[
            "N/A", "No parallel group is required because the self-test has one serial step",
            "none", "no parallel writes", "not launched", "none", "no serial exception",
        ]]),
        markdown_table(REQUIRED_TABLES[HEADINGS[8]][2], [["PATH-001", "STEP-001 EDGE-001", "short", "none", "none", "only path"]]),
        markdown_table(REQUIRED_TABLES[HEADINGS[8]][3], [["GATE-001", "STEP-001", "steps/STEP-001.md", "PRODUCT", "required plan behavior", "EDGE-001 terminal", "STEP-001 return route"]]),
        HEADINGS[10],
    ]
    for header in REQUIRED_TABLES[HEADINGS[10]]:
        if header == REQUIRED_TABLES[HEADINGS[10]][0]:
            root_parts.append(markdown_table(header, [
                ["LANE-NORMAL", "MI-NORMAL-ACCEPT", "worker", "member dispatch", "read only", "orchestrator", "HANDOFF-NORMAL published", "normal failure route"],
                ["LANE-S1", "MI-FL2-S1-REPAIR-EXIT", "worker", "member dispatch", "source root", "orchestrator", "HANDOFF-S1 published", "Series 1 failure route"],
                ["LANE-S2", "MI-FL2-S2-RECONCILE", "worker", "member dispatch", "read only", "orchestrator", "HANDOFF-S2 published", "Series 2 failure route"],
            ]))
        elif header == REQUIRED_TABLES[HEADINGS[10]][3]:
            root_parts.append(markdown_table(header, [
                ["HANDOFF-NORMAL", "worker", "orchestrator", "none", "PROCESS-NORMAL and INVOCATION-NORMAL", "publish at completion", "accepted for review", "normal failure route"],
                ["HANDOFF-S1", "worker", "orchestrator", "none", "PROCESS-S1 and INVOCATION-S1", "publish at completion", "accepted for review", "Series 1 failure route"],
                ["HANDOFF-S2", "worker", "orchestrator", "none", "PROCESS-S2 and INVOCATION-S2", "publish at completion", "accepted for review", "Series 2 failure route"],
            ]))
        else:
            root_parts.append(markdown_table(header, [[
                "N/A", "No manifest entry is required because the self-test has no runtime allocation",
                *(["none"] * (len(header) - 2)),
            ]]))
    root_parts += [
        HEADINGS[12],
        markdown_table(REQUIRED_TABLES[HEADINGS[12]][0], [[
            "N/A", "No synthetic-to-real transition is required because the self-test uses direct validation",
            "none", "none", "none", "none", "orchestrator", "terminal",
        ]]),
        HEADINGS[13],
        markdown_table(REQUIRED_TABLES[HEADINGS[13]][0], [[
            "N/A", "No state transition is required because the self-test has one terminal validation state",
            "none", "none", "none", "none", "none", "orchestrator",
        ]]),
        HEADINGS[14],
        markdown_table(REQUIRED_TABLES[HEADINGS[14]][0], [[
            "N/A", "No unresolved item is retained because every self-test input is fixed and known",
            "none", "none", "orchestrator", "terminal",
        ]]),
    ]

    global_parts = ["# Validator Self Test - Global Workflow Rules", HEADINGS[9]]
    for policy in POLICY_HEADINGS:
        global_parts += [policy, markdown_table(POLICY_TABLE, [[
            "orchestrator", "checkpoint and FAST_LANE_V2",
            "input map; first unresolved; earliest required; ordinary failure continuation; "
            "Series 1 complete pool, motivating test, compile, review, integration, and smoke credit; "
            "Series 2 progress bound, join, and saved work",
            "recorded", "plan", "MI-NORMAL-ACCEPT, MI-FL2-S1-REPAIR-EXIT, MI-FL2-S2-RECONCILE"
        ]])]
        if policy.startswith("### P14"):
            global_parts.append(markdown_table(EXCEPTION_TABLE, [[
                "N/A", "No exception classes are declared because the self-test uses only normal policy routes",
                "none declared", "orchestrator", "no alternate action", "no confirmation required",
                "all results preserved", "no results invalidated", "self-test package", "plan completion",
            ]]))

    validation_parts = [
        "# Validator Self Test - Plan Validation",
        HEADINGS[15],
        markdown_table(REQUIRED_TABLES[HEADINGS[15]][0], [[
            rule_id, f"validation.md Section 15 row {rule_id}",
            f"Concrete {rule_id} behavior is applied by the self-test package and validator checks",
        ] for rule_id in RULE_IDS]),
        HEADINGS[16],
        markdown_table(REQUIRED_TABLES[HEADINGS[16]][0], [[
            check_id, "PASS", f"validation.md Section 16 row {check_id} records concrete self-test package inspection",
        ] for check_id in CHECK_IDS]),
        markdown_table(AUDIT_META_TABLE, [
            ["Plan writer", "fixture-author-session"],
            ["Review panel", "Four synthetic independent group declarations below"],
            ["Plan revision", "fixture-final-revision"],
            ["Review evidence", "Synthetic review transcript for validator contract testing only"],
            ["Requested outcome and non-goals", "Synthetic request: validate the fixture; no product campaign"],
            ["Scope and authority review", "Fixture stages cover only REQ-001; applicable rules inspected"],
            ["Topology and simplicity review", "Formal fixture requested; one direct worker and one gate"],
            ["Verification and budget review", "Fixture structure only; local validator cost, no live execution"],
            ["Execution authorization boundary", "Synthetic fixture only; no product or external action authorized"],
            ["Plan review verdict", "PASS"],
            ["ROOT acceptance", "Synthetic ROOT disposition accepts the unchanged fixture scope"],
            ["Audit status", "ACCEPTED"],
        ]),
        markdown_table(AUDIT_GROUP_TABLE, [[
            group, f"fixture-{group.lower()}-reviewer", "fixture-final-revision",
            f"Synthetic {group} final approval for validator testing only",
            "Synthetic no-material-findings result; unchanged final fixture", "PASS",
        ] for group in AUDIT_GROUPS]),
        markdown_table(AUDIT_SCOPE_TABLE, [[
            "STEP-001", "modules/M05.md acceptance cards for all three entries",
            "REQ-001 acceptance criterion and its declared observation",
            "One acceptance decision; no provider or platform product is proposed",
            "Read-only inspection; time estimate uncertain until measured",
            "REQ-001 requires inspection of the local fixture declarations; no external environment is needed",
            "One declared acceptance decision per entry; no repeated observations or combination matrix is required",
            "Retain the existing local inspection: it decides REQ-001 without new assets or recurring external cost",
            "Synthetic reviewer reports no material findings in the fixture scope",
            "Retain existing criterion; no change and no follow-up needed",
            "ACCEPTED",
        ]]),
        "PLAN_STRUCTURE=VALID",
    ]

    module_texts: dict[str, str] = {}
    for module_id in MODULE_IDS:
        selected = module_id == "M05"
        selected_ids = "MI-NORMAL-ACCEPT, MI-FL2-S1-REPAIR-EXIT, MI-FL2-S2-RECONCILE" if selected else "N/A"
        module_parts = [
            f"# {module_id} - Self Test Module",
            MODULE_HEADINGS[0],
            markdown_table(MODULE_SELECTION_TABLE, [[
                module_id, "SELECTED" if selected else "OMITTED", selected_ids,
                "Self-test module decision based on concrete package facts",
            ]]),
            MODULE_HEADINGS[1],
            "Stable typed input and output; internal process changes preserve this public contract.",
            MODULE_HEADINGS[2],
            "Concrete module rules cite P01-P15 and preserve the catalog recipe.",
            markdown_table(MODULE_ACTION_TABLE, [[str(index), action_id, f"execute {action_id}", "fixed self-test parameter", "orchestrator"] for index, action_id in enumerate(MODULE_ACTIONS[module_id], 1)]),
            MODULE_HEADINGS[3],
        ]
        if selected:
            for instance_id, name, governing_id, member_id, lane_id, handoff_id in (
                ("MI-NORMAL-ACCEPT", "Normal acceptance", "CARD-NORMAL-G", "CARD-NORMAL-M", "LANE-NORMAL", "HANDOFF-NORMAL"),
                ("MI-FL2-S1-REPAIR-EXIT", "Series 1 repair exit", "CARD-S1-G", "CARD-S1-M", "LANE-S1", "HANDOFF-S1"),
                ("MI-FL2-S2-RECONCILE", "Series 2 progress-bound re-entry", "CARD-S2-G", "CARD-S2-M", "LANE-S2", "HANDOFF-S2"),
            ):
                module_parts.append(f"### {instance_id} - M05: {name}")
                for field in INSTANCE_FIELDS:
                    module_parts.append(f"#### {field}")
                    if field == "Local instructions":
                        for card_kind, card_id, actions in (
                            ("Governing", governing_id, MODULE_ACTIONS["M05"]),
                            ("Member", member_id, ["M05-A1"]),
                        ):
                            module_parts.append(f"##### {card_kind} task card: {card_id}")
                            task_rows = [[task_field, f"self-test concrete {task_field}"] for task_field in TASK_FIELDS]
                            task_rows[0][1] = (
                                f"schema=self-test; card_id={card_id}; module_instance_id={instance_id}; "
                                "deliverable_id=DEL-001; stage_cohort_id=COHORT-001; "
                                "gate_id=GATE-001; loop_id=LOOP-001"
                            )
                            task_rows[TASK_FIELDS.index("workflow_role")][1] = (
                                "orchestrator" if card_kind == "Governing" else "worker"
                            )
                            if card_kind == "Member":
                                runtime_tag = lane_id.removeprefix("LANE-")
                                task_rows[TASK_FIELDS.index("starting_state")][1] = (
                                    f"preassigned INVOCATION-{runtime_tag}; launch records PROCESS-{runtime_tag} "
                                    "before worker execution"
                                )
                                task_rows[TASK_FIELDS.index("allowed_tools_capabilities_resources")][1] = (
                                    f"self-test workspace resources in {lane_id}"
                                )
                                task_rows[TASK_FIELDS.index("completion_review_owner_and_handoff")][1] = (
                                    f"orchestrator reviews terminal {handoff_id}"
                                )
                            task_rows[TASK_FIELDS.index("ordered_actions")][1] = "; ".join(actions)
                            task_rows[TASK_FIELDS.index("cited_global_policy_ids_and_exception_ids")][1] = "P01"
                            module_parts.append(markdown_table(("Field", "Value"), task_rows))
                    elif field == "Owner and roles":
                        module_parts.append(f"orchestrator owns dispatch inventory: {member_id}=worker")
                    elif field == "Purpose" and instance_id == "MI-FL2-S1-REPAIR-EXIT":
                        module_parts.append(
                            "Correction path compiles, runs the motivating test, completes review and integration, "
                            "and returns an accepted exit to the progress bound."
                        )
                    elif field == "Purpose" and instance_id == "MI-FL2-S2-RECONCILE":
                        module_parts.append(
                            "Join accepted Series 1 exits, apply invalidation, preserve unaffected PASS credit, "
                            "run remaining checks from the earliest required unit, and return to the normal successor."
                        )
                    else:
                        module_parts.append("Self-test concrete value.")
        module_texts[f"{module_id}.md"] = "\n\n".join(module_parts) + "\n"

    valid_product_gate = [
        "GATE-001 / LOOP-001", "PRODUCT", "revision",
        "Does the required product plan behavior satisfy its acceptance contract?", "MI-NORMAL-ACCEPT",
        "plan semantics", "DEL-001 product acceptance only",
        "only when a required product criterion fails or is genuinely undecidable",
        "EDGE-001 advances to terminal", "same MI-NORMAL-ACCEPT task", "one decision", "one owner",
        "unrelated credit preserved", "split on independent criterion",
    ]
    step_parts = [
        "# STEP-001 - Acceptance Step",
        STEP_HEADINGS[0],
        markdown_table(("Field", "Value"), [[field, {
            "Step ID": "STEP-001",
            "Acceptance owner": "orchestrator",
            "Deliverable and requirement coverage": "DEL-001 and REQ-001",
        }.get(field, f"concrete {field}")] for field in STEP_CONTRACT_FIELDS]),
        STEP_HEADINGS[1], "Candidate input is ready and protected boundaries are fixed.",
        STEP_HEADINGS[2], STEP_FAST_LANE_CANONICAL_BLOCK, markdown_table(STEP_ENTRY_TABLE, [
            ["NORMAL", "normal predecessor activation", "candidate", "MI-NORMAL-ACCEPT", "accepted normal output", "EDGE-001 normal successor", "normal checkpoint credit", "original full path; no fast-lane claim", "normal product failure route"],
            ["FAST_LANE_V2_SERIES_1", "activates after complete pool and scoped correction objective", "complete pool with motivating test", "MI-FL2-S1-REPAIR-EXIT", "accepted integrated repaired output after independent review and integration", "later current progress bound Series 2 entry", "compile and motivating test smoke credit", "saved broad campaign work", "normal material route on failure"],
            ["FAST_LANE_V2_SERIES_2", "activates when this step is current progress bound", "accepted Series 1 exits", "MI-FL2-S2-RECONCILE", "updated checkpoint and output", "normal successor after remaining checks", "input invalidation; preserve unaffected PASS; earliest required remaining units", "saved full restart work", "normal checking route on failure"],
        ]),
        STEP_HEADINGS[3], markdown_table(STEP_COMPOSITION_TABLE, [
            ["1", "MI-NORMAL-ACCEPT", "M05", "candidate", "accepted normal result", "normal activation"],
            ["2", "MI-FL2-S1-REPAIR-EXIT", "M05", "complete pool", "accepted repair exit", "Series 1 activation"],
            ["3", "MI-FL2-S2-RECONCILE", "M05", "accepted Series 1 exits", "resumed result", "Series 2 progress-bound activation"],
        ]),
        STEP_HEADINGS[4], "Accepted result advances through EDGE-001 to terminal.",
        STEP_HEADINGS[5], markdown_table(STEP_GATE_TABLE, [valid_product_gate]),
        STEP_HEADINGS[6], "Classified failure returns to MI-NORMAL-ACCEPT at its first unresolved action; unrelated credit is preserved.",
        STEP_HEADINGS[7], "One isolated lane; runtime IDs, cleanup, and terminal state are concrete.",
        STEP_HEADINGS[8], "Short expected range with one gate and no avoidable serial cost.",
    ]
    return (
        "\n\n".join(root_parts) + "\n",
        "\n\n".join(global_parts) + "\n",
        "\n\n".join(validation_parts) + "\n",
        {"STEP-001.md": "\n\n".join(step_parts) + "\n"},
        module_texts,
    )


def run_self_test() -> list[str]:
    root, global_rules, validation_doc, steps, modules = build_self_test_package()
    failures: list[str] = []

    def check(root_text: str = root, global_text: str = global_rules, validation_text: str = validation_doc,
              step_texts: dict[str, str] | None = None, module_texts: dict[str, str] | None = None,
              roles: set[str] | None = None) -> list[str]:
        self_test_plan_path = (Path.cwd() / "__validator_self_test__" / "package").resolve()
        self_test_mapping_path = self_test_plan_path / "mapping.json"
        return validate_package_texts(
            root_text, global_text, validation_text,
            steps if step_texts is None else step_texts,
            modules if module_texts is None else module_texts,
            {"orchestrator", "worker"} if roles is None else roles, "mapping.json",
            self_test_mapping_path, self_test_plan_path,
        )

    if errors := check():
        failures.append("valid fixture failed: " + "; ".join(errors))
    for field in AUDIT_FIELDS[4:9]:
        missing_assessment = "\n".join(
            line for line in validation_doc.splitlines() if not line.startswith(f"| {field} |")
        )
        if not check(validation_text=missing_assessment):
            failures.append(f"plan audit missing {field} was accepted")
        waived_assessment = re.sub(
            rf"(?m)^\| {re.escape(field)} \|.*$", f"| {field} | N/A |", validation_doc
        )
        if not check(validation_text=waived_assessment):
            failures.append(f"plan audit with waived {field} was accepted")
    # Acceptance design is required even with four PASS reviewers and valid V rows.
    audit_rows = extract_table(validation_doc, AUDIT_SCOPE_TABLE) or []
    accepted_audit = markdown_table(AUDIT_SCOPE_TABLE, audit_rows)
    for field in ACCEPTANCE_ASSESSMENT_FIELDS:
        field_index = AUDIT_SCOPE_TABLE.index(field)
        for invalid_assessment in (
            "", "N/A", "PENDING", "NONE", "UNKNOWN", "UNAVAILABLE", "NOT REVIEWED",
            "YES", "NO", "PASS", "ACCEPTED", "APPROVED", "SUFFICIENT", "COMPLETE",
            "BLOCK", "FAIL", "FAILED", "REJECTED",
        ):
            incomplete_rows = [row.copy() for row in audit_rows]
            incomplete_rows[0][field_index] = invalid_assessment
            incomplete_doc = validation_doc.replace(
                accepted_audit, markdown_table(AUDIT_SCOPE_TABLE, incomplete_rows)
            )
            assessment_errors = check(validation_text=incomplete_doc)
            if not any(field in error for error in assessment_errors):
                failures.append(f"acceptance design {field}={invalid_assessment!r} did not fail its assessment check")
        reduced_headers = tuple(name for name in AUDIT_SCOPE_TABLE if name != field)
        reduced_rows = [[value for index, value in enumerate(row) if index != field_index] for row in audit_rows]
        if not check(validation_text=validation_doc.replace(
            accepted_audit, markdown_table(reduced_headers, reduced_rows)
        )):
            failures.append(f"acceptance design missing {field} column was accepted")
    # Concrete family references and justified repetition are allowed, not a fixed proof taxonomy/count.
    referenced_rows = [row.copy() for row in audit_rows]
    for field in ACCEPTANCE_ASSESSMENT_FIELDS:
        referenced_rows[0][AUDIT_SCOPE_TABLE.index(field)] = (
            f"Synthetic VERIFICATION/TOPOLOGY_SIMPLICITY/EXECUTION_RESOURCES review: "
            f"modules/M05.md all-entry REQ-001 family {field} decision"
        )
    if errors := check(validation_text=validation_doc.replace(
        accepted_audit, markdown_table(AUDIT_SCOPE_TABLE, referenced_rows)
    )):
        failures.append("specific reviewed-family references failed: " + "; ".join(errors))
    repeated_rows = [row.copy() for row in audit_rows]
    repeated_rows[0][AUDIT_SCOPE_TABLE.index("Multiplicity assessment")] = (
        "Synthetic REQ-001 review requires repeated measurements to decide its uncertainty bound; "
        "each observation follows the specified stopping rule"
    )
    if errors := check(validation_text=validation_doc.replace(
        accepted_audit, markdown_table(AUDIT_SCOPE_TABLE, repeated_rows)
    )):
        failures.append("justified repeated-observation declaration failed: " + "; ".join(errors))
    # Exercise approval aggregation through complete packages, not wording matches.
    for group in AUDIT_GROUPS:
        group_line = next(line for line in validation_doc.splitlines() if line.startswith(f"| {group} |"))
        invalid_group_rows = {
            "missing group": "",
            "duplicate group": group_line + "\n" + group_line,
            "unknown group": group_line.replace(group, "UNKNOWN_GROUP", 1),
            "blocked group": group_line.rsplit("PASS", 1)[0] + "BLOCK |",
            "pending group": group_line.rsplit("PASS", 1)[0] + "PENDING |",
            "stale approval": group_line.replace("fixture-final-revision", "fixture-prior-revision"),
            "writer reviewing itself": group_line.replace(f"fixture-{group.lower()}-reviewer", "fixture-author-session"),
            "missing evidence": group_line.replace(f"Synthetic {group} final approval for validator testing only", "N/A"),
            "missing dispositions": group_line.replace("Synthetic no-material-findings result; unchanged final fixture", "N/A"),
        }
        for defect, changed_line in invalid_group_rows.items():
            if not check(validation_text=validation_doc.replace(group_line, changed_line)):
                failures.append(f"{group}: {defect} was accepted despite aggregate PASS")
    for marker in ("PENDING", "NONE", "UNKNOWN", "UNAVAILABLE", "MISSING", "NOT REVIEWED", "NOT RUN"):
        incomplete_declarations = {
            "final revision": validation_doc.replace("fixture-final-revision", marker),
            "reviewer identity": validation_doc.replace("fixture-verification-reviewer", marker),
            "review evidence": validation_doc.replace("Synthetic VERIFICATION final approval for validator testing only", marker),
        }
        for field, incomplete in incomplete_declarations.items():
            if not check(validation_text=incomplete):
                failures.append(f"absent {field} marker {marker} was accepted")
    reused_identity = validation_doc.replace(
        "fixture-execution_resources-reviewer", "FIXTURE-VERIFICATION-REVIEWER"
    )
    if not check(validation_text=reused_identity):
        failures.append("one identity used for two groups was accepted")
    updated_revision = validation_doc.replace("fixture-final-revision", "fixture-reapproved-revision")
    if errors := check(validation_text=updated_revision):
        failures.append("all groups approving updated revision failed: " + "; ".join(errors))
    checkpoint_root = root
    checkpoint_global = global_rules
    if errors := check(root_text=checkpoint_root, global_text=checkpoint_global):
        failures.append("valid checkpoint protocol failed: " + "; ".join(errors))
    fast_lane_global = checkpoint_global
    if errors := check(root_text=checkpoint_root, global_text=fast_lane_global):
        failures.append("valid FAST_LANE_V2 protocol failed: " + "; ".join(errors))

    corruptions: dict[str, list[str]] = {
        "test-only audit missing conformance review": check(validation_text="\n".join(
            line for line in validation_doc.splitlines()
            if not any(line.startswith(f"| {field} |") for field in AUDIT_FIELDS[4:10])
        )),
        "blocked plan with accepted test audit": check(validation_text=validation_doc.replace(
            "| Plan review verdict | PASS |", "| Plan review verdict | BLOCK |")),
        "pending plan with accepted test audit": check(validation_text=validation_doc.replace(
            "| Plan review verdict | PASS |", "| Plan review verdict | PENDING |")),
        "missing scope audit": check(validation_text=validation_doc[:validation_doc.index("| Audit field")]
                                     + "PLAN_STRUCTURE=VALID\n"),
        "self-reviewed scope": check(validation_text=validation_doc.replace(
            "fixture-verification-reviewer", "fixture-author-session")),
        "pending scope audit": check(validation_text=validation_doc.replace(
            "| Audit status | ACCEPTED |", "| Audit status | PENDING |")),
        "missing step audit": check(validation_text="\n".join(
            line for line in validation_doc.splitlines()
            if not line.startswith("| STEP-001 | modules/M05.md")
        )),
        "unknown audited step": check(validation_text=validation_doc.replace(
            "| STEP-001 | modules/M05.md", "| STEP-999 | modules/M05.md")),
        "missing audit cost": check(validation_text=validation_doc.replace(
            "Read-only inspection; time estimate uncertain until measured", "N/A")),
        "unresolved audit disposition": check(validation_text=validation_doc.replace(
            "no change and no follow-up needed | ACCEPTED", "material coverage unresolved | PENDING")),
        "placeholder": check(root_text=root + "\n{{UNFILLED}}\n"),
        "disabled exact verification protocol": check(
            root_text=root.replace(
                "| Verification protocol | CHECKPOINTED_VERIFICATION_V1 |",
                "| Verification protocol | CHECKPOINTED_VERIFICATION_V1 disabled |",
                1,
            )
        ),
        "checkpoint marker without policy": check(
            global_text=global_rules.replace("input map", "inputs")
        ),
        "checkpoint marker outside Section 0": check(
            root_text=root.replace("CHECKPOINTED_VERIFICATION_V1", "N/A", 1)
            + "\nCHECKPOINTED_VERIFICATION_V1\n"
        ),
        "FAST_LANE_V2 without checkpoint protocol": check(
            root_text=root.replace("CHECKPOINTED_VERIFICATION_V1", "N/A", 1)
        ),
        "checkpoint protocol without earliest required route": check(
            root_text=checkpoint_root,
            global_text=checkpoint_global.replace("earliest required", "resume point"),
        ),
        "FAST_LANE_V2 without complete pool": check(
            root_text=checkpoint_root,
            global_text=fast_lane_global.replace("complete pool", "partial result"),
        ),
    }
    short_hierarchy = root.replace(
        "| 9 | authority layer 9 | layer 9 owned behavior | layers above 9 |\n", "", 1
    )
    corruptions["incomplete directive hierarchy"] = check(root_text=short_hierarchy)
    corruptions["non-final plan status"] = check(
        root_text=root.replace("| Status | VALIDATED |", "| Status | DRAFT |", 1)
    )
    corruptions["open final outcome"] = check(
        root_text=root.replace(
            "| OUT-001 | valid plan behavior | validator pass | orchestrator | covered |",
            "| OUT-001 | valid plan behavior | validator pass | orchestrator | OPEN |",
            1,
        )
    )
    corruptions["waived required verification"] = check(
        root_text=root.replace(
            "| REQ-001 | SRC-001 | DEL-001 | orchestrator | CHECK-001 | orchestrator | covered |",
            "| REQ-001 | SRC-001 | DEL-001 | orchestrator | WAIVED by project discretion | orchestrator | covered |",
            1,
        )
    )
    corruptions["skipped required verification"] = check(
        root_text=root.replace(
            "| REQ-001 | SRC-001 | DEL-001 | orchestrator | CHECK-001 | orchestrator | covered |",
            "| REQ-001 | SRC-001 | DEL-001 | orchestrator | SKIPPED by project discretion | orchestrator | covered |",
            1,
        )
    )
    corruptions["reasoned N/A in non-first hard table cell"] = check(
        root_text=root.replace(
            "| BOUND-001 | in scope | validation | self test | orchestrator |",
            "| BOUND-001 | in scope | N/A because this boundary was waived | self test | orchestrator |",
            1,
        )
    )
    missing_module = dict(modules); missing_module.pop("M10.md")
    corruptions["missing M file"] = check(module_texts=missing_module)
    corruptions["missing indexed step"] = check(step_texts={})
    bad_action = dict(modules)
    bad_action["M05.md"] = bad_action["M05.md"].replace("| 10 | M05-A10 |", "| 10 | M05-A9 |", 1)
    corruptions["module action inventory"] = check(module_texts=bad_action)
    copied_action_step = dict(steps); copied_action_step["STEP-001.md"] += "\nM05-A1\n"
    corruptions["step copies module process"] = check(step_texts=copied_action_step)
    bad_gate = dict(steps)
    bad_gate["STEP-001.md"] = bad_gate["STEP-001.md"].replace("| GATE-001 / LOOP-001 | PRODUCT |", "| GATE-001 / LOOP-001 | ADVISORY |", 1)
    corruptions["gate class"] = check(step_texts=bad_gate)
    bare_card = dict(modules)
    bare_card["M05.md"] = bare_card["M05.md"].replace("| objective | self-test concrete objective |", "| objective | N/A |", 1)
    corruptions["bare dispatch field"] = check(module_texts=bare_card)
    missing_card = dict(modules)
    missing_card["M05.md"] = missing_card["M05.md"].replace("##### Governing task card: CARD-NORMAL-G", "##### Member task card: CARD-NORMAL-G", 1)
    corruptions["missing governing card"] = check(module_texts=missing_card)
    bad_member_actions = dict(modules)
    bad_member_actions["M05.md"] = bad_member_actions["M05.md"].replace("| ordered_actions | M05-A1 |", "| ordered_actions | M05-A2; M05-A1 |", 1)
    corruptions["member action order"] = check(module_texts=bad_member_actions)
    duplicate_card = dict(modules)
    duplicate_card["M05.md"] = duplicate_card["M05.md"].replace("##### Member task card: CARD-NORMAL-M", "##### Member task card: CARD-NORMAL-G", 1)
    corruptions["duplicate task-card ID"] = check(module_texts=duplicate_card)
    missing_entry = dict(steps)
    missing_entry["STEP-001.md"] = missing_entry["STEP-001.md"].replace(
        "| FAST_LANE_V2_SERIES_2 | activates when this step is current progress bound |",
        "| FAST_LANE_V2_SERIES_X | activates when this step is current progress bound |",
        1,
    )
    corruptions["missing exact STEP entry"] = check(step_texts=missing_entry)
    missing_usage_block = dict(steps)
    missing_usage_block["STEP-001.md"] = missing_usage_block["STEP-001.md"].replace(
        STEP_FAST_LANE_CANONICAL_BLOCK + "\n\n", "", 1
    )
    corruptions["missing canonical FAST_LANE_V2 usage block"] = check(step_texts=missing_usage_block)
    altered_usage_block = dict(steps)
    altered_usage_block["STEP-001.md"] = altered_usage_block["STEP-001.md"].replace(
        "avoid redoing heavy computations", "avoid repeated work", 1
    )
    corruptions["altered canonical FAST_LANE_V2 usage block"] = check(step_texts=altered_usage_block)
    disabled_fast_lane = dict(steps)
    disabled_fast_lane["STEP-001.md"] = disabled_fast_lane["STEP-001.md"].replace(
        "activates after complete pool and scoped correction objective",
        "INELIGIBLE; use normal route",
        1,
    )
    corruptions["INELIGIBLE fast-lane escape hatch"] = check(step_texts=disabled_fast_lane)
    alternate_opt_out = dict(steps)
    alternate_opt_out["STEP-001.md"] = alternate_opt_out["STEP-001.md"].replace(
        "activates after complete pool and scoped correction objective", "DISABLED; use normal route", 1
    )
    corruptions["alternate fast-lane opt-out"] = check(step_texts=alternate_opt_out)
    negative_modality_opt_out = dict(steps)
    negative_modality_opt_out["STEP-001.md"] = negative_modality_opt_out["STEP-001.md"].replace(
        "accepted integrated repaired output after independent review and integration",
        "accepted integrated repaired output after independent review and integration; must never execute",
        1,
    )
    corruptions["negative-modality fast-lane opt-out"] = check(step_texts=negative_modality_opt_out)
    impossible_fast_lane = dict(steps)
    impossible_fast_lane["STEP-001.md"] = impossible_fast_lane["STEP-001.md"].replace(
        "activates after complete pool and scoped correction objective",
        "literal false condition; never activates despite complete pool and correction objective",
        1,
    )
    corruptions["unsatisfiable fast-lane activation"] = check(step_texts=impossible_fast_lane)
    prohibited_fast_lane = dict(steps)
    prohibited_fast_lane["STEP-001.md"] = prohibited_fast_lane["STEP-001.md"].replace(
        "activates after complete pool and scoped correction objective",
        "activates after complete pool and scoped correction objective; execution prohibited for all events",
        1,
    )
    corruptions["prohibited fast-lane activation"] = check(step_texts=prohibited_fast_lane)
    prose_mi_path = dict(steps)
    prose_mi_path["STEP-001.md"] = prose_mi_path["STEP-001.md"].replace(
        "| MI-FL2-S1-REPAIR-EXIT | accepted integrated repaired output",
        "| do not run MI-FL2-S1-REPAIR-EXIT | accepted integrated repaired output",
        1,
    )
    corruptions["prose-disguised MI path"] = check(step_texts=prose_mi_path)
    reused_entry_mi = dict(steps)
    reused_entry_mi["STEP-001.md"] = reused_entry_mi["STEP-001.md"].replace(
        "| FAST_LANE_V2_SERIES_2 | activates when this step is current progress bound | accepted Series 1 exits | MI-FL2-S2-RECONCILE |",
        "| FAST_LANE_V2_SERIES_2 | activates when this step is current progress bound | accepted Series 1 exits | MI-FL2-S1-REPAIR-EXIT |",
        1,
    )
    corruptions["STEP entry MI reuse"] = check(step_texts=reused_entry_mi)
    wrong_prefix_modules = dict(modules)
    wrong_prefix_modules["M05.md"] = wrong_prefix_modules["M05.md"].replace(
        "MI-FL2-S1-REPAIR-EXIT", "MI-WRONG-S1-REPAIR-EXIT"
    )
    wrong_prefix_steps = dict(steps)
    wrong_prefix_steps["STEP-001.md"] = wrong_prefix_steps["STEP-001.md"].replace(
        "MI-FL2-S1-REPAIR-EXIT", "MI-WRONG-S1-REPAIR-EXIT"
    )
    wrong_prefix_global = global_rules.replace(
        "MI-FL2-S1-REPAIR-EXIT", "MI-WRONG-S1-REPAIR-EXIT"
    )
    corruptions["STEP entry wrong MI prefix"] = check(
        global_text=wrong_prefix_global,
        module_texts=wrong_prefix_modules,
        step_texts=wrong_prefix_steps,
    )
    broad_fast_lane = dict(steps)
    broad_fast_lane["STEP-001.md"] = broad_fast_lane["STEP-001.md"].replace(
        "saved broad campaign work", "ordinary work", 1
    )
    corruptions["Series 1 without saved broad work"] = check(step_texts=broad_fast_lane)
    na_gate = dict(steps)
    na_gate["STEP-001.md"] = na_gate["STEP-001.md"].replace(
        "| GATE-001 / LOOP-001 | PRODUCT |", "| N/A | PRODUCT |", 1
    )
    corruptions["N/A STEP gate"] = check(step_texts=na_gate)
    uncovered_step = dict(steps)
    uncovered_step["STEP-001.md"] = uncovered_step["STEP-001.md"].replace(
        "DEL-001 and REQ-001", "DEL-001 without requirement coverage", 1
    )
    corruptions["uncovered requirement"] = check(step_texts=uncovered_step)
    bare_policy = global_rules.replace(
        "| orchestrator | checkpoint and FAST_LANE_V2 |",
        "| N/A | checkpoint and FAST_LANE_V2 |",
        1,
    )
    corruptions["bare mandatory policy owner"] = check(global_text=bare_policy)
    unknown_policy_instance = global_rules.replace("MI-NORMAL-ACCEPT", "MI-NORMAL-UNKNOWN", 1)
    corruptions["unknown policy MI reference"] = check(global_text=unknown_policy_instance)
    bare_instance = dict(modules)
    bare_instance["M05.md"] = bare_instance["M05.md"].replace(
        "#### Purpose\n\nSelf-test concrete value.", "#### Purpose\n\nN/A", 1
    )
    corruptions["bare instance field"] = check(module_texts=bare_instance)
    empty_public_interface = dict(modules)
    empty_public_interface["M05.md"] = empty_public_interface["M05.md"].replace(
        "Stable typed input and output; internal process changes preserve this public contract.", "", 1
    )
    corruptions["empty module public interface"] = check(module_texts=empty_public_interface)
    bare_rule_basis = validation_doc.replace(
        "| R1 | validation.md Section 15 row R1 | Concrete R1 behavior is applied by the self-test package and validator checks |",
        "| R1 | validation.md Section 15 row R1 | N/A because this condition does not require the rule here |",
        1,
    )
    corruptions["bare rule-matrix basis"] = check(validation_text=bare_rule_basis)
    no_member_cards = dict(modules)
    no_member_cards["M05.md"] = re.sub(
        r"(?ms)^##### Member task card: CARD-[^\n]+\n.*?(?=^##### |^### |\Z)", "", no_member_cards["M05.md"]
    )
    corruptions["missing all member dispatch cards"] = check(module_texts=no_member_cards)
    reasoned_na_card = dict(modules)
    reasoned_na_card["M05.md"] = reasoned_na_card["M05.md"].replace(
        "| objective | self-test concrete objective |",
        "| objective | N/A because recipe condition does not require any objective |",
        1,
    )
    corruptions["reasoned N/A in mandatory task field"] = check(module_texts=reasoned_na_card)
    bare_none_card = dict(modules)
    bare_none_card["M05.md"] = bare_none_card["M05.md"].replace(
        "| objective | self-test concrete objective |", "| objective | none |", 1
    )
    corruptions["bare none in mandatory task field"] = check(module_texts=bare_none_card)
    omitted_hard_outcome = root.replace(
        "| OUT-001 | valid plan behavior |",
        "| OUT-001 | OMITTED because the author calls this required behavior unnecessary |",
        1,
    )
    corruptions["omitted hard outcome behavior"] = check(root_text=omitted_hard_outcome)
    malformed_extra_outcome = root.replace(
        "| OUT-001 | valid plan behavior | validator pass | orchestrator | covered |",
        "| OUT-001 | valid plan behavior | validator pass | orchestrator | covered |\n"
        "| OUT-BAD? | hidden required behavior | validator pass | orchestrator | covered |",
        1,
    )
    corruptions["malformed extra outcome ID"] = check(root_text=malformed_extra_outcome)
    empty_identity = dict(modules)
    empty_identity["M05.md"] = empty_identity["M05.md"].replace(
        "stage_cohort_id=COHORT-001", "stage_cohort_id=", 1
    )
    corruptions["empty identity assignment"] = check(module_texts=empty_identity)
    self_certified_basis = validation_doc.replace(
        "Concrete R1 behavior is applied by the self-test package and validator checks",
        "Author self-certifies that R1 is satisfied by the package",
        1,
    )
    corruptions["self-certified validation basis"] = check(validation_text=self_certified_basis)
    detached_row = dict(modules)
    detached_row["M05.md"] += "\n| M05 | OMITTED | N/A | detached contradictory decision |\n"
    corruptions["detached pipe-table row"] = check(module_texts=detached_row)
    duplicate_known_table = dict(modules)
    duplicate_known_table["M05.md"] += "\n" + markdown_table(MODULE_SELECTION_TABLE, [[
        "M05", "OMITTED", "N/A", "Contradictory duplicate decision with a substantive explanation",
    ]]) + "\n"
    corruptions["duplicate known schema table"] = check(module_texts=duplicate_known_table)
    missing_member_handoff = dict(modules)
    missing_member_handoff["M05.md"] = missing_member_handoff["M05.md"].replace(
        "orchestrator reviews terminal HANDOFF-NORMAL", "orchestrator reviews terminal result", 1
    )
    corruptions["member card without mandatory handoff"] = check(module_texts=missing_member_handoff)
    missing_member_lane = dict(modules)
    missing_member_lane["M05.md"] = missing_member_lane["M05.md"].replace(
        "self-test workspace resources in LANE-NORMAL", "self-test workspace resources", 1
    )
    corruptions["member card without mandatory lane"] = check(module_texts=missing_member_lane)
    worker_step_owner_root = root.replace(
        "| STEP-001 | steps/STEP-001.md | candidate | accepted result | GATE-001 | orchestrator |",
        "| STEP-001 | steps/STEP-001.md | candidate | accepted result | GATE-001 | worker |",
        1,
    )
    worker_step_owner_steps = dict(steps)
    worker_step_owner_steps["STEP-001.md"] = worker_step_owner_steps["STEP-001.md"].replace(
        "| Acceptance owner | orchestrator |", "| Acceptance owner | worker |", 1
    )
    corruptions["worker assigned STEP acceptance"] = check(
        root_text=worker_step_owner_root, step_texts=worker_step_owner_steps
    )
    self_handoff_root = root.replace(
        "| LANE-NORMAL | MI-NORMAL-ACCEPT | worker | member dispatch | read only | orchestrator |",
        "| LANE-NORMAL | MI-NORMAL-ACCEPT | worker | member dispatch | read only | worker |",
        1,
    ).replace(
        "| HANDOFF-NORMAL | worker | orchestrator |",
        "| HANDOFF-NORMAL | worker | worker |",
        1,
    )
    corruptions["member self-consumes terminal handoff"] = check(root_text=self_handoff_root)
    empty_step_activation = dict(steps)
    empty_step_activation["STEP-001.md"] = empty_step_activation["STEP-001.md"].replace(
        "Candidate input is ready and protected boundaries are fixed.", "", 1
    )
    corruptions["empty STEP activation contract"] = check(step_texts=empty_step_activation)
    missing_step_successor = dict(steps)
    missing_step_successor["STEP-001.md"] = missing_step_successor["STEP-001.md"].replace(
        "Accepted result advances through EDGE-001 to terminal.",
        "Fictional output advances to a fictional destination.",
        1,
    )
    corruptions["STEP without typed successor"] = check(step_texts=missing_step_successor)
    duplicate_gate_index = root.replace(
        "| GATE-001 | STEP-001 | steps/STEP-001.md | PRODUCT | required plan behavior | EDGE-001 terminal | STEP-001 return route |",
        "| GATE-001 | STEP-001 | steps/STEP-001.md | PRODUCT | required plan behavior | EDGE-001 terminal | STEP-001 return route |\n"
        "| GATE-001 | STEP-001 | steps/STEP-001.md | PRODUCT | required plan behavior | EDGE-001 terminal | STEP-001 return route |",
        1,
    )
    corruptions["duplicate Section 8 gate index"] = check(root_text=duplicate_gate_index)
    worker_governing_card = dict(modules)
    worker_governing_card["M05.md"] = worker_governing_card["M05.md"].replace(
        "| workflow_role | orchestrator |", "| workflow_role | worker |", 1
    )
    corruptions["worker role on governing card"] = check(module_texts=worker_governing_card)
    root_member_card = dict(modules)
    root_member_card["M05.md"] = root_member_card["M05.md"].replace(
        "CARD-NORMAL-M=worker", "CARD-NORMAL-M=orchestrator", 1
    ).replace(
        "| workflow_role | worker |", "| workflow_role | orchestrator |", 1
    )
    root_member_manifest = root.replace(
        "| LANE-NORMAL | MI-NORMAL-ACCEPT | worker |", "| LANE-NORMAL | MI-NORMAL-ACCEPT | orchestrator |", 1
    ).replace(
        "| HANDOFF-NORMAL | worker | orchestrator |", "| HANDOFF-NORMAL | orchestrator | orchestrator |", 1
    )
    corruptions["ROOT role on member dispatch"] = check(
        root_text=root_member_manifest, module_texts=root_member_card
    )
    unknown_card_references = dict(modules)
    unknown_card_references["M05.md"] = unknown_card_references["M05.md"].replace(
        "deliverable_id=DEL-001; stage_cohort_id=COHORT-001; gate_id=GATE-001; loop_id=LOOP-001",
        "deliverable_id=DEL-BOGUS; stage_cohort_id=COHORT-001; gate_id=GATE-BOGUS; loop_id=LOOP-BOGUS",
        1,
    )
    corruptions["unknown task-card graph references"] = check(module_texts=unknown_card_references)
    missing_process_id = dict(modules)
    missing_process_id["M05.md"] = missing_process_id["M05.md"].replace("PROCESS-NORMAL", "process record", 1)
    corruptions["member card without PROCESS ID"] = check(module_texts=missing_process_id)
    worker_owned_p01 = global_rules.replace(
        "| orchestrator | checkpoint and FAST_LANE_V2 |",
        "| worker | checkpoint and FAST_LANE_V2 |",
        1,
    )
    corruptions["P01 without ROOT-owned row"] = check(global_text=worker_owned_p01)
    fast_contract_opt_out = dict(modules)
    fast_contract_opt_out["M05.md"] = fast_contract_opt_out["M05.md"].replace(
        "and returns an accepted exit to the progress bound.",
        "and returns an accepted exit to the progress bound. FAST_LANE_V2 Series 1 path is optional.",
        1,
    )
    corruptions["fast-lane MI contract opt-out"] = check(module_texts=fast_contract_opt_out)
    actual_exception_na = global_rules.replace(
        "| N/A | No exception classes are declared because the self-test uses only normal policy routes | none declared | orchestrator | no alternate action | no confirmation required | all results preserved | no results invalidated | self-test package | plan completion |",
        "| EXC-001 | P01 | exact alternate trigger | orchestrator | bounded alternate action | N/A because confirmation was waived | all results preserved | exact result invalidated | self-test package | plan completion |",
        1,
    )
    corruptions["reasoned N/A in actual exception"] = check(global_text=actual_exception_na)
    unresolved_root = root.replace(
        "| N/A | No unresolved item is retained because every self-test input is fixed and known |",
        "| LEDGER-001 | BLOCKING_INPUT | required choice pending | validation cannot decide | orchestrator | later |",
        1,
    )
    corruptions["disguised blocking item in valid package"] = check(root_text=unresolved_root)
    omitted_m05 = dict(modules)
    omitted_m05["M05.md"] = omitted_m05["M05.md"].replace(
        "| M05 | SELECTED | MI-NORMAL-ACCEPT, MI-FL2-S1-REPAIR-EXIT, MI-FL2-S2-RECONCILE |",
        "| M05 | OMITTED | N/A |",
        1,
    )
    corruptions["omitted mandatory M05"] = check(module_texts=omitted_m05)
    deferred_module = dict(modules)
    deferred_module["M01.md"] = deferred_module["M01.md"].replace("| M01 | OMITTED |", "| M01 | DEFERRED |", 1)
    corruptions["deferred optional module decision"] = check(module_texts=deferred_module)
    ineligible_omitted_ids = dict(modules)
    ineligible_omitted_ids["M01.md"] = ineligible_omitted_ids["M01.md"].replace(
        "| M01 | OMITTED | N/A |", "| M01 | OMITTED | INELIGIBLE |", 1
    )
    corruptions["ineligible label in omitted module instance IDs"] = check(module_texts=ineligible_omitted_ids)
    reasoned_na_module_decision = dict(modules)
    reasoned_na_module_decision["M01.md"] = reasoned_na_module_decision["M01.md"].replace(
        "Self-test module decision based on concrete package facts",
        "N/A because this optional module was omitted by project judgment",
        1,
    )
    corruptions["N/A optional-module decision reason"] = check(module_texts=reasoned_na_module_decision)
    hard_na_root = root.replace(
        "| OUT-001 | valid plan behavior | validator pass | orchestrator | covered |",
        "| N/A | No required outcome exists because this justification attempts to waive the hard outcome table | validator pass | orchestrator | covered |",
        1,
    )
    corruptions["explained N/A in hard outcome table"] = check(root_text=hard_na_root)
    corruptions["mapping-role mismatch"] = check(roles={"different-role"})
    nested_authority = root.replace("| Orchestration topology | ROOT_DIRECT_WORKERS |", "| Orchestration topology | ROOT_WITH_LANE_SUB_ORCHESTRATORS |", 1)
    nested_authority = nested_authority.replace(
        "| orchestrator | ROOT | N/A | worker | accept | 1 | bounded | none | none | plan ready | plan |\n"
        "| worker | WORKER | orchestrator | N/A | execute | 1 | bounded | source | workspace | dispatched | task |",
        "| orchestrator | ROOT | N/A | lane | accept | 1 | bounded | none | none | plan ready | plan |\n"
        "| lane | LANE_SUB_ORCHESTRATOR | orchestrator | nested | direct lane | 1 | bounded | none | lane | dispatched | lane |\n"
        "| nested | LANE_SUB_ORCHESTRATOR | lane | worker | direct nested lane | 1 | bounded | none | nested lane | dispatched | lane |\n"
        "| worker | WORKER | nested | N/A | execute | 1 | bounded | source | workspace | dispatched | task |",
        1,
    )
    corruptions["third orchestration tier"] = check(
        root_text=nested_authority,
        roles={"orchestrator", "lane", "nested", "worker"},
    )
    shallow_lane = root.replace(
        "| Orchestration topology | ROOT_DIRECT_WORKERS |", "| Orchestration topology | ROOT_WITH_LANE_SUB_ORCHESTRATORS |", 1
    ).replace(
        "| orchestrator | ROOT | N/A | worker | accept | 1 | bounded | none | none | plan ready | plan |\n"
        "| worker | WORKER | orchestrator | N/A | execute | 1 | bounded | source | workspace | dispatched | task |",
        "| orchestrator | ROOT | N/A | lane | accept | 1 | bounded | none | none | plan ready | plan |\n"
        "| lane | LANE_SUB_ORCHESTRATOR | orchestrator | worker | x | 1 | x | x | x | x | x |\n"
        "| worker | WORKER | lane | N/A | execute | 1 | bounded | source | workspace | dispatched | task |",
        1,
    )
    corruptions["lane sub-orchestrator without full contract"] = check(
        root_text=shallow_lane, roles={"orchestrator", "lane", "worker"}
    )
    corruptions["duplicate mapping path"] = check(root_text=root + "\nmapping.json\n")
    corruptions["wrong mapping location"] = check(
        root_text=root.replace("| Agent mapping | mapping.json |", "| Agent mapping | wrong/mapping.json |", 1)
    )
    corruptions["worker as global decision owner"] = check(
        root_text=root.replace("| Decision owner | orchestrator |", "| Decision owner | worker |", 1)
    )
    corruptions["worker as requirement acceptance owner"] = check(
        root_text=root.replace("| CHECK-001 | orchestrator | covered |", "| CHECK-001 | worker | covered |", 1)
    )
    bad_policy = dict(modules)
    bad_policy["M05.md"] = bad_policy["M05.md"].replace("P01-P15", "P98", 1)
    corruptions["unknown module policy"] = check(module_texts=bad_policy)
    bad_owner = dict(modules)
    bad_owner["M05.md"] = bad_owner["M05.md"].replace("| orchestrator |", "| unknown-owner |", 1)
    corruptions["unknown module decision owner"] = check(module_texts=bad_owner)
    corruptions["bounded agent session"] = check(
        global_text=global_rules + "\nAgent and subagent sessions have a 30-second maximum lifetime.\n"
    )
    corruptions["mixed bounded agent session exception"] = check(
        global_text=global_rules
        + "\nAgent sessions are unbounded, but review agent sessions have a 30-second deadline.\n"
    )
    corruptions["role-named bounded invocation"] = check(
        global_text=global_rules + "\nReviewer invocations have a 30-second deadline.\n"
    )
    corruptions["bounded session within duration"] = check(
        global_text=global_rules + "\nAgent sessions must finish within 30 seconds.\n"
    )
    corruptions["agent session bounded to duration"] = check(
        global_text=global_rules + "\nAgent sessions are bounded to 30 seconds.\n"
    )
    if optional_decision_error("OMITTED: project facts show this profile adds no useful behavior"):
        failures.append("valid optional-profile omission decision was rejected")
    if not optional_decision_error("INELIGIBLE"):
        failures.append("ineligible optional-profile pseudo-decision was accepted")
    if optional_decision_error("SELECTED: execute the concrete selected profile action", selected_requires_detail=True):
        failures.append("valid selected internal-profile action was rejected")
    if not optional_decision_error("SELECTED", selected_requires_detail=True):
        failures.append("selected internal-profile action without concrete process was accepted")
    profile_sections = {
        HEADINGS[12]: markdown_table(REQUIRED_TABLES[HEADINGS[12]][0], [[
            "EXT-001", "M08", "SELECTED", "authorized fake resource", "readiness proof",
            "real operation remains separate", "orchestrator", "block exact operation",
        ]]),
        HEADINGS[13]: markdown_table(REQUIRED_TABLES[HEADINGS[13]][0], [[
            "N/A", "No integration profile is required because this isolated profile test selects only M08",
            "none", "none", "none", "none", "none", "orchestrator",
        ]]),
    }
    profile_action_rows = []
    for action_id in MODULE_ACTIONS["M08"]:
        process = f"execute {action_id} concrete process"
        if action_id == "M08-A2":
            process = "SELECTED: execute concrete recordability preflight"
        if action_id == "M08-A3":
            process = "OMITTED: project facts contain no external control-flow operation"
        profile_action_rows.append(["1", action_id, process, "fixed", "orchestrator"])
    profile_modules = {"M08.md": markdown_table(MODULE_ACTION_TABLE, profile_action_rows)}
    if profile_errors := validate_optional_profile_decisions(
        profile_sections, profile_modules, {"MI-PROFILE-TEST": "M08"}
    ):
        failures.append("valid optional-profile decisions failed: " + "; ".join(profile_errors))
    missing_profile_sections = dict(profile_sections)
    missing_profile_sections[HEADINGS[12]] = markdown_table(REQUIRED_TABLES[HEADINGS[12]][0], [[
        "N/A", "No external profile is recorded because this corruption hides a selected M08 decision",
        "none", "none", "none", "none", "orchestrator", "terminal",
    ]])
    if not validate_optional_profile_decisions(
        missing_profile_sections, profile_modules, {"MI-PROFILE-TEST": "M08"}
    ):
        failures.append("selected M08 without a Section 12 decision row was accepted")
    omitted_only_profile_sections = dict(profile_sections)
    omitted_only_profile_sections[HEADINGS[12]] = markdown_table(REQUIRED_TABLES[HEADINGS[12]][0], [[
        "EXT-001", "M08", "OMITTED: author declines to materialize the selected readiness behavior",
        "N/A", "N/A", "N/A", "orchestrator", "terminal",
    ]])
    if not validate_optional_profile_decisions(
        omitted_only_profile_sections, profile_modules, {"MI-PROFILE-TEST": "M08"}
    ):
        failures.append("selected M08 with only OMITTED Section 12 behavior rows was accepted")
    hollow_selected_profile_sections = dict(profile_sections)
    hollow_selected_profile_sections[HEADINGS[12]] = markdown_table(REQUIRED_TABLES[HEADINGS[12]][0], [[
        "EXT-001", "M08", "SELECTED", "authorized fake resource", "N/A",
        "real operation remains separate", "orchestrator", "block exact operation",
    ]])
    if not validate_optional_profile_decisions(
        hollow_selected_profile_sections, profile_modules, {"MI-PROFILE-TEST": "M08"}
    ):
        failures.append("selected M08 behavior with an N/A synthetic proof was accepted")
    for label, errors in corruptions.items():
        if not errors:
            failures.append(f"{label} corruption was not detected")
    with tempfile.TemporaryDirectory() as temp_dir:
        package = Path(temp_dir)
        for filename in ("plan-workflow.md", "global-rules.md", "validation.md"):
            (package / filename).write_text("self-test\n", encoding="utf-8")
        (package / "steps").mkdir()
        (package / "modules").mkdir()
        (package / "unexpected.bin").write_bytes(b"unexpected")
        package_errors = load_package(package)[-1]
        if "unexpected root package file: unexpected.bin" not in package_errors:
            failures.append("extra non-Markdown package file was not detected")
        empty_mapping = package / "empty-mapping.json"
        empty_mapping.write_text(json.dumps({"roles": {"worker": {"provider": ""}}}), encoding="utf-8")
        if not load_mapping(empty_mapping)[1]:
            failures.append("empty provider/runtime launch selection was not detected")
        placeholder_mapping = package / "placeholder-mapping.json"
        placeholder_mapping.write_text(
            json.dumps({"roles": {"worker": {"provider": "N/A", "runtime": "TBD later"}}}),
            encoding="utf-8",
        )
        if not load_mapping(placeholder_mapping)[1]:
            failures.append("placeholder provider/runtime launch selection was not detected")
        omitted_mapping = package / "omitted-mapping.json"
        omitted_mapping.write_text(
            json.dumps({"roles": {"worker": {"provider": "OMITTED"}}}), encoding="utf-8"
        )
        if not load_mapping(omitted_mapping)[1]:
            failures.append("omitted provider/runtime launch selection was not detected")
    return failures


def load_mapping(path: Path) -> tuple[set[str], list[str]]:
    try:
        data: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return set(), [f"cannot read role-agent mapping {path}: {exc}"]
    if not isinstance(data, dict) or not isinstance(data.get("roles"), dict):
        return set(), ["role-agent mapping must be a JSON object containing a roles object"]
    roles = data["roles"]
    errors: list[str] = []
    launch_key_re = re.compile(r"(?:provider|model|agent|command|profile|effort|tier|selector|runtime)", re.IGNORECASE)
    invalid_launch_re = re.compile(
        r"\b(?:N/?A|not\s+applicable|TBD|TODO|UNKNOWN|DEFERRED|INELIGIBLE|not\s+required|"
        r"NONE|DISABLED|SKIPPED|OMITTED|UNAVAILABLE|waiv(?:e|ed|er)|exempt(?:ed|ion)?|"
        r"self[- ]certif(?:y|ies|ied|ication))\b",
        re.IGNORECASE,
    )

    def launch_scalar_values(value: Any) -> list[str]:
        if isinstance(value, dict):
            return [item for child in value.values() for item in launch_scalar_values(child)]
        if isinstance(value, list):
            return [item for child in value for item in launch_scalar_values(child)]
        return [str(value)] if value is not None else []

    for role, value in roles.items():
        if not isinstance(value, dict) or not value:
            errors.append(f"mapping role {role!r} must contain a nonempty agent-selection object")
            continue
        launch_values = [item for key, item in value.items() if launch_key_re.search(str(key))]
        if not launch_values or not any(
            (isinstance(item, str) and bool(item.strip()))
            or (isinstance(item, (int, float, bool)))
            or (isinstance(item, (dict, list)) and bool(item))
            for item in launch_values
        ):
            errors.append(
                f"mapping role {role!r} has no nonempty provider/runtime launch-selection field"
            )
        invalid_values = [
            scalar for item in launch_values for scalar in launch_scalar_values(item)
            if invalid_launch_re.search(scalar)
        ]
        if invalid_values:
            errors.append(f"mapping role {role!r} uses a placeholder or waiver in launch selection")
    if not roles:
        errors.append("role-agent mapping contains no roles")
    return set(roles), errors


def load_package(path: Path) -> tuple[str, str, str, dict[str, str], dict[str, str], list[str]]:
    errors: list[str] = []
    if not path.is_dir():
        return "", "", "", {}, {}, [f"execution plan path must be a package directory: {path}"]
    required_files = ("plan-workflow.md", "global-rules.md", "validation.md")
    texts: dict[str, str] = {}
    for filename in required_files:
        file_path = path / filename
        try:
            texts[filename] = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            errors.append(f"cannot read required package file {file_path}: {exc}")

    for entry in path.iterdir():
        if entry.is_dir() and entry.name not in {"steps", "modules"}:
            errors.append(f"unexpected package directory: {entry.name}")
        if entry.is_file() and entry.name not in required_files:
            errors.append(f"unexpected root package file: {entry.name}")

    child_texts: dict[str, dict[str, str]] = {"steps": {}, "modules": {}}
    for dirname in ("steps", "modules"):
        directory = path / dirname
        if not directory.is_dir():
            errors.append(f"missing required package directory: {dirname}/")
            continue
        for entry in directory.iterdir():
            if not entry.is_file() or entry.suffix.lower() != ".md":
                errors.append(f"unexpected item in {dirname}/: {entry.name}")
                continue
            try:
                child_texts[dirname][entry.name] = entry.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as exc:
                errors.append(f"cannot read {entry}: {exc}")
    return (
        texts.get("plan-workflow.md", ""),
        texts.get("global-rules.md", ""),
        texts.get("validation.md", ""),
        child_texts["steps"],
        child_texts["modules"],
        errors,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a modular execution-plan package's deterministic structure.")
    parser.add_argument("plan", nargs="?", help="generated execution-plan package directory")
    parser.add_argument("--mapping", help="canonical role-agent mapping JSON path")
    parser.add_argument("--self-test", action="store_true", help="run validator contract tests")
    args = parser.parse_args()

    if args.self_test:
        failures = run_self_test()
        if failures:
            for failure in failures:
                print(f"SELF-TEST ERROR: {failure}", file=sys.stderr)
            return 1
        print("execution plan validator self-test: PASS")
        return 0

    if args.plan is None or args.mapping is None:
        parser.error("plan and --mapping are required unless --self-test is used")
    mapping_path = Path(args.mapping)
    mapping_roles, mapping_errors = load_mapping(mapping_path)
    if mapping_errors:
        for error in mapping_errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    root_text, global_text, validation_text, step_texts, module_texts, package_errors = load_package(Path(args.plan))
    errors = package_errors
    if not errors:
        errors = validate_package_texts(
            root_text,
            global_text,
            validation_text,
            step_texts,
            module_texts,
            mapping_roles,
            mapping_path.name,
            mapping_path,
            Path(args.plan),
        )
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("execution plan validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
