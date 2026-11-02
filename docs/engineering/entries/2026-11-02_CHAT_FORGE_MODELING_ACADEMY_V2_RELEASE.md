# §C × §E Model Atelier Academy v2 — source and guarded Chat publication

**Event:** 2026-11-02 · §C contextual instruction upgrade to §E v11.220 hand rig/animation semantics.
**Truth state:** SOURCE_VERIFIED + CHAT_SPACE_UPLOADED, **DEPLOYED_UNVERIFIED** for real conversation, §E host edits and Quest/Android acceptance.

## Learning changes
- Academy's original 36 public teacher-authored cases were expanded with 31 source-anchored v2 cases M037–M067 (67 total public open-book cases) through PR [#334](https://github.com/kaministrator999-ui/Swrlzkamico/pull/334). All 31 new anchors matched their actual source. The v11.220 hand source adds 17 hierarchical bones, four-influence SkinnedMesh skinning, Rig · Pose · Animate controls and saved keyframes for new hand starters, not existing saved copies. This source upgrade makes the v11.217 'no rig' baseline historically limited.
- §C's current 700M, Qwen and native Brain planner already import `forge_modeling_lessons.select_modeling_lesson`. PR [#335](https://github.com/kaministrator999-ui/Swrlzkamico/pull/335) updated only that shared selector and its regression tests. The 1150-character budget and irrelevant-query zero-context gate remain; distinct v11.220 rig versus timeline lessons clarify actual editor UI and missing Chat-native operations.
- The Chat typed allowlist, original snapshot ID validation, approval, host receipts, project history, §E engine files, and both models' weights were unchanged. §E can rig/pose through its own UI; §C Chat still does not expose a typed bone/keyframe operation or verified Quest sensor retargeting.

## Source checks
- Verified source candidate HEAD `c02fc9c45c0e29471b5805d218e7d8676d139a50`; PR merge result `a133e3a821a83fccc42a71cd0bef5b639da28946` had **zero changed files** relative to tested HEAD.
- HF Candidate Offline Validation [#41497943812](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41497943812) **SUCCESS**. Actual GitHub Actions logs show all **10/10** `ForgeModelingLessonTests` passed, including four new rig/pose/permission constraints. Existing native editor and Chat guards passed. These are deterministic source checks, not real model evaluation.

## Guarded Chat-only release
- `main:.deploy/HF_SPACE_REQUEST.txt` request commit `1ff666ca8320f9ee2c1564b483c20c63dcb94168` pinned `SOURCE_REF=a133e3a821a83fccc42a71cd0bef5b639da28946` with `TARGET=kamiloki/Swyrlz`.
- Guarded Hugging Face deploy [#41498642772](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41498642772) **SUCCESS**, with selected source SHA, validated package, native R39 reconstruction, 700M budget, identity/fast-inference gates, rollback snapshot and upload receipt.
- Resulting provider Space revision: `3843e804ebaab38de66caeb0475db1bfef357c39`.
- Rollback Space revision: `9232b4510b67c13cf7f5c8b0a3fcfa13a8aceda5`.
- Release checkpoint: `knownGood: false`, `verificationState: DEPLOYED_UNVERIFIED`. Successful upload is not proof of running model answers, joined user/host edits or physical acceptance.

## Version owners
This governed Chat+LALM+Server publication advances canonical Repository Work, LALM Engine and Server Runtime relative to immediately preceding v1 release (1.0.259 / 2.1.206 / 2.3.450). Web Chat UI, weight checkpoint and independent §E engine versions stay unchanged. The canonical `runtime:versions/` files and the Roadmap event must be kept synchronized.

## Acceptance intentionally deferred
Kami explicitly requested continued teaching and a later test. Do not run or claim live student/modeler/Quest acceptance in this tier. Later compare real 700M vs Qwen responses to held-out cases (separate from public 67), then test approved real native mesh changes and rig UI behavior with visible receipts. Preserve failures as correction candidates; do not promote public teacher cases to independently validated LoRA data or imply any weight update.
