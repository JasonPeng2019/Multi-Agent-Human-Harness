"""``operator_launch view``: a read-only, terminal-native lane viewer.

The interactive screen uses only the standard library: ANSI escape sequences
for drawing, ``msvcrt`` for keys on Windows, and ``termios``/``select`` on
POSIX.  It re-reads runtime records every refresh interval, redraws only the
lines that changed, and always restores the terminal on exit. It never writes
runtime records or participates in harness process management.
"""

from __future__ import annotations

import os
import math
import shutil
import sqlite3
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator, TextIO

from . import view_artifacts, view_render, view_state
from .view_feed import Feed

VIEW_OK = "VIEW_OK"
VIEW_CONFIG_INVALID = "VIEW_CONFIG_INVALID"
VIEW_EPOCH_INVALID = "VIEW_EPOCH_INVALID"
VIEW_REPLAY_INVALID = "VIEW_REPLAY_INVALID"

FRAME_SECONDS = 0.05
DEFAULT_REFRESH_SECONDS = 2.0

_ENTER_SCREEN = "\x1b[?1049h\x1b[?25l\x1b[2J"
_LEAVE_SCREEN = "\x1b[0m\x1b[?25h\x1b[?1049l"
_SYNC_BEGIN = "\x1b[?2026h"
_SYNC_END = "\x1b[?2026l"


def color_depth(stream: TextIO, *, no_color: bool = False, force_color: bool = False) -> int:
    """An explicit --color overrides inherited NO_COLOR; --no-color wins."""
    if no_color or (os.environ.get("NO_COLOR") and not force_color) or not _is_tty(stream):
        return view_render.NO_COLOR
    if os.environ.get("COLORTERM", "").lower() in ("truecolor", "24bit") or os.environ.get("WT_SESSION"):
        return view_render.COLOR_TRUE
    if "256" in os.environ.get("TERM", "") or os.name == "nt":
        return view_render.COLOR_256
    return view_render.COLOR_16


def _is_tty(stream: Any) -> bool:
    try:
        return bool(stream.isatty())
    except (AttributeError, ValueError):
        return False


def _enable_windows_vt() -> None:
    """Turn on ANSI processing for the Windows console (no-op elsewhere)."""
    if os.name != "nt":
        return
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    except Exception:
        pass


class _Keys:
    """Non-blocking key reader returning 'up', 'down', 'enter', 'escape', 'q', or None."""

    def __init__(self) -> None:
        self._saved: Any = None

    @contextmanager
    def raw(self) -> Iterator["_Keys"]:
        if os.name == "nt":
            yield self
            return
        import termios
        import tty

        fd = sys.stdin.fileno()
        self._saved = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            yield self
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, self._saved)

    def read(self, timeout: float) -> str | None:
        if os.name == "nt":
            return self._read_windows(timeout)
        return self._read_posix(timeout)

    @staticmethod
    def _read_windows(timeout: float) -> str | None:
        import msvcrt

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ("\x00", "\xe0"):
                    code = msvcrt.getwch()
                    return {"H": "up", "P": "down", "K": "left", "M": "right", "I": "pageup", "Q": "pagedown", "G": "home", "O": "end"}.get(code)
                return _map_char(ch)
            time.sleep(0.02)
        return None

    @staticmethod
    def _read_posix(timeout: float) -> str | None:
        import select

        ready, _, _ = select.select([sys.stdin], [], [], timeout)
        if not ready:
            return None
        ch = os.read(sys.stdin.fileno(), 1).decode("utf-8", errors="ignore")
        if ch != "\x1b":
            return _map_char(ch)
        ready, _, _ = select.select([sys.stdin], [], [], 0.03)
        if not ready:
            return "escape"
        rest = os.read(sys.stdin.fileno(), 8).decode("utf-8", errors="ignore")
        return {"[A": "up", "[B": "down", "OA": "up", "OB": "down", "[C": "right", "[D": "left", "[5~": "pageup", "[6~": "pagedown", "[H": "home", "[F": "end", "[1~": "home", "[4~": "end", "OH": "home", "OF": "end"}.get(rest, None)


def _map_char(ch: str) -> str | None:
    if ch in ("\r", "\n"):
        return "enter"
    if ch == "\x1b":
        return "escape"
    if ch in ("q", "Q", "\x03"):
        return "q"
    if ch in ("k", "K"):
        return "up"
    if ch in ("j", "J"):
        return "down"
    if ch in (" ", "r", "l", "[", "]", "+", "-", "="):
        return ch
    if ch == "\t":
        return "right"
    if ch == "g":
        return "home"
    if ch == "G":
        return "end"
    return None


def _terminal_size() -> tuple[int, int]:
    size = shutil.get_terminal_size((120, 32))
    return size.columns, size.lines


def _safe_collect(collect: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return collect()
    except Exception as exc:  # the viewer reports, never crashes on a bad record
        return {"status": "no_runtime", "lanes": [], "needs_you": [
            {"lane_id": None, "text": f"viewer could not read runtime: {exc}", "hint": "", "age_seconds": None}
        ], "monitor": {}, "run_seconds": None}


def choose_epoch(rt: Path, *, out: TextIO, depth: int, ascii_only: bool,
                 refresh_seconds: float = DEFAULT_REFRESH_SECONDS) -> str | None:
    """Choose a durable epoch before loading its agents; refresh the list live."""
    _enable_windows_vt()
    keys = _Keys()

    def epoch_choices() -> list[dict[str, Any]]:
        return [dict(item, recorded=(rt / 'replay' / f"{item['epoch_id']}.sqlite3").is_file())
                for item in view_state.list_epochs(rt)]

    choices = epoch_choices()
    selected = next((i for i, item in enumerate(choices) if item['status'] == 'open'), 0)
    refreshed = time.monotonic()
    previous: list[str] = []
    out.write(_ENTER_SCREEN)
    try:
        with keys.raw():
            while True:
                now = time.monotonic()
                if now - refreshed >= refresh_seconds:
                    identity = choices[selected]['epoch_id'] if choices else None
                    choices = epoch_choices()
                    selected = next((i for i, item in enumerate(choices) if item['epoch_id'] == identity), 0)
                    refreshed = now
                width, height = _terminal_size()
                lines = view_render.render_epochs(choices, width, height, selected=selected,
                                                  depth=depth, ascii_only=ascii_only)
                if lines != previous:
                    out.write(_SYNC_BEGIN + '\x1b[H' + '\r\n'.join(lines) + _SYNC_END)
                    out.flush()
                    previous = lines
                key = keys.read(FRAME_SECONDS)
                if key in ('q', 'escape'):
                    return None
                if key == 'enter' and choices:
                    return str(choices[selected]['epoch_id'])
                if key == 'up':
                    selected = max(0, selected - 1)
                elif key == 'down':
                    selected = min(max(0, len(choices) - 1), selected + 1)
    except KeyboardInterrupt:
        return None
    finally:
        out.write(_LEAVE_SCREEN)
        out.flush()


def _display_lanes(state: dict[str, Any]) -> list[dict[str, Any]]:
    return list(state.get('lanes') or []) + ([state['root']] if state.get('root') else [])


def _lane_identity(lane: dict[str, Any]) -> tuple[Any, ...]:
    return lane.get('epoch_id'), lane.get('lane_id'), lane.get('run_id')


def run_interactive(
    collect: Callable[[], dict[str, Any]],
    *,
    out: TextIO = sys.stdout,
    depth: int,
    ascii_only: bool,
    refresh_seconds: float = DEFAULT_REFRESH_SECONDS,
    allow_epoch_selection: bool = False,
    playback: Any = None,
    replay_factory: Callable[[], Any] | None = None,
) -> bool:
    """Draw the live screen until the user quits."""
    _enable_windows_vt()
    keys = _Keys()
    try:
        state = playback.state() if playback else _safe_collect(collect)
    except (OSError, ValueError, sqlite3.Error) as exc:
        if playback:
            playback.close()
        playback = None
        state = _safe_collect(collect)
        state['replay_error'] = str(exc)
    last_collect = time.monotonic()
    selected, details, frame = 0, False, 0
    panel, scroll, follow = None, 0, False
    artifact_text, artifact_key, artifact_time = "", None, 0.0
    feed = Feed()
    latest_output = ""
    from . import view_events
    event_entries, event_diagnostics = [], []
    event_selected = None
    event_expanded: set[str] = set()
    event_focus = False
    previous: list[str] = []
    previous_size = (0, 0)
    out.write(_ENTER_SCREEN)
    out.flush()
    try:
        with keys.raw():
            while True:
                now = time.monotonic()
                old_lanes = _display_lanes(state)
                identity = _lane_identity(old_lanes[selected]) if selected < len(old_lanes) else None
                if playback:
                    try:
                        state = playback.state()
                    except (OSError, ValueError, sqlite3.Error) as exc:
                        playback.close()
                        playback = None
                        state = _safe_collect(collect)
                        state['replay_error'] = str(exc)
                        panel, scroll, follow = None, 0, False
                        artifact_key, artifact_text, latest_output = None, '', ''
                        feed = Feed()
                        event_entries, event_diagnostics, event_expanded = [], [], set()
                        event_selected, event_focus = None, False
                        last_collect = now
                elif now - last_collect >= refresh_seconds:
                    state = _safe_collect(collect)
                    last_collect = now
                display_lanes = _display_lanes(state)
                selected = next((i for i, item in enumerate(display_lanes)
                                 if _lane_identity(item) == identity), selected)
                lane_count = len(display_lanes)
                selected = max(0, min(selected, lane_count - 1)) if lane_count else 0
                width, height = _terminal_size()
                if (width, height) != previous_size:
                    previous = []
                    previous_size = (width, height)
                    out.write("\x1b[2J")
                lane = display_lanes[selected] if lane_count else None
                key_identity = (*_lane_identity(lane), panel, playback.generation if playback else None) if lane else None
                if panel and lane and (artifact_key != key_identity or playback or now - artifact_time >= refresh_seconds):
                    opening = artifact_key != key_identity
                    if panel == "output":
                        if opening:
                            feed = Feed(width=max(10, width - 4))
                        blocks = view_artifacts.output_blocks(lane)
                        feed.update(blocks, now, immediate=opening or bool(playback))
                        latest_output = feed.full_text
                        if opening or playback:
                            artifact_text = feed.text(now)
                    elif panel == "events":
                        event_entries, event_diagnostics = view_events.mailbox_entries(lane)
                        keys_available = [item[0] for item in event_entries]
                        if event_selected not in keys_available:
                            event_selected = keys_available[0] if keys_available else None
                        event_focus = event_focus or opening
                    else:
                        artifact_text = view_artifacts.panel_text(lane, panel)
                    artifact_key, artifact_time = key_identity, now
                if panel == "events" and lane:
                    artifact_text = view_events.mailbox_text(
                        lane, expanded=event_expanded, selected=event_selected,
                        entries=event_entries, diagnostics=event_diagnostics, width=width - 4)
                    if event_focus:
                        body = view_render.artifact_lines(artifact_text, width, 0)
                        position = next((i for i, line in enumerate(body) if '> [' in line), 0)
                        if position < scroll or position >= scroll + max(1, view_render.artifact_viewport(height, state)):
                            scroll = max(0, position - 1)
                        event_focus = False
                feed.width = max(10, width - 4)
                if panel == "output" and follow:
                    artifact_text = feed.text(now)
                new_activity = panel == "output" and not follow and latest_output != artifact_text
                frame = int((playback.position if playback else now) / 0.25)
                lines = view_render.render(
                    state, width, height, selected=selected, frame=frame,
                    depth=depth, ascii_only=ascii_only, details=details,
                    panel=panel, artifact_text=artifact_text, scroll=scroll, follow=follow,
                    new_activity=new_activity, revealing=panel == "output" and follow and feed.revealing,
                )
                chunks = [_SYNC_BEGIN]
                for row, line in enumerate(lines):
                    if row >= len(previous) or previous[row] != line:
                        chunks.append(f"\x1b[{row + 1};1H{line}")
                chunks.append(_SYNC_END)
                out.write("".join(chunks))
                out.flush()
                previous = lines

                key = keys.read(FRAME_SECONDS)
                if key == "q":
                    break
                if playback and key in (' ', 'r', '[', ']', '+', '-', '='):
                    playback.control(key)
                    if key in ('r', '[', ']'):
                        artifact_key, scroll = None, 0
                    continue
                if key == 'l' and playback:
                    playback.close()
                    playback = None
                    state = _safe_collect(collect)
                    artifact_key, artifact_text, latest_output = None, '', ''
                    feed = Feed()
                    event_entries, event_diagnostics, event_expanded = [], [], set()
                    event_selected, event_focus = None, False
                    scroll = 0
                    continue
                if key == 'r' and not playback and replay_factory:
                    try:
                        playback = replay_factory()
                        artifact_key, scroll = None, 0
                    except Exception as exc:
                        state['replay_error'] = str(exc)
                    continue
                if key == "enter" and lane_count and not panel:
                    panel, scroll = "output", 0
                    follow = lane.get("lifecycle") in ("running", "resuming")
                    artifact_key = None
                elif panel == "events" and key in ("enter", "up", "down"):
                    event_keys = [item[0] for item in event_entries]
                    if event_keys:
                        if key == "enter":
                            if event_selected in event_expanded:
                                event_expanded.remove(event_selected)
                            else:
                                event_expanded.add(event_selected)
                        else:
                            index = event_keys.index(event_selected) if event_selected in event_keys else 0
                            event_selected = event_keys[max(0, min(len(event_keys) - 1, index + (-1 if key == "up" else 1)))]
                        event_focus = True
                        follow = False
                elif key in ("left", "right") and panel:
                    tabs = ("prompt", "output", "result", "events")
                    panel = tabs[(tabs.index(panel) + (-1 if key == "left" else 1)) % len(tabs)]
                    scroll = 0
                    follow = panel == "output" and lane.get("lifecycle") in ("running", "resuming")
                    artifact_key = None
                elif key in ("home", "end") and panel:
                    scroll, follow = 0, key == "end"
                    if panel == "output" and key == "end":
                        feed.finish(time.monotonic())
                elif key in ("up", "down", "pageup", "pagedown") and panel:
                    count = len(view_render.artifact_lines(artifact_text, width, 0, prompt=panel == "prompt"))
                    end = max(0, count - view_render.artifact_viewport(height, state))
                    if follow:
                        scroll = end
                    follow = False
                    amount = max(1, view_render.artifact_viewport(height, state) - 2) if key in ("pageup", "pagedown") else 1
                    scroll = min(end, max(0, scroll + (-amount if key in ("up", "pageup") else amount)))
                elif key == "up":
                    selected = max(0, selected - 1)
                elif key == "down":
                    selected = min(max(0, lane_count - 1), selected + 1)
                elif key == "escape":
                    if not panel and allow_epoch_selection:
                        return True
                    details = False
                    panel = None
    except KeyboardInterrupt:
        pass
    finally:
        if playback:
            playback.close()
        out.write(_LEAVE_SCREEN)
        out.flush()
    return False


def run_view(
    *,
    runtime_root: str | None = None,
    epoch_id: str | None = None,
    list_epochs: bool = False,
    replay: bool = False,
    replay_speed: float = 1.5,
    list_replays: bool = False,
    once: bool = False,
    no_color: bool = False,
    force_color: bool = False,
    ascii_only: bool = False,
    refresh_seconds: float = DEFAULT_REFRESH_SECONDS,
    out: TextIO | None = None,
) -> dict[str, Any]:
    """Public ``view`` entry point returning the standard structured result."""
    out = out or sys.stdout
    try:
        from .config import find_harness_root, load_config

        rt = Path(runtime_root).expanduser().resolve() if runtime_root else load_config(find_harness_root()).runtime_root
    except Exception as exc:
        return {
            "ok": False,
            "code": VIEW_CONFIG_INVALID,
            "summary": str(exc),
            "evidence_paths": [],
            "next_action": "pass --runtime-root pointing to an existing .harness-runtime directory",
        }

    def collect() -> dict[str, Any]:
        return view_state.collect_state(rt, epoch_id=epoch_id)

    if list_epochs:
        choices = view_state.list_epochs(rt)
        return {
            'ok': True, 'code': VIEW_OK,
            'summary': '\n'.join(f"{item['epoch_id']}  {item['status']}  {item['opened_at']}  {item['lane_count']} agents" for item in choices) or 'No stored epochs.',
            'evidence_paths': [str(rt)], 'next_action': 'open view --epoch <epoch-id>',
            'epochs': choices,
        }

    from . import view_replay

    if list_replays:
        items = view_replay.recordings(rt)
        return {
            'ok': True, 'code': VIEW_OK,
            'summary': '\n'.join(f"{item['epoch_id']}  {item['opened_at']}  {'Recorded' if item['recorded'] else 'Approximate only' if item['status'] == 'closed' else 'Not yet recorded'}" for item in reversed(items)) or 'No stored epochs.',
            'recordings': items, 'evidence_paths': [str(rt)],
            'next_action': 'view --replay --epoch <epoch-id>',
        }

    def replay_error(exc: Exception) -> dict[str, Any]:
        return {'ok': False, 'code': VIEW_REPLAY_INVALID, 'summary': str(exc),
                'evidence_paths': [str(rt)], 'next_action': 'use view --list-replays to find an available epoch'}

    if not math.isfinite(replay_speed) or not .25 <= replay_speed <= 8:
        return replay_error(ValueError('Replay speed must be between 0.25 and 8.'))

    def replay_factory() -> Any:
        return view_replay.Playback(rt, epoch=epoch_id, speed=replay_speed)

    interactive = not once and _is_tty(out) and _is_tty(sys.stdin)
    try:
        initial_state = collect() if not replay and (not interactive or epoch_id is not None) else None
    except ValueError as exc:
        return {'ok': False, 'code': VIEW_EPOCH_INVALID, 'summary': str(exc),
                'evidence_paths': [str(rt)], 'next_action': 'use view --list-epochs to find a stored epoch ID'}

    depth = color_depth(out, no_color=no_color, force_color=force_color)
    if not interactive:
        playback = None
        try:
            playback = replay_factory() if replay else None
            state = playback.state() if playback else initial_state
        except Exception as exc:
            return replay_error(exc)
        finally:
            if playback:
                playback.close()
        width, _ = _terminal_size() if _is_tty(out) else (120, 0)
        lanes = len(_display_lanes(state))
        height = 3 + 6 * max(1, lanes) + (2 if replay else 0)
        lines = view_render.render(
            state, width, height, depth=depth, ascii_only=ascii_only, interactive=False,
        )
        return {
            "ok": True,
            "code": VIEW_OK,
            "summary": "\n".join(line.rstrip() for line in lines),
            "evidence_paths": [str(rt)],
            "next_action": "run `view` in a terminal for the live screen",
            "state": state,
        }
    while True:
        if epoch_id is None:
            epoch_id = choose_epoch(rt, out=out, depth=depth, ascii_only=ascii_only,
                                    refresh_seconds=refresh_seconds)
            if epoch_id is None:
                break
        try:
            playback = replay_factory() if replay else None
        except Exception as exc:
            return replay_error(exc)
        if not run_interactive(collect, out=out, depth=depth, ascii_only=ascii_only,
                               refresh_seconds=refresh_seconds, allow_epoch_selection=True,
                               playback=playback, replay_factory=replay_factory):
            break
        epoch_id = None
    return {
        "ok": True,
        "code": VIEW_OK,
        "summary": "viewer closed",
        "evidence_paths": [],
        "next_action": "none",
    }
