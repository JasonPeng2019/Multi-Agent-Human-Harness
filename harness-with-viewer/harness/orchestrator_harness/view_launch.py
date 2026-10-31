"""Open the terminal viewer in its own window when ``visualizer`` is ``auto``.

Two triggers use this module: ``harness setup`` (when the stored setting is
already ``auto``) and the persistent monitor (when the user changes the
setting from ``off`` to ``auto`` while the runtime is open).  Launching is
best-effort: a host with no usable terminal gets a clear ``next_action`` and
the harness continues unchanged.  A live viewer records its exact
PID-plus-creation identity so a second window is never opened for it.
"""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from . import processes
from .core import read_json
from .records import atomic_write_json

VIEWER_SCHEMA = "viewer-process/v1"
VIEW_COMMAND = ("-m", "orchestrator_harness.operator_launch", "view")


def viewer_record_path(rt: Path) -> Path:
    return rt / "viewer" / "VIEWER.json"


def viewer_running(rt: Path) -> bool:
    """Return whether the recorded viewer is the same live process."""
    path = viewer_record_path(rt)
    if not path.is_file():
        return False
    try:
        record = read_json(path)
    except (OSError, ValueError):
        return False
    return bool(processes.identity_matches(record.get("pid"), record.get("creation_time")))


def record_viewer(rt: Path) -> Path | None:
    """Record this process as the live viewer (best effort)."""
    identity = processes.process_identity(os.getpid())
    if identity is None or not rt.is_dir():
        return None
    path = viewer_record_path(rt)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_json(path, {"schema": VIEWER_SCHEMA, **identity})
    except OSError:
        return None
    return path


def clear_viewer(path: Path | None) -> None:
    """Remove this process's viewer record, only if it is still ours."""
    if path is None:
        return
    try:
        record = read_json(path)
        if record.get("pid") == os.getpid():
            path.unlink()
    except (OSError, ValueError):
        pass


def _applescript_string(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def terminal_command(harness_root: Path) -> tuple[list[str], str] | None:
    """Return (argv, method) that opens the viewer in a new terminal, or None."""
    python = sys.executable
    root = str(harness_root)
    view = [python, *VIEW_COMMAND, "--color"]
    if os.name == "nt":
        if shutil.which("wt"):
            return ["wt", "-w", "0", "split-pane", "-d", root, *view], "windows-terminal"
        return ["cmd", "/c", "start", "Harness viewer", "/D", root, *view], "windows-console"
    shell_line = f"cd {shlex.quote(root)} && {shlex.join(view)}"
    if os.environ.get("TMUX") and shutil.which("tmux"):
        return ["tmux", "split-window", "-h", "-c", root, shlex.join(view)], "tmux"
    if sys.platform == "darwin" and shutil.which("osascript"):
        script = f"tell application \"Terminal\" to do script {_applescript_string(shell_line)}"
        return [
            "osascript", "-e", script, "-e", 'tell application "Terminal" to activate',
        ], "macos-terminal"
    for name, flag in (("gnome-terminal", "--"), ("konsole", "-e"), ("x-terminal-emulator", "-e")):
        if shutil.which(name):
            return [name, flag, "sh", "-c", shell_line], name
    return None


def open_viewer_window(harness_root: Path, rt: Path) -> dict[str, Any]:
    """Open the viewer in a new terminal unless one is already live."""
    if viewer_running(rt):
        return {"launched": False, "reason": "a viewer is already open"}
    command = terminal_command(harness_root)
    if command is None:
        return {
            "launched": False,
            "reason": "no terminal could be opened from here",
            "next_action": "run `python -m orchestrator_harness.operator_launch view` in a terminal",
        }
    argv, method = command
    try:
        subprocess.Popen(
            argv,
            cwd=str(harness_root),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            **({"start_new_session": True} if os.name != "nt" else {}),
        )
    except OSError as exc:
        return {
            "launched": False,
            "reason": f"{method} launch failed: {exc}",
            "next_action": "run `python -m orchestrator_harness.operator_launch view` in a terminal",
        }
    return {"launched": True, "method": method}


def watch_setting(harness_root: Path, rt: Path, previous: str) -> str:
    """Open the viewer when the stored setting changes to ``auto``.

    Returns the current setting so the caller can detect the next change.
    Any configuration error keeps the previous value and never raises.
    """
    from .config import load_config

    try:
        current = load_config(harness_root).visualizer
    except Exception:
        return previous
    if current == "auto" and previous != "auto":
        try:
            open_viewer_window(harness_root, rt)
        except Exception:
            pass
    return current
