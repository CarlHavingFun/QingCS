from __future__ import annotations

from typing import Any, Mapping, Sequence

from .common import ALLOWED_RATIOS, H3_FIELD_NAMES, H3ValidationError
from .references import reference_mapping_text, scene_lock_text


def build_h3_prompt(
    grid: Mapping[str, Any],
    defaults: Mapping[str, Any],
    references: Sequence[Mapping[str, Any]],
    scenes: Sequence[Mapping[str, Any]] = (),
) -> str:
    style_lock = str(defaults.get("style_lock", ""))
    negative = str(defaults.get("global_negative", ""))
    post_text = str(defaults.get("post_text_policy", ""))
    reference_mapping = reference_mapping_text(references)
    scene_lock = scene_lock_text(scenes)

    if grid.get("format") == "director" and grid.get("h3_fields"):
        h3_fields: Mapping[str, str] = grid["h3_fields"]
        field_lines = [
            f"{name}: {h3_fields[name]}" for name in H3_FIELD_NAMES if h3_fields.get(name)
        ]
        prompt = "\n".join(
            [
                "输出规格：MiniMax-H3，15秒，16:9，电影级半写实国漫，原生立体声。",
                f"全局视觉锁定：{style_lock}",
                reference_mapping,
                scene_lock,
                "总段 00:00-00:15：只完成本格的一个因果节拍，并在明确终态上停住。",
                *field_lines,
                f"POST_TEXT_POLICY: {post_text}",
                f"GLOBAL_NEGATIVE: {negative}",
            ]
        )
    else:
        timeline_lines = [
            f"- {phase['range']}：{phase['action']}" for phase in grid.get("timeline", [])
        ]
        prompt = "\n".join(
            [
                "输出规格：MiniMax-H3，15秒，16:9，电影级半写实国漫，原生立体声。",
                f"全局视觉锁定：{style_lock}",
                reference_mapping,
                scene_lock,
                f"总段 00:00-00:15：{grid.get('relationship_beat', '')}",
                "分拍时间线：",
                *timeline_lines,
                f"镜头与地点：{grid.get('location', '')}",
                f"空间与调度锚点：{grid.get('spatial_anchors', '')}",
                f"对白与声音：{grid.get('dialogue_audio', '')}",
                f"可核验比赛/流程事实：{grid.get('cs_facts', '')}",
                "终态锁定：10—15秒的结果、台词或证据必须保持到切出，不新增第二个事件。",
                f"后期文字策略：{post_text}",
                f"负面约束：{negative}；不要额外人物、不要越轴、不要把参考图排版复制进场景。",
            ]
        )
    if len(prompt) > 7000:
        raise H3ValidationError(
            f"grid {grid.get('grid')}: compiled prompt exceeds MiniMax-H3 7000-character limit"
        )
    return prompt


def validate_job(job: Mapping[str, Any]) -> None:
    errors: list[str] = []
    if job.get("model") != "MiniMax-H3":
        errors.append("model must be MiniMax-H3")
    duration = job.get("duration")
    if not isinstance(duration, int) or not 4 <= duration <= 15:
        errors.append("duration must be an integer from 4 through 15")
    if job.get("ratio") not in ALLOWED_RATIOS:
        errors.append(f"ratio must be one of {sorted(ALLOWED_RATIOS)}")

    prompt = job.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        errors.append("prompt must be a non-empty string")
    elif len(prompt) > 7000:
        errors.append("prompt exceeds 7000 characters")

    images = list(job.get("reference_images") or [])
    videos = list(job.get("reference_videos") or [])
    audios = list(job.get("reference_audios") or [])
    image = job.get("image")
    last_frame = job.get("last_frame")
    mode = job.get("mode")

    if len(images) > 9:
        errors.append("at most 9 reference images are allowed")
    if len(videos) > 3:
        errors.append("at most 3 reference videos are allowed")
    if len(audios) > 3:
        errors.append("at most 3 reference audios are allowed")
    if len(images) + len(videos) + len(audios) > 12:
        errors.append("at most 12 mixed reference items are allowed")
    if audios and not (images or videos):
        errors.append("reference audio requires at least one reference image or video")

    has_refs = bool(images or videos or audios)
    has_frames = bool(image or last_frame)
    if has_refs and has_frames:
        errors.append("frame mode cannot be mixed with reference mode")
    if mode == "t2va" and (has_refs or has_frames):
        errors.append("t2va cannot include frame or reference inputs")
    elif mode == "i2va" and (not image or last_frame or has_refs):
        errors.append("i2va requires image only")
    elif mode == "fl2va" and (not image or not last_frame or has_refs):
        errors.append("fl2va requires image and last_frame, without references")
    elif mode == "l2va" and (image or not last_frame or has_refs):
        errors.append("l2va requires last_frame only")
    elif mode == "ref2va" and (not (images or videos) or has_frames):
        errors.append("ref2va requires reference image/video and no frame inputs")
    elif mode not in {"t2va", "i2va", "fl2va", "l2va", "ref2va"}:
        errors.append("unsupported H3 mode")
    if not job.get("download"):
        errors.append("download path is required")
    if errors:
        raise H3ValidationError(f"{job.get('job_id', '<job>')}: " + "; ".join(errors))


def build_mmx_command(
    job: Mapping[str, Any],
    *,
    mmx_executable: str = "mmx",
    poll_interval: int = 10,
    timeout: int = 1800,
) -> list[str]:
    validate_job(job)
    command = [
        mmx_executable,
        "video",
        "generate",
        "--model",
        "MiniMax-H3",
        "--prompt",
        str(job["prompt"]),
        "--duration",
        str(job["duration"]),
        "--ratio",
        str(job["ratio"]),
    ]
    mode = job["mode"]
    if mode in {"i2va", "fl2va"}:
        command.extend(["--image", str(job["image"])])
    if mode in {"fl2va", "l2va"}:
        command.extend(["--last-frame", str(job["last_frame"])])
    if mode == "ref2va":
        for path in job.get("reference_images", []):
            command.extend(["--reference-image", str(path)])
        for path in job.get("reference_videos", []):
            command.extend(["--reference-video", str(path)])
        for path in job.get("reference_audios", []):
            command.extend(["--reference-audio", str(path)])
    command.extend(
        [
            "--download",
            str(job["download"]),
            "--poll-interval",
            str(poll_interval),
            "--timeout",
            str(timeout),
            "--non-interactive",
        ]
    )
    return command
