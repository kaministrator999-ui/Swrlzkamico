# Server v2.3.35 — Streaming stability + LALM coding/prefill correction

**Date:** 2026-09-11

## Module state

- **Server Runtime:** v2.3.35
- **Web Chat:** v1.4.30
- **LALM Engine:** v2.1.24 (`2.1.24-hot-boundary-v15-progressive-prefill-code-verify`)
- **LALM UI:** unchanged
- **Deployment:** NONE — runtime-only hot update
- **Server restart:** NONE

## Failure lineage carried forward

Server v2.3.34 / Chat v1.4.29 attempted to reduce stream rendering churn, but user browser verification showed that the Chat surface still flashed black repeatedly during LALM generation. That attempt remains part of the lineage and is not treated as a successful visual fix.

The same acceptance run also exposed two LALM issues that become inputs to this correction: a coding response could be structurally complete while still containing code/explanation inconsistencies, and an interrupted prefill discarded substantial already-computed prefix work.

## What v2.3.35 changes

### Chat v1.4.30

- Streaming no longer replaces the active assistant article on every streamed update.
- While generation is active, one stable response bubble stays mounted and only its live text node is updated.
- Rich markdown/code-artifact reconstruction is deferred until the response becomes terminal, where one final full render is allowed.
- Browser-local state persistence is throttled during active generation instead of serializing the full conversation on every token/update.
- Scroll-follow remains line-aware and operates against the stable bubble rather than a newly replaced article.
- The intent is to eliminate the user-observed black/whole-interface flash caused by repeated DOM replacement.

### LALM Engine v2.1.24

- Progressive prompt-prefill checkpoints are now published every 32 newly-prefilled tokens. These checkpoints intentionally store recurrent state without terminal vocabulary logits and are eligible only when a later request still has suffix tokens to prefill.
- A retry or later exact-prefix request can therefore resume from a partially completed prompt checkpoint instead of always rebuilding the entire prefix after interruption.
- Conversation checkpoint capacity increased to preserve progressive prompt checkpoints alongside prompt, assistant-live, terminal, assistant-close, and next-user-open states.
- Coding guidance now explicitly requires silent checks of formulas, operators, types, control flow, syntax, examples, and stated input/output behavior before the response ends.
- Code explanations are required to match the code actually shown; the model is explicitly told not to claim interactive user input when the example hardcodes a value.
- Coding completion contracts now include consistency checks in addition to structural completeness/explanation presence.
- The semantic checker includes deterministic detection for the Fahrenheit→Celsius regression that triggered this event and for explanation claims of user input that are inconsistent with the shown code.
- Grouped-attention arithmetic now uses batched matrix multiplication instead of an optimized einsum path on every token, reducing Python/einsum planning overhead. The dominant direct-quantized matrix-vector work remains unchanged, so decode-speed improvement must be measured rather than assumed.
- Progress telemetry is kept coarser during decode/prefill so diagnostics do not add unnecessary browser/server event churn.

## Verification requirements

1. Live `/api/lalm/status` must report LALM Engine v2.1.24 and the v15 revision.
2. Live `chat_stream_incremental.js` must be served from the `runtime` branch and contain the stable live-text streaming renderer.
3. Browser acceptance: generate a long LALM response and confirm the repeated black/full-interface flash is gone.
4. Prefill acceptance: interrupt/retry or continue an exact-prefix workload and inspect the camera log for `prefill-progress-*` checkpoint reuse.
5. Coding acceptance: repeat the C++ temperature converter test and verify the conversion formula, explanation, and actual input behavior are mutually consistent.
6. Performance acceptance: compare fresh-prefill seconds/token and decode seconds/token against the previous receipt (~0.32 s/prefill token and ~0.47–0.50 s/decode token). Do not claim a speedup until measured.

## Relevant lineage

- Stable-stream Chat correction: `eb0828943bfb9c699ad39ccb3b1cecaa82f3a5ef`
- LALM v2.1.24 source: `78e38de0bd7d4c1505d990b8f2796b898ea918a1`
- Server runtime authority v2.3.35: `1078e9a7f7925e244e5e1135facf108308c1b2cb`
- Chat authority v1.4.30: `f6b58ef5e422ab5f23dc685aca8949c4d48e654f`
- LALM authority v2.1.24: `787921dbfedec9444c0342d758b11954ae7734c8`

## Rollback note

The update is runtime-owned. The stable deployed loader/infrastructure was not modified. If the v15 engine fails to load, the hot-runtime backup/fallback mechanism remains the rollback boundary; if the Chat renderer regresses, the prior runtime asset can be restored without a Vercel deployment.
