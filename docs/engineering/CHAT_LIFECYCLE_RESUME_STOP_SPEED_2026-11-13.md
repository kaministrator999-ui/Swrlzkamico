# §C long coding lifecycle: source visibility, background sync, Stop and event overhead

Date: November 13–14, 2026 (America/Chicago). Production authority: Hugging Face Space `kamiloki/Swyrlz`. Never route §C/§E through Vercel. Preserve the current Qwen3.5-9B, 16-CPU quota/18-thread configuration, 16,384-token KV context, account-owned chats/project revisions, and existing GitHub and native §E permissions.

## Actual report

The user observed an HTML/JS code turn remaining in a thinking/generating state after **34:50**, with a large provisional code draft. Later §C said it checkpointed **23,088 bytes**, and a subsequent **Continue code** turn showed newly generated code but not the original saved bytes. Stop sometimes failed to interrupt generation. Re-entering Chrome after backgrounding must reflect server-owned generation state, not trigger another request. The user also reported resumed decoding felt slower.

## Source-level findings

- `station.py` owns model inference via a background worker and an in-process activeGeneration snapshot. Browser stream loss does **not** imply cancelling that worker. A dedicated `POST /api/lalm_station/cancel` sets `cancelRequested`. The coding engine previously had no interrupt callback inside `model.create_chat_completion`'s native streaming loop, so Stop could be delayed for the entire native generation.
- The resumed model consumed a **bounded 4,800-character suffix** from the checkpoint and held the original source in memory for final assembly; it did not need to regenerate the previous 23 KB. However, `station.py` initialized the *new* generation's preview to an empty string, and the Chat UI hid provisional drafts once an explanatory message or terminal state appeared. This is why stored code could appear to disappear despite a saved checkpoint.
- CPU decode continuation permitted up to **eight** segments of up to 4,096 output tokens, and its time limit was evaluated only between segments, allowing a single native segment to run much longer than the intended budget.
- The coding preview emitted potentially one Station event per tiny native token chunk. That incurred repeated server snapshot updates and Chat DOM replacement.
- The code continuation overlap-trimmer ran throughout a segment at 256-character intervals. An independent deterministic test detected legitimate repetitive source being removed. This was corrected **before** any rollout.

## Patch invariants

1. Seed `activeGeneration.previewText` with the exact hashed, server-validated saved source on a same-thread Continue command. Carry an explicit unverified checkpoint receipt. Keep the original text visible while appending new code; the preview must remain unverified until validation succeeds.
2. Keep a paused, incomplete draft visible alongside the status message. Clear the saved-draft UI marker only when the matching assembled source is accepted.
3. Append new text to the existing provisional `pre` text node instead of replacing the entire 23 KB string on every update. Preserve the previous scroll-follow behavior and user scroll pause.
4. Coalesce model preview deltas into small chunks, flushing at 128 characters or about 350 ms and at the end of each native segment. **Deterministic regression:** 1,296 fake-model native chunks required **41** preview events with exact byte-for-byte output. This measures event overhead, not a guaranteed model tokens/sec improvement.
5. Trim exact duplicate code at most **once per native segment**, not after every buffered chunk. Test exact 27,374-character assembled source and exact new preview suffix, including repeated code.
6. Add Station-owned, process-only `_cancelCheck` to the coder engine. Check between yielded native tokens and within focused patch generation, and stop after explicit cancellation. Do not treat a browser disconnect as a stop signal.
7. A coding attempt has a bounded per-invocation native decode budget (240 seconds); a short repair has a separate 115-second maximum. Incomplete output remains unverified and checkpoints under the existing system; long projects still require per-file source edits.
8. On frontend reconnection, merge server-stream deltas using server-supplied UTF-16 offsets and request IDs. If the local stream diverges, trigger a fresh authoritative sync instead of duplicating code. Existing visibility/focus/pageshow/online sync hooks continue to rehydrate the UI.
9. The Stop button awaits an affirmative Station cancel receipt instead of aborting the browser stream before the worker can report a terminal state.
10. All changes are bounded to `qwen_coder_engine.py`, `station.py`, and `chat/§wyrlz/index.html`, with exact source hashes, immutable preflight snapshot and guarded rollback.

## Evidence and limitations

- [Read-only source and JS/UTF-16 offset preflight](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43562080479) passed before an additional synthetic event-stream test.
- Earlier synthetic stream test [run 43561948940](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43561948940) exposed incorrect repeated overlap trimming, which would have lost legitimately repeated continuation bytes. Fixed before release.
- [Updated preflight with exact source tests](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43562080479) passed: coalesced preview events, original source prefix retention, native Stop, and bounded generation checks.
- [Guarded live release](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43562282033) uses a SHA-pinned source, snapshots exact prior bytes, requires the updated Chat UI, checks Qwen model/threads and exercises a synthetic Stop through the live endpoint before retaining the release.
- The real user's long 23 KB source has not been downloaded or replayed. Synthetic tests do **not** prove its output is complete or that the model is objectively faster in tokens/second. A source version commit alone is not a live acceptance test. Mobile browser/background testing still requires user-device confirmation.
- In-process generation does **not** survive a Hugging Face Space process restart. That would require a durable worker/job queue and independently verified checkpoint recovery.


## Guarded production result · verified November 14, 2026 UTC

- [Guarded live deployment run 43562282033](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43562282033) **passed**. Old Chat Space revision: `c56c9222cda2955db380da68847c00d11c7c9334`; new revision: **`3badea18e4e0ad23acf5d6f5fddfded9b38fa7cb`**. The publishing workflow verified exact hashes for `qwen_coder_engine.py`, `station.py`, and `chat/§wyrlz/index.html`.
- The live HTML UI URL was confirmed to serve the new code; resident model verification remained Qwen3.5-9B, 18 decode/batch threads, and 16-core quota. Real isolated server request was admitted, hydrated via `/api/lalm_station/sync`, stopped via authenticated `/cancel`, and confirmed terminal **CANCELLED** in subsequent sync. The test did not read or change any user's private thread.
- [Deterministic code-stream preflight run 43562080479](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43562080479) passed the corrected source. Native streaming emulation coalesced **1,296 tiny chunks to 41 UI preview events**, preserved the precise 27,374-character seeded/continued source, simulated cancellation inside native decode, and triggered a bounded work cutoff. The intermediate failing test is retained because it detected the legitimate-content loss caused by repeated overlap removal. That path was fixed *before* deployment.
- Independent post-release short real coding smoke is tracked at the [lifecycle smoke workflow](https://github.com/kaministrator999-ui/Swrlzkamico/actions/workflows/hf-chat-lifecycle-live-code-smoke.yml). That test must be checked independently before claiming ordinary HTML coding was validated after the new release.
- Scope remains bounded: no restart-resistant worker job queue, no unlimited output tokens, and no measured claim of improved native model tokens/second. This milestone reduces frontend and Station update overhead and makes long turns/cancellation bounded and visible, subject to native decode yielding events. Mobile browser/Quest acceptance remains an explicit user test.
