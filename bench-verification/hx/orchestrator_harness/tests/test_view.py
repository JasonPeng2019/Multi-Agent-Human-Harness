from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from orchestrator_harness import operator_launch, processes, view_render, view_state, view_term
from orchestrator_harness.view_state import DONE, NOW, SKIP, WAIT

NOW_UTC = datetime(2026, 9, 26, 12, 0, 0, tzinfo=timezone.utc)
EPOCH = "e" * 32


def _iso(delta_seconds: float) -> str:
    return (NOW_UTC - timedelta(seconds=delta_seconds)).isoformat()


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


class ViewFixture:
    """A minimal on-disk runtime with four lanes in different steps."""

    def __init__(self, root: Path) -> None:
        self.rt = root / ".harness-runtime"
        self.worktrees = root / "worktrees"
        _write(self.rt / "CURRENT_EPOCH.json", {
            "schema": "current-epoch/v1", "epoch_id": EPOCH, "lane_mode": "managed",
            "queue_id": "q" * 32, "opened_at": _iso(3600),
        })
        _write(self.rt / "epochs" / EPOCH / "epoch-state.json", {
            "schema": "epoch-state/v1", "epoch_id": EPOCH, "lifecycle": "active",
            "lane_mode": "managed", "opened_at": _iso(3600),
        })
        _write(self.rt / "monitor" / "MONITOR.json", {
            "schema": "monitor/v1", "last_heartbeat_at": _iso(8),
        })
        _write(self.rt / "manager" / "QUEUE.json", {
            "schema": "manager-queue/v1", "epoch_id": EPOCH, "queue_id": "q" * 32,
            "events": [{
                "event_id": "ev1", "type": "COMPLETION_REVIEW_REQUIRED", "lane_id": "lane-3",
                "summary": "lane-3 finished, ready for review", "state": "PENDING",
                "history": [{"state": "PENDING", "at": _iso(240)}],
            }],
        })
        me = processes.process_identity(os.getpid())
        self.lanes = [
            self._lane("lane-1", "running", task="Fix date parser regression", memory=True,
                       process={"pid": me["pid"], "creation_time": me["creation_time"]} if me else {}),
            self._lane("lane-2", "prepared", task="Add retry to upload client", memory=False,
                       events=["controller_started", "lease_busy"]),
            self._lane("lane-3", "review_pending", task="Migrate config schema v3", memory=True,
                       recorded="review_pending"),
            self._lane("lane-4", "accepted", task="UART driver timeout", memory=True),
        ]
        _write(self.rt / "epochs" / EPOCH / "active-lanes.json", {
            "schema": "active-lanes/v1", "epoch_id": EPOCH,
            "lanes": [{"lane_id": lane["lane_id"], "run_id": lane["run_id"]} for lane in self.lanes],
        })

    def _lane(self, lane_id: str, lifecycle: str, *, task: str, memory: bool,
              process: dict | None = None, recorded: str | None = None,
              events: list[str] | None = None) -> dict:
        worktree = self.worktrees / lane_id
        aw = worktree / ".agent-workspace"
        card: dict = {"schema": "project-task-card/v1", "task": task + "\nMore detail here."}
        if memory:
            card["memory_handoff"] = {
                "plan_state": "execution_accepted",
                "plan": {"plan_id": "schema-migration:obj", "source": {"branch": "direct_fill"}},
            }
            _write(aw / "memory-dispatch.json", {
                "strategy": "standard", "plan_id": "schema-migration:obj", "plan_state": "accepted",
                "optional_content": [{"id": "a", "origin": "everos"}, {"id": "b", "origin": "atlas"}],
                "delivery_trace": {"selected": [], "packed": [], "context_delivered": [{}, {}], "omitted": [{}]},
            })
        _write(aw / "task-card.json", card)
        _write(aw / "controller.status.json", {
            "schema": "controller-status/v1", "lane_id": lane_id, "run_id": f"run-{lane_id}",
            "controller_state": "running", "provider_state": {"state": "running"},
            "result_state": "valid" if recorded else "absent", "cleanup_proven": True,
            "recorded_status": recorded,
        })
        _write_jsonl(aw / "controller.events.jsonl",
                     [{"schema": "controller-events/v1"}] + [
                         {"ts": _iso(600), "run_id": f"run-{lane_id}", "event_type": name, "detail": ""}
                         for name in (events or ["controller_started"])
                     ])
        _write_jsonl(aw / "controller.attempts.jsonl", [{"attempt": 1}, {"attempt": 2}] if lane_id == "lane-1" else [])
        lane = {
            "schema": "lane/v1", "lane_id": lane_id, "run_id": f"run-{lane_id}",
            "worktree_path": str(worktree), "result_path": str(worktree / "RESULT.json"),
            "controller_status_path": str(aw / "controller.status.json"),
            "controller_events_path": str(aw / "controller.events.jsonl"),
            "transcript_path": str(aw / "provider-transcript.jsonl"),
            "attempts_path": str(aw / "controller.attempts.jsonl"),
            "provider": {"id": "codex", "model": "gpt-test"},
            "session": {}, "process": process or {}, "lifecycle": lifecycle,
        }
        if memory:
            lane["memory_plan_state"] = "execution_accepted"
        _write(self.rt / "epochs" / EPOCH / "lanes" / lane_id / "lane.json", lane)
        return lane


def _tree_fingerprint(root: Path) -> dict[str, tuple[int, int]]:
    return {
        str(path.relative_to(root)): (path.stat().st_size, path.stat().st_mtime_ns)
        for path in sorted(root.rglob("*"))
    }


class ViewStateTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.fixture = ViewFixture(self.root)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _state(self) -> dict:
        return view_state.collect_state(self.fixture.rt, now=NOW_UTC)

    def _lane(self, state: dict, lane_id: str) -> dict:
        return next(lane for lane in state["lanes"] if lane["lane_id"] == lane_id)

    def test_lanes_map_to_seven_steps(self) -> None:
        state = self._state()
        self.assertEqual("open", state["status"])
        self.assertEqual("healthy", state["monitor"]["state"])

        working = self._lane(state, "lane-1")
        if processes.process_identity(os.getpid()) is not None:
            self.assertEqual([DONE, DONE, DONE, DONE, NOW], working["steps"][:5])
            self.assertEqual("Fixing its report", working["label"])
        self.assertEqual("Fix date parser regression", working["task"])
        self.assertEqual(2, working["memory"]["delivered"])
        self.assertIn("reused plan", working["detail"])

        plain = self._lane(state, "lane-2")
        self.assertEqual([SKIP] * 4, plain["steps"][:4])
        self.assertEqual(WAIT, plain["steps"][4])
        self.assertEqual("Waiting for a key", plain["label"])

        accepted = self._lane(state, "lane-4")
        self.assertEqual([DONE] * 7, accepted["steps"])
        self.assertEqual("good", accepted["tone"])

    def test_pending_queue_event_is_listed_once(self) -> None:
        needs = self._state()["needs_you"]
        lane3 = [item for item in needs if item["lane_id"] == "lane-3"]
        self.assertEqual(1, len(lane3))
        self.assertAlmostEqual(240, lane3[0]["age_seconds"], delta=1)
        self.assertIn("orchestrator: inspect result and record completion-review", lane3[0]["hint"])

    def test_active_review_agent_replaces_manual_review_prompt(self) -> None:
        _write(
            self.fixture.worktrees / "lane-3" / ".agent-workspace" / "review-agent.json",
            {
                "schema": "harness-review-agent/v1",
                "state": "running",
                "provider": "claude-code",
                "model": "sonnet",
            },
        )
        state = self._state()
        lane = self._lane(state, "lane-3")
        self.assertEqual("Agent reviewing", lane["label"])
        self.assertFalse(any(item["lane_id"] == "lane-3" for item in state["needs_you"]))

    def test_demo_progress_does_not_create_a_benchmark_epoch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = Path(tmp) / ".harness-runtime"
            runtime.mkdir()
            _write(
                runtime / "DEMO_PROGRESS.json",
                {
                    "schema": "harness-demo-progress/v1",
                    "lane_id": "fix-average-memory-new",
                    "task": "Fix average",
                    "provider": "claude-code",
                    "model": "sonnet",
                    "phase": "Recall",
                    "state": "waiting",
                    "started_at": _iso(0),
                },
            )
            state = view_state.collect_state(runtime, now=NOW_UTC)
        self.assertEqual("idle", state["status"])
        self.assertEqual([], state["lanes"])

    def test_collect_and_render_never_write(self) -> None:
        before = _tree_fingerprint(self.root)
        state = self._state()
        view_render.render(state, 140, 40)
        view_render.render(state, 140, 40, details=True, selected=1)
        self.assertEqual(before, _tree_fingerprint(self.root))

    def test_missing_runtime_and_closed_run(self) -> None:
        missing = view_state.collect_state(self.root / "absent", now=NOW_UTC)
        self.assertEqual("no_runtime", missing["status"])

        (self.fixture.rt / "CURRENT_EPOCH.json").unlink()
        state_path = self.fixture.rt / "epochs" / EPOCH / "epoch-state.json"
        record = json.loads(state_path.read_text(encoding="utf-8"))
        record.update({"lifecycle": "closed", "closed_at": _iso(0)})
        state_path.write_text(json.dumps(record), encoding="utf-8")
        closed = view_state.collect_state(self.fixture.rt, now=NOW_UTC)
        self.assertEqual("closed", closed["status"])
        self.assertEqual(4, len(closed["lanes"]))
        self.assertAlmostEqual(3600, closed["run_seconds"], delta=1)


class ViewRenderTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.state = view_state.collect_state(ViewFixture(Path(self._tmp.name)).rt, now=NOW_UTC)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_every_line_fits_exactly(self) -> None:
        for width in (60, 100, 160):
            for details in (False, True):
                lines = view_render.render(self.state, width, 30, depth=view_render.NO_COLOR, details=details)
                self.assertEqual(30, len(lines))
                for line in lines:
                    self.assertEqual(width, view_render.text_width(line), repr(line))

    def test_overview_shows_agents_with_stage_lights(self) -> None:
        text = "\n".join(view_render.render(self.state, 160, 30, depth=view_render.NO_COLOR))
        self.assertIn("Enter open", text)
        self.assertIn("Fix date parser regression", text)
        self.assertIn("Recall", text)
        self.assertNotIn("p/o/r/x", text)
        self.assertIn("Awaiting orchestrator review", text)
        self.assertIn("lane-3", text)

    def test_only_active_agents_pulse_on_overview(self) -> None:
        first = view_render.render(self.state, 160, 30, depth=0, frame=0)
        second = view_render.render(self.state, 160, 30, depth=0, frame=2)
        self.assertNotEqual(first[3], second[3])
        self.assertNotEqual(first[4], second[4])
        for row in (9, 10, 15, 16, 21, 22):
            self.assertEqual(first[row], second[row])
        self.state['status'] = 'closed'
        self.assertEqual(
            view_render.render(self.state, 160, 30, depth=0, frame=0),
            view_render.render(self.state, 160, 30, depth=0, frame=2))

    def test_ascii_mode_is_plain_ascii(self) -> None:
        lines = view_render.render(self.state, 120, 30, depth=view_render.NO_COLOR, ascii_only=True, interactive=False)
        for line in lines:
            line.encode("ascii")

    def test_colour_output_resets_styles(self) -> None:
        lines = view_render.render(self.state, 120, 30, depth=view_render.COLOR_TRUE)
        self.assertTrue(any("\x1b[" in line for line in lines))
        for line in lines:
            if "\x1b[" in line:
                self.assertTrue(line.endswith("\x1b[0m") or line.endswith(" "), repr(line[-12:]))

    def test_empty_states_render(self) -> None:
        for status in ("no_runtime", "idle"):
            lines = view_render.render({"status": status, "lanes": [], "needs_you": []}, 80, 12,
                                       depth=view_render.NO_COLOR)
            self.assertEqual(12, len(lines))


class ViewCommandTests(unittest.TestCase):
    def test_parser_accepts_view_options(self) -> None:
        parsed = operator_launch._build_parser().parse_args(["view", "--once", "--ascii", "--no-color"])
        self.assertEqual("view", parsed.command)
        self.assertTrue(parsed.once and parsed.ascii and parsed.no_color)

    def test_once_returns_snapshot_result(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = ViewFixture(Path(tmp))
            config = mock.Mock(runtime_root=fixture.rt)
            with mock.patch("orchestrator_harness.config.find_harness_root", return_value=Path(tmp)), \
                 mock.patch("orchestrator_harness.config.load_config", return_value=config):
                result = view_term.run_view(once=True, out=io.StringIO())
        self.assertTrue(result["ok"])
        self.assertEqual(view_term.VIEW_OK, result["code"])
        self.assertIn("lane-1", result["summary"])
        self.assertNotIn("\x1b[", result["summary"])
        self.assertEqual(4, len(result["state"]["lanes"]))

    def test_no_color_env_disables_colour(self) -> None:
        tty = mock.Mock()
        tty.isatty.return_value = True
        with mock.patch.dict(os.environ, {"NO_COLOR": "1"}):
            self.assertEqual(view_render.NO_COLOR, view_term.color_depth(tty))
        with mock.patch.dict(os.environ, {"NO_COLOR": "", "COLORTERM": "truecolor"}):
            self.assertEqual(view_render.COLOR_TRUE, view_term.color_depth(tty))


if __name__ == "__main__":
    unittest.main()

