from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

try:
    from .h3_pipeline import (
        H3ValidationError,
        build_mmx_command,
        compile_manifest,
        write_json,
    )
except ImportError:  # pragma: no cover - direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from tools.h3_pipeline import (  # type: ignore
        H3ValidationError,
        build_mmx_command,
        compile_manifest,
        write_json,
    )


def require_execute_scope(
    *,
    execute: bool,
    chapters: Sequence[int],
    grids: Sequence[int],
    all_grids: bool,
) -> None:
    if not execute:
        return
    if len(chapters) != 1:
        raise H3ValidationError("paid execution requires exactly one --chapter")
    if all_grids and grids:
        raise H3ValidationError("use either --all-grids or --grid, not both")
    if not all_grids and not grids:
        raise H3ValidationError("paid execution requires --grid or --all-grids")
    invalid = [grid for grid in grids if grid < 1 or grid > 10]
    if invalid:
        raise H3ValidationError(f"grid numbers must be 1-10: {invalid}")


def ensure_api_key_auth(status: Mapping[str, Any]) -> None:
    if status.get("method") != "api-key":
        raise H3ValidationError(
            "MiniMax-H3 requires a Pay-as-you-go/Credit API key; run 'mmx auth login' and choose API key"
        )


def filter_jobs(
    compiled_chapters: Iterable[Mapping[str, Any]],
    *,
    chapters: set[int] | None = None,
    grids: set[int] | None = None,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for chapter in compiled_chapters:
        chapter_number = int(chapter["chapter"])
        if chapters is not None and chapter_number not in chapters:
            continue
        for job in chapter.get("jobs", []):
            if grids is not None and int(job["grid"]) not in grids:
                continue
            selected.append(dict(job))
    return selected


def _auth_status(mmx_executable: str, cwd: Path) -> dict[str, Any]:
    result = subprocess.run(
        [mmx_executable, "auth", "status", "--output", "json", "--quiet"],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise H3ValidationError(
            "unable to verify MMX authentication; run 'mmx auth status --output json --quiet' locally"
        )
    try:
        status = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise H3ValidationError("MMX auth status did not return valid JSON") from exc
    if not isinstance(status, dict):
        raise H3ValidationError("MMX auth status JSON must be an object")
    ensure_api_key_auth(status)
    return status


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compile QingCS storyboards and optionally run official MiniMax-H3 MMX jobs."
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--chapter", type=int, action="append", default=[])
    parser.add_argument("--grid", type=int, action="append", default=[])
    parser.add_argument("--all-grids", action="store_true")
    parser.add_argument("--compile-only", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--generated-dir", type=Path, default=None)
    parser.add_argument("--mmx", default=os.environ.get("MMX_EXECUTABLE", "mmx"))
    parser.add_argument("--poll-interval", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=1800)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        require_execute_scope(
            execute=args.execute,
            chapters=args.chapter,
            grids=args.grid,
            all_grids=args.all_grids,
        )
        chapter_set = set(args.chapter) or None
        compiled = compile_manifest(args.manifest, chapter_numbers=chapter_set)
        generated_dir = args.generated_dir
        if generated_dir is None:
            generated_dir = args.manifest.resolve().parents[1] / "generated"
        generated_dir.mkdir(parents=True, exist_ok=True)
        for chapter in compiled["chapters"]:
            target = generated_dir / f"ch{int(chapter['chapter']):02d}.h3.json"
            write_json(target, chapter)

        grids = set(args.grid) if args.grid else None
        jobs = filter_jobs(compiled["chapters"], chapters=chapter_set, grids=grids)
        project_root = Path(compiled["project_root"])

        if args.compile_only:
            print(f"compiled {len(compiled['chapters'])} chapter(s), {len(jobs)} job(s) -> {generated_dir}")
            return 0

        if not args.execute:
            for job in jobs:
                command = build_mmx_command(
                    job,
                    mmx_executable=args.mmx,
                    poll_interval=args.poll_interval,
                    timeout=args.timeout,
                )
                print(shlex.join(command))
            return 0

        _auth_status(args.mmx, project_root)
        if args.all_grids:
            jobs = filter_jobs(compiled["chapters"], chapters=chapter_set, grids=None)

        for job in jobs:
            output = project_root / str(job["download"])
            if output.exists():
                print(f"SKIP {job['job_id']}: output already exists at {output}")
                continue
            output.parent.mkdir(parents=True, exist_ok=True)
            command = build_mmx_command(
                job,
                mmx_executable=args.mmx,
                poll_interval=args.poll_interval,
                timeout=args.timeout,
            )
            print(f"RUN {job['job_id']}")
            result = subprocess.run(command, cwd=project_root, check=False)
            if result.returncode != 0:
                print(
                    f"STOP {job['job_id']}: mmx exited with {result.returncode}; no automatic retry was submitted",
                    file=sys.stderr,
                )
                return result.returncode
        return 0
    except H3ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
