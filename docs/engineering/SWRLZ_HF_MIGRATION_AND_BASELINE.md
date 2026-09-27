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

## Active continuation — 2026-09-27: Hugging Face server and R39 speed parity

**User direction:** Continue §wyrlz server development on the EXISTING Hugging Face Space `kamiloki/Swyrlz`, with the original GGUF model retained as an independent selectable control. Hugging Face is the active candidate/inference development target; this does not assert that the Vercel account/persistence authority has already migrated or authorize its retirement. Do not create a replacement Space or Vercel project. Preserve existing Space revision and original Test Bench before publishing.

**Exact comparison:** original `LiquidAI/LFM2-350M-GGUF` / `LFM2-350M-Q4_K_M.gguf` at pinned revision `31cd51db1365` via `llama_cpp.Llama`, versus native §wyrlz R39 physical checkpoint SHA256 `65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee` and accepted v90 chain. These are different model architectures/checkpoints; compare latency and throughput under matched conditions without claiming identical compute cost or quality.

**Deployment owner:** `feature/hf-space-manual-deploy:.github/workflows/manual-hf-space.yml` stages `hf_space/` via `scripts/prepare_hf_space.py`, verifies pinned original source, native kernels and exact R39 transport, snapshots the existing Space, then uploads to `kamiloki/Swyrlz` only in explicitly approved `deploy` mode. `validate` is deployment-inert. A `main` registration-only workflow is NOT the deploy authority. HF uploads rebuild/restart the Space; treat them as deployment-producing. Preserve `/legacy`, `/probe`, and the existing Chat/Station path. No paid hardware or inference endpoint without separate approval.

**Performance diagnosis order:** collect paired live probe JSONs on the same Space/hardware with identical prompts, output budgets, warm state, concurrency and repeat counts. Measure queue/load, tokenization, prompt token count, prefill, first DELTA, decode tokens/s, total latency, CPU/RSS, backend and native/batch availability. Existing observed original short-turn probe: 0.255 s terminal, 0.056 s first DELTA, 31 DELTAs, 128 response characters; this is a single user-supplied observation, NOT a matched R39 benchmark or tokens/s. Reproduce it. Inspect R39 native build/import, batch prefill, Python fallback, per-token Python/NumPy overhead, prompt inflation, camera overhead and streaming buffering. Preserve numerical/token parity and Truth Firewall; never fake speed by shortening responses, bypassing cognition, swapping to stock, or suppressing errors. Optimize the canonical R39 owner, not a cosmetic UI delay. Benchmark each isolated change and revert regressions. Target parity is a goal, not a verified achievement.

**Acceptance:** native and batch available on actual HF runtime; real R39 DELTA and COMPLETED; matched warm/cold and short/long prompt trials, 128 and 2,000 generated-token budgets where supported; report prefill tokens/s, decode tokens/s, TTFT, total time, response quality/correctness and resource usage. Compare baseline → candidate with reproducible logs. Publish only after validation, snapshot, explicit approval and source/revision verification. Distinguish source/static, Space build, runtime, and user-visible truth. Keep this continuation in the Roadmap and reconcile Repository Work/module versions at governed closure.

## R39 native llama.cpp adapter experiment — 2026-09-27

User directs an actual attempt to run **R39's own checkpoint** through llama.cpp, not the stock model as a substitute. Source inspection establishes the R39 reference profile is LFM2-shaped: 16 layers, embedding width 1024, hybrid short-convolution/attention layers, GGML-compatible q4_0/q8_0/q4_k/q6_k tensor block types, and BPE tokenizer. This is a candidate for lossless GGUF packaging with LFM2 architecture metadata; it is NOT yet proven to match the pinned stock LFM2 checkpoint's exact tensor names, dimensions, token IDs, shortconv semantics, or runtime behavior.

Implementation gates:
1. Inspect the exact pinned original GGUF metadata/tensor directory and the reconstructed R39 SWRLZX manifest, graph, tokenizer and tensor directory. Emit a machine-readable compatibility report: architecture keys, tensor name/shape/type, tensor data hash, vocabulary and special IDs, merge order, chat template, and RoPE/convolution settings. Do not assume that matching family name implies compatible layout.
2. Implement an isolated deterministic `SWRLZX -> GGUF` exporter from R39's verified raw SHA256 `65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee`. Preserve original quantized tensor bytes only when their layout and quantizer match GGML exactly; otherwise perform explicit validated conversion. Retain R39 lineage/provenance in GGUF metadata and report resulting artifact SHA256. Never relabel or overwrite the original GGUF.
3. Load the converted R39 GGUF via `llama_cpp.Llama` as a third experimental route `r39_llama`, independent of `stock` and `r39`. Fail closed on unsupported architecture/tensor/tokenizer; no silent fallback to stock. Keep existing routes and user selection unchanged until parity is proven.
4. Run tokenizer encode/decode fixtures, per-layer or final-logit numerical comparisons on deterministic token sequences, greedy token parity, multi-turn and long-context tests, and Truth Firewall/accepted overlay behavior. Distinguish physical model execution from accepted R39 cognitive overlays: llama.cpp replaces only compatible tensor inference, not policy/identity/continuation orchestration.
5. Compare matched hardware and warm/cold state: original stock llama.cpp, existing R39 native, and converted R39 llama.cpp. Measure prompt tokens, prefill tok/s, decode tok/s, first DELTA, total, RSS and CPU at 128 and 2,000 output-token budgets. Do not infer tokens/s from delta count or character count. Require correctness and measurable gain before promoting route to Chat.

**Current state:** compatibility investigation only; no verified R39 GGUF artifact, no llama.cpp R39 runtime result, no production speed-parity claim. Existing HF publish remains explicit-owner-approved after snapshot/validation.

### Implemented read-only compatibility probe

Source: `scripts/inspect_r39_gguf.py` (commit `0cbf8c4f64c4c17799a3542a175ae5ac002e6f10`). Run from the repository root after `python scripts/prepare_hf_space.py` and dependency installation:

```bash
PYTHONPATH=hf_space python scripts/inspect_r39_gguf.py --download-stock --output r39-gguf-compatibility.json
```

It SHA-verifies the canonical R39 artifact, downloads the exact pinned original GGUF revision, reads GGUF metadata and tensor directory, and reports tensor name/shape/quantizer differences, tokenizer ID equality, and LFM2 metadata. It does not export GGUF, modify the live Space, or prove runtime/logit parity. A `DIRECT_LAYOUT_CANDIDATE` result is necessary but not sufficient for lossless conversion. Treat `ADAPTER_REQUIRED` as an explicit mapping task, not permission to silently substitute the original.
