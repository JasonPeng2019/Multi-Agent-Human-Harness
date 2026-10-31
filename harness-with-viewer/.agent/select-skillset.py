from __future__ import annotations

"""Select the small, visible skill catalog for this portable workspace."""

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_RELATIVE = Path(".agent") / "skillsets.json"
RESEARCH_SOURCE_RELATIVE = Path(".agent") / "skillsets" / "research"
CATALOGS = (Path(".agents") / "skills", Path(".claude") / "skills")


class SkillsetError(ValueError):
    pass


def load_manifest(root: Path) -> tuple[str, tuple[str, ...]]:
    try:
        raw: Any = json.loads((root / MANIFEST_RELATIVE).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SkillsetError(f"cannot read {MANIFEST_RELATIVE}: {exc}") from exc
    if not isinstance(raw, dict) or set(raw) != {"schema", "default", "skillsets"}:
        raise SkillsetError("skillset manifest must contain only schema, default, and skillsets")
    if raw["schema"] != "portable-skillsets/v1" or raw["default"] != "software":
        raise SkillsetError("skillset manifest has an unsupported schema or default")
    skillsets = raw["skillsets"]
    if not isinstance(skillsets, dict) or set(skillsets) != {"software", "research"}:
        raise SkillsetError("skillset manifest must declare exactly software and research")
    if skillsets["software"] != []:
        raise SkillsetError("software skillset must not add optional research skills")
    research = skillsets["research"]
    if (
        not isinstance(research, list)
        or not research
        or any(not isinstance(name, str) or not name or Path(name).name != name for name in research)
        or len(set(research)) != len(research)
    ):
        raise SkillsetError("research skill names must be a unique non-empty flat string list")
    return raw["default"], tuple(research)


def source_for(root: Path, skill: str) -> Path:
    source = root / RESEARCH_SOURCE_RELATIVE / skill
    if not (source / "SKILL.md").is_file():
        raise SkillsetError(f"research skill source is incomplete: {source.relative_to(root)}")
    return source


def trees_match(left: Path, right: Path) -> bool:
    if not left.is_dir() or not right.is_dir():
        return False
    left_files = {path.relative_to(left) for path in left.rglob("*") if path.is_file()}
    right_files = {path.relative_to(right) for path in right.rglob("*") if path.is_file()}
    return left_files == right_files and all(
        (left / relative).read_bytes() == (right / relative).read_bytes() for relative in left_files
    )


def catalog_mode(root: Path, research: tuple[str, ...]) -> str:
    states: list[set[str]] = []
    for relative in CATALOGS:
        catalog = root / relative
        if not catalog.is_dir():
            raise SkillsetError(f"missing visible skill catalog: {relative}")
        states.append({skill for skill in research if (catalog / skill).exists()})
    if states[0] != states[1]:
        raise SkillsetError("Codex and Claude skill catalogs disagree; rerun the intended selection")
    if not states[0]:
        return "software"
    if states[0] == set(research):
        for relative in CATALOGS:
            catalog = root / relative
            for skill in research:
                if not trees_match(source_for(root, skill), catalog / skill):
                    raise SkillsetError(
                        f"visible research skill differs from its source: {relative / skill}; "
                        "edit .agent/skillsets/research and reselect research"
                    )
        return "research"
    raise SkillsetError("research catalog is partial; rerun the intended selection")


def install_skill(source: Path, destination: Path) -> None:
    if destination.exists():
        if not trees_match(source, destination):
            raise SkillsetError(
                f"refusing to overwrite changed visible research skill: {destination.name}; "
                "edit the source under .agent/skillsets/research instead"
            )
        return
    with tempfile.TemporaryDirectory(prefix="skillset-", dir=destination.parent) as temporary:
        staged = Path(temporary) / destination.name
        shutil.copytree(source, staged)
        staged.replace(destination)


def select(root: Path, mode: str) -> str:
    _, research = load_manifest(root)
    sources = {skill: source_for(root, skill) for skill in research}
    if mode == "research":
        for relative in CATALOGS:
            catalog = root / relative
            if not catalog.is_dir():
                raise SkillsetError(f"missing visible skill catalog: {relative}")
            for skill in research:
                install_skill(sources[skill], catalog / skill)
    else:
        for relative in CATALOGS:
            catalog = root / relative
            if not catalog.is_dir():
                raise SkillsetError(f"missing visible skill catalog: {relative}")
            for skill in research:
                destination = catalog / skill
                if destination.exists():
                    shutil.rmtree(destination)
    return catalog_mode(root, research)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("current", "software", "research"))
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        _, research = load_manifest(root)
        if args.command == "current":
            print(catalog_mode(root, research))
        else:
            print(select(root, args.command))
    except SkillsetError as exc:
        print(f"select-skillset: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
