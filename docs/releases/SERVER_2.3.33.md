# Server v2.3.33 — Completion Contracts + Smooth Streaming

Date: 2026-09-11

## Module state

- Server Runtime: v2.3.33
- Web Chat: v1.4.28
- LALM Engine: v2.1.23 (`2.1.23-hot-boundary-v14-completion-contract-fast-decode`)
- LALM UI: unchanged
- Stream contract: unchanged
- Google Account architecture: unchanged

## Why this release exists

A captured coding response showed that adaptive budgeting was working but the model could still accept EOS after producing the code while omitting an explicitly requested explanation of both the helper function and `main()`. The same browser session also showed visually choppy response generation because the Chat render path rebuilt the whole conversation DOM on each stream update and persisted the full conversation state too frequently.

## LALM behavior changes

- Added a response-completion contract derived from explicit request obligations.
- Coding requests can require complete code, requested explanation/overview, and function/`main()` explanation when the user asks for those parts.
- EOS is deferred when explicit response obligations remain incomplete, within the existing safety ceiling.
- Completion headroom can extend in bounded increments for missing requested parts as well as open code/syntax structures.
- Replaced the prior per-request model-facing budget directive with a stable response directive so system-prefix changes do not invalidate exact-prefix conversation checkpoints.
- The stable response directive asks §wyrlz to answer completely, use a natural/lightly personable tone when appropriate, and avoid unsolicited model-identity introductions.
- Adaptive response planning remains active as runtime control/telemetry instead of a large changing system-prompt suffix.

## LALM performance changes

- Grouped attention work was vectorized to reduce Python-level per-head loop overhead.
- Q/K RMS normalization was vectorized across heads.
- Progress telemetry cadence was reduced after the initial steps to lower stream/UI overhead.
- Stable response-directive reuse is expected to reduce first-turn/continuation prefill compared with the previous dynamic budget-directive path and improve checkpoint reuse consistency.
- Actual generation-speed improvement remains measurement-gated; compare the next camera log against the previous roughly 0.50–0.54 s/token coding sample instead of assuming a gain.

## Chat streaming changes

- Added a final runtime streaming renderer that updates only the active assistant message during generation rather than rebuilding the entire conversation DOM for every stream event.
- Browser-local conversation persistence is throttled during active generation instead of serializing/writing the whole state on every delta/status event.
- Existing user scroll-follow behavior remains respected; line centering occurs only when the generated response advances a rendered line and follow mode is active.
- Code-artifact promotion is deferred until the assistant message is complete so the nested artifact UI is not repeatedly reconstructed while the code is still streaming.

## Failure / correction lineage inside this event

- The first code-artifact deferral edit briefly introduced incorrect default filename mappings for Swift/Ruby. It was corrected immediately before release closure and did not require a deployment.

## Verification

- `/api/lalm/status` reports runtime override LALM v2.1.23 with the new completion-contract, EOS-deferral, stable-directive, and vectorized-attention capabilities enabled.
- `/live/assets/chat_stream_incremental.js` returns HTTP 200 from the GitHub `runtime` source.
- Live `/chat` returns from `github-runtime` and includes `chat_stream_incremental.js` last in the runtime script chain.
- Browser-visible smoothness and measured decode/prefill performance remain acceptance tests for the user's next generation/camera log.

## Deployment / restart

- Production deployment: NONE
- Server restart: NONE
- Path: runtime-hot only

## Relevant lineage

- Incremental Chat streaming asset: `d07b9bbfc34994d77c0d2f2a546151df8d3689f4`
- Runtime manifest wiring: `aea3fb94b7f1fd4555fbd2d96b4ab6d679d91108`
- Code artifact deferral: `dc0133b0c7a7391086c83bf0280bd6ddd6feb7c3`
- Code artifact filename correction: `ea651de51f6d10f552f574499a2787ee69c32a9d`
- LALM v2.1.23: `dfa3c71793d0bd33bba01d129cfeb650e38a3f48`
- LALM version authority: `8897046723f983bfdafaeb178c78ed18b4443e62`
- Server Runtime version authority: `3c044c71a59ba4a600ee00268ffeeb1726c25b6c`
- Web Chat version authority: `f8f72f2c77a4c5ddb1ca045f9375cc09bae8064c`
