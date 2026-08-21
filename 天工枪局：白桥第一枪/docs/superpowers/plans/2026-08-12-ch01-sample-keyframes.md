# Chapter 1 Sample Keyframes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce one approved GPT Image keyframe for each of the 18 sample shots, with stable character identity and ComfyUI-qualified 864×480 H3 inputs.

**Architecture:** GPT Image creates the Zhou Ye identity master and 18 cinematic semi-realistic Chinese-animation masters at 16:9. Existing approved female identity masters are reused as references. kk9850 ComfyUI is a repair and normalization stage, not the creative source: it corrects hands, firearm geometry, reference consistency, and creates exact H3 input canvases while preserving approved composition.

**Tech Stack:** GPT Image 2 host-native generation, kk9850 ComfyUI, ImageMagick/ffmpeg inspection, perceptual and SHA-256 manifests.

## Global Constraints

- Follow the `gpt-image`/`imagegen` workflow and this repository's visual prompt source for every generation or edit.
- Style is original cinematic semi-realistic Chinese animation, never live action, chibi, palace glamour, or named-studio imitation.
- All masters are 16:9 without readable text. Exact score, names, HUD, and paper writing remain empty safe areas for post.
- Zhou Ye is the same 24-year-old Chinese man in every layer; modern scenes retain the dark team jersey and right wrist brace.
- Su He, Jiang Ning, Tang Xia, and Xu An retain their separate face, hair, body and role anchors, but their old 2D boards must be upgraded to the approved Zhou Ye master's cinematic 3D material level before group-shot production.
- Firearms use modern receiver, gas system, magazine, stock, sight, ejection port, and correct grip.
- The approved high-resolution master is never overwritten; ComfyUI writes versioned repairs and H3 inputs separately.
- ComfyUI generation and H3 generation never overlap on kk9850.

---

### Task 1: Create the production manifest and folders

**Files:**
- Create: `天工枪局：白桥第一枪/AI生产/样片01/视觉/keyframe-manifest.json`
- Create: `天工枪局：白桥第一枪/AI生产/样片01/视觉/README.md`

**Interfaces:**
- Consumes: the 18 IDs and prompts in `分镜/第01章_70秒样片关键帧与视频运动提示词.md`.
- Produces: one state record per shot with `raw`, `repaired`, `approved`, and `h3_input` paths.

- [ ] **Step 1: Seed exactly 18 records**

Each record contains `shot_id`, `duration`, `mode`, `prompt_sha256`, `reference_ids`, `raw_path`, `repaired_path`, `approved_path`, `h3_input_path`, `qa`, and `status`. Initial paths are null and status is `planned`.

- [ ] **Step 2: Validate ID parity**

```bash
prompts='天工枪局：白桥第一枪/分镜/第01章_70秒样片关键帧与视频运动提示词.md'
manifest='天工枪局：白桥第一枪/AI生产/样片01/视觉/keyframe-manifest.json'
diff <(rg '^SHOT_ID:' "$prompts" | sed 's/^SHOT_ID: //' | sort) <(jq -r '.shots[].shot_id' "$manifest" | sort)
```

Expected: no output.

### Task 2: Generate and approve the Zhou Ye identity master

**Files:**
- Create: `天工枪局：白桥第一枪/视觉资产/人物外观母版/00_周野_外观母版.png`
- Create: `天工枪局：白桥第一枪/AI生产/样片01/视觉/identity-review.md`

**Interfaces:**
- Consumes: Zhou Ye's dossier and the formal identity prompt in the visual skill.
- Produces: the reference used by every Zhou Ye keyframe.

- [ ] **Step 1: Generate one identity board with GPT Image**

Generate a neutral full-body front view plus head/hand detail in one portrait board: 24-year-old Chinese man, lean strength, slightly forward training posture, short black hair, lucid tired eyes, mouse-hand calluses, dark fictional pro jersey, black right wrist brace, empty hands, neutral background, no logos or weapons.

- [ ] **Step 2: Inspect at original resolution**

Reject female proportions, celebrity likeness, extra fingers, asymmetric brace placement, readable fake branding, or weapons. Record face, hair, body, jersey, wrist, and hand verdicts.

### Task 3: Upgrade and audit the four existing White Bridge masters

**Files:**
- Modify: `天工枪局：白桥第一枪/AI生产/样片01/视觉/identity-review.md`

**Interfaces:**
- Consumes: `视觉资产/人物外观母版/01_苏禾_外观母版.png` through `04_许安_外观母版.png`.
- Produces: four cinematic 3D identity masters, approved reference IDs and role-specific invariants.

- [ ] **Step 1: Preserve identity anchors and upgrade rendering**

Use each old image only as an identity anchor. Rebuild in the same 16:9 layout as Zhou Ye: giant face close-up on the left and full-body front/profile/back views on the right, white studio background, empty hands, no text. Check face separation, height/build separation, hairstyle, work clothing, hand visibility, and absence of weapon/identity corruption.

- [ ] **Step 2: Record reference hashes**

```bash
shasum -a 256 '天工枪局：白桥第一枪/视觉资产/人物外观母版/'*.png
```

Expected: one stable checksum per identity source.

### Task 4: Generate 18 raw keyframes with GPT Image

**Files:**
- Create: `天工枪局：白桥第一枪/AI生产/样片01/视觉/keyframes/raw/<SHOT_ID>_v001.png`
- Modify: `天工枪局：白桥第一枪/AI生产/样片01/视觉/keyframe-manifest.json`

**Interfaces:**
- Consumes: each `KEYFRAME_PROMPT`, `KEYFRAME_NEGATIVE`, and applicable identity masters.
- Produces: one raw 16:9 image per stable shot ID.

- [ ] **Step 1: Generate serially by scene**

Use GPT Image at landscape high quality. Supply only the identity references visible in that shot. S03_SH02 is its L2VA final frame; every other frame is its I2VA first frame.

- [ ] **Step 2: Verify each raw image before continuing**

Check `1920×1080` target framing or larger 16:9 master, no readable text, exact character count/sex/position, right wrist brace, medal continuity, correct reality layer, correct near-point/right-corridor axis, and correct static moment.

### Task 5: Repair and normalize through kk9850 ComfyUI

**Files:**
- Create: `天工枪局：白桥第一枪/AI生产/样片01/视觉/keyframes/repaired/<SHOT_ID>_vNNN.png`
- Create: `天工枪局：白桥第一枪/AI生产/样片01/视觉/keyframes/h3-input/<SHOT_ID>.png`
- Modify: `天工枪局：白桥第一枪/AI生产/样片01/视觉/keyframe-manifest.json`

**Interfaces:**
- Consumes: only raw frames that failed a named QA axis.
- Produces: approved master and exact 864×480 H3 input per shot.

- [ ] **Step 1: Preflight the shared GPU**

Require ComfyUI queue `running=0`, `pending=0`, and no H3 global lock. Run only one repair workflow at a time.

- [ ] **Step 2: Apply surgical repairs**

Use reference-aware Qwen Image Edit or a local equivalent for hands, faces, gun parts, or prop placement. State the invariant: change only the failed region and preserve identity, camera, lighting, geometry, and safe areas.

- [ ] **Step 3: Produce deterministic H3 inputs**

Resize/crop approved masters to exact `864×480` without changing aspect ratio, write a separate file, and record its SHA-256.

### Task 6: Final visual QA and commit

**Files:**
- Create: `天工枪局：白桥第一枪/AI生产/样片01/视觉/keyframe-qa.md`

**Interfaces:**
- Consumes: all 18 approved masters and H3 inputs.
- Produces: an approved set for the video plan.

- [ ] **Step 1: Validate counts and dimensions**

```bash
test "$(find '天工枪局：白桥第一枪/AI生产/样片01/视觉/keyframes/h3-input' -type f -name '*.png' | wc -l | tr -d ' ')" -eq 18
for f in '天工枪局：白桥第一枪/AI生产/样片01/视觉/keyframes/h3-input/'*.png; do identify -format '%wx%h\n' "$f"; done | sort -u | test "$(cat)" = '864x480'
jq -e '[.shots[] | select(.status == "approved")] | length == 18' '天工枪局：白桥第一枪/AI生产/样片01/视觉/keyframe-manifest.json'
```

Expected: 18 files, only `864x480`, and 18 approved manifest records.

- [ ] **Step 2: Commit assets and provenance**

```bash
git add -- '天工枪局：白桥第一枪/视觉资产/人物外观母版/00_周野_外观母版.png' '天工枪局：白桥第一枪/AI生产/样片01/视觉'
git commit -m 'assets: add chapter 1 sample keyframes'
```
