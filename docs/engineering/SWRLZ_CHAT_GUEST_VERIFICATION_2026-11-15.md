# §C guest chat verification and unresolved code generation — 2026-11-15

## Source-of-truth boundaries
- Repository: `kaministrator999-ui/Swrlzkamico` main.
- Live Space: `kamiloki/Swyrlz` (`https://kamiloki-swyrlz.hf.space`). Vercel is not in this deployment flow.
- Testing was synthetic, anonymous guest-only Chromium/API. Never infer account-specific persistence from guest tests.
- The server's `model_router.py` routes model ID `700m` to the conversational generator; a true `codingTask` is automatically routed to `coder`. The live `app.py` binds the conversational generator to `lfm2_700m_engine.generate_events` and the coding generator to `qwen_coder_engine.generate_events`.

## Verified improvement: guest reload
- Original failure: Chromium reloaded to New conversation with no visible retained test message.
- The guarded first-hydration source fix deployed in run [43752966195](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43752966195). Immediate post-publication UI acceptance **failed**, so deployment alone was not accepted.
- Isolated full guest test [43756286435](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43756286435): **PASS_EVIDENCE, 2/2 turns**, server had one two-message test thread before and after refresh, and the browser rendered its saved user turn.
- Repeat guest test [43758952683](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43758952683): **PASS_EVIDENCE, 2/2 turns**, server revision 2, thread count 1, two retained messages before and after refresh, browser had one retained user bubble and one thread button, and correctly recalled `silver otter`.
- The post-fix behavior is supported in **two independent runs**, not a claim of universal reliability.

## Verified improvement: explicit no-code explanation
- The initial direct programming-intent patch and coder-side output guard were insufficient by themselves.
- Tracing the deployed app and model router located the ordinary explanation path in `lfm2_700m_engine.py`, separate from the code-delivery generator.
- Guarded conversational source patch deployed at Space revision `1be1c6379b7666c31b3114bd856a1979ac145c3f` in [43757532442](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43757532442). Immediate end-to-end run failed (Python response included code fences and a later JavaScript follow-up timed out); do not treat it as acceptance.
- Isolated warmed-runtime case [43758376930](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43758376930): **PASS_EVIDENCE** for the Python first turn at approximately **36.95 seconds**. The reply explained replacing subtraction with addition without showing source code.
- This confirms the intended output format in the warmed sample, not all code-related prompts or two-turn conversations.

## Remaining issue: slow or incomplete HTML coding
- Baseline short HTML page [43756836045](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43756836045): **PASS_EVIDENCE**, one turn, about **97.87 seconds**. Static structural checks passed; no claim of executing generated page interactions.
- The guarded compact-output budget experiment [43757718043](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43757718043) generated the first page (PASS, about **110.06 seconds**) but timed out on the follow-up before completion. **The source was rolled back automatically**, with verified rollback Space revision `7c906b67bc0a609ffadce0d8768a6aac958ea243`. The experiment is **not** a verified speed improvement and is not active.
- Prior full guest suite [43752038318](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43752038318) recorded additional HTML timeouts, validator-review answers, and incomplete revised projects. See its uploaded batch reports.
- Do not reclassify an inference timeout as a code correctness failure. Also do not accept an unvalidated draft as a completed project.

## Next engineering checks
1. Establish a deployed-worker version receipt before each post-publication acceptance run, to avoid testing an older serving worker while a new Space revision warms.
2. Instrument the coder route's response token/prefill budget and per-turn generation duration for a single small HTML task and its full-page revision. Preserve candidate-validator reasons and partial-code checkpoint receipts without leaking account data.
3. Improve small multi-turn HTML responsiveness by addressing actual measured decoding/context/repair overhead, **not** merely increasing evaluator timeouts or weakening code validation.
4. Test HTML output structurally and, where possible, execute the generated interactions in a sandboxed Chromium page; preserve normal full-source deliverables and larger project budgets.
5. Re-run all three guest batches after verified targeted improvements, keeping guest session restore separate from model-generation latency.

No paid hardware upgrade, model-weight retraining, new Space, or new authentication flow was part of this work.
