from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

try:
    from .h3_pipeline import H3ValidationError, compile_manifest, write_json
except ImportError:  # pragma: no cover - direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from tools.h3_pipeline import H3ValidationError, compile_manifest, write_json  # type: ignore


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compile QingCS ten-grid storyboards into portable MiniMax-H3 JSON jobs."
    )
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--chapter", type=int, action="append", default=[])
    parser.add_argument("--generated-dir", type=Path, default=None)
    parser.add_argument(
        "--allow-partial-manifest",
        action="store_true",
        help="Allow a manifest with fewer than the production 44 chapters; intended for tests or staged authoring.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        chapter_numbers = set(args.chapter) or None
        expected_count = None if args.allow_partial_manifest else 44
        compiled = compile_manifest(
            args.manifest,
            chapter_numbers=chapter_numbers,
            expected_chapter_count=expected_count,
        )
        generated_dir = args.generated_dir
        if generated_dir is None:
            generated_dir = args.manifest.resolve().parents[1] / "generated"
        generated_dir.mkdir(parents=True, exist_ok=True)

        index_chapters: list[dict[str, object]] = []
        job_count = 0
        for chapter in compiled["chapters"]:
            number = int(chapter["chapter"])
            target = generated_dir / f"ch{number:02d}.h3.json"
            write_json(target, chapter)
            count = len(chapter.get("jobs", []))
            job_count += count
            index_chapters.append(
                {
                    "chapter": number,
                    "title": chapter.get("title", ""),
                    "status": chapter.get("status", "unreviewed"),
                    "source_storyboard": chapter.get("source_storyboard", ""),
                    "job_count": count,
                    "file": target.name,
                }
            )

        write_json(
            generated_dir / "index.json",
            {
                "schema_version": "1.0",
                "project_id": compiled["project_id"],
                "chapter_count": len(index_chapters),
                "job_count": job_count,
                "chapters": index_chapters,
            },
        )
        print(
            f"compiled {len(index_chapters)} chapter(s), {job_count} H3 job(s) -> {generated_dir}"
        )
        return 0
    except H3ValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
