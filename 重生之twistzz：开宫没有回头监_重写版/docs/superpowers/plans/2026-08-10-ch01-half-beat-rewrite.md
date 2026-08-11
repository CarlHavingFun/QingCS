# Chapter 1 Half-Beat Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Chapter 1 with a fully rewritten “差半拍” opening and a matching ten-shot MiniMax H3 storyboard while preserving the Chapter 2 handoff and all locked long-term plot constraints.

**Architecture:** Treat the Chapter 1 design document as the canonical narrative contract. The prose, storyboard, chapter outline, directory examples, production registry, and SHA snapshot are updated as one atomic content package; validation scripts compare the same canonical facts across every changed file.

**Tech Stack:** Markdown, GitHub contents API, shell/Python text validation, SHA-256.

## Global Constraints

- Work only on branch `agent/ch01-half-beat-rewrite`; never write directly to `main`.
- Public prose uses Chinese aliases and original nation/team names only; no real player IDs, real teams, or real-person likenesses.
- Chapter 1 uses first-person narration and keeps the modern protagonist male until physical and documentary evidence confirms the parallel adult female identity.
- Canonical match facts are `《荒漠迷城》`, `16:18 → 16:19`, series `1:2`, runner-up, and `4v3 → 3v3 → 3v2 → 2v1` with a defuse kit.
- Chapter 1 contains no emperor, no Tian-gong explanation, no system task, no automatic permission/starting-slot grant, and no unearned nicknames.
- Chapter 2 must continue unchanged from `六点四十，午门值守收走我的到场卡，只换给我一张训练牌。`
- Storyboard remains ten shots at 15 seconds per shot and must match the prose exactly.

---

### Task 1: Commit the approved narrative design

**Files:**
- Create: `重生之twistzz：开宫没有回头监_重写版/docs/superpowers/specs/2026-08-10-ch01-half-beat-rewrite-design.md`
- Create: `重生之twistzz：开宫没有回头监_重写版/docs/superpowers/plans/2026-08-10-ch01-half-beat-rewrite.md`

**Interfaces:**
- Consumes: approved A-route design from the user.
- Produces: the canonical constraints used by all later tasks.

- [ ] **Step 1:** Create the design document with the exact title, match facts, crossing sequence, character boundaries, ten-shot structure, and acceptance criteria.
- [ ] **Step 2:** Create this implementation plan beside the design document.
- [ ] **Step 3:** Scan both files for `TBD`, `TODO`, contradictions, and references to a different map/score.
- [ ] **Step 4:** Commit both files with message `docs: lock chapter 1 half-beat rewrite`.

### Task 2: Replace the Chapter 1 prose and title

**Files:**
- Create: `重生之twistzz：开宫没有回头监_重写版/正文/第01章_差半拍.md`
- Delete: `重生之twistzz：开宫没有回头监_重写版/正文/第01章_第一枪先响.md`

**Interfaces:**
- Consumes: design document canonical facts.
- Produces: the only Chapter 1 prose source for the storyboard and metadata.

- [ ] **Step 1:** Write the complete first-person chapter with six movements: last half-beat, runner-up aftermath, three-stage replay anomaly, shot-triggered crossing, unfamiliar body/familiar voices, national-team roster hook.
- [ ] **Step 2:** Ensure the chapter ends with the temporary card `明早六点四十｜午门换训练牌` and only signs the attendance row.
- [ ] **Step 3:** Run text checks for the canonical map, scores, series result, roster fields, and banned concepts.
- [ ] **Step 4:** Create the new file and delete the old file in the same branch.
- [ ] **Step 5:** Commit with message `rewrite: replace chapter 1 with 差半拍`.

### Task 3: Replace the ten-shot storyboard

**Files:**
- Modify: `重生之twistzz：开宫没有回头监_重写版/分镜/第01章_十格分镜.md`

**Interfaces:**
- Consumes: new Chapter 1 prose.
- Produces: ten 15-second visual units and MiniMax H3 T2VA prompts that do not invent extra events.

- [ ] **Step 1:** Write ten shots matching the design sequence and exact prose facts.
- [ ] **Step 2:** For every shot include time range, location/framing, action, camera, dialogue/sound, CS continuity, relationship function, spatial anchors, English integrated prompt, soundscape, and music.
- [ ] **Step 3:** Verify character IDs remain stable from modern male consciousness through the parallel adult female body.
- [ ] **Step 4:** Verify every shot has one core action and no new round, fake system UI, real-person likeness, or sexualized body framing.
- [ ] **Step 5:** Commit with message `rewrite: sync chapter 1 storyboard to 差半拍`.

### Task 4: Synchronize chapter indexes and production state

**Files:**
- Modify: `重生之twistzz：开宫没有回头监_重写版/04_新版44章总纲.md`
- Modify: `重生之twistzz：开宫没有回头监_重写版/正文/目录说明.md`
- Modify: `重生之twistzz：开宫没有回头监_重写版/00_重写版状态.md`
- Modify: `重生之twistzz：开宫没有回头监_重写版/审核/正文分镜生产登记.md`
- Modify: `重生之twistzz：开宫没有回头监_重写版/审核/2026-08-09-current-sha256.txt`

**Interfaces:**
- Consumes: final prose and storyboard bytes.
- Produces: one consistent title, status, and hash record.

- [ ] **Step 1:** Update the Ch1 canonical source section in the 44-chapter outline to the half-beat anomaly and shot-triggered crossing.
- [ ] **Step 2:** Replace directory examples and title references from `第一枪先响` to `差半拍`.
- [ ] **Step 3:** Mark Chapter 1 prose/storyboard as newly rewritten and synchronized, pending independent review; remove stale blind-review and 36/36 claims for the replaced files.
- [ ] **Step 4:** Compute SHA-256 for `正文/第01章_差半拍.md` and the new storyboard; remove the old path hash and insert the new path hash while preserving 88 chapter/storyboard rows.
- [ ] **Step 5:** Commit with message `docs: sync chapter 1 rewrite metadata`.

### Task 5: Run cross-file validation

**Files:**
- Validate all files changed in Tasks 1—4.

**Interfaces:**
- Consumes: complete branch diff.
- Produces: verification evidence for the draft PR.

- [ ] **Step 1:** Confirm exactly one `正文/第01章_*.md` file remains.
- [ ] **Step 2:** Confirm prose and storyboard both contain `荒漠迷城`, `16:18`, `16:19`, `1:2`, `亚军`, `大清战队`, `凤仪五席`, `二号位首发`, `六点四十`, and `午门`.
- [ ] **Step 3:** Confirm no prose/storyboard occurrence of `核爆小镇`, `系统任务`, `自动首发`, `好感度`, `皇帝`, or unearned nicknames. `7:5` may appear only as an explicitly impossible anomaly, never as the actual match result.
- [ ] **Step 4:** Confirm the storyboard has exactly ten `## 第N格` headings and every range is 15 seconds.
- [ ] **Step 5:** Compare the branch to `main` and inspect every changed path for unrelated modifications.

### Task 6: Publish a draft pull request

**Files:**
- No additional content files.

**Interfaces:**
- Consumes: verified branch.
- Produces: a reviewable GitHub draft PR targeting `main`.

- [ ] **Step 1:** Open a draft PR titled `rewrite: 第一章《差半拍》与十格分镜完全重构`.
- [ ] **Step 2:** Document what changed, why the previous opening felt procedural, the exact continuity checks, and the remaining independent literary/video review work.
- [ ] **Step 3:** Fetch the PR diff and verify the changed-file set and title one final time.
