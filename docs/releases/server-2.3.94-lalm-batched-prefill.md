# Server 2.3.94 — LALM batched/vectorized prefill + performance telemetry

Date: 2026-09-12
Server Runtime: `2.3.93` → `2.3.94`
LALM Engine: `2.1.31` → `2.1.32`
LALM Revision: `2.1.32-hot-batched-prefill-rmcca-v22`
Deployment / restart: **NONE**

## Purpose

Move the expensive uncached R39 prompt path from token-at-a-time execution toward checkpoint-aligned vectorized blocks without disturbing the proven exact-context, response, and decode contracts. The same event adds instrumentation that separates prompt-prefill cost from decode cost so future optimization is benchmark-driven.

## What changed

### Batched/vectorized prefill

A runtime-owned `runtime_hot/r39_batch_prefill.py` adapter was derived from the repository's existing vectorized prefill implementation. It executes prompt blocks with matrix-matrix projections, vectorized RMSNorm and RoPE, block-causal grouped-query attention, and batched feed-forward operations.

The active v22 hot wrapper pins the adapter to commit `569332d9573ffb1c05cce229a56d3adee6c0c704`, downloads/caches it beside the single-file hot engine when needed, and installs it into the v17 execution core. This is necessary because the stable deployed hot loader intentionally hydrates only `runtime_hot/r39_engine.py`.

### Checkpoint-aligned safety model

- Batched prefill block size: `96` tokens.
- Progressive prefill checkpoint interval remains `96` tokens.
- Decode remains single-token.
- Exact prefix reuse, terminal assistant checkpoints, speculative next-turn warmup, background generation, and semantic completion logic remain intact.
- Each vectorized block executes against a cloned shadow recurrent state.
- The real recurrent state is replaced only after the full vectorized block succeeds.
- Any vectorized failure falls back to the original serial `_forward_hot` path using the untouched real state.

This avoids publishing a checkpoint from a partially processed block and makes the acceleration path fail-safe rather than correctness-critical.

### Memory policy

Native direct-quantized `matmat` is preferred when the compiled batch extension is available. Dense float32 materialization is a bounded fallback only:

- dense cache budget: 128 MiB;
- max single dense item: 32 MiB;
- dense materialization requires at least 32 buffered tokens.

This intentionally differs from the older 384 MiB experimental dense-cache setting because the production worker must already hold the R39 model, recurrent/KV state, and existing decoded caches.

### Performance telemetry

Each completed generation now emits a `PERF_METRICS` status receipt containing:

- first-token latency / TTFT;
- reused cached tokens;
- uncached prompt-token count;
- total prefill seconds;
- uncached prefill tokens/sec;
- tokens and block count processed by the batch path;
- serial-prefill fallback token count;
- batch fallback count and latest fallback reason when applicable;
- decode model-step token count;
- decode compute seconds;
- decode-compute tokens/sec.

This separates prefill throughput from decode throughput so future work can identify the actual bottleneck instead of treating all latency as one number.

### RMCCA remains canonical cognition

No additional intent/router stack was introduced. v22 retains v21's rule:

`RMCCA cognitive envelope → canonical task profile → execution policy`

The server regex classifier remains only a fallback for non-Chat callers or degraded/missing RMCCA envelopes.

## Deployment boundary

Current production workflow inspection still shows deployment occurring only through explicit workflow dispatch or a `main` push touching `.deploy/REQUEST.txt`. This event changes only the `runtime` branch. Deployment and restart are therefore `NONE`.

## Version/concurrency evidence

Immediately before assignment, authorities were re-read and remained:

- Server Runtime `2.3.93`, SHA `05b59bee142fb50b1dafc6fed77d03f9605bc60a`;
- LALM Engine `2.1.31`, SHA `6d632ed8d021ef45b083ecf031a03ff4909d035c`.

No concurrent authority advance was observed. The event then advanced them to Server `2.3.94` and LALM `2.1.32`.

## Verification state

Repository/source verification completed:

- vectorized helper is durable on `runtime`;
- v22 wrapper pins the exact helper commit;
- hot manifest revision matches `2.1.32-hot-batched-prefill-rmcca-v22`;
- Server Runtime and LALM Engine authorities were advanced from fresh baseline SHAs;
- no `main` deployment-trigger file was changed.

Live acceptance remains the next measurement step. A real Chat request should confirm hot revision `2.1.32`, a `COGNITIVE_ROUTE` receipt, and a terminal `PERF_METRICS` receipt. The first useful comparison is a cold/uncached prompt large enough to exercise at least one 96-token vectorized block, followed by a same-thread request to measure exact-prefix reuse.

## Relevant lineage

- Batched prefill adapter: `569332d9573ffb1c05cce229a56d3adee6c0c704`
- v22 hot engine: `5c59eac61256bc76b9eca6e33843ff7d4911877e`
- Hot manifest: `01e3281e3d9ad5d3722f48b4ff5893f1ec5c0ff8`
- Server Runtime authority: `1681ef9b349dffa676019ea0c7d40c50af57caad`
- LALM Engine authority: `a9b47f358cbf9d332133679ac2fbfd0d303148c4`

## Rollback

Preserve Server `2.3.94` / LALM `2.1.32` as historical lineage. Any live regression should be corrected in the next versioned runtime event. The batch adapter is explicitly fail-safe to serial prefill; a correction does not require a Vercel deployment or process restart.
