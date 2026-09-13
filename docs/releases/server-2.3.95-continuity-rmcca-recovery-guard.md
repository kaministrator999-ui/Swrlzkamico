# Server 2.3.95 — Continuity-safe recovery, RMCCA transport restoration, and bounded generation

Date: 2026-09-12
Server Runtime: `2.3.94` → `2.3.95`
LALM Engine: `2.1.32` → `2.1.33`
Web Chat: `1.4.77` → `1.4.78`
LALM Revision: `2.1.33-hot-continuity-rmcca-guard-v23`
Deployment / restart: **NONE**

## Purpose

Repair the benchmark failure where a long local R39 response could lose its stream, detect a new server instance, regenerate the same request from scratch, overwrite a better earlier partial answer, and become progressively worse on each retry. The same event restores the canonical RMCCA cognitive envelope across the existing stable server normalizer without requiring a stable deployment, bounds runaway coding generations, stops obvious output degeneration, and makes batched-prefill timing report block work instead of misleading per-token zeros/spikes.

## Chat recovery integrity

A new runtime page overlay, `web/chat_recovery_integrity.js`, loads immediately after `chat_background_resume.js`.

Recovery policy is now:

- exact replay while regenerated output is still byte-prefix-compatible with the saved partial;
- continuation when regenerated output reaches and extends the saved partial;
- preserve the saved partial and stop automatic redo on server-instance change, RESET, or divergent regenerated text;
- delete the pending auto-retry receipt when preservation is triggered so the same message cannot keep replacing itself on later focus/pageshow/online events.

This intentionally prefers a visibly incomplete but coherent answer over destructive stochastic regeneration.

## RMCCA transport restoration

The benchmark camera showed `canonicalRequestPrepared=false`, `canonicalEnvelopePreserved=false`, and `cognitive source=server-fallback`. The browser canonical layer was producing RMCCA, but the deployed stable normalizer only preserves its known request fields.

To avoid a stable deployment, Chat 1.4.78 adds a compact transport carrier as a final history item. It contains only the RMCCA cognitive clock/envelope IDs and compact user-time context. The existing stable normalizer already preserves user/assistant history text, so the carrier crosses the deployed boundary unchanged.

R39 v23 removes the carrier before prompt rendering, reconstructs `swrlzCognitiveContext` / `swrlzUserTimeContext`, and then delegates to the existing v22 task-aware path. The carrier is therefore transport metadata and is never intended to become model-visible conversation text.

## LALM generation guard

R39 v23 preserves v22 batching/native execution but adds:

- explicit evidence discipline against invented retrieved messages, scores, percentages, benchmark results, repository facts, or test results;
- coding policy that prioritizes the runnable artifact before extended explanation;
- default non-manual coding budget capped to approximately 352 planned / 304 wrap / 448 hard tokens instead of the prior 512/416/704 behavior observed in the benchmark;
- bounded completion-contract repair: once a very long answer is still missing only `complete-code`, the engine no longer keeps forcing EOS deferral indefinitely;
- a degeneration guard for repetitive/fragmented prose outside fenced code, including the observed uppercase-fragment failure mode;
- graceful completion of the coherent response already emitted when degeneration is detected.

Manual generation budgets remain caller-controlled.

## Prefill telemetry correction

v22 proved that the 96-token vectorized path works, but the inherited progress messages displayed buffered token ordinals as `0.000s` and then charged the whole block to the flush token. v23 suppresses non-flush pseudo-token timing and rewrites flush receipts as block-level timing with block token count and tokens/sec.

## Preserved architecture

- v22 batched/vectorized prompt prefill remains intact.
- Native `_r39_native` and `_r39_batch` execution remain intact.
- Exact conversation checkpoints and prefix reuse remain intact.
- Decode remains single-token; speculative decoding is not introduced in this event.
- RMCCA remains the single canonical cognitive router; no competing router was added.
- No stable `main` API, middleware, deployment, or restart was changed.

## Version/concurrency evidence

Immediately before version assignment, authoritative runtime files still reported:

- Server Runtime `2.3.94`, SHA `5b7b3be86c2d771a416f5cca60bc8e2d7c26b05a`;
- LALM Engine `2.1.32`, SHA `bb427d83b98c047277e33e9665ca181928e5a400`;
- Web Chat `1.4.77`, SHA `26c15eeef3e7487980897b7f27d8705a139a9304`.

No concurrent authority advance was observed. This event then assigned Server `2.3.95`, LALM `2.1.33`, and Web Chat `1.4.78`.

## Verification state

- `r39_engine_v23.py` passed Python syntax compilation before publication.
- `chat_recovery_integrity.js` passed `node --check` before publication.
- Runtime page manifest v16 loads the recovery overlay after canonical context/background resume.
- Runtime hot manifest points to `2.1.33-hot-continuity-rmcca-guard-v23`.
- Active hot entry loads the pinned v23 source commit.
- No deployment/restart action was performed.

Live acceptance should verify: `hotRevision=2.1.33-hot-continuity-rmcca-guard-v23`, `COGNITIVE_ROUTE` reports `cognitive source=RMCCA`, batched PREFILL status uses `Prefill batch flush`, and any later instance-change recovery leaves the prior response intact with `backgroundResumeMode=partial-preserved` rather than `redo`.

## Relevant lineage

- v23 engine source: `c35b08a162112ed29552d408123fdb5ebddc7434`
- Chat recovery overlay: `a6af2f573d428fc998ff0d21dbe3051cb3fbe5e7`
- Active v23 entry: `c82602940449f66652327a44e1d1a43770f88a44`
- Hot manifest: `b24e55e155667d3a0bcee150f467acb3ed2daa6b`
- Runtime page manifest v16: `f1dad866a76c43152ca812790d25e838b555ba14`
- Server authority: `04d9f841c2306f3cacb22400220c6add8f9128c4`
- LALM authority: `630c32345f483ec6268eb523849ead182eceefcb`
- Web Chat authority: `18e39e93c5478d0cb40cfecb9a4787b6ce908622`

## Rollback

Preserve Server 2.3.95 / LALM 2.1.33 / Chat 1.4.78 as historical lineage. A future correction should create a new versioned event rather than rewriting this release. The prior v22 engine remains pinned and can be used as the base of a correction without deployment.
