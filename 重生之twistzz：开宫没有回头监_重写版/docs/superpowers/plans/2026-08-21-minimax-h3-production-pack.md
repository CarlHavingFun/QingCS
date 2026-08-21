# QingCS MiniMax-H3 Production Pack Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-safe pipeline that converts the existing 44 QingCS ten-grid storyboards into portable MiniMax-H3 JSON jobs and explicit official MMX commands without creating a second narrative source of truth.

**Architecture:** Keep Markdown storyboards authoritative. A dependency-free Python parser recognizes the chapter-1 director format and the chapter-2–44 six-field format, resolves character and scene registries, validates H3 mode constraints, and writes portable per-chapter JSON. A separate runner defaults to free dry-run output and gates every paid call by chapter/grid scope and API-key authentication.

**Tech Stack:** Python 3.11+ standard library, JSON/JSON Schema, official `mmx-cli`, GitHub Git Data API.

**Spec:** `AI生产/H3生产包/00_改编与生产总览.md`

## Global Constraints

- Chapters 1—44 are executable only from their existing `分镜/第NN章_十格分镜.md` files.
- Chapters 45—56 remain outline-only until prose and ten-grid storyboards exist.
- MiniMax model is exactly `MiniMax-H3`; duration is an integer from 4 through 15; production default is 15; ratio is 16:9.
- Frame input mode and multimodal reference mode never mix.
- Exact visible text is post-production only.
- Paid execution requires exactly one chapter and an explicit grid list or `--all-grids`.
- No API key, output video, generated JSON cache, or local state is committed.

---

### Task 1: Storyboard parser and prompt compiler

**Files:**
- Create: `AI生产/H3生产包/tools/common.py`
- Create: `AI生产/H3生产包/tools/storyboard.py`
- Create: `AI生产/H3生产包/tools/references.py`
- Create: `AI生产/H3生产包/tools/h3_jobs.py`
- Create: `AI生产/H3生产包/tools/manifest.py`
- Create: `AI生产/H3生产包/tools/h3_pipeline.py` (compatibility facade)
- Test: `AI生产/H3生产包/tests/test_h3_pipeline.py`

**Interfaces:**
- Consumes: chapter Markdown text, defaults, character registry, optional scene registry.
- Produces: `parse_storyboard_text`, `build_h3_prompt`, `compile_storyboard`, `validate_job`, `build_mmx_command`.

- [x] Write failing tests for both storyboard formats, ten-grid strictness, three-phase extraction and embedded director fields.
- [x] Run tests and confirm failure before implementation.
- [x] Implement strict parsing and two-layer H3 prompt compilation.
- [x] Add character/scene lock resolution and H3 mode validation.
- [x] Verify all parser/compiler tests pass.

### Task 2: Manifest compiler and portable JSON

**Files:**
- Create: `AI生产/H3生产包/tools/compile_storyboards.py`
- Create: `AI生产/H3生产包/config/qingcs-h3-manifest.json`
- Create: `AI生产/H3生产包/schema/qingcs-h3-batch.schema.json`
- Test: `AI生产/H3生产包/tests/test_manifest_runner.py`
- Test: `AI生产/H3生产包/tests/test_compile_cli.py`

**Interfaces:**
- Consumes: 44-entry manifest and authoritative Markdown storyboards.
- Produces: `generated/chNN.h3.json` and `generated/index.json` with no absolute project paths.

- [x] Write failing tests for duplicate chapters, path resolution, selected-chapter compile and portable CLI output.
- [x] Implement manifest validation and chapter selection.
- [x] Implement JSON writer and index generation.
- [x] Register chapters 1—44 and mark 45—56 outline-only.
- [x] Verify 16 unit/integration tests pass locally.

### Task 3: Paid-run safety and official MMX adapter

**Files:**
- Create: `AI生产/H3生产包/tools/run_h3_batch.py`
- Modify: `AI生产/H3生产包/tests/test_manifest_runner.py`

**Interfaces:**
- Consumes: manifest, chapter/grid scope and local MMX authentication.
- Produces: dry-run commands or blocking paid H3 calls with stop-on-failure behavior.

- [x] Write failing tests for explicit paid scope, API-key auth and job filtering.
- [x] Implement free dry-run as default.
- [x] Require one chapter plus grid(s) or `--all-grids` for `--execute`.
- [x] Skip existing outputs, disable automatic retry and stop on first non-zero MMX exit.
- [x] Build commands with explicit H3 model, duration, ratio, references, download, poll and timeout flags.

### Task 4: Character and scene production registries

**Files:**
- Create: `AI生产/H3生产包/assets/characters.json`
- Create: `AI生产/H3生产包/assets/scenes.json`
- Create: `AI生产/H3生产包/01_场景设定总表.md`
- Create: `AI生产/H3生产包/02_人物设定总表.md`

**Interfaces:**
- Consumes: existing character dossiers, palace index and accepted visual assets.
- Produces: stable IDs, textual appearance/performance locks, scene visual/continuity locks and seven accepted character reference paths.

- [x] Map all 22 core characters to stable IDs and authority boundaries.
- [x] Attach only the seven already accepted three-view images.
- [x] Map modern, palace-work, competition and map spaces to stable scene IDs.
- [x] Prevent multi-panel scene concept boards from being automatically attached as H3 references.

### Task 5: Documentation and project Skill

**Files:**
- Create: `AI生产/H3生产包/README.md`
- Create: `AI生产/H3生产包/00_改编与生产总览.md`
- Create: `AI生产/H3生产包/03_分镜与H3提示词规范.md`
- Create: `AI生产/H3生产包/generated/README.md`
- Create: `skills/qingcs-minimax-h3-production/SKILL.md`
- Modify: `README.md`
- Modify: `00_重写版状态.md`

**Interfaces:**
- Consumes: implemented pipeline and official MMX/H3 operating constraints.
- Produces: one production entrance, local commands, QA gates and current project status.

- [x] Document free compile, free dry-run and explicit paid execution.
- [x] Document exact-text post policy, character references and scene locks.
- [x] Define the new project Skill and its read order.
- [x] Refresh stale root status statements while preserving independent-review warnings.

### Task 6: Verification and branch commit

**Files:**
- Verify all files in this plan.

**Interfaces:**
- Consumes: working tree and GitHub main branch.
- Produces: one feature-branch commit and an auditable diff.

- [x] Run full unit test discovery and Python bytecode compilation.
- [x] Parse every committed JSON file.
- [x] Validate manifest entry count, chapter uniqueness, stable file paths and 440-job expectation.
- [x] Verify authoritative source paths through GitHub API because the execution container cannot clone the public repository.
- [x] Create a feature branch, assemble one atomic Git Data tree, commit through the GitHub API, and fetch committed files back for verification.
