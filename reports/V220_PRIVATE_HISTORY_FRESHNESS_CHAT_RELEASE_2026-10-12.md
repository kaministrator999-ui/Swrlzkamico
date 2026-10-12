# v220 — §wyrlz private-history vs freshness routing

**Date:** 2026-10-12. **State:** CI PASSED, existing Chat HF Space guarded published; signed-in live memory behavior not verified.

## User objective
A conversational request such as "What did we talk about today?" must not send the question to public internet search merely due to `today`. The history owner uses verified user scope and account opt-in; web search must remain available for genuine current/external questions.

## Implementation
Exact base `68eb54f76319515a9ed69a153b5bc0bd78b6f088` (v219); candidate `302d3b3669bb22275fc42f7fd7b394984412bb0a`, [draft PR #123](https://github.com/kaministrator999-ui/Swrlzkamico/pull/123).
- `hf_space/station.py`: computes canonical personal-history intent once from incoming prompt/history, preserves memory opt-in and encrypted-owner evidence path, passes boolean in internal model payload.
- `hf_space/model_router.py`: when internal historical intent and generic freshness both hold, bypass unnecessary public search, provide a bounded status phase. Explicit web, weather, and time still have their own routes.
- `tests/test_hf_candidate.py`: synthetic server handoff, modeled dispatch with forbidden public search, positive current-news and explicit-web assertions.
No stored history migration, no new provider, OAuth, engine source, or model weight mutation.

## Verification
- [Exact HF offline #38284745231](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38284745231): SUCCESS.
- [Canonical HF Chat release #38284840022](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38284840022): SUCCESS.
- New Space revision `85c521293bda1a796ad3db20e7b9fd2c83bcbe7f`. Preserved rollback `e3d823f3b5e7c887370733bc6f74a1daff8a08de`.
- Artifacts: release `11762563697`, rollback `11763201262`, predeploy snapshot `11762244160`.
- Receipt `DEPLOYED_UNVERIFIED`, `knownGood=false`.
- Registry: Repository Work 1.0.161, Server Runtime 2.3.373, LALM Engine 2.1.196. Web Chat 1.5.109 / Online Research 1.0.31 / Google Account 1.0.15 unchanged.

## Live checks pending
With authenticated ChatGPT-history recall enabled, ask a specific private conversation question containing `today`; confirm no `SEARCH_STARTED`, evidence-grounded recalled result or honest no-match. Then request current headlines, current weather/time and explicit online lookup. Runtime publication is not proof of 700M answer accuracy.

Next independent work: full live social/history model acceptance, source-grounded reply attribution, and test-runner+bounded repair support for model-generated code. §E game-engine release remains a separate lane.
