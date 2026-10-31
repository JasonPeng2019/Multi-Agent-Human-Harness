"""Bootstrap one lane with a full memory handoff for a local demo.

    python3 -m orchestrator_harness.tests.memory_demo \
        --lane-id fix-average --task-card <card.json> \
        --provider claude-code --model sonnet --effort low

The ordinary ``lane bootstrap`` command passes no memory search stores.  This
demo builds the two trusted sources the MVP uses and hands them to the real
bootstrap:

* an EverOS generated stored skill (EverOS service replaced by the product's
  in-process test double), and
* an Atlas shared procedure found by vector search (Atlas collection and
  vector index replaced by the product's in-process test doubles).

Everything after retrieval is the real product path: eligibility checks, the
ROOT-accepted plan bound to both sources, the bounded final context, the
worker prompt, and the lane's durable memory store.  Launch, review, and
retire then use the normal ``operator_launch`` commands.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Callable

PRODUCT = Path(__file__).resolve().parents[3]
for entry in (PRODUCT / "src", PRODUCT):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

from memory_harness import atlas, atlas_adapters, contracts, everos_adapters  # noqa: E402
from tests.local.preparation import (  # noqa: E402
    test_step04_atlas_search_adapters as atlas_fixture,
    test_step04_everos_generated_skill_store as everos_fixture,
)

from orchestrator_harness import bootstrap  # noqa: E402
from orchestrator_harness.config import find_harness_root, load_config  # noqa: E402
from orchestrator_harness.core import iso_utc  # noqa: E402
from orchestrator_harness.records import atomic_write_json  # noqa: E402

EVEROS_GUIDANCE = (
    "Lesson from a past run: when an average or mean is wrong, check the divisor "
    "first; it must be len(values), never len(values) + 1. "
    "EVEROS_MVP_MARKER=check-the-divisor"
)
ATLAS_GUIDANCE = (
    "Shared procedure: after fixing calc.py, run `python3 -m unittest -v` and put "
    "its exact summary line in RESULT.json evidence. "
    "ATLAS_MVP_MARKER=prove-with-unittest"
)
SEARCH_TEXT = "fix average bug calc py divisor mean unittest tests pass commit result"


class _Sources(unittest.TestCase):
    """Build both trusted sources with the product's own accepted fixtures."""

    def runTest(self) -> None:  # pragma: no cover - required by TestCase
        pass

    def build(
        self,
        *,
        task: str,
        base_commit: str,
        branch: str,
        progress: Callable[[str], None] | None = None,
    ) -> tuple[dict, tuple]:
        if progress is not None:
            progress("Recall")
        self.everos = everos_fixture.Step04EverOSGeneratedSkillStoreTests()
        self.everos.setUp()
        self.addCleanup(self.everos.tearDown)
        receiver, limits = self.everos.receiver, self.everos.limits

        skill, _approval, everos_procedure = self.everos._generated_artifacts(
            "average-divisor-lesson", content=EVEROS_GUIDANCE,
        )
        self.everos.fake.skill_results = [self.everos._skill(skill)]
        everos_store = everos_adapters.make_everos_generated_skill_search_store(
            experience_service=self.everos.experience_service,
            procedure_service=self.everos.procedure_service,
            memory_store=self.everos.memory_store,
            adapter=self.everos.adapter,
            scope=self.everos.scope,
            receiver=receiver,
            facts={"language": "python"},
            route="ordinary",
            limits=limits,
        )

        atlas_procedure = contracts.make_procedure_revision(
            logical_name="prove-fix-with-unittest",
            origin="curated",
            origin_scope=receiver,
            body=ATLAS_GUIDANCE,
            references=[{"id": "guide://unittest", "content": "Run the unit tests."}],
            predicates={
                "applicability": {"all": [
                    {"field": "language", "operator": "equals", "value": "python"}
                ]},
                "conflicts": {}, "capabilities": {},
                "routes": {"all": [
                    {"field": "route", "operator": "equals", "value": "ordinary"}
                ]},
            },
            source={"kind": "curated_authoring", "provenance_ref": "curation://demo"},
        )
        approval = contracts.make_procedure_approval(
            approval_id="demo-atlas-approval",
            procedure=atlas_procedure,
            issuer="ROOT",
            recipients=[receiver],
            authority_evidence={"policy_id": "trusted-root/v1", "subject": "root"},
        )
        owner = self.everos.procedure_service
        owner.record_approved_revision(atlas_procedure, approval)
        representation = self.everos._representation(atlas_procedure, search_text=SEARCH_TEXT)
        owner.record_representation(representation)
        designation = owner.designate(
            procedure=atlas_procedure, approval=approval,
            partition=self.everos.partition, issuer="ROOT",
        )
        self.vector_store = atlas_fixture._VectorStore()
        adapter = atlas.AtlasProcedureAdapter(
            collection=atlas_fixture._Collection(), vector_store=self.vector_store,
        )
        owner.publish_designation(designation, adapter)
        publication = owner.publish(
            procedure=atlas_procedure, approval=approval,
            representation=representation, designation=designation, adapter=adapter,
        )
        self.vector_store.publication_ids.append(publication["publication_id"])
        atlas_store = atlas_adapters.make_atlas_search_store(
            procedure_service=owner, adapter=adapter, receiver=receiver,
            facts={"language": "python"}, route="ordinary", limits=limits,
        )

        if progress is not None:
            progress("Vet")
            progress("Plan")
        plan = contracts.make_plan(
            plan_id="demo-accepted-plan",
            objective_id="fix-average-divisor",
            route="ordinary",
            state="accepted",
            accepted_by="ROOT",
            content={"steps": [
                "apply the recalled divisor lesson to average() in calc.py",
                "run python3 -m unittest -v and confirm every test passes",
                "commit the fix, then write RESULT.json with the unittest summary",
            ]},
            source={"kind": "selected_memory", "dependencies": [
                {"logical_id": p["logical_id"], "revision_id": p["revision_id"]}
                for p in (everos_procedure, atlas_procedure)
            ]},
        )
        card = contracts.make_task_card(
            task=task,
            base_commit=base_commit,
            branch=branch,
            memory_handoff=contracts.make_memory_handoff(
                objective_id=plan["objective_id"], route="ordinary",
                plan=plan, checkpoint="demo-checkpoint",
            ),
        )
        if progress is not None:
            progress("Pack")
        return card, (everos_store, atlas_store)


def _progress_writer(path: Path | None) -> Callable[[str], None] | None:
    if path is None:
        return None

    def update(phase: str) -> None:
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            existing = {"schema": "harness-demo-progress/v1"}
        existing.update({"phase": phase, "state": "running", "updated_at": iso_utc()})
        atomic_write_json(path, existing)

    return update


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--lane-id", required=True)
    parser.add_argument("--task-card", required=True, help="plain project-task-card/v1 JSON")
    parser.add_argument("--provider", default="claude-code")
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--effort", default="low")
    parser.add_argument("--progress-file", type=Path)
    args = parser.parse_args(argv)

    plain = json.loads(Path(args.task_card).read_text(encoding="utf-8"))
    config = load_config(find_harness_root())
    base = subprocess.run(
        ["git", "-C", str(config.root_workspace), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    sources = _Sources()
    try:
        card, stores = sources.build(
            task=plain["task"], base_commit=base,
            branch=plain.get("branch") or f"lane/{args.lane_id}",
            progress=_progress_writer(args.progress_file),
        )
        card_path = Path(args.task_card).with_name(f"{args.lane_id}.memory-card.json")
        card_path.write_text(json.dumps(card, indent=2), encoding="utf-8")
        result = bootstrap.run_bootstrap(
            lane_id=args.lane_id,
            provider=args.provider,
            model=args.model,
            launch_config={"effort": args.effort},
            exclusive_resources=[],
            task_card_path=str(card_path),
            search_stores=stores,
        )
    finally:
        sources.doCleanups()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
