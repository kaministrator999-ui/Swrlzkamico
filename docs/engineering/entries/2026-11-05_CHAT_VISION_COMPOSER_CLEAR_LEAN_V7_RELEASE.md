# 2026-11-05 — §C Pending Image Composer Handoff and Lean Vision v7

**Scope:** existing authenticated §wyrlz Chat on free Hugging Face CPU Basic Space `kamiloki/Swyrlz`. Source branch `fix/chat-embed-mobile-composer-v1-20261103`. No §E editor, microphone, Google login, model weights, payment provider or GPU changes.

## Owner-reported problem and grounded diagnosis

An Android screenshot from the owner showed the pending Little Crystal Mage multi-view reference image and its question in BOTH the active chat progress card and the bottom composer while the real `ANALYZING` stage displayed approximately 2m46 elapsed. Earlier owner tests had returned more quickly, so this observation is evidence of inconsistent current latency, not proof of a single root cause. Source inspection showed the browser encoding up to **1600px** while the server always downscaled to **768px** for local vision. The local SmolVLM image instruction and maximum generation budget had also grown to **192 tokens** in v4 from an initial **112**; effects on actual CPU speed were not benchmarked.

## Implemented changes

- `chat/§wyrlz/index.html`: when the authenticated image-job POST returns HTTP 202 with a valid `jobId`, the **pending** image+question are represented by the existing activity card and the bottom text/thumbnail composer is cleared. This is explicitly NOT a durable Chat send; authoritative Station `/send` still occurs only when vision description completes. Keep attachment object and URL alive for actual message preview and for recovery.
- If vision fails, the user stops watching, or Station does not acknowledge a proposed image-derived Chat turn, restore the previously attached image and draft text into an empty composer (without clobbering newly typed text), report the failure, and remove only our own provisional unsaved user message. Existing pre-accept errors leave the composer intact. On genuine Station acknowledgment, move original image URL into the existing `imagePreviews` map and render the accepted user turn as before.
- The browser converts the image to a bounded JPEG with its longest edge at most **768px**, rather than unnecessarily transferring a 1600px version that the server would shrink again. The full original image remains for the user's browser-side pending/accepted preview; pixels are not saved in account Chat export.
- `hf_space/chat_vision.py`: make visual inventory instructions more concise without dropping the same-image turnaround vs temporal transformation rule. Limit max generated text to **112 tokens** rather than 192. This reduces worst-case local text decoding and may reduce answer detail; no unsupported claim of a measured speedup. SmolVLM-256M Q8_0 + mmproj, model revision, 768px server preprocessing, 2 CPU threads, one-running/one-queued job gating, timers, and v4 image-to-text JSON export remain unchanged.

## Test and publication evidence

- [PR #380](https://github.com/kaministrator999-ui/Swrlzkamico/pull/380) merged into the actual HF-source branch with squash commit `8b189ec88ec2529e5291e760893a35cead26f76e`.
- [HF Candidate Offline Validation #42127310208](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42127310208): **focused Python vision mocked runtime, JS image/composer contracts and inline syntax PASS**. Overall workflow marked **FAIL** due to the four pre-existing unrelated §E modeler lesson assertions. Unchanged old Mobile Lyric Reader Integrity also marked FAIL, separately. Android scroll/live response and Chat widget checks passed. No claim of a fully green repository suite.
- Guarded deployment requested from `main:.deploy/HF_SPACE_REQUEST.txt` commit `a1ce89b12a12dc1e1d4e7f771ad3edfd0a85987c`.
- [Hugging Face Space Deployment #42127480563](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42127480563) **SUCCESS**: exact source staged, isolated package validated, R39 and 700M protected by prepublish gates, prior Space snapshot and immutable rollback checkpoint captured, approved code uploaded to existing Space, release checkpoint captured.
- **Published HF Space revision:** `aacd341852ced9c957374a452943806e9f5b9f49`.
- **Rollback revision:** `8040777723164065b3d45b8099bc3a64e6e6b251`.
- Runtime lineage: Repository Work **1.0.267**, Server Runtime **2.3.458**, Web Chat **1.5.174**. Canonical `chat/§wyrlz/VERSION.txt` UI version contract remains 1.1.22.

## Acceptance boundary

**DEPLOYED_UNVERIFIED**. The GitHub deployment conclusively reports publication and rollback; it does not show a verified post-deploy phone request or actual SmolVLM throughput. Owner should refresh the Chat Space, attach the Little Crystal Mage image, and press Send. After a valid accepted image-job ID, expect the bottom composer to clear while the chat progress card holds the pending image/question and total/current-stage timers continue. On a failed job, expect the composer text+image to be restored and the chat progress card to show a truthful error. When a response arrives, compare visual quality and elapsed time to earlier screenshots; if native CPU is still very slow, inspect runtime logs/CPU/memory rather than inserting a paid API or inventing a speed result.
