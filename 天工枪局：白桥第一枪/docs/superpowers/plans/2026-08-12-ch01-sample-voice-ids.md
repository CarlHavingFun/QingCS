# Chapter 1 Sample Voice IDs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create stable original local-H3 reference voices, preview audio, synthesis presets, and a production registry for every speaking sample role.

**Architecture:** The locally deployed MiniMax H3 Ref2VA/FL2VA stack on `kk9850` is both timbre source and dialogue renderer. A 32×32 audio-only H3 pass creates an original reference seed from locked script dialogue; subsequent Ref2VA shots cite that seed as the character's stable local Voice ID. No MiniMax cloud API or API key is used. Zhou Ye's inner voice reuses `ZHOU_YE_V002` with a restrained inner-delivery instruction instead of creating a second identity.

**Tech Stack:** local MiniMax H3 in ComfyUI, FLAC/WAV, JSON manifests, Whisper ASR, `ffprobe`, SHA-256.

## Global Constraints

- No cloud API and no paid MiniMax call.
- Create original local reference identities as each speaking role enters production; current approved candidates are `ZHOU_YE_V002`, `ZHAO_YU_V001`, and `CHEN_MO_V001`.
- `ZHOU_YE_INNER` must map to `ZHOU_YE_V002`; it is not a separate timbre.
- Reference seeds use exact dialogue from `声音/dialogue-lock.json`; no invented audition sentence, padding, paraphrase, or explanatory narration is allowed.
- Every seed and shot output receives Whisper ASR plus human-listen status before final approval.
- Do not imitate a living actor, streamer, or professional player's recognizable voice.
- H3 calls are serial under `/mnt/e/ComfyUI/gobro_jobs/.h3-active.lock`.

---

### Task 1: Create the voice design contract

**Files:**
- Create: `天工枪局：白桥第一枪/AI生产/样片01/声音/voice-design-spec.json`
- Create: `天工枪局：白桥第一枪/AI生产/样片01/声音/voice-registry.json`
- Create: `天工枪局：白桥第一枪/AI生产/样片01/声音/README.md`

**Interfaces:**
- Consumes: character dossiers and dialogue in `分镜/第01章_70秒样片逐镜头分镜.md`.
- Produces: seven design requests and a registry schema consumed by Tasks 2–4.

- [ ] **Step 1: Write exact design entries**

Use these identity targets and preview lines:

```text
ZHOU_YE: 24-year-old Chinese man; low-mid register; clear but tired; restrained, observant, precise; no radio-announcer resonance. Preview: 我听见第二个脚步了，没及时报。明早重走这一波。
SU_HE: Chinese woman in her early thirties; stable mid-low register; concise operator; warm authority without aristocratic polish. Preview: 曜京南城，白桥枪馆。先试训，七日客籍再谈。
JIANG_NING: Chinese woman in her late twenties; cool narrow tone; quiet and technical; short clean consonants. Preview: 右廊瞄具偏半格，我先校准，再给你看记录。
TANG_XIA: Chinese woman in her late twenties; broad energetic tone; direct workshop cadence; low center of gravity, no childish brightness. Preview: 给不给闪？别犹豫，横梁会吃掉投掷线。
XU_AN: Chinese woman in her late twenties; soft low-volume alto; meticulous and calm; ledger-reader pace. Preview: 账我记着，条件不合适就划掉，记录不会少一行。
ZHAO_YU: Chinese male young professional teammate; fast compact tactical radio speech; crisp numbers, no bravado. Preview: A1 两个。包边先别动，第二个脚步还没到。
CHEN_MO: Chinese male team captain around thirty; controlled mid-low voice; neutral authority; debrief rather than accusation. Preview: 不找替罪羊，只把当时听见的、看见的说清楚。
```

- [ ] **Step 2: Define registry fields**

Each role object must contain `character_id`, `voice_id`, `design_prompt`, `preview_text`, `model`, `speed`, `vol`, `pitch`, `emotion`, `preview_path`, `activation_path`, `sha256`, `status`, and `created_at`. Initial `voice_id`, paths, checksum, and date are JSON `null`; initial status is `specified`.

- [ ] **Step 3: Validate the contract**

Run:

```bash
jq -e '.voices | length == 7' '天工枪局：白桥第一枪/AI生产/样片01/声音/voice-design-spec.json'
jq -e '[.voices[].character_id] | sort == ["CHEN_MO","JIANG_NING","SU_HE","TANG_XIA","XU_AN","ZHAO_YU","ZHOU_YE"]' '天工枪局：白桥第一枪/AI生产/样片01/声音/voice-design-spec.json'
rg '现实演员|真人声纹|模仿.*(演员|主播|选手)' '天工枪局：白桥第一枪/AI生产/样片01/声音/voice-design-spec.json' && exit 1 || true
```

Expected: both `jq` commands return true; the final scan has no output.

### Task 2: Pass the credential and account gate

**Files:**
- Modify: `天工枪局：白桥第一枪/AI生产/样片01/声音/README.md`

**Interfaces:**
- Consumes: a user-controlled `MINIMAX_API_KEY` environment variable.
- Produces: a verified API connection without persisting the credential.

- [ ] **Step 1: Check the variable without revealing it**

Run:

```bash
test -n "${MINIMAX_API_KEY:-}" && echo MINIMAX_API_KEY_PRESENT
```

Expected: exactly `MINIMAX_API_KEY_PRESENT`. If absent, stop only paid voice calls and request that the user sign in to MiniMax and set the variable locally; continue the independent image plan.

- [ ] **Step 2: Perform a non-secret API preflight**

Call the official Get Voice endpoint with the Bearer variable, discard response bodies containing account data, and record only HTTP status plus `base_resp.status_code`. Expected: HTTP 200 and status code 0.

### Task 3: Design and approve seven voice identities

**Files:**
- Create: `天工枪局：白桥第一枪/AI生产/样片01/声音/previews/<CHARACTER_ID>.mp3`
- Modify: `天工枪局：白桥第一枪/AI生产/样片01/声音/voice-registry.json`
- Create: `天工枪局：白桥第一枪/AI生产/样片01/声音/voice-review.md`

**Interfaces:**
- Consumes: Task 1 design requests and Task 2 credential gate.
- Produces: seven Voice IDs and audible previews.

- [ ] **Step 1: Submit one Voice Design request**

POST `prompt` and `preview_text` to `https://api.minimax.io/v1/voice_design`; never include the token in logs. Decode `trial_audio` from hex to the named preview path and capture the returned `voice_id` in the registry.

- [ ] **Step 2: Verify the preview artifact**

Run for each role:

```bash
test -s '天工枪局：白桥第一枪/AI生产/样片01/声音/previews/<CHARACTER_ID>.mp3'
ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 '天工枪局：白桥第一枪/AI生产/样片01/声音/previews/<CHARACTER_ID>.mp3'
```

Expected: non-empty audio and positive duration. Record naturalness, identity fit, Mandarin clarity, and pairwise distinctness in `voice-review.md`.

- [ ] **Step 3: Accept or replace before moving on**

Accept only if all four review axes pass. If rejected, delete only that generated voice through the official Delete Voice endpoint with `voice_type=voice_generation`, retain its rejection note, and make one new serial attempt.

### Task 4: Activate IDs and render sample dialogue masters

**Files:**
- Create: `天工枪局：白桥第一枪/AI生产/样片01/声音/dialogue/<SHOT_ID>_<CHARACTER_ID>.wav`
- Modify: `天工枪局：白桥第一枪/AI生产/样片01/声音/voice-registry.json`
- Create: `天工枪局：白桥第一枪/AI生产/样片01/声音/dialogue-manifest.json`

**Interfaces:**
- Consumes: approved Voice IDs and exact dialogue from the shot sheet.
- Produces: final isolated voice clips used by the edit plan.

- [ ] **Step 1: Render one activation line per ID**

Use `speech-2.8-hd`, `stream=false`, `language_boost=Chinese`, and mono 44.1 kHz WAV. This both verifies the ID and activates it within the documented seven-day window.

- [ ] **Step 2: Render exact shot dialogue**

Render only verbatim dialogue from the shot sheet. Use the same `ZHOU_YE` ID for `ZHOU_YE_INNER` with the inner preset. Do not synthesize SFX, narration not present in the script, or UI text.

- [ ] **Step 3: Validate registry and audio set**

Run:

```bash
jq -e '[.voices[] | select(.status == "activated")] | length == 7' '天工枪局：白桥第一枪/AI生产/样片01/声音/voice-registry.json'
jq -e '.inner_voice.voice_id == .voices.ZHOU_YE.voice_id' '天工枪局：白桥第一枪/AI生产/样片01/声音/dialogue-manifest.json'
find '天工枪局：白桥第一枪/AI生产/样片01/声音/dialogue' -type f -name '*.wav' -size 0 -print | test -z "$(cat)"
```

Expected: seven activated identities, one Zhou Ye identity shared by inner voice, and no empty WAV files.

- [ ] **Step 4: Commit non-secret production metadata**

```bash
git add -- '天工枪局：白桥第一枪/AI生产/样片01/声音'
git commit -m 'assets: add chapter 1 sample voice identities'
```
