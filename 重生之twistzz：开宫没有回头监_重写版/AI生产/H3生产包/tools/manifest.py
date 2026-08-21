from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from .common import ALLOWED_RATIOS, H3ValidationError
from .h3_jobs import build_h3_prompt, validate_job
from .references import detect_character_references, detect_scene_references
from .storyboard import parse_storyboard_text


def compile_storyboard(
    *,
    source_path: Path,
    chapter_config: Mapping[str, Any],
    defaults: Mapping[str, Any],
    character_registry: Mapping[str, Any],
    output_root: str,
    scene_registry: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    parsed = parse_storyboard_text(
        source_path.read_text(encoding="utf-8"), source=str(source_path), strict=True
    )
    expected_chapter = int(chapter_config.get("chapter", parsed["chapter"]))
    if parsed["chapter"] != expected_chapter:
        raise H3ValidationError(
            f"{source_path}: manifest chapter {expected_chapter} != source chapter {parsed['chapter']}"
        )

    protagonist_id = str(chapter_config.get("protagonist_id", "CHAR_ZEIZEI"))
    protagonist_from = int(chapter_config.get("protagonist_ref_from_grid", 1))
    jobs: list[dict[str, Any]] = []
    for grid in parsed["grids"]:
        protagonist = protagonist_id if int(grid["grid"]) >= protagonist_from else None
        references = detect_character_references(
            str(grid.get("raw_text", "")),
            character_registry,
            protagonist_id=protagonist,
            max_images=9,
        )
        scenes = detect_scene_references(str(grid.get("raw_text", "")), scene_registry)
        reference_images = [str(item["reference_image"]) for item in references]
        mode = "ref2va" if reference_images else "t2va"
        job_id = f"QINGCS_CH{expected_chapter:02d}_G{int(grid['grid']):02d}"
        job = {
            "job_id": job_id,
            "chapter": expected_chapter,
            "chapter_title": chapter_config.get("title") or parsed["title"],
            "grid": int(grid["grid"]),
            "grid_title": grid.get("title", f"第{grid['grid']}格"),
            "source_storyboard": str(source_path),
            "model": defaults.get("model", "MiniMax-H3"),
            "mode": mode,
            "duration": int(defaults.get("duration", 15)),
            "ratio": defaults.get("ratio", "16:9"),
            "prompt": build_h3_prompt(grid, defaults, references, scenes),
            "image": None,
            "last_frame": None,
            "reference_images": reference_images,
            "reference_videos": [],
            "reference_audios": [],
            "download": f"{output_root.rstrip('/')}/ch{expected_chapter:02d}/{job_id}.mp4",
            "post_text_policy": defaults.get("post_text_policy", ""),
            "source_format": grid.get("format"),
            "scene_ids": [item["id"] for item in scenes],
        }
        validate_job(job)
        jobs.append(job)

    return {
        "schema_version": "1.0",
        "project_id": "qingcs-rewrite-minimax-h3",
        "chapter": expected_chapter,
        "title": chapter_config.get("title") or parsed["title"],
        "source_storyboard": str(source_path),
        "status": chapter_config.get("status", "unreviewed"),
        "jobs": jobs,
    }


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise H3ValidationError(f"{path}: top-level JSON value must be an object")
    return value


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def validate_manifest(
    manifest: Mapping[str, Any], *, expected_chapter_count: int | None = 44
) -> None:
    errors: list[str] = []
    if manifest.get("schema_version") != "1.0":
        errors.append("schema_version must be '1.0'")
    if not manifest.get("project_id"):
        errors.append("project_id is required")
    if not isinstance(manifest.get("project_root"), str):
        errors.append("project_root is required")

    defaults = manifest.get("defaults")
    if not isinstance(defaults, Mapping):
        errors.append("defaults must be an object")
    else:
        if defaults.get("model") != "MiniMax-H3":
            errors.append("defaults.model must be MiniMax-H3")
        duration = defaults.get("duration")
        if not isinstance(duration, int) or not 4 <= duration <= 15:
            errors.append("defaults.duration must be an integer from 4 through 15")
        if defaults.get("ratio") not in ALLOWED_RATIOS:
            errors.append("defaults.ratio is unsupported")
        if not defaults.get("output_root"):
            errors.append("defaults.output_root is required")

    registries = manifest.get("registries")
    if not isinstance(registries, Mapping) or not registries.get("characters"):
        errors.append("registries.characters is required")

    chapters = manifest.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        errors.append("chapters must be a non-empty array")
    else:
        numbers: list[int] = []
        for index, chapter in enumerate(chapters, start=1):
            if not isinstance(chapter, Mapping):
                errors.append(f"chapters[{index}] must be an object")
                continue
            number = chapter.get("chapter")
            if not isinstance(number, int) or number <= 0:
                errors.append(f"chapters[{index}].chapter must be a positive integer")
            else:
                numbers.append(number)
            if not chapter.get("title"):
                errors.append(f"chapters[{index}].title is required")
            if not chapter.get("storyboard"):
                errors.append(f"chapters[{index}].storyboard is required")
        if len(numbers) != len(set(numbers)):
            errors.append("chapter numbers must be unique")
        if expected_chapter_count is not None and len(chapters) != expected_chapter_count:
            errors.append(
                f"manifest must contain exactly {expected_chapter_count} chapter entries"
            )
    if errors:
        raise H3ValidationError("manifest: " + "; ".join(errors))


def compile_manifest(
    manifest_path: Path,
    *,
    chapter_numbers: set[int] | None = None,
    expected_chapter_count: int | None = 44,
) -> dict[str, Any]:
    manifest_path = manifest_path.resolve()
    manifest = load_json(manifest_path)
    validate_manifest(manifest, expected_chapter_count=expected_chapter_count)
    project_root = (manifest_path.parent / str(manifest["project_root"])).resolve()
    character_registry = load_json(
        project_root / str(manifest["registries"]["characters"])
    )
    scene_registry: Mapping[str, Any] | None = None
    scene_registry_rel = manifest.get("registries", {}).get("scenes")
    if scene_registry_rel:
        scene_registry = load_json(project_root / str(scene_registry_rel))
    defaults = dict(manifest["defaults"])
    output_root = str(defaults["output_root"])

    selected = [
        chapter
        for chapter in manifest["chapters"]
        if chapter_numbers is None or int(chapter["chapter"]) in chapter_numbers
    ]
    if chapter_numbers is not None:
        found = {int(item["chapter"]) for item in selected}
        missing = sorted(chapter_numbers - found)
        if missing:
            raise H3ValidationError(f"manifest does not contain chapters: {missing}")

    compiled_chapters: list[dict[str, Any]] = []
    for chapter in selected:
        source_relative = str(chapter["storyboard"])
        source_path = project_root / source_relative
        if not source_path.is_file():
            raise H3ValidationError(f"storyboard not found: {source_relative}")
        compiled = compile_storyboard(
            source_path=source_path,
            chapter_config=chapter,
            defaults=defaults,
            character_registry=character_registry,
            output_root=output_root,
            scene_registry=scene_registry,
        )
        compiled["source_storyboard"] = source_relative
        for job in compiled["jobs"]:
            job["source_storyboard"] = source_relative
        compiled_chapters.append(compiled)

    return {
        "schema_version": "1.0",
        "project_id": manifest["project_id"],
        "manifest_path": str(manifest_path),
        "project_root": str(project_root),
        "defaults": defaults,
        "chapters": compiled_chapters,
    }
