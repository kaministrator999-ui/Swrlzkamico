# §C coding follow-up intent and bounded source continuation — 2026-11-14

## Problem and reproduction

After the live 16K context and bounded output continuation releases, the user's *existing* HTML coding thread still failed with `Generation failed: OUTPUT_TOKEN_LIMIT` on the exact follow-up **"Now improve the page"**.

An exact-source classifier reproduction exposed a separate root cause from the token cap:
- `Now improve it` — classified as programming.
- `Now improve the page` — **not** classified as programming despite prior HTML source.
- `Improve this HTML page` — classified as programming.

Consequently, this exact wording could bypass the source-preserving coding engine and its long-output continuation protections. A larger token window alone could not fix the routing problem.

## Scoped repair

Production file: `brain_programming.py` only. This uses source-grounded artifact evidence:
- Natural refinements: *improve, polish, refine, enhance, redesign, modernize, upgrade, clean up, make the page better*, and similar requests.
- Requires an existing authored code artifact or approved code pin. Web/page/layout refinements require actual HTML/CSS/JS source evidence.
- Preserves the **existing** project scope, prior artifact, source language, and coding validation. It does not manufacture authorization to edit a stored artifact or initialize an unrelated new project.
- No changes to §E, model weights, user accounts, memory persistence, 16K context window, or 18-thread CPU plan.

## Regression testing and failure lineage

Read-only preflight workflow: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43536531623

- 13 helper positive examples and 10 negatives.
- 36 complete classifier follow-up cases over multiple history depths: immediately after the HTML artifact and with one or two prior `OUTPUT_TOKEN_LIMIT` failures in the conversation.
- Four noncoding page-discussion negatives, plus independent checks that genuinely new projects remain new and explanation prompts remain explanatory.
- All these source-level tests passed.

The first two guarded production release attempts were **rejected and rolled back** due to synthetic session/request-ID mismatch in the multi-turn acceptance harness, not a failing source-level classifier. This exposed another nearby failure mode: a production Space rollout can rotate an anonymous test session, and transient connection loss must not be construed as a coding failure or a successful model completion. The harness was adjusted to validate exact request-ID on streamed events, verify first-turn HTML actually persisted, and repeat the complete disposable two-turn conversation if a rollout invalidates a session.

## Final guarded production release

Workflow: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43536683648

Final production Hugging Face Space source revision: `b5803acb3468f46bfad401802ce6e64a40d713f4`.

**Passed** complete new two-turn project through §C's live send/stream/sync API:
1. "Generate a short complete HTML demonstration page with a heading and a toggle button. Keep the single-file source under 100 lines." — 1,313 HTML characters, candidate `PASS`, 77.95 seconds.
2. **"Now improve the page"** — routed as `codingTask=true`, `changeClass=feature`, `projectContext=existing`, produced 3,318 HTML characters, candidate `PASS`, status `COMPLETE`, 145.55 seconds.

The successful second turn showed first provisional source at 49.30 seconds and validated final source at 145.40 seconds. The full model still used 16K context and 18 decode/batch threads on a 16-core quota. The first attempt's session mismatch was treated as a test failure; only the successful second full conversation qualified the final release.

**Boundary:** The synthetic project was intentionally small and did not reproduce the user's exact long HTML source. This verifies correct routing and a working complete-project follow-up, **not** unlimited output or guaranteed resolution of all `OUTPUT_TOKEN_LIMIT` failures when a larger generated result exhausts all bounded continuation segments. The existing four-segment completion protection continues to apply, and the user's existing project thread should be retested.

## Future repair requirement

When user reports a failure, test the immediate example **and the adjacent equivalence class**, including:
- Short rephrasings and synonyms
- Success, failure, and multiple-failure histories
- Sources several turns back, pinned artifacts, and genuine new-project requests
- Normal conversational false positives
- Provider and client routing, stream/terminal signals, source retention, and final validation
- Exact rollback if any stage fails

Preserve negative outcomes and receipts, including test harness defects, rather than rewriting history as all tests passing on first attempt.
