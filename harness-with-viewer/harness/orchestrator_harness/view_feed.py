"""Presentation-only line reveal; provider records and execution are untouched."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Block:
    key: str
    text: str
    prose: bool = False
    heading: str = ""

    def render(self, text: str | None = None) -> str:
        body = self.text if text is None else text
        return (self.heading + "\n" if self.heading else "") + body


def prose_blocks(key: str, text: str, heading: str = "### Agent") -> list[Block]:
    """Separate prose and fenced code while preserving their original order."""
    parts = re.split(r'(```[^\n]*\n.*?(?:```|\Z)|~~~[^\n]*\n.*?(?:~~~|\Z))', text, flags=re.S)
    blocks = []
    for index, part in enumerate(parts):
        if part:
            blocks.append(Block(f"{key}:{index}", part, not part.startswith(('```', '~~~')),
                                heading if not blocks else ""))
    return blocks


class Feed:
    """Append-only presentation queue revealing complete lines in arrival order."""
    LINES_PER_SECOND = 12

    def __init__(self, width: int = 76) -> None:
        self.blocks: list[Block] = []
        self.entries: dict[str, str] = {}
        self.full_text = ""
        self.visible = 0
        self.width = width
        self._last_tick = 0.0
        self._credit = 0.0

    def update(self, blocks: list[Block], now: float, *, immediate: bool = False) -> None:
        from difflib import SequenceMatcher
        self.advance(now)
        pending = self.revealing
        if immediate:
            self.full_text = "\n\n".join(block.render() for block in blocks)
            self.visible = len(self.full_text)
            self.entries = {block.key: block.render() for block in blocks}
            self._last_tick, self._credit = now, 0.0
        else:
            additions = []
            for block in blocks:
                text = block.render()
                previous = self.entries.get(block.key)
                if previous is None:
                    additions.append(text)
                elif text != previous:
                    # Completed commands replace their initial records in the source.
                    # Append only changed/new lines; never expand content above the reader.
                    old, new = previous.splitlines(keepends=True), text.splitlines(keepends=True)
                    delta = text[len(previous):] if text.startswith(previous) else ''.join(
                        ''.join(new[j:k]) for op, _, _, j, k in
                        SequenceMatcher(None, old, new).get_opcodes() if op in ('insert', 'replace'))
                    if delta:
                        additions.append(delta)
                self.entries[block.key] = text
            if additions:
                self.full_text += ("\n\n" if self.full_text else "") + "\n\n".join(additions)
                if not pending:
                    self._last_tick, self._credit = now, 0.0
        self.blocks = blocks

    def advance(self, now: float) -> None:
        if not self.revealing:
            self._last_tick, self._credit = now, 0.0
            return
        self._credit += max(0.0, now - self._last_tick) * self.LINES_PER_SECOND
        self._last_tick = now
        count = int(self._credit)
        self._credit -= count
        # Match the renderer's word wrapping, so completed lines never reflow.
        import textwrap
        from .view_render import text_width
        for _ in range(count):
            if not self.revealing:
                break
            newline = self.full_text.find('\n', self.visible)
            stop = len(self.full_text) if newline < 0 else newline
            raw = self.full_text[self.visible:stop]
            chunks = textwrap.wrap(raw, width=max(10, self.width), replace_whitespace=False,
                                   drop_whitespace=False, expand_tabs=False) or [""]
            chunk = chunks[0]
            length, columns = 0, 0
            for char in chunk:
                size = 4 if char == '\t' else text_width(char)
                if columns + size > max(10, self.width) and length:
                    break
                columns += size
                length += 1
            self.visible += length
            if self.visible == stop and newline >= 0:
                self.visible += 1

    def finish(self, now: float) -> None:
        """Explicit End action: skip the presentation queue and show received text."""
        self.visible = len(self.full_text)
        self._last_tick, self._credit = now, 0.0

    @property
    def revealing(self) -> bool:
        return self.visible < len(self.full_text)

    def text(self, now: float) -> str:
        self.advance(now)
        return self.full_text[:self.visible]
