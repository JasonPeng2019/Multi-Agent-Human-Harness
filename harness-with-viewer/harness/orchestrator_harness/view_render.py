"""Pure rendering for the terminal viewer.

``render(state, width, height, ...)`` turns one ``view_state`` snapshot into
exactly ``height`` terminal lines of exactly ``width`` visible columns.  It
performs no I/O, so the same function drives the live screen, ``view --once``,
and snapshot tests.
"""

from __future__ import annotations

import unicodedata
import textwrap
from functools import lru_cache
from dataclasses import dataclass, field
from typing import Any

from .view_state import (
    DONE,
    FAIL,
    NOW,
    SKIP,
    STEPS,
    TODO,
    WAIT,
)

# Colour depth: 0 = none, 1 = 16 colours, 2 = 256 colours, 3 = truecolor.
NO_COLOR, COLOR_16, COLOR_256, COLOR_TRUE = 0, 1, 2, 3

PALETTE: dict[str, tuple[int, int, int]] = {
    "text": (231, 236, 245),
    "muted": (140, 153, 181),
    "faint": (84, 96, 124),
    "live": (122, 215, 240),
    "memory": (245, 184, 97),
    "plan": (183, 156, 255),
    "review": (231, 236, 245),
    "good": (110, 224, 166),
    "bad": (255, 127, 122),
    "attention": (245, 184, 97),
    "idle": (140, 153, 181),
    "bar": (24, 35, 60),
}
_ANSI16 = {
    "text": 97, "muted": 37, "faint": 90, "live": 96, "memory": 93, "plan": 95,
    "review": 97, "good": 92, "bad": 91, "attention": 93, "idle": 37, "bar": 44,
}
STEP_COLORS = ("memory", "memory", "plan", "plan", "live", "review", "good")

UNICODE_GLYPHS = {
    DONE: "●", NOW: "◉", WAIT: "◌", FAIL: "✕", TODO: "○", SKIP: "·",
    "line_done": "━", "line_todo": "┄", "line_skip": " ",
    "select": "▸", "flag": "⚑", "dot": "●", "rule": "─", "key": "⚿",
}
ASCII_GLYPHS = {
    DONE: "#", NOW: "@", WAIT: "o", FAIL: "x", TODO: ".", SKIP: " ",
    "line_done": "=", "line_todo": "-", "line_skip": " ",
    "select": ">", "flag": "!", "dot": "*", "rule": "-", "key": "k",
}


def text_width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1 for ch in text)


def _truncate(text: str, width: int) -> str:
    if width <= 0:
        return ""
    if text_width(text) <= width:
        return text
    out, used = [], 0
    for ch in text:
        w = text_width(ch)
        if used + w > width - 1:
            break
        out.append(ch)
        used += w
    return "".join(out) + "…"


def _sgr(color: str | None, depth: int, *, bold: bool = False, dim: bool = False, bg: str | None = None) -> str:
    if depth == NO_COLOR:
        return ""
    codes: list[str] = []
    if bold:
        codes.append("1")
    if dim:
        codes.append("2")
    for name, is_bg in ((color, False), (bg, True)):
        if name is None:
            continue
        r, g, b = PALETTE[name]
        if depth == COLOR_TRUE:
            codes.append(f"{48 if is_bg else 38};2;{r};{g};{b}")
        elif depth == COLOR_256:
            index = 16 + 36 * round(r / 255 * 5) + 6 * round(g / 255 * 5) + round(b / 255 * 5)
            codes.append(f"{48 if is_bg else 38};5;{index}")
        else:
            base = _ANSI16[name]
            codes.append(str(base + 10 if is_bg and base < 90 else base))
    return f"\x1b[{';'.join(codes)}m" if codes else ""


@dataclass
class Line:
    """One styled terminal line built from (text, style) segments."""

    depth: int
    segments: list[tuple[str, str]] = field(default_factory=list)
    width: int = 0

    def add(self, text: str, color: str | None = None, *, bold: bool = False, dim: bool = False,
            bg: str | None = None) -> "Line":
        if text:
            self.segments.append((text, _sgr(color, self.depth, bold=bold, dim=dim, bg=bg)))
            self.width += text_width(text)
        return self

    def pad_to(self, column: int) -> "Line":
        if column > self.width:
            self.add(" " * (column - self.width))
        return self

    def finish(self, width: int, *, bg: str | None = None) -> str:
        reset = "\x1b[0m" if self.depth != NO_COLOR else ""
        fill = _sgr(None, self.depth, bg=bg) if bg else ""
        out: list[str] = []
        used = 0
        for text, style in self.segments:
            remaining = width - used
            if remaining <= 0:
                break
            if text_width(text) > remaining:
                text = _truncate(text, remaining)
            out.append(f"{fill}{style}{text}{reset}" if (style or fill) else text)
            used += text_width(text)
        if used < width:
            out.append(f"{fill}{' ' * (width - used)}{reset}" if fill else " " * (width - used))
        return "".join(out)


_ASCII_MAP = str.maketrans({"·": "-", "…": ".", "→": ">", "↑": "^", "↓": "v", "─": "-", "━": "="})


def _asciify(line: str) -> str:
    """Replace every non-ASCII character with same-width ASCII."""
    line = line.translate(_ASCII_MAP)
    if line.isascii():
        return line
    return "".join(ch if ch.isascii() else "?" * text_width(ch) for ch in line)


def _lane_counts(lanes: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"working": 0, "review": 0, "waiting": 0, "done": 0, "problem": 0}
    for lane in lanes:
        tone = lane["tone"]
        if tone == "live":
            counts["working"] += 1
        elif lane["label"] == "Awaiting orchestrator review":
            counts["review"] += 1
        elif tone == "good":
            counts["done"] += 1
        elif tone == "bad":
            counts["problem"] += 1
        else:
            counts["waiting"] += 1
    return counts


def _centered(message: str, width: int, depth: int, color: str = "muted") -> str:
    pad = max(0, (width - text_width(message)) // 2)
    return Line(depth).add(" " * pad).add(message, color).finish(width)


@lru_cache(maxsize=4)
def artifact_lines(text: str, width: int, depth: int, *, prompt: bool = False) -> list[str]:
    """Readable, consistently wrapped content shared by drawing and scrolling."""
    from .view_artifacts import safe_text
    body = []
    fenced = False
    for raw in safe_text(text).expandtabs(4).splitlines():
        if raw.startswith("```") and not prompt:
            fenced = not fenced
            continue
        heading = raw.startswith(("# ", "## ", "### "))
        color = "text"
        if heading:
            raw = raw.lstrip("# ")
            color = "live"
        elif raw.startswith("$ "):
            color = "memory"
        elif raw.startswith("+ "):
            color = "good"
        elif raw.startswith("- ") and fenced:
            color = "bad"
        elif fenced or raw.startswith("    "):
            color = "muted"
        # Split by display columns so wide Unicode does not disappear at the edge.
        chunks = textwrap.wrap(raw, width=max(10, width - 4),
                               replace_whitespace=False, drop_whitespace=False) or [""]
        for chunk in chunks:
            piece, used = "", 0
            for char in chunk:
                size = text_width(char)
                if used + size > width - 4:
                    body.append(Line(depth).add("  " + piece, color, bold=heading).finish(width))
                    piece, used = "", 0
                piece += char
                used += size
            body.append(Line(depth).add("  " + piece, color, bold=heading).finish(width))
    return body


def artifact_viewport(height: int, state: dict, interactive: bool = True) -> int:
    extra = 2 if state.get('replay') else (1 if state.get('replay_error') else 0)
    return max(0, height - 4 - int(interactive) - extra)


def render(
    state: dict[str, Any],
    width: int,
    height: int,
    *,
    selected: int = 0,
    frame: int = 0,
    depth: int = COLOR_TRUE,
    ascii_only: bool = False,
    details: bool = False,
    interactive: bool = True,
    panel: str | None = None,
    artifact_text: str = "",
    scroll: int = 0,
    follow: bool = False,
    new_activity: bool = False,
    revealing: bool = False,
) -> list[str]:
    """Two screens: agent overview, or one agent's Prompt / Output / Result / Events."""
    from .view_artifacts import safe_text
    width, height = max(40, width), max(8, height)
    glyphs = ASCII_GLYPHS if ascii_only else UNICODE_GLYPHS
    lanes = list(state.get("lanes") or [])
    if state.get("root"):
        lanes.append(state["root"])
    panel = panel or ("output" if details and lanes else None)
    lines = []
    replay = state.get('replay')
    if replay:
        label = 'PAUSED' if replay['paused'] else 'PLAYING'
        banner = f" REPLAY {replay['speed']:g}x · {label} · {replay['position']:.1f}/{replay['duration']:.1f}s"
        if replay.get('warning'):
            banner += ' · ' + replay['warning']
        lines.append(Line(depth).add(banner, 'attention', bold=True).finish(width, bg='bar'))
        lines.append(Line(depth).add(' Space pause · r restart · [/] seek 10s · +/- speed · l live', 'muted').finish(width))
    elif state.get('replay_error'):
        lines.append(Line(depth).add(' Replay unavailable: ' + safe_text(state['replay_error']), 'attention').finish(width))
    if panel and lanes:
        lane = lanes[max(0, min(selected, len(lanes) - 1))]
        lines.append(Line(depth).add(" " + safe_text(str(lane['lane_id'])), "text", bold=True)
                     .add("  ·  " + safe_text(str(lane.get('label', ''))), "muted").finish(width, bg="bar"))
        provider = " · ".join(str(lane.get(k) or "") for k in ("provider", "model"))
        lines.append(Line(depth).add(" " + safe_text(provider), "muted").finish(width))
        tabs = Line(depth).add(" ")
        for name in ("prompt", "output", "result", "events"):
            tabs.add(f" [{name.title()}] " if name == panel else f"  {name.title()}  ", "live" if name == panel else "muted", bold=name == panel,
                     bg="bar" if name == panel else None)
        lines.append(tabs.finish(width))
        lines.append(Line(depth).add(glyphs["rule"] * width, "faint").finish(width))
        body = artifact_lines(artifact_text, width, depth, prompt=panel == "prompt")
        room = max(0, height - len(lines) - (1 if interactive else 0))
        end = max(0, len(body) - room)
        start = end if follow else min(max(0, scroll), end)
        lines.extend(body[start:start + room])
        while len(lines) < height - (1 if interactive else 0):
            lines.append(Line(depth).finish(width))
        if interactive:
            position = ("Replay" if replay else "Live · revealing" if revealing else "Live") if follow else f"{min(start + 1, len(body))}–{min(start + room, len(body))}/{len(body)}"
            if panel == "events":
                footer = " ↑/↓ event · Enter expand/collapse · PgUp/PgDn scroll · ←/→ tab · Esc back"
            elif new_activity:
                footer = " New activity ↓ · End latest · ↑/↓ scroll · Esc all agents"
            else:
                footer = " ←/→ section · ↑/↓ scroll · Esc all agents"
                if panel == "output":
                    footer += " · End follow"
                footer += "  " + position
            lines.append(Line(depth).add(footer, "muted").finish(width, bg="bar"))
    else:
        status = state.get("status")
        title = " AGENTS" + ("  ·  Run complete" if status == "closed" else "")
        lines.append(Line(depth).add(title, "text", bold=True).finish(width, bg="bar"))
        workers = [lane for lane in lanes if lane.get("role") != "root"]
        counts = _lane_counts(workers)
        summary = f" {len(workers)} agents  ·  {counts['working']} working  ·  {counts['review']} awaiting review  ·  {counts['done']} accepted"
        if counts['problem']:
            summary += f"  ·  {counts['problem']} need attention"
        lines.append(Line(depth).add(summary, "muted").finish(width))
        lines.append(Line(depth).add(glyphs["rule"] * width, "faint").finish(width))
        body = []
        if not lanes:
            message = "No run yet. Start a harness run to see its agents." if status in ("no_runtime", "idle") else "Preparing agents…"
            body = [Line(depth).finish(width), _centered(message, width, depth)]
        for index, lane in enumerate(lanes):
            active = index == selected and interactive
            label = str(lane.get("label", ""))
            color = {"live": "live", "good": "good", "bad": "bad", "attention": "attention"}.get(lane.get("tone"), "muted")
            prefix = " > " if active else "   "
            row = Line(depth).add(prefix, "live").add(safe_text(str(lane['lane_id'])), "text", bold=True)
            running = status == "open" and (
                lane.get("lifecycle") in ("running", "resuming")
                or (lane.get("review_agent") or {}).get("state") == "running"
                or (lane.get("lifecycle") == "preparing" and NOW in lane.get("steps", []))
            )
            pulse = interactive and running and frame % 4 >= 2
            lamp = ("o" if pulse else "*") if ascii_only else ("◌" if pulse else "●")
            row.add("  " + lamp + " " + safe_text(label), color, dim=pulse)
            body.append(row.finish(width, bg="bar" if active else None))
            lights, labels = Line(depth).add("   "), Line(depth).add("   ")
            cell_width = max(5, min(13, (width - 6) // len(STEPS)))
            for stage, code in zip(STEPS, lane.get("steps", [])):
                stage_color = {DONE: "good", NOW: "live" if running else "attention",
                               WAIT: "attention", FAIL: "bad", TODO: "faint", SKIP: "faint"}.get(code, "faint")
                if code == NOW:
                    lamp = ("ooo" if pulse else "***") if ascii_only else ("○○○" if pulse else "●●●")
                else:
                    lamp = {DONE: "###" if ascii_only else "●●●", WAIT: "ooo" if ascii_only else "○○○",
                            FAIL: "xxx", SKIP: "---", TODO: "..."}.get(code, "...")
                lights.add(("[" + lamp + "]").center(cell_width), stage_color, bold=True)
                labels.add(_truncate(stage, cell_width).center(cell_width), stage_color,
                           bold=code in (NOW, DONE, FAIL))
            body.extend([lights.finish(width), labels.finish(width)])
            body.append(Line(depth).add("   " + safe_text(str(lane.get('task') or 'Preparing task…')), "text").finish(width))
            who = " · ".join(str(lane.get(k)) for k in ("provider", "model") if lane.get(k))
            body.append(Line(depth).add("   " + safe_text(who), "muted").finish(width))
            body.append(Line(depth).finish(width))
        room = max(0, height - len(lines) - (1 if interactive else 0))
        start = max(0, min(max(0, len(body) - room), 6 * selected + 6 - room))
        lines.extend(body[start:start + room])
        while len(lines) < height - (1 if interactive else 0):
            lines.append(Line(depth).finish(width))
        if interactive:
            lines.append(Line(depth).add(" ↑/↓ select agent   Enter open   r replay   q quit", "muted").finish(width, bg="bar"))
    result = lines[:height]
    return [_asciify(line) for line in result] if ascii_only else result
