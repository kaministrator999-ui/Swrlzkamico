# §C long HTML/code output exhaustion — resumable checkpoint repair

Date: 2026-11-13 US Central (verification 2026-11-14 UTC).
Source of truth: live Hugging Face Space `kamiloki/Swyrlz`.
Production revision retained: `266404be909890b2dd421c0a980190dcc61b4662`.

## Reported failure

A real §C coding session upgrading an existing fully featured page exhausted three attempts (activity approximately 8:50 PM to 9:14 PM), producing `OUTPUT_TOKEN_LIMIT` with rejected incomplete HTML/CSS/JavaScript, unclosed code fence and unfinished HTML document. Repeating a full candidate after a length limit wasted substantial CPU time. The user wants total project work unbounded by a single model response, while preserving all existing features.

## Root causes confirmed against production source

- Native model context: **16,384 tokens**, which includes current input and reserved output; cannot be made arbitrarily large without memory/performance changes.
- Prior automatic same-request continuation: `max_segments=4` and **only** a classified existing-project task; new code/artifact requests could still be rejected and regenerated.
- After a length-terminated attempt, the guarded generation path could regenerate a complete candidate twice more; at the end the backend raised `OUTPUT_TOKEN_LIMIT`, dropping the partial preview rather than retaining it as a source work item.
- The prior `source_sized_budget` still has a **16,384-token complete-source output ceiling**. A long-term solution requires file-level edit/merge, not an arbitrarily increased native `n_ctx`.

## Delivered guarded fix

- HF source files modified: `qwen_coder_engine.py`, `station.py`; exact previous bytes backed up as an Actions artifact and source-hash verified.
- Coding output, both new and existing, now supports up to **eight segments per attempt**; each extension is bounded to at most 4,096 tokens and the resident 16K KV window remains unchanged. A nine-minute boundary stops the next segment without interrupting native token decode.
- A length-stopped draft is saved as a **same-thread, unverified source checkpoint** (`pendingCodeGeneration`), SHA-256 bound to the exact source and its original coding intent. No unfinished source is promoted to `codeArtifacts`.
- Code reaching the segment/time budget no longer triggers two more from-scratch full-page regeneration attempts. The user-visible response explicitly says the source is incomplete and how to resume.
- The accepted user command `Continue code` (or `Resume code`) retrieves the matching same-thread saved draft; the model continues only from the retained suffix and appends it to the prior code.
- Resume requires a validated saved hash and the same imported artifact version, if bound. No arbitrary browser-provided continuation payload is trusted.
- Existing final validation must pass before the assembled source is displayed as accepted final code. The checkpoint clears only on a matching successful completion. Missing/invalid/stale/oversized drafts are refused, not promoted.
- Native §E editor lease permissions, GitHub write scopes, model weights, 16-core quota, 18 inference threads, and 16K context remain unchanged.

## Evidence

1. Read-only source and deterministic streaming preflight: [run 43552324252](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43552324252): eight length-terminated segments, seeded suffix continuation, native stop requirement, no partial acceptance, Python AST and unchanged integration guards all passed.
2. First guarded release: [run 43552412292](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43552412292): produced complete small HTML, but the smoke harness mistakenly read only the client SSE stream for a validation receipt instead of the request-scoped Station sync state. This was treated as an unverified deployment and rolled back to exact prior bytes.
3. Corrected guarded release: [run 43552667654](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43552667654): passed. Live real coding smoke: complete HTML, 992 characters, 992 draft characters, terminal COMPLETE, candidate validation `PASS`, correct request ID. Production revision retained `266404be909890b2dd421c0a980190dcc61b4662`.
4. Independent read-only Station branch regression: [run 43552921419](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43552921419): passed account-thread checkpoint storage, wrong-hash/oversize denial, exact-source-only clearing, explicit resume command binding, and no accidental code artifact promotion. This uses synthetic source data against the exact live Python AST, without reading the user's thread.

## Strict verification limits

- Native full-code `OUTPUT_TOKEN_LIMIT` and cross-turn resumes have been **simulated with deterministic model and Station source tests**. The live smoke used a short code request that finished without triggering the limit. It does not prove the user's original long HTML thread has completed. That requires user testing or a specific live long-input acceptance run.
- Per-checkpoint source is currently capped at **240 KiB**, to prevent account-chat storage exhaustion. Eight segments is the *per-attempt* ceiling; multiple explicit `Continue code` turns can extend work, but there is no promise that any arbitrarily large single source file can be assembled in the current storage schema.
- The user requests zero arbitrary total *project* ceiling. The next independent milestone is **changed-file/patch delivery with revision CAS**, not huge repeated full-file outputs; save and validate complete individual files or changed hunks, preserve unchanged files, and assemble the complete download from versioned source files.
- Do not claim runtime/browser/device/behavioral tests passed based only on syntactic validation. Retest §C on the user's exact source and preserve failure evidence, especially missing CSS/JS, fence and HTML closure.

## User test

Refresh the §C tab and retry the original long HTML improvement in the same thread. If the current turn reaches its safe generation boundary, the response should say the incomplete draft was preserved. Send `Continue code` in that same thread. The verified final code should only appear once the candidate passes its full validation gate.
