# §C × §E WebXR modeling and animation teaching · v3 publication receipt

**Date:** 2026-11-02  
**Scope:** Chat contextual modeling instruction; not §E Engine/runtime mutation or trained weights.  
**State:** PUBLISHED TO EXISTING HF SPACE; REAL MODELING BEHAVIOR AND DEVICE ACCEPTANCE UNVERIFIED.

## Sources and exact publication

- Canonical curriculum: 100 open-book, teacher-authored §E modeling practice cases M001–M100 in `training/forge-modeling` on `main`. A separate [25→17 WebXR anatomical retargeting reference](../../../training/forge-modeling/HAND_RETARGETING_REFERENCE_V3.md) was merged via [PR #343](https://github.com/kaministrator999-ui/Swrlzkamico/pull/343).
- Current instructional engine sources: §E v11.220 skeletal hand rig, v11.221 14 gestures and thumb opposition, v11.223 eight-key 2.20-second wrist-wave and stronger fist. Subsequent §E versions have independent patch lineage and do not automatically imply changes to this Chat source.
- Official external reference: [W3C WebXR Hand Input Module Level 1 Working Draft of 2026-10-29](https://www.w3.org/TR/2026/WD-webxr-hand-input-1-20261029/), defines `XRHand.size=25`. §E's rig defines 17 target bones; proposed mapping is explicitly a not-yet-implemented engineering reference.
- Source candidate PR [#345](https://github.com/kaministrator999-ui/Swrlzkamico/pull/345); tested head SHA `01364416cd4f373006e6beeff24ff9c822b5a17c`; accepted Chat merge SHA `de4f12b72c8cfeef652524918612a5f17f4c8a40`. GitHub comparison found zero content differences between tested head and accepted merge.
- Offline test receipt: [HF Candidate Offline Validation #41518182891](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41518182891), **SUCCESS**. Syntax and existing Chat candidate checks succeeded, including **all 7 added v3 focused tests**. These are source/routing checks, not actual inference accuracy or headset acceptance.
- Immutable deployment request: `main:.deploy/HF_SPACE_REQUEST.txt` committed as `dddfe5698d8d5fbdddc9f019958d9924b15f985e`, target `kamiloki/Swyrlz`, source `de4f12b72c8cfeef652524918612a5f17f4c8a40`.
- Guarded [Hugging Face Space Deploy Request #41518630642](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41518630642): **SUCCESS**, verified immutable source and completed model packaging/R39 kernel, profile-budget and identity safety smoke gates, snapshot and upload.
- Provider `kamiloki/Swyrlz` **new revision** `9c54f113cb6ff06bc234496653f9297cdcf48994`.
- **Prior rollback revision** `bb8cd0a54e9944a487be0f7a588bbf8b9d59448c`.
- Provider checkpoint intentionally: `verificationState=DEPLOYED_UNVERIFIED`, `knownGood=false`.

## Changes: bounded educational context, no new edit tools

- In `hf_space/forge_modeling_lessons.py`, add a §E-only WebXR/retargeting topic. Teach that tracked source joint spaces are distinct from local target bones, need handedness, valid session, parent-local calibration and handling of occlusion. No actual `XRInputSource.hand` access or sensor capture is added.
- Correct §E animation lesson: v11.223 Wave uses **8 keys over 2.20 seconds**; ordinary gestures use **3 keys over 1.5 seconds**. New stronger fist uses differentiated MCP/PIP/DIP and thumb motion. The selector remains bounded and irrelevant turns receive no lesson.
- Retain existing `online_tools.py` canonical bounded web retrieval, existing `onlineContext` delivery and source-trust rule. Web retrieval is reference evidence, never tool instruction or host authority.
- Retain exact §C native editor typed-operations/approval/lease/receipt constraints, existing account model and no new permissions. No `rig.rotate`, `rig.keyframe`, VR mocap, sculpt vertex or unchecked JS tool was added.

## Deferred owner-controlled acceptance

The owner expressly requested continued teaching now and hands-on evaluation **later**. This release does **not** assert that 700M/Qwen answers are correct in a live conversational test, that the HF Space has been visually accepted on the Moto phone or Quest, that any Chat-proposed rig edit executes in §E, or that model weights received LoRA/gradient updates.

When authorized later, run a short scripted conversation and real-device pass over (1) ask-vs-act, (2) W3C 25-source/§E 17-target distinction, (3) v11.223 Wave/Fist facts, (4) official web source citation, (5) unsupported bone edit abstention, and (6) actual host-approved primitive changes/receipts. Record raw failures for correction; never promote public practice cases to held-out proof.
