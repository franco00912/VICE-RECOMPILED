#!/usr/bin/env python3
"""VICE RECOMPILED: local-only status and revision tooling for research builds.

This companion never reads game-file contents.  It inspects paths, completion
manifests and Git metadata so a long build can be resumed deliberately.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import platform
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class PoolState:
    relative_path: str
    size_bytes: int
    output_dir: str
    complete: bool


def pool_output(game: Path, work: Path, source: Path) -> Path:
    rel = source.relative_to(game)
    parts = rel.parts
    root = work / "assets"
    if parts and parts[0].lower() == "pack" and len(parts) > 1:
        root = root / "ttpf_pack" / parts[1]
    else:
        root = root / "ttpf"
    return root / source.stem


def discover_pools(game: Path, work: Path) -> list[PoolState]:
    rows: list[PoolState] = []
    for source in sorted(game.rglob("*.ttpf"), key=lambda p: (p.stat().st_size, str(p).lower())):
        output = pool_output(game, work, source)
        rows.append(PoolState(
            relative_path=str(source.relative_to(game)),
            size_bytes=source.stat().st_size,
            output_dir=str(output),
            complete=(output / "manifest.json").is_file(),
        ))
    return rows


def git_value(repo: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args], check=True, capture_output=True,
            text=True, encoding="utf-8", errors="replace",
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    value = result.stdout.strip()
    return value or None


def atomic_write(path: Path, payload: str) -> None:
    """Publish a report only after its complete contents are safely on disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(payload, encoding="utf-8")
    os.replace(temp, path)


def compare_reports(previous: dict, current: dict) -> dict:
    old_rows = {
        row["relative_path"]: bool(row["complete"])
        for row in previous.get("texture_pools", {}).get("items", [])
        if isinstance(row, dict) and isinstance(row.get("relative_path"), str)
    }
    new_rows = {
        row["relative_path"]: bool(row["complete"])
        for row in current.get("texture_pools", {}).get("items", [])
        if isinstance(row, dict) and isinstance(row.get("relative_path"), str)
    }
    completed = sorted(path for path, done in new_rows.items() if done and not old_rows.get(path, False))
    regressed = sorted(path for path, done in new_rows.items() if not done and old_rows.get(path, False))
    return {
        "previous_revision": previous.get("revision"),
        "current_revision": current.get("revision"),
        "newly_completed_pools": completed,
        "regressed_pools": regressed,
        "pool_delta": len(completed) - len(regressed),
    }


def status_document(game: Path, work: Path, repo: Path) -> dict:
    pools = discover_pools(game, work)
    complete = sum(row.complete for row in pools)
    free = shutil.disk_usage(work).free if work.exists() else shutil.disk_usage(work.parent).free
    return {
        "schema": 1,
        "game": str(game),
        "work": str(work),
        "repo": str(repo),
        "revision": git_value(repo, "rev-parse", "HEAD"),
        "revision_short": git_value(repo, "rev-parse", "--short", "HEAD"),
        "submodules": git_value(repo, "submodule", "status", "--recursive"),
        "working_tree_clean": git_value(repo, "status", "--porcelain") is None,
        "game_executable_present": (game / "game_scarlett_master.exe").is_file(),
        "free_bytes": free,
        "texture_pools": {
            "total": len(pools),
            "complete": complete,
            "incomplete": len(pools) - complete,
            "items": [asdict(row) for row in pools],
        },
        "markers": {
            "ogg": (work / "assets" / "audio" / "ogg.done").is_file(),
            "xma": (work / "assets" / "audio" / "xma.done").is_file(),
            "shaders": (work / "shaders" / "spirv" / "index.json").is_file(),
        },
        "tool": {
            "name": "VICE RECOMPILED",
            "schema": 1,
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
    }


def print_human(doc: dict) -> None:
    pools = doc["texture_pools"]
    print(f"Source revision: {doc['revision_short'] or 'unknown'}")
    print(f"Working tree clean: {'yes' if doc['working_tree_clean'] else 'no'}")
    print(f"Free space: {doc['free_bytes'] / 2**30:.1f} GiB")
    print(f"TTPF pools: {pools['complete']}/{pools['total']} complete")
    print(f"Game executable: {'present' if doc['game_executable_present'] else 'missing'}")
    missing = [row for row in pools["items"] if not row["complete"]]
    if missing:
        print("Incomplete pools:")
        for row in missing:
            print(f"  - {row['relative_path']} ({row['size_bytes'] / 2**30:.2f} GiB source)")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="vice-recompiled")
    parser.add_argument("--game", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-report", type=Path)
    parser.add_argument("--write-lock", type=Path,
                        help="write a revision/toolchain lockfile without game contents")
    parser.add_argument("--baseline", type=Path,
                        help="compare with an earlier JSON report and fail if completed pools regress")
    args = parser.parse_args(argv)

    for label, path in (("game", args.game), ("repo", args.repo)):
        if not path.is_dir():
            parser.error(f"{label} folder does not exist: {path}")
    if not args.work.exists() and not args.work.parent.is_dir():
        parser.error(f"work folder and its parent do not exist: {args.work}")

    doc = status_document(args.game.resolve(), args.work.resolve(), args.repo.resolve())
    if args.baseline:
        try:
            previous = json.loads(args.baseline.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            parser.error(f"cannot read baseline {args.baseline}: {exc}")
        doc["comparison"] = compare_reports(previous, doc)
    payload = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    if args.write_report:
        atomic_write(args.write_report, payload)
    if args.write_lock:
        lock = {
            "schema": 1,
            "source_revision": doc["revision"],
            "source_submodules": doc["submodules"],
            "working_tree_clean": doc["working_tree_clean"],
            "tool": doc["tool"],
        }
        atomic_write(args.write_lock, json.dumps(lock, indent=2, ensure_ascii=False) + "\n")
    if args.json:
        print(payload, end="")
    else:
        print_human(doc)
    if doc.get("comparison", {}).get("regressed_pools"):
        print("ERROR: one or more completed pools regressed", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
