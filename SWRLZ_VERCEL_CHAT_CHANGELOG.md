# SWRLZ Vercel Chat Changelog

## Unified SERVER 2.1.4 / Chat 1.3.0 — 2026-09-07

Added:
- canonical SWRLZX v1 header/TOC parser for active physical section locations;
- tokenizer, tensor-directory, and tensor-data payload reconstruction;
- tensor routing through declared `dataSectionId` values with range validation;
- local R39 Python/NumPy reference executor for the supplied LFM2 profile;
- BPE tokenization and incremental UTF-8 decoding;
- recurrent short-convolution and GQA/KV state execution;
- `f32`, `f16`, `bf16`, `q4_0`, `q8_0`, `q4_k`, and `q6_k` tensor readers;
- bounded generation controls and local cancellation checks;
- local `LOCAL_R39` stream route when no upstream URL is configured;
- Gate 5 engine probe that distinguishes physical payload reconstruction from executable one-token readiness;
- source verifier `scripts/verify_r39_inference.py`.

Preserved:
- proof-bound upstream stream/cancel mode and upstream contract validation;
- browser/Admin auth separation and runtime Chat-token override;
- Truth Firewall: only `DELTA.text` becomes assistant prose;
- 2.1.3 Admin/Live Web/control-plane implementation, preserved in `api/server_v213.py` and wrapped by the 2.1.4 release entrypoint;
- R39 Forge transport, exact SHA/size checks, snapshots, activity receipts, capability/release state, and deployment suppression on `dev`.

Truth boundary:
- source-level local inference wiring is complete and verified against the R299 SERVER architecture contracts;
- the executor fails closed on unsupported graph/tensor/profile/quantizer/layout states;
- source verification does **not** claim Vercel latency or live completion within platform limits;
- production readiness requires deployment receipts plus a successful streamed local R39 request.

## Unified SERVER 2.1.3 / Chat 1.2.0 — 2026-09-06

Added paired Chat/Admin control planes: evidence drawers, retry/fork/context diagnostics, stream camera and generation controls on Chat; runtime Chat-token management, Live Web manager, capability/health/release state, snapshots/rollback, activity receipts, and promote manifests on Admin.

## Unified SERVER 2.1.0 / Chat 1.0.0 — 2026-09-06

Checkpoint: `INT-VERCEL-CHAT-001A`  
Baseline: SERVER 2.0.7 at `0375f42f57d1e4df000a53a6ec02659bb7a6a5df`

Initial additive `/api/chat` integration added the R299-derived responsive UI, browser-local threads, V2 NDJSON streaming contract, independent Chat token, proof-bound upstream bridge, Gate 5 verification, Admin Chat entrypoint, contract/checkpoint documentation, and fail-closed local status-only behavior while inference payload locations were still unresolved.
