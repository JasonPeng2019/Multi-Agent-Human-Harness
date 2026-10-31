"""Show the live viewer with four sample lanes: ``python3 -m orchestrator_harness.tests.view_demo``.

The sample runtime lives in a temporary directory and is removed on exit.
Press ``q`` to quit.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from orchestrator_harness import view_state, view_term
from orchestrator_harness.tests.test_view import ViewFixture


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        rt = ViewFixture(Path(tmp)).rt
        view_term.run_interactive(
            lambda: view_state.collect_state(rt),
            depth=view_term.color_depth(__import__("sys").stdout),
            ascii_only=False,
        )


if __name__ == "__main__":
    main()
