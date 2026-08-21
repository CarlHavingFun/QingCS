"""Compatibility facade for QingCS MiniMax-H3 production helpers."""

from .common import ALLOWED_RATIOS, H3_FIELD_NAMES, STANDARD_FIELD_NAMES, H3ValidationError
from .h3_jobs import build_h3_prompt, build_mmx_command, validate_job
from .manifest import (
    compile_manifest,
    compile_storyboard,
    load_json,
    validate_manifest,
    write_json,
)
from .references import detect_character_references, detect_scene_references
from .storyboard import parse_storyboard_text

__all__ = [
    "ALLOWED_RATIOS",
    "H3_FIELD_NAMES",
    "STANDARD_FIELD_NAMES",
    "H3ValidationError",
    "build_h3_prompt",
    "build_mmx_command",
    "compile_manifest",
    "compile_storyboard",
    "detect_character_references",
    "detect_scene_references",
    "load_json",
    "parse_storyboard_text",
    "validate_job",
    "validate_manifest",
    "write_json",
]
