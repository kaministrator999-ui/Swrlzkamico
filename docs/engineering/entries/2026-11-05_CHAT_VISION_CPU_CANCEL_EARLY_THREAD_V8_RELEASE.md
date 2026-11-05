# 2026-11-05 — §C Early Image Chat Thread & Cancellable CPU Vision (v8, v8.1)

**Owner intent:** Image uploads in the existing authenticated §wyrlz Chat must immediately create and open a real conversation instead of waiting several minutes for local vision inference, and subsequent uploads should not sit in the CPU queue indefinitely behind abandoned image jobs. Preserve the existing free HF CPU, no per-image provider charges, chat export, voice, text models and §E architecture.

## Evidence and diagnosis

The owner’s real Android screenshot of the Little Crystal Mage upload showed the composer correctly cleared and a real image progress card, but after **1m55** the server remained in `QUEUED` with the message `waiting for local CPU slot`. This indicates the request had been accepted but had not entered image preprocessing: the app deliberately serializes all SmolVLM MTMD calls on `_inference_lock`. An earlier model call can hold the lock for a long time even after the original browser stops waiting. The previous "Stop waiting" control aborted only browser polling and could not request a backend stop.

## Implemented changes (PR #381)

- `hf_space/chat_vision.py`: owner-authorized POST `/api/lalm_station/vision/cancel` marks an active or queued vision job for cancellation. MTMD uses `stream=True` (supported by pinned llama-cpp-python 0.3.35) and checks stop flags before waiting for the lock, while waiting on it, after image preparation/model loading, and between generated output chunks. Closing the generator allows native decoding to stop cooperatively. The single model lock is **never** released early while native execution might still be accessing it. Job status exposes terminal `CANCELLED` rather than pretending it completed. Original image pixels remain ephemeral and no third-party inference API is introduced.
- Job polling refreshes a server monotonic watcher lease; on incoming requests or status polling, other jobs with no progress watcher for 90 seconds are flagged for cooperative cancellation. One native inference at a time plus one queued remains the memory/CPU limit. **Native synchronous image embedding/prefill cannot necessarily be interrupted immediately**: this change can free cancelled queue slots and reduce abandoned generation, not guarantee instant allocation or faster uncancelled processing.
- `chat/§wyrlz/index.html`: progress card action renamed **Cancel analysis**; performs authenticated server cancellation (best-effort) and stops the browser watcher, rather than merely hiding the wait. Progress text clarifies the image is queued behind the local worker.
- On the first authenticated image-job **HTTP 202 acceptance** in **draft** mode, §C now awaits existing `/api/chat_state` `UPSERT_THREAD` and `SET_CURRENT_THREAD`, creates and selects a durable titled conversation, updates sidebar projection and top title, and moves the pending image progress card to that thread. Image uploads to an existing thread stay there. The pending card is not an authoritative saved chat user message; only completed vision handoff through Station `/api/lalm_station/send` creates that user turn/response. On image failure, the new thread remains truthfully present and the draft/image are recoverable. Navigation guard avoids creating a thread in the wrong chat.

## Mobile reconnect edge correction (PR #382)

- Refresh the returning job's own `lastPolledAt` before cancelling unrelated stale jobs. Otherwise, resuming a suspended mobile page could wrongly cancel its own in-progress analysis after the watch lease.
- Treat a real `CANCELLED` status as terminal and restore a recoverable draft/error, rather than retrying the status forever as a transient network outage.

## Focused tests and independent failures

- [PR #381](https://github.com/kaministrator999-ui/Swrlzkamico/pull/381) merged canonical HF Chat source as `533dce73e3e5703c469a2aee95cefb0f0728e87c`. [Focused validation #42130806133](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42130806133) PASS for local vision streaming mocks, cancellation/ownership/isolation, stale watcher semantics, early durable thread and JS composer syntax/contract.
- [PR #382](https://github.com/kaministrator999-ui/Swrlzkamico/pull/382) merged final source `6a561f95296930449d2cc43648d12d24347c8966`. [Focused validation #42131346209](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42131346209) PASS for vision + Chat and reconnect/cancel semantics.
- Overall HF Candidate Offline Validation still FAILS on **four pre-existing unrelated §E Forge modeling lessons** expectations. A separate old Mobile Lyric Reader Integrity test remains red on its source-string expectation; neither component was changed in this scope. Do not represent the broad suite as passing.

## Production release receipts

- Initial guarded source `533dce73e3e5703c469a2aee95cefb0f0728e87c` [HF deployment #42130946647](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42130946647) **SUCCESS**, resulting Space revision `f269dc6d830dec44c8a7bbb6ec20f33d5d96e942`, rollback `aacd341852ced9c957374a452943806e9f5b9f49`.
- Final source `6a561f95296930449d2cc43648d12d24347c8966` requested via `main:.deploy/HF_SPACE_REQUEST.txt` commit `a84136b8dd8866aa108d404d02da06b801e419a8`. [Final guarded deployment #42131506681](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42131506681) **SUCCESS**: package checked, protected R39 and 700M acceptance, production snapshot, rollback checkpoint, upload and postrelease source checkpoint.
- **Final Space revision:** `282535dd89b344d19cbe7c9a60e22be06e0cf6de`.
- **Rollback Space revision:** `f269dc6d830dec44c8a7bbb6ec20f33d5d96e942`.
- Runtime version authority: Repository Work **1.0.268**, Server Runtime **2.3.459**, Web Chat **1.5.175**. Existing canonical UI local version string `1.1.22` unchanged; R39/700M/Qwen weights unchanged.

## Verification boundary

**DEPLOYED_UNVERIFIED**: GitHub confirms both guarded publications, not that the real free HF CPU releases a cancelled native MTMD operation promptly or that the owner’s Android UI correctly shows the new thread in every session. For device acceptance: refresh §C, start a new conversation, attach a small test image and press Send. After the Space accepts the image job, the sidebar should immediately display a new titled conversation with the image progress card inside it. If another image is queued behind a stopped/abandoned job, the old worker should cooperatively stop at a safe point; a native prefill step may continue until it returns. No paid provider, GPU upgrade or unsupported performance guarantee.
