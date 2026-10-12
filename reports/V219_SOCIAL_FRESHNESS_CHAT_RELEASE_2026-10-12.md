# §wyrlz Chat v219 — Social-checkin vs online freshness routing

**Status:** Source/static CI PASSED; guarded existing HF Space deployment PASSED; actual signed-in user greeting/behavior UNVERIFIED.

## Problem and owner
Prior real-user traces documented basic conversation being diverted into inappropriate web searches when freshness words appeared. `hf_space/online_tools.py` used generic regex freshness `today`; existing `hf_space/social_checkin.py` already identified the same input as a simple check-in. The source-level contradiction could route a greeting to public online search before the model responded.

## Source
- Exact previously deployed base `23a540ab0257e14009147d7202be203743c8641f`, final candidate `68eb54f76319515a9ed69a153b5bc0bd78b6f088`, PR #122 (draft, review, not merged).
- Added one narrow no-online result for `is_simple_checkin(text)` after higher-priority time/weather/explicit-web branches in `classify_online_request`.
- No code or weights changed in the generative model; already-established social style hint still applies.
- Added positive/negative classifier and 700M model dispatch regression in mandatory offline unit suite; extra script test guards the same boundary.

## Checks
- [HF offline exact SHA run #38283579845](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38283579845): SUCCESS.
- [Guarded Chat publication #38283705692](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38283705692): SUCCESS.
- Existing Space revision: `e3d823f3b5e7c887370733bc6f74a1daff8a08de`.
- Rollback: `5b6c4ef067b6b0389acd51c318918a890cd1ca42`.
- Release checkpoint `11762502211`, rollback checkpoint `11762482022`, predeploy reference `11762546894`.
- Deployment receipt: `DEPLOYED_UNVERIFIED`, `knownGood=false`; do not infer user-visible model quality.
- Runtime authority after release: Repository Work 1.0.160, Server Runtime 2.3.372, Online Research 1.0.31. Web Chat 1.5.109, LALM Engine 2.1.195, Google Account 1.0.15 unchanged.

## Acceptance and next step
On an authenticated browser, ask "Hey, how are you today?"; check for direct conversational answer and absence of online search; ask genuine current headlines, weather, time and explicit online search to confirm their routes. Independent next work must test private past-chat retrieval with freshness language and improve model-generated reply fidelity without leaking account data or self-authorizing GitHub writes.
