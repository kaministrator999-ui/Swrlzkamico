# §C HTML coding quality and source-aware editing (2026-11-14 / 2026-11-15 UTC)

## Scope

User requested improving §C's coding model/workflow, not editing one previously generated Aether page. Keep HF Space \`kamiloki/Swyrlz\` authoritative; \`chat/§wyrlz/index.html\` UI, original account data, §E engine, model weights, CPU thread profile and deployment authority unchanged.

### What already exists (preserve)

Source-backed intent recognition for short “improve the page” follow-ups, bounded code output continuation and checkpoints, targeted candidate-repair validation, source evidence imports, guarded multi-turn live release. Do not duplicate or silently replace those implementations. See \`docs/chat-grounded-page-refinement-regression-2026-11-14.md\` and \`scripts/project_code_targeted_repair_v1.py\`.

## New source modules

- \`scripts/html_code_quality_v1.py\`: scoped coding guidance + conservative HTML diagnostics for definite defects and advisory mobile/performance issues.
- \`scripts/test_html_code_quality_v1.py\`: regression from Aether for invalid rgba hex syntax, dynamic rgba hex interpolation, undefined Pause variable, valid RGBA, noncoding isolation and touch/performance warnings.
- \`scripts/hf_chat_html_quality_release_v1.py\`: exact-current-source Hugging Face engine patch, SHA manifest, parent-CAS release, strict request-ID end-to-end acceptance, rollback.
- \`scripts/test_hf_chat_html_quality_release_v1.py\`: patch contract and failure/retry contract.
- \`.github/workflows/hf-chat-html-quality-preflight.yml\`: read-only source preflight and baseline synthetic coding acceptance.
- \`.github/workflows/hf-chat-html-quality-release.yml\`: governed source release only on authorized request, pinned commit, source snapshot and live acceptance.

The new validator rejects only specifically recognized defects; potential Canvas shadows, quadratic particle connections, pointer-only mouse handlers and backdrop blur are warnings. This is not a full JS runtime execution test or a proof of mobile frame rate. The source quality hints are not model weight training.

## Evidence / failed first production attempt

- First static preflight **passed 8 tests and source patch**: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43672135736
- First guarded live release https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43672223226 **failed**. Published candidate HF revision \`e03fd73f455e921ee0b4da569c2aaff07a816921\` had correct uploaded source SHA and reported resident model readiness. Synthetic live test returned no request-ID-matched accepted candidate (\`finalLength=0\`, \`matchingRequest=false\`, no terminal or validator receipt).
- Guard restored original engine source with HF revision \`1d43aa7a75795b3ccc008d136f48eff791514fea\`; rollback readiness passed. **Do not count first candidate as deployed.**
- Failure classification remains **undetermined**: synthetic anonymous session might have rotated during Space restart or inference/test transport could be faulty. Cannot call it a model-quality failure without a matching run receipt.
- Follow-up source change primes a fresh anonymous session, explicitly checks send ACK request ID, logs stream event types and retries complete synthetic sessions three times. A read-only **baseline on existing restored coder** is required before another release to distinguish the failure.

## Verification boundaries

- The user's specific generated Aether page has not been patched, overwritten or committed.
- Mobile performance needs real-device benchmarking; static warnings are not quantified FPS gains.
- The integration is safe to promote only after repeatable baseline + guarded live acceptance; source-level tests alone are insufficient.

## Final guarded release (verified)

- Read-only preflight with baseline live coder: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43672835617 — **success**. Seven HTML diagnostics tests, four release/rollback tests, exact live-source AST/source SHA preflight, and synthetic baseline live HTML generation. Baseline completed 4,963 HTML chars with matching request ID and validator \`PASS\`.
- Second guarded release: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43673090268 — **success**, protected source SHA with unchanged model/hardware/user data. Accepted Hugging Face source revision \`fe4e0bd87a30ac63117998e43a682e0aa54e668c\` (prior rollback source \`1d43aa7a75795b3ccc008d136f48eff791514fea\`).
- Synthetic attempt one produced 247 provisional code deltas but no matching terminal/validation receipt; **rejected**, not counted as success.
- The retry used a fresh anonymous session; final 6,335 HTML chars, 350 provisional deltas, terminal \`COMPLETE\`, matching request ID, candidate validator \`PASS\`, and zero specifically detected HTML defects.
- Final workflow logged \`LIVE_RELEASE_KEPT\`. Exact source and rollback receipts retained in the workflow artifacts.

**Scope of proof:** successful end-to-end normal synthetic HTML generation through the real §C API with the quality overlay integrated, in addition to deterministic tests of defect rejection. This does not prove improved performance on the user's physical phone or that the user's much larger Aether source was itself edited. The earlier session failure remains in the release history.
