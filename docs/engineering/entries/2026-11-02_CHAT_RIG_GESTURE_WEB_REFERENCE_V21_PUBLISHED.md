# §C ⇄ §E rigging/animation teaching v2.1 — deployed-source receipt

**Date:** 2026-11-02  
**Component:** §wyrlz Chat (700M/Qwen contextual lessons and pre-existing online-research route)  
**State:** PUBLISHED TO EXISTING HUGGING FACE SPACE · `DEPLOYED_UNVERIFIED` · LIVE STUDENT/DEVICE TEST DEFERRED

## Published scope

- Scope-limited `hf_space/forge_modeling_lessons.py` now teaches §E v11.220's real 17-bone weighted hand rig, source-anchored differences between neutral geometry/weights/poses/animation, keyframe constraints and JSON versus OBJ export. §E v11.221 adds thumb CMC opposition and 14 native hand gestures (not 14 separate Chat commands).
- `hf_space/online_tools.py` routes explicit rigging/animation documentation requests to the **existing** bounded online-research service; neither 700M nor Qwen gains unrestricted network access. The research evidence remains untrusted external text; names/URLs must come from actual retrieved sources, never be invented.
- Both student inference routes already consume compact modeling lesson text and bounded retrieved `onlineContext`, with source authority separate from editing authority. No Chat-native `rig.pose`, `bone.rotate`, `rig.keyframe.add`, Quest hand sensor capture, direct sculpt, UV authoring or unrestricted editor code execution is added.
- Academy teaching materials remain in `training/forge-modeling/`: original M001–M036, 31 rig/animation cases M037–M067, gesture continuation M068–M079, source-anchor validator and research guide. The later [WebXR W3C draft reference](https://www.w3.org/TR/2026/WD-webxr-hand-input-1-20261029/) is research-only and expressly does not claim a tracked-hand retargeter exists.

## Source, CI, and provider receipts

- Accepted Chat predecessor: `a133e3a821a83fccc42a71cd0bef5b639da28946`.
- Approved incremental Chat source: `e0c0ca756edb3c6db2cd345c2099509816e53dda` ([PR #339](https://github.com/kaministrator999-ui/Swrlzkamico/pull/339)). Verified it contains all preceding source changes; its file tree matches tested PR head `e6561fd5770bd3f9e049f88a796e72fe7784ccbe` without an untested delta.
- [Candidate offline validation run #41506771211](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41506771211): SUCCESS. Earlier [run #41505872672](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41505872672) showed six v1 and eleven v2 lesson tests PASS (including v11.221 and source-search guards). Automated tests prove source/routing shape, not generative competence.
- Dedicated main deployment request commit: `8924beeba8c5bfe2e1caa1d976c333a330ec14fd`, request nonce `chat-forge-rig-gesture-webref-v21-e0c0ca75-20261102-release-1`, target `kamiloki/Swyrlz`.
- [Guarded HF deploy run #41509663778](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41509663778): **SUCCESS**. Workflow verified checkout source SHA, rebuilt/smoke-tested the existing model package, captured a provider rollback snapshot, uploaded the release and wrote a deployed checkpoint.
- **New HF provider revision:** `bb8cd0a54e9944a487be0f7a588bbf8b9d59448c`.
- **Previous HF revision (rollback):** `3843e804ebaab38de66caeb0475db1bfef357c39`.
- The provider release checkpoint explicitly says `verificationState: DEPLOYED_UNVERIFIED` and `knownGood: false`. This is a successful publication, **not proof of a currently running service or a human-approved behavior result**.

## Preserved independent acceptance gates

1. Later, use real 700M/Qwen turns (and actual retrieved URLs) to evaluate rigging, source comparisons, output intent and failure attribution without leaking public practice cases into a held-out score.
2. Independently evaluate native §E editor action outcomes via authenticated owner-approved host receipts, saved model geometry and scoped undo/redo; no model-generated prose is an edit receipt.
3. Owner Moto G Power / Quest 2 visual and ergonomics testing remains separate. Hand retargeting from the WebXR sensor's joints to the 17-bone authored glove is an unimplemented/unevaluated future capability.
4. No gradient/LoRA training, weight changes, new native operations or changes to §E deployment were part of this Chat release.
