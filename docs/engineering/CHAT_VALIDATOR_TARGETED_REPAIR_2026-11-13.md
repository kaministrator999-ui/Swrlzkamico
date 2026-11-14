# §C validator-directed source repair: generate once, patch, revalidate

2026-11-13 US Central · Existing §C/§E engineering lineage.

## Failure evidence

§C has repeatedly exhausted large coding turns and rejected near-complete HTML when its structural validator identified unclosed HTML/code fences, missing required CSS or JavaScript, or partial JavaScript code. Despite retaining unfinished drafts after the long-code checkpoint release, the prior normal validator retry specifically instructed the model to **return the complete corrected candidate**. This can require reconstructing thousands of unchanged lines and lose working behavior.

## New bounded repair contract

The original candidate is the immutable baseline. Once an actual code deliverable's first candidate reaches a normal model stop but fails the existing deterministic contract gate:

1. Extract the exact validator reasons and a bounded source map (head, tail, structural markers, SHA-256), without resending an entire megabyte-scale project.
2. Ask the same resident Qwen3.5-9B model for **one JSON patch**, not a replacement page. Supported operations: `insert_before`, `insert_after`, `replace_once` of a small region, and `append` for a genuinely unfinished suffix.
3. Require the patch's source SHA to equal the saved candidate. Reject ambiguous anchors, oversized edits, malformed JSON, missing native completion, or attempts to rewrite a large source region.
4. Apply the patch **only in memory**. Preserve the prefix and suffix exactly, re-run `_candidate_structure_check`, `completion_validation` and `enforce_strategy_change`. A still-failing patch must strictly reduce the existing set of deterministic failure reasons without creating new ones; otherwise discard that patch while retaining the preceding candidate.
5. Perform at most two short focused repairs on one coding turn, then either accept the complete, verified candidate or save an **unverified incomplete checkpoint** in the same account-owned thread. Never treat partial or syntactically invalid code as the finished project.
6. On `Continue code`, a structural-repair checkpoint enters targeted repair directly rather than appending unrelated source to a closed HTML document. Ordinary length-terminated checkpoints still continue from their saved ending.
7. Noncoding chat and the existing special external-source planning route retain their previous behavior. Existing GitHub write permissions and §E editor leases remain separate.

## Hard boundaries

- This repairs *candidate completeness and source-shape* according to existing validators. It is not proof a button works in a real browser, that a VR menu lines up, or that a full end-to-end project deploys. Those require actual browser/device tests and authorization.
- Patches are limited to a maximum of 10,000 new characters, a unique anchor at most 2,500 characters, and replacements of at most 1,600 old characters. A candidate draft is capped at 240 KiB for safe account storage.
- The model's 16,384-token context and the 18-thread / 16-core resident CPU allocation remain unchanged.
- Full projects of arbitrary size still need bounded per-file source revisions and tests; no single inference call is unlimited.

## Test evidence

- Read-only source-level preflight and exact-source hash snapshot: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43557259160
- Regression unit tests: 13 tests covering two sequential CSS/JS insertions, literal source preservation, small replacement, append, ambiguous or stale anchors, oversized/corrupt payloads, and strict reduction of validator failures.
- Native fake model test: requires actual `finish_reason=stop`, rejects truncated patch JSON, and confirms no full source regeneration request.
- Production guarded release workflow: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43557350468
- Do not infer production acceptance from a source commit alone. The workflow keeps the exact previous engine for rollback and runs a fresh anonymous normal HTML code smoke test. The real user-reported large HTML failure remains a distinct end-to-end retest requirement.

## Follow-on tests

- Real long code with CSS and JavaScript accidentally omitted, including both missing simultaneously.
- User files with an existing documented design theme; targeted patch must retain class names, actions, and rendering behavior.
- Failed patch JSON and stale fingerprint, multiple possible anchors, regressions after a patch.
- A saved repair checkpoint resumed after another user turn.
- Source files larger than the current single-draft cap: route to independently verified per-file edits, not a speculative larger model window.

**Operational rule:** retain working code, use validation evidence to repair the smallest source region, test after each change, and never demolish an entire project to fix one line.


## Live release and branch-level verification (2026-11-14 UTC)

- First guarded release [run 43557350468](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43557350468) **failed acceptance** after an isolated synthetic conversation returned no terminal receipt. The exact previous coding engine was restored at HF revision `11b41391daae2675cd13aede1c7fbc3227827707`. This failure is retained as part of the lineage, not rewritten as a pass.
- The check was updated to retry a fresh isolated synthetic request if a worker rollout breaks the stream and to read the request-scoped validator and completion receipt from Station sync. This does not mark unknown requests as successful.
- Corrected guarded release [run 43558503907](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43558503907) **passed**, publishing HF coding engine revision `c56c9222cda2955db380da68847c00d11c7c9334`. Live Qwen3.5-9B hardware remained 18 decode/batch threads with 16 CPU quota cores and unchanged 16K context. Live synthetic single-file HTML request delivered **1,094 characters**, terminal **COMPLETE**, request-bound candidate validator **PASS**, and 308 provisional code-delta events.
- Independent read-only branch regression [run 43558666968](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43558666968) executed the **actual source-patched** `generate_events` repair condition using test doubles: a validator-directed CSS insertion preserved the prior HTML and passed; an invalid JSON repair preserved the prior draft as `UNVERIFIED_INCOMPLETE`, without resetting or silently accepting the bad code.
- These results verify the engine behavior and normal small-HTML regression, **not** real-browser functionality or a full reproduction of the user's large HTML/JS failure. Future acceptance should retest that exact project or a representative long code candidate containing simultaneous missing CSS and JS.

## Concurrent UI enhancement

The code preview/final code box scroll-follow is a **separate UI-only release**, [run 43558187512](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43558187512), HF revision `6ac16e5a6869a0b746e9c80b59d1a52e8f7ce263` immediately before the repair deployment. Its source test verified bottom-follow, manual-scroll pause, preserved code viewport state, and unchanged media/file/voice controls. The live served Chat page was checked; phone and Quest touch-scroll acceptance remain user-device tests.
