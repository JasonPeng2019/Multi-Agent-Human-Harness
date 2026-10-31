"""Epoch/history viewer regressions using disk fixtures, never live agents."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from orchestrator_harness import (
    operator_launch, view_artifacts, view_events, view_render, view_state, view_term,
)
from orchestrator_harness.tests.test_view import (
    EPOCH, NOW_UTC, ViewFixture, _iso, _tree_fingerprint, _write,
)


NEW_EPOCH = "newer-benchmark-epoch"


class EpochViewerTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.fixture = ViewFixture(self.root)
        self.rt = self.fixture.rt

    def epoch(self, epoch_id: str, *, opened: str, current: bool = False,
              lane_ids: tuple[str, ...] = ()) -> None:
        _write(self.rt / "epochs" / epoch_id / "epoch-state.json", {
            "schema": "epoch-state/v1", "epoch_id": epoch_id,
            "lifecycle": "active" if current else "closed", "lane_mode": "managed",
            "opened_at": opened, "closed_at": None if current else _iso(60),
        })
        for lane_id in lane_ids:
            _write(self.rt / "epochs" / epoch_id / "lanes" / lane_id / "lane.json", {
                "schema": "lane/v1", "lane_id": lane_id, "run_id": f"run-{lane_id}",
                "worktree_path": str(self.root / epoch_id / lane_id),
                "lifecycle": "prepared", "provider": {"id": "claude-code", "model": "test"},
            })
        if current:
            _write(self.rt / "CURRENT_EPOCH.json", {
                "schema": "current-epoch/v1", "epoch_id": epoch_id,
                "lane_mode": "managed", "queue_id": "q" * 32, "opened_at": opened,
            })

    def retire(self, lane_id: str = "lane-4") -> dict:
        path = self.rt / "epochs" / EPOCH / "lanes" / lane_id / "lane.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        record.update(lifecycle="retired", acceptance_advancement={"approval": "ACCEPTED"})
        _write(path, record)
        _write(self.rt / "epochs" / EPOCH / "active-lanes.json", {
            "schema": "active-lanes/v1", "epoch_id": EPOCH,
            "lanes": [{"lane_id": "lane-1", "run_id": "run-lane-1"}],
        })
        return record

    def test_active_epoch_keeps_retired_lanes_after_active_index_shrinks(self) -> None:
        self.retire()
        before = _tree_fingerprint(self.root)
        state = view_state.collect_state(self.rt, epoch_id=EPOCH, now=NOW_UTC)
        self.assertEqual("open", state["status"])
        self.assertEqual(["lane-1", "lane-2", "lane-3", "lane-4"],
                         [lane["lane_id"] for lane in state["lanes"]])
        retired = state["lanes"][-1]
        self.assertEqual("retired", retired["lifecycle"])
        self.assertIn("retired", retired["label"])
        self.assertEqual(before, _tree_fingerprint(self.root))

    def test_historical_epoch_excludes_current_lanes_queue_and_monitor_without_writes(self) -> None:
        self.retire()
        self.epoch(NEW_EPOCH, opened=_iso(30), current=True, lane_ids=("new-only",))
        _write(self.rt / "manager" / "QUEUE.json", {
            "schema": "manager-queue/v1", "epoch_id": NEW_EPOCH, "queue_id": "q" * 32,
            "events": [{"event_id": "new-event", "lane_id": "lane-3", "run_id": "run-lane-3",
                        "type": "LANE_STATUS_CHANGED", "summary": "NEW EPOCH ONLY",
                        "state": "PENDING"}],
        })
        before = _tree_fingerprint(self.root)
        state = view_state.collect_state(self.rt, epoch_id=EPOCH, now=NOW_UTC)
        text = "\n".join(view_render.render(state, 120, 38, depth=0))
        text += view_events.mailbox_text(state["root"])
        self.assertEqual("closed", state["status"])
        self.assertEqual(EPOCH, state["epoch_id"])
        self.assertEqual("missing", state["monitor"]["state"])
        self.assertEqual(4, len(state["lanes"]))
        self.assertNotIn("new-only", text)
        self.assertNotIn("NEW EPOCH ONLY", text)
        self.assertEqual(before, _tree_fingerprint(self.root))

    def test_epoch_list_orders_by_open_time_and_counts_retired_lanes(self) -> None:
        self.retire()
        self.epoch("older-epoch", opened=_iso(7200), lane_ids=("old-worker",))
        self.epoch(NEW_EPOCH, opened=_iso(30), current=True, lane_ids=("new-worker",))
        before = _tree_fingerprint(self.root)
        epochs = view_state.list_epochs(self.rt)
        self.assertEqual([NEW_EPOCH, EPOCH, "older-epoch"], [item["epoch_id"] for item in epochs])
        self.assertEqual([1, 4, 1], [item["lane_count"] for item in epochs])
        self.assertEqual(["open", "closed", "closed"], [item["status"] for item in epochs])
        self.assertEqual(before, _tree_fingerprint(self.root))

    def test_malformed_epoch_and_lane_records_are_ignored_in_picker_and_count(self) -> None:
        self.epoch("bad-json", opened=_iso(20))
        (self.rt / "epochs" / "bad-json" / "epoch-state.json").write_text("{broken", encoding="utf-8")
        _write(self.rt / "epochs" / "wrong-id" / "epoch-state.json", {
            "schema": "epoch-state/v1", "epoch_id": "somewhere-else", "opened_at": _iso(1),
        })
        _write(self.rt / "epochs" / "array-record" / "epoch-state.json", [])
        lane_root = self.rt / "epochs" / EPOCH / "lanes"
        _write(lane_root / "wrong-id" / "lane.json", {"schema": "lane/v1", "lane_id": "other"})
        _write(lane_root / "wrong-schema" / "lane.json", {"schema": "other/v1", "lane_id": "wrong-schema"})
        _write(lane_root / "array-record" / "lane.json", [])
        self.assertEqual([EPOCH], [item["epoch_id"] for item in view_state.list_epochs(self.rt)])
        self.assertEqual(4, view_state.list_epochs(self.rt)[0]["lane_count"])
        self.assertEqual(4, len(view_state.collect_state(self.rt, now=NOW_UTC)["lanes"]))

    def test_invalid_and_path_epoch_selectors_return_structured_cli_error(self) -> None:
        before = _tree_fingerprint(self.root)
        for epoch_id in ("missing", "../outside", "..\\outside", "/absolute", "C:\\absolute", "..", ""):
            with self.subTest(epoch_id=epoch_id):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    exit_code = operator_launch.main([
                        "--json", "view", "--runtime-root", str(self.rt),
                        "--epoch", epoch_id, "--once",
                    ])
                result = json.loads(output.getvalue())
                self.assertNotEqual(0, exit_code)
                self.assertFalse(result["ok"])
                self.assertEqual(view_term.VIEW_EPOCH_INVALID, result["code"])
        self.assertEqual(before, _tree_fingerprint(self.root))

    def test_cli_list_reports_epochs_and_explicit_snapshot_reads_requested_epoch(self) -> None:
        self.epoch(NEW_EPOCH, opened=_iso(30), current=True, lane_ids=("new-worker",))
        before = _tree_fingerprint(self.root)
        for options, key in ((["--list-epochs"], "epochs"), (["--epoch", EPOCH, "--once"], "state")):
            with self.subTest(options=options):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    exit_code = operator_launch.main(["--json", "view", "--runtime-root", str(self.rt), *options])
                result = json.loads(output.getvalue())
                self.assertEqual(0, exit_code)
                self.assertTrue(result["ok"])
                self.assertIn(key, result)
                if key == "state":
                    self.assertEqual(EPOCH, result["state"]["epoch_id"])
        self.assertEqual(before, _tree_fingerprint(self.root))

    def test_public_interactive_picker_and_view_never_write_runtime(self) -> None:
        self.retire()
        before = _tree_fingerprint(self.root)
        with (mock.patch.object(view_term, "_is_tty", return_value=True),
              mock.patch.object(view_term._Keys, "raw"),
              mock.patch.object(view_term._Keys, "read", side_effect=["enter", "q"])):
            result = view_term.run_view(runtime_root=str(self.rt), out=io.StringIO(), no_color=True)
        self.assertTrue(result["ok"])
        self.assertEqual(before, _tree_fingerprint(self.root))

    def test_retired_claude_lane_displays_realistic_crlf_stream_and_result(self) -> None:
        record = self.retire()
        record["provider"] = {"id": "claude-code", "model": "claude-test"}
        _write(self.rt / "epochs" / EPOCH / "lanes" / "lane-4" / "lane.json", record)
        records = [
            {"type": "system", "subtype": "init", "session_id": "claude-session"},
            {"type": "assistant", "message": {"id": "msg-1", "content": [
                {"type": "text", "text": "I will inspect the benchmark fix."},
                {"type": "tool_use", "id": "tool-1", "name": "Bash", "input": {"command": "python -m unittest"}},
            ]}},
            {"type": "user", "message": {"content": [
                {"type": "tool_result", "tool_use_id": "tool-1", "content": "Ran 8 tests\nOK"},
            ]}},
            {"type": "assistant", "message": {"id": "msg-2", "content": [
                {"type": "text", "text": "The fix passes all eight checks."},
            ]}},
            {"type": "result", "is_error": False, "session_id": "claude-session",
             "result": "The fix passes all eight checks.",
             "modelUsage": {"claude-test": {"inputTokens": 20, "outputTokens": 30}}},
        ]
        Path(record["transcript_path"]).write_bytes(
            ("\r\n".join(json.dumps(item) for item in records) + "\r\n").encode("utf-8")
        )
        Path(record["result_path"]).write_bytes(json.dumps({
            "summary": "Benchmark patch verified", "outcome": "PASS",
        }).encode("utf-8") + b"\r\n")
        before = _tree_fingerprint(self.root)
        state = view_state.collect_state(self.rt, epoch_id=EPOCH, now=NOW_UTC)
        lane = next(item for item in state["lanes"] if item["lane_id"] == "lane-4")
        output = view_artifacts.panel_text(lane, "output")
        result = view_artifacts.panel_text(lane, "result")
        self.assertEqual("claude-code", lane["provider"])
        self.assertIn("I will inspect the benchmark fix.", output)
        self.assertIn("$ python -m unittest", output)
        self.assertIn("Ran 8 tests\nOK", output)
        self.assertEqual(1, output.count("The fix passes all eight checks."))
        self.assertNotIn("\r", output)
        self.assertNotIn("modelUsage", output)
        self.assertIn("Benchmark patch verified", result)
        self.assertEqual(before, _tree_fingerprint(self.root))


class EpochNavigationTests(unittest.TestCase):
    def test_picker_scrolls_to_and_opens_epoch_beyond_first_screen(self) -> None:
        epochs = [{"epoch_id": f"epoch-{index:02d}", "status": "closed", "opened_at": None,
                   "lane_count": index} for index in range(12)]
        output = io.StringIO()
        with (mock.patch.object(view_state, "list_epochs", return_value=epochs),
              mock.patch.object(view_term._Keys, "raw"),
              mock.patch.object(view_term._Keys, "read", side_effect=["down"] * 10 + ["enter"]),
              mock.patch.object(view_term, "_terminal_size", return_value=(80, 8))):
            selected = view_term.choose_epoch(Path("unused"), out=output, depth=0, ascii_only=True)
        self.assertEqual("epoch-10", selected)
        self.assertIn(" > epoch-10", output.getvalue())
        self.assertTrue(output.getvalue().endswith(view_term._LEAVE_SCREEN))

    def test_picker_empty_runtime_and_escape_leave_terminal_clean(self) -> None:
        output = io.StringIO()
        with (mock.patch.object(view_state, "list_epochs", return_value=[]),
              mock.patch.object(view_term._Keys, "raw"),
              mock.patch.object(view_term._Keys, "read", return_value="escape")):
            selected = view_term.choose_epoch(Path("unused"), out=output, depth=0, ascii_only=True)
        self.assertIsNone(selected)
        self.assertIn("No stored epochs", output.getvalue())
        self.assertTrue(output.getvalue().endswith(view_term._LEAVE_SCREEN))

    def test_escape_from_agent_returns_overview_then_epoch_picker(self) -> None:
        state = {"status": "closed", "epoch_id": EPOCH, "lanes": [
            {"lane_id": "retired", "run_id": "run-retired", "epoch_id": EPOCH,
             "lifecycle": "retired", "label": "Retired", "tone": "idle"},
        ]}
        frames = []
        render = view_render.render

        def capture(*args, **kwargs):
            frames.append(kwargs["panel"])
            return render(*args, **kwargs)

        output = io.StringIO()
        with (mock.patch.object(view_term._Keys, "raw"),
              mock.patch.object(view_term._Keys, "read", side_effect=["enter", "escape", "escape"]),
              mock.patch.object(view_render, "render", side_effect=capture)):
            back = view_term.run_interactive(lambda: state, out=output, depth=0,
                                             ascii_only=True, allow_epoch_selection=True)
        self.assertTrue(back)
        self.assertEqual([None, "output", None], frames)
        self.assertTrue(output.getvalue().endswith(view_term._LEAVE_SCREEN))

    def test_lane_focus_survives_insertion_before_selected_lane(self) -> None:
        old = {"status": "closed", "lanes": [
            {"epoch_id": EPOCH, "lane_id": lane, "run_id": "run-" + lane,
             "label": "Retired", "tone": "idle"}
            for lane in ("lane-b", "lane-c")
        ]}
        new = copy.deepcopy(old)
        new["lanes"].insert(0, {"epoch_id": EPOCH, "lane_id": "lane-a", "run_id": "run-lane-a",
                               "label": "Retired", "tone": "idle"})
        moment = [0.0]
        selected = []
        keys = iter(((1.0, "down"), (3.0, None), (3.0, "q")))
        render = view_render.render

        def read(_timeout):
            moment[0], key = next(keys)
            return key

        def capture(state, *args, **kwargs):
            selected.append(state["lanes"][kwargs["selected"]]["lane_id"])
            return render(state, *args, **kwargs)

        with (mock.patch.object(view_term._Keys, "raw"),
              mock.patch.object(view_term._Keys, "read", side_effect=read),
              mock.patch.object(view_term.time, "monotonic", side_effect=lambda: moment[0]),
              mock.patch.object(view_render, "render", side_effect=capture)):
            view_term.run_interactive(mock.Mock(side_effect=[old, new]), out=io.StringIO(),
                                      depth=0, ascii_only=True, refresh_seconds=2)
        self.assertEqual(["lane-b", "lane-c", "lane-c"], selected)

    def test_selected_epoch_stays_fixed_until_user_returns_to_picker(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fixture = ViewFixture(Path(temporary))
            rt = fixture.rt
            _write(rt / "epochs" / NEW_EPOCH / "epoch-state.json", {
                "schema": "epoch-state/v1", "epoch_id": NEW_EPOCH, "lifecycle": "active",
                "lane_mode": "managed", "opened_at": _iso(30),
            })
            observed = []

            def interactive(collect, **kwargs):
                observed.append(collect()["epoch_id"])
                if len(observed) == 1:
                    _write(rt / "CURRENT_EPOCH.json", {
                        "schema": "current-epoch/v1", "epoch_id": NEW_EPOCH,
                        "lane_mode": "managed", "queue_id": "q" * 32, "opened_at": _iso(30),
                    })
                    self.assertEqual(EPOCH, collect()["epoch_id"])
                    return True
                return False

            with (mock.patch.object(view_term, "_is_tty", return_value=True),
                  mock.patch.object(view_term, "choose_epoch", side_effect=[EPOCH, NEW_EPOCH]) as choose,
                  mock.patch.object(view_term, "run_interactive", side_effect=interactive)):
                result = view_term.run_view(runtime_root=str(rt), no_color=True, out=io.StringIO())
            self.assertTrue(result["ok"])
            self.assertEqual([EPOCH, NEW_EPOCH], observed)
            self.assertEqual(2, choose.call_count)


if __name__ == "__main__":
    unittest.main()
