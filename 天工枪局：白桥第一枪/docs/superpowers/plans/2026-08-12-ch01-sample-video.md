# Chapter 1 Complete-Sound Sample Video Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate 18 MiniMax H3 audiovisual shots on kk9850, replace guide dialogue with stable character voices, composite post text, mix sound, and deliver a 1920×1080 24 fps 68.5-second MP4 sample.

**Architecture:** Each approved keyframe drives one isolated local MiniMax H3 job. All jobs use the proven 864×480, 124-frame, 24 fps audiovisual workflow and run serially under the global H3 lock; outputs are trimmed to exact shot durations. H3 Ref2VA cites approved local character voice seeds and may produce final dialogue together with synchronized ambience/SFX. A shot whose locked dialogue fails ASR is repaired at the audio layer or regenerated; no paid T2A dependency is required. The final edit upscales, overlays exact UI/subtitles, and mixes to a single 1080p master.

**Tech Stack:** kk9850 ComfyUI MiniMax H3 Ref2VA/FL2VA, ComfyUI frame upscale, FFmpeg/ffprobe, Whisper ASR, JSON manifests, SHA-256.

## Global Constraints

- One H3 job at a time on kk9850; never overlap H3 with ComfyUI image repair or upscale.
- Each job uses `864×480`, 24 fps, `length=124`, 20 steps, `res_multistep`, and the installed H3 audio/video VAEs.
- `S03_SH02` uses `last_frame`; the other 17 shots use `first_frame`.
- H3 output is accepted as the dialogue source only when its cited Voice ID, exact script content, timing and ASR all pass; otherwise dialogue is regenerated from the same local reference seed.
- Trim every shot to its authored duration; final duration is exactly 68.5 seconds at 24 fps.
- Exact UI, scores, names, and paper text are post-production overlays only.
- Never publish ports; ComfyUI remains loopback-only on kk9850.
- Preserve job request, seed, source checksum, prompt checksum, elapsed time, output checksum, GPU telemetry, and QA result.

---

### Task 1: Build the 18-job H3 manifest

**Files:**
- Create: `天工枪局：白桥第一枪/AI生产/样片01/视频/h3-job-manifest.json`
- Create: `天工枪局：白桥第一枪/AI生产/样片01/视频/README.md`

**Interfaces:**
- Consumes: 18 H3 prompts and 18 approved H3 input images.
- Produces: 18 versioned ComfyUI requests with exact source hashes and output prefixes.

- [ ] **Step 1: Create one record per shot**

Each record contains `shot_id`, `duration`, `mode`, `input_path`, `input_sha256`, `prompt_sha256`, `seed`, `length=124`, `fps=24`, `remote_output_prefix`, `local_raw_path`, `trimmed_path`, `qa`, and `status`.

- [ ] **Step 2: Validate the contract**

```bash
jq -e '.shots | length == 18' '天工枪局：白桥第一枪/AI生产/样片01/视频/h3-job-manifest.json'
jq -e '[.shots[] | select(.length == 124 and .fps == 24)] | length == 18' '天工枪局：白桥第一枪/AI生产/样片01/视频/h3-job-manifest.json'
```

Expected: both return true.

### Task 2: Generate and approve one proof shot

**Files:**
- Create: `天工枪局：白桥第一枪/AI生产/样片01/视频/raw/S04_SH01_v001.mp4`
- Create: `天工枪局：白桥第一枪/AI生产/样片01/视频/reports/S04_SH01_v001.json`

**Interfaces:**
- Consumes: `S04_SH01` first frame and H3 prompt.
- Produces: a proof that identity, audiovisual output, remote workflow, download, and QA work end-to-end.

- [ ] **Step 1: Pass live preflight**

Verify queue empty, H3 global lock absent, model files present, `first_frame` supported, input checksum matches, and no competing GPU-heavy process is active.

- [ ] **Step 2: Submit exactly one workflow**

Use the recovered graph: `LoadImage → MiniMaxH3ImageToVideo → BasicGuider → SamplerCustomAdvanced → VAEDecode + VAEDecodeAudio → CreateVideo → SaveVideo`.

- [ ] **Step 3: Download and inspect**

Require 864×480, 24 fps, audio stream present, non-zero duration, stable Zhou Ye identity, wrist brace and medal, no portal effect, and authored motion order.

### Task 3: Generate the remaining 17 H3 shots serially

**Files:**
- Create: `天工枪局：白桥第一枪/AI生产/样片01/视频/raw/<SHOT_ID>_vNNN.mp4`
- Create: `天工枪局：白桥第一枪/AI生产/样片01/视频/reports/<SHOT_ID>_vNNN.json`
- Modify: `天工枪局：白桥第一枪/AI生产/样片01/视频/h3-job-manifest.json`

**Interfaces:**
- Consumes: approved proof workflow and the remaining inputs.
- Produces: one accepted raw take per shot.

- [ ] **Step 1: Run the scene order**

Generate `S01` through `S07`; do not queue the next shot until the current output is downloaded and the global lock is released.

- [ ] **Step 2: Reject only named failures**

Reject identity drift, hand/weapon geometry failure, wrong layer, wrong action order, unreadable action, invented text, missing audio stream, or camera motion forbidden by the shot. Make at most two versioned repair attempts per failed shot before escalating.

### Task 4: Trim, upscale, and prepare clean picture

**Files:**
- Create: `天工枪局：白桥第一枪/AI生产/样片01/视频/trimmed/<SHOT_ID>.mov`
- Create: `天工枪局：白桥第一枪/AI生产/样片01/视频/upscaled/<SHOT_ID>.mov`

**Interfaces:**
- Consumes: 18 accepted raw takes.
- Produces: 18 exact-duration 1920×1080 24 fps picture masters.

- [ ] **Step 1: Trim to authored duration**

Use frame-accurate 24 fps trims: duration × 24 frames for each shot. Preserve guide audio in a separate stem.

- [ ] **Step 2: Upscale through ComfyUI**

Process frames with a local detail-preserving upscale model, then center crop/pad to exact 1920×1080. Preserve film grain and line detail; no new faces, text, or weapon parts.

- [ ] **Step 3: Validate all picture masters**

Require 1920×1080, 24 fps, exact authored frame count, and no missing frames for all 18 clips.

### Task 5: Build dialogue, SFX, ambience, and music stems

**Files:**
- Create: `天工枪局：白桥第一枪/AI生产/样片01/剪辑/audio/dialogue.wav`
- Create: `天工枪局：白桥第一枪/AI生产/样片01/剪辑/audio/sfx.wav`
- Create: `天工枪局：白桥第一枪/AI生产/样片01/剪辑/audio/ambience.wav`
- Create: `天工枪局：白桥第一枪/AI生产/样片01/剪辑/audio/music.wav`
- Create: `天工枪局：白桥第一枪/AI生产/样片01/剪辑/audio-mix-manifest.json`

**Interfaces:**
- Consumes: locked local-H3 dialogue and selected H3 ambience/SFX regions.
- Produces: four synchronized 68.5-second stereo stems.

- [ ] **Step 1: Place locked dialogue**

Use exact shot timing and `dialogue-lock.json`. `ZHOU_YE_INNER` stays off-screen and uses Zhou Ye's same reference timbre. Duck ambience and music under every line; never retain an H3 take that adds, drops or paraphrases dialogue.

- [ ] **Step 2: Curate physical sound**

Retain usable H3 footsteps, gunfire, room tone, bell, metal slide, paper, and equipment sounds only when synchronized and artifact-free. Replace failed cues with project-owned/generated effects.

- [ ] **Step 3: Create restrained non-diegetic music**

Use sparse low strings/electronic pulse for the Major, near-silence at the transition, restrained industrial-acoustic texture at White Bridge, and no heroic swell.

### Task 6: Composite UI, subtitles, and final edit

**Files:**
- Create: `天工枪局：白桥第一枪/AI生产/样片01/剪辑/subtitles.ass`
- Create: `天工枪局：白桥第一枪/AI生产/样片01/剪辑/edit-list.json`
- Create: `天工枪局：白桥第一枪/AI生产/样片01/交付/第01章_70秒完整声音样片_1080p.mp4`
- Create: `天工枪局：白桥第一枪/AI生产/样片01/交付/delivery-report.md`

**Interfaces:**
- Consumes: 18 upscaled clips, four audio stems, and every `POST_TEXT` field.
- Produces: the user-visible sample.

- [ ] **Step 1: Assemble in authored order**

Use the 18 shot IDs, authored durations, and `EDIT_OUT` transitions. Composite exact scores, HUD, names, and registration writing only in their reserved safe areas.

- [ ] **Step 2: Burn styled Simplified Chinese subtitles**

Use bottom-safe subtitles with speaker-aware timing; do not subtitle non-verbal SFX. The inner voice is visually distinguished without adding an on-screen speaking mouth.

- [ ] **Step 3: Encode the delivery master**

Encode H.264 High profile, 1920×1080, constant 24 fps, yuv420p, stereo AAC 48 kHz, faststart.

- [ ] **Step 4: Verify delivery**

```bash
out='天工枪局：白桥第一枪/AI生产/样片01/交付/第01章_70秒完整声音样片_1080p.mp4'
test -s "$out"
ffprobe -v error -show_entries format=duration -show_entries stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels -of json "$out"
```

Expected: duration 68.5 seconds within one video frame, H.264 1920×1080 at 24 fps, and AAC stereo 48 kHz.

- [ ] **Step 5: Commit manifests and delivery metadata**

```bash
git add -- '天工枪局：白桥第一枪/AI生产/样片01'
git commit -m 'assets: deliver chapter 1 complete-sound sample'
```
