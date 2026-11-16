# §C Qwen HTTP 500 on remix-critique follow-up — source-grounded repair

Date: 2026-11-15 US Central. User shared an Android screenshot with a durable user turn at 10:37 PM:
"I was just trying to tell you this is the issues with your remix version of the song".
At 10:39 PM the assistant wrote `Generation failed: QWEN35HTTP500` (underscores in original internal status may render as Markdown). The saved turn is a **critique**, not a request to retrieve copyright-protected lyrics or create another song.

## Root-cause isolation

- Read-only current production audit [Actions #43806029203](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43806029203) verified Space `e49039b3af00d726742c84077ce3da3b10a0b425` was the RUNNING revision.
- The live `music_transform_quality.py` classified a prompt containing the noun **remix** plus any music cue as a music transformation without testing whether a user asked for creative work. Hence a critique could enter long, buffered remix generation instead of conversation.
- Separately, the live `stop_transport.py` raised `QWEN35_HTTP_500` directly on a local llama.cpp HTTP 500 response. `qwen35_single_runtime.py` did not recover; Station appended a generic failure bubble. An HTTP 500 alone does not establish whether the model server fault was memory, cached KV state, context-window exhaustion, cancellation or a transient internal error. Do not assert a definitive server-side cause without evidence.
- The existing `online_tools.py` critique/lyrics routing is already correct and remains unchanged. The newest user message was visibly submitted, so don't label this a client send or lyric-lookup failure.

## Scoped fix

1. Music transformation intent requires an actual affirmative request: "write a parody", "remix these lyrics", "please fix your remix", "I want a new remix". Descriptive complaint phrasing, questions and negatives cannot accidentally start generation.
2. The generation engine responds to music feedback as conversation, addressing the reported faults without rewriting the song or re-searching the original unless directly requested.
3. Native llama.cpp HTTP 500 before any SSE bytes triggers **at most one** uncached retry, using the same prompt and bounded token budget. No retry if the user stopped, output was already emitted, or the status differs. The original native error remains visible if both attempts fail, with a plain-language failure message and saved user prompt.
4. All previous model weights, source-evidence gates, original music transformation semantics, Stop/cancel ownership and already-deployed Hugging Face files are preserved. No third-party APIs, exports, account changes, web UI packages or Vercel deployments.

## Validation and production deployment

- Deterministic scenarios cover the exact screenshot sentence, several feedback variants, legitimate creative commands, 500-then-success, repeated 500, 400, midstream error, prior Stop and concurrent non-retry safety.
- Source of truth: `scripts/music_transform_quality_v1.py`, `scripts/qwen_http500_recovery_v1.py`; regression suite: `tests/test_qwen_http500_feedback_v1.py`.
- Exact-live code patch: `scripts/hf_chat_http500_feedback_v1.py`. It validates file anchors, parses modified Python with AST, pins one immutable parent Space SHA, records exact original byte hashes, commits only four existing files plus one helper, verifies every output by byte readback and attempts an exact-content rollback on verification failure.
- Official release gate: `main:.deploy/HF_SPACE_REQUEST.txt` → `hf-space-request.yml` → `manual-hf-space.yml` with `CHANGE_SCOPE=http500-music-feedback-v1`.
- No source commit equals deployment. A genuine guest follow-up response and real owner-device behavior remain acceptance stages after the release.

## Production and acceptance receipts

- Source PR: [#438](https://github.com/kaministrator999-ui/Swrlzkamico/pull/438), merged commit `78187b1e6ed13886fb4c96c69d4e869111aa2065`.
- Scoped official release request commit: `38d0cf15b64fbb58341e689eaee990cafe6d059a`, `CHANGE_SCOPE=http500-music-feedback-v1`.
- Governed release: [Actions #43807133417](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43807133417), success. The exact pre-release Space revision `e49039b3af00d726742c84077ce3da3b10a0b425` advanced to `a72f505a00557ecd7218e6e68fff1fc2baad9e8a`. All five files byte-for-byte readback verified; previous exact files archived before mutation. Other deployment modes skipped.
- Unit and actual-live-source preflight: [#43807012414](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43807012414), success.
- Independent guest acceptance workflow: [#43807349170](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43807349170). Inspect its actual result before claiming user-visible quality. This test uses a synthetic lyric reference and an exact copy of the reported feedback text, never an account login.
- Remaining uncertainty: this improves response routing and recovers one transient native 500; exact internal llama.cpp cause of the original screenshot's HTTP500 was not determined, and if the local server repeatedly returns 500 an ordinary FAILED result remains possible. Real-device/account-thread acceptance is separate from synthetic guest verification.

## Real guest follow-up acceptance result

- Workflow [#43807349170](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43807349170): **PASS** on deployed `a72f505a00557ecd7218e6e68fff1fc2baad9e8a`; runtime confirmed RUNNING and serving exact SHA.
- Synthetic reference/remix first turn: 202 accepted, final `COMPLETE`, 1,064 characters, 82,653 ms, no HTTP500 in visible terminal status.
- The exact user's correction follow-up: 202 accepted, final `COMPLETE`, 261-character assistant response. No generated new song, no lyrics-retrieval status, no model-failure message, and no HTTP500 in terminal status.
- Critical performance caveat: second turn required **286,414 ms** (approximately 4 minutes 46 seconds) despite only 261 characters. This could include model queue, input prefill, CPU decode, or a silent successful HTTP500 retry. Available guest receipts do not isolate the cause; do not claim it was fast or assume queue versus model fault.
- Functional criteria for the reported critique: passed. Performance / user-owned historical long-thread reliability: **not accepted** by this single synthetic guest case; should be independently investigated before making latency claims.
