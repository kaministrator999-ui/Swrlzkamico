# §wyrlz Hugging Face migration and comparison gates

## Scope
GitHub PR #17 stages an isolated candidate; it does **not** retire Vercel or silently replace the existing Hugging Face Gradio bootstrap. The previous Space repository and revision must be snapshotted before any publishing. Existing HF bootstrap is a reference for environment/hardware measurements, not a language-quality comparator.

## Canonical migration map
- Vercel `api/index.py` and `api/lalm_station.py`: authenticated account, queue and persistence owner. **Not portable as-is**; require explicit independent HF session/storage/queue design.
- `accepted_runtime/lalm/r39_engine.py` + accepted overlays: cognitive owner. Candidate stages exact source and historical overlay pins.
- `swyrlz/r39_inference.py` and `swyrlz/backend.py`: model reader and SHA-verified transport reconstruction. Candidate stages exact source; model chunks stay in GitHub and are pinned to source commit.
- `chat/§wyrlz/index.html` and assets: staged as parity references, **not yet served** as canonical Chat.
- Gradio `hf_space/app.py`: isolated real-engine probe only, not a substitute for the account-backed UI.

## Required acceptance gates
1. CI structural checks, syntax, manifest and provenance checks pass.
2. Reconstruct all 54 chunks, verify archive, gzip and raw SWRLZX SHA/size on target runtime.
3. Verify accepted v90 chain loads, `inspect_engine` reports model ready, and a real request yields DELTA and COMPLETED; fail on silent echo/fallback.
4. Preserve old Space revision, README, app, requirements and hardware/SDK before publishing.
5. Verify live latency, tokens/s, CPU, RSS, available/limit RAM, runtime route, model hash, and error/timeout rates.
6. Migrate canonical Chat/account/queue with independent authentication and persistence tests before declaring parity.

## Fixed R39 versus stock reference models
Use the same prompt suite, system instructions, generation budget, temperature/top-p/seed when supported, context length, and hardware class; log mismatches rather than assuming equality. Separate correctness/quality from throughput. Prompt groups: basic instruction following, multi-turn recall, programming with executable tests, mathematics with exact answer checks, long-context retrieval, factual evidence handling, refusal/truth firewall, and streaming/reconnect. Record prompt-set version, exact model revision/hash, tokenizer, runtime backend, quantization, hardware, wall-clock prefill/decode, output tokens, and independent blinded quality judgments. Do not claim a win from an untested fixture. No paid inference endpoint or hardware change without explicit approval.
