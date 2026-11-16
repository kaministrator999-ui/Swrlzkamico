# §C HTML coding reliability — verified engineering handoff (2026-11-15)

## Accepted production improvement — later update, November 15 local time

The original failure/rollback analysis below remains an accurate historical record, **not the current production disposition**. A newer, tightly scoped production fix passed complete acceptance.

- **Release:** `scripts/hf_small_html_source_assembler_v1.py`, published to the existing Hugging Face Space at revision `2281c964f39e27d4e1397b92148f2987bf2e3b55`. [Guarded release run 43781409876](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43781409876) **PASSED**, with the rollback step skipped.
- **Mechanism:** For an explicitly small, new, standalone HTML page only, §C generates a bounded, SHA-checked body edit against an existing complete minimal HTML shell. Host source-assembly restores the full file; normal structural validation and safety checks remain mandatory. If a patch cannot be validated, the existing full-generation path takes over. Larger projects, imported sources, subsequent conversation edits, and non-HTML work retain the original path.
- **Live release gates:** Anonymous API generation + actual Chromium button click, anonymous mobile Chat generation + actual Chromium button click, and independent imported-source Reset-button revision + Change/Reset/Change interaction all **PASSED**. The API release sample took 127.6s and the mobile release sample 69.4s, indicating that the fallback route still occurs in some cases.
- **Independent repeatability:** [Mobile repeat run 43782208202](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43782208202) **PASSED** twice. Both runs used the assembled HTML marker and generated functional pages in **37.5s** and **40.6s**. The earlier warmed UI baseline was **121.6s**, equivalent to approximately 68% lower latency for these two samples; do not infer a global guarantee.
- **Regression scope:** 15 preflight source/eligibility tests passed. `scripts/test_guest_html_first_turn.py` executes the generated page inside a network-isolated Chromium context, testing real DOM modification. The existing imported-source revision test separately passed with a working Reset button.
- **Remaining validation:** End-to-end new-page-then-Reset revision in the **same** anonymous thread should be treated separately from the imported-source regression. [Two-turn workflow](https://github.com/kaministrator999-ui/Swrlzkamico/actions/workflows/chat-html-two-turn-final-acceptance.yml) tracks that case. Full §C coding reliability across larger HTML, CSS, JS, app generation and regressions remains out of scope of this limited release.


## Current production disposition

No experimental HTML speed, prompt compression, targeted feature-patch, or
feature-vs-repair classifier change from this round is accepted in production.
Each attempted publication was revision-guarded and **rolled back** after failing
the guest-only end-to-end test. The prior deployed code remains the baseline.
This is a closed test cycle, **not** a claim that HTML coding is fixed.

The main remaining failure is complete HTML generation and follow-up revision
latency/quality on the resident `qwen3.5-9b` coder. Do not confuse a model
timeout with an invalid source artifact, or static validation with browser
execution.

## Verified evidence

| Investigation | Result | Source |
|---|---|---|
| Guest reload after refresh | Two independent 2/2-turn PASS runs | [43756286435](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43756286435), [43758952683](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43758952683) |
| Python explanation without code | Warmed-runtime PASS (~37s), not a universal instruction guarantee | [43758376930](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43758376930) |
| Original small HTML page | One page passed structural checks (~98s); button behavior not independently executed in that run | [43756836045](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43756836045) |
| Actual HTML button verifier | Offline synthetic Change/Reset/Change browser interactions all PASS; external requests blocked | [43771932912](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43771932912) |
| Compact instruction profile | 17 static tests PASS; no first live answer within deadline, reverted to prior coder source | [43771654929](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43771654929) |
| SHA-checked feature patch first | 12 static tests and host SHA self-test PASS; initial HTML answered in ~100s but revision timed out. Reverted | [43773073771](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43773073771) |
| Additive feature vs repair routing | **Reproduced bug:** “keep the page and add Reset” wrongly set `canonicalCarry=true`. Patched classifier passed 9 real-function fixtures. Initial live HTML test failed to finish, and guard reverted the Brain change | [43776584258](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43776584258), [43776659949](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43776659949) |

### Exact last rollback receipt

In run `43776659949` the Brain classifier patch was published
(`04fb31dc967f5492253d994a7f560d469a92aa4f` → `ef403aa9529d53d47074fe8bbdd59fac73d68cc0`).
The guest test returned `BLOCKED`, `turns=0`,
`TimeoutError: No committed reply within the per-turn deadline`.
Rollback succeeded:
`ef403aa9529d53d47074fe8bbdd59fac73d68cc0` →
`a19558c0b9e69e73840e1a11f9632a4a08bcbe6f`.
The rollback source was the exact pre-change `brain_programming.py`.

## Source-owned findings

The authoritative installed modules, not older GitHub copies, determine routing.
`brain_programming.py` can conflate an affirmative requirement to preserve an
existing HTML page with a repair/correction via `canonicalCarry`, which sends
the second turn to the heavier repair context path. The positive-edit classifier
candidate is staged as `scripts/hf_html_feature_routing_fix_v1.py`; its unit
checks passed, but end-to-end acceptance did **not**.

`qwen_coder_engine.py` has a large full-page output reservation, guarded
source validation, a resumable code draft, and `_swrlz_code_candidate_preview`.
The decode loop checks source closure after each model segment, not every
individual streamed chunk. Coding tasks can continue producing unrequested CSS
or behavior and exhaust time before a completed result. The model can also
stall before its first committed response.

`project_code_targeted_repair_v1.py` already includes strict source SHA,
unique-anchor and single-operation patch safety. This mechanism can be reused,
but the model path must first be proven on a **pre-seeded existing HTML source**.
A fresh two-turn test can time out on the initial page before it tests the
feature-edit path. Do not interpret that as proof the patch fast path failed.

## Implementation next steps (not yet verified or deployed)

1. Establish a deterministic model-worker revision/ready receipt (not merely
   `ready=true`) before sending evaluation prompts. Recheck HTTP reachability
   and Station generation status independently.
2. Add a **seeded-source single-turn test** through the existing
   `projectFiles` import and current guest session, using synthetic HTML only,
   to isolate an additive feature revision from full-page creation latency.
3. Confirm the exact `changeClass`, `canonicalCarry`, `repairTurn`, context
   tokens, output tier, and patch eligibility from Station before decoding.
   Keep traces free of account names, cookies, hidden reasoning and user files.
4. If the seeded feature path works, validate its returned full source with
   `scripts/test_guest_html_functionality.py` (Change, Reset, repeat Change),
   and test no unrelated styles/handlers were deleted. Use exact source
   fingerprint checks, no speculative UI, and fail closed on ambiguity.
5. Independently benchmark when a single HTML file is parser-complete during
   streaming. Early parser-aware stopping needs accurate finish-reason
   provenance and must still pass the deterministic candidate gate; never
   mark an unfinished or rejected code draft complete.
6. Deploy only after a complete two-turn guest test plus interactive browser
   validation passes twice. Continue preserving exact HF before-bytes,
   active revision, and guarded rollback.

## Non-goals

No changes to Vercel, auth/login policy, user or account history, model weights,
or other §E systems. No unverified code execution claims. All tests are
synthetic guest conversations.
