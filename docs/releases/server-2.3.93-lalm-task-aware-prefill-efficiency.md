# Server 2.3.93 — LALM task-aware intelligence + prefill efficiency

Date: 2026-09-12
Server Runtime: `2.3.92` → `2.3.93`
LALM Engine: `2.1.30` → `2.1.31`
LALM Revision: `2.1.31-hot-task-aware-prefill-efficiency-v21`
Deployment / restart: **NONE**

## Purpose

Advance the runtime-hot §wyrlz LALM without replacing the proven v17 execution core. The event focuses on two high-value boundaries at once: better model-facing reasoning behavior for different classes of user requests, and less recurrent-state checkpoint cloning during prefill/generation.

## What changed

### Task-aware cognitive routing

The active hot wrapper now classifies the immediate request into one of eight compact profiles: social, coding, math/logic, research/factual, analysis, planning, creative, or general. Each profile supplies a concise task-specific execution contract while preserving the common §wyrlz identity, truthfulness, temporal-context, and direct-response rules.

Coding guidance now explicitly prioritizes the actual project/code context, architecture preservation, complete directly applicable code when requested, syntax/control-flow/interface/I/O checks, code/explanation consistency, causal debugging, and minimal correct repairs rather than symptom masking. Math/logic, research, analysis, planning, and creative requests receive similarly targeted compact policies rather than sharing one generic instruction block.

### Adaptive sampling defaults

When the caller has not explicitly selected generation controls, the wrapper now applies task-sensitive temperatures around the Liquid LFM2 family recommendation of approximately `0.3`. Deterministic tasks such as math and coding receive lower temperatures; social and creative requests receive more expressive defaults. Explicit/manual caller generation settings remain authoritative and are not overwritten. The existing v17 repetition penalty remains `1.05`.

### Prefill/checkpoint efficiency

The exact-token v17 continuation system remains intact, but checkpoint clone frequency is reduced:

- progressive prefill checkpoint interval: `32` → `96` tokens;
- live generated-state checkpoint interval: `16` → `32` tokens;
- retained conversation checkpoints per thread: `10` → `6`.

This keeps prefix recovery, terminal assistant checkpoints, and speculative next-turn warmup while reducing repeated deep copies of recurrent convolution/KV state and lowering cache/allocation pressure.

### Preserved architecture

The following proven behavior is intentionally unchanged:

- resident warm R39 model;
- compiled direct-quantized native matvec path when available;
- Python/Numpy fallback;
- token-exact same-thread prefix reuse;
- terminal assistant checkpoint publication;
- speculative next-user boundary warmup;
- detached/background generation and resume;
- adaptive response budgets and semantic completion checks;
- canonical runtime hot-loader boundary;
- Chat and frontend modules.

## Research basis

External implementation guidance was used as supporting evidence, not as a replacement architecture. Liquid AI's LFM2 model documentation recommends a ChatML-style conversation template, `temperature=0.3`, and `repetition_penalty=1.05`; §wyrlz already uses the compatible ChatML framing and existing repetition penalty. vLLM's prefix-caching documentation identifies multi-round shared-prefix reuse as a direct prefill-latency optimization, consistent with §wyrlz's token-exact recurrent checkpoint design. llama.cpp documentation similarly treats prompt caching and resident/memory-mapped model state as standard inference optimizations.

## Version/concurrency evidence

- Event-entry and pre-assignment authorities were re-read from `VERSION.txt`, `versions/server-runtime.txt`, and `versions/lalm-engine.txt`.
- Both checks remained at Server `2.3.92` / LALM `2.1.30`; no concurrent authority advance was detected.
- Runtime deployment risk was checked against the current production workflow. The only automatic push trigger is `main` + `.deploy/REQUEST.txt`; this event mutates only `runtime`, so no deployment action is caused.

## Verification

- New wrapper source was syntax-compiled before publication.
- Published `runtime_hot/r39_engine.py` was re-fetched after commit and contains revision `2.1.31-hot-task-aware-prefill-efficiency-v21`.
- Hot manifest was advanced to the same revision and continues to expose only `r39_engine.py` through the existing single-file loader contract.
- Post-publication version-authority verification is required before final closure.
- Live worker/browser acceptance should confirm the `COGNITIVE_ROUTE` status receipt, hot revision `2.1.31`, and normal response generation after the runtime loader refreshes.

## Relevant lineage

- LALM v21 wrapper: `af48786be065ff378ff6c8e5ed208a77e526cc40`
- Hot manifest: `97fd3d33d2c2dee6e68ccad710c7f2b4a7c2f7c3`
- Server Runtime authority: `7aa48d7b91cfdb6402b2dfcf4386ad015da5bf5b`
- LALM Engine authority: `16b7a256ba104b7a1741631a250047ae991ba980`

## Rollback

Do not silently rewrite this event. If live verification reveals a regression, preserve Server 2.3.93 / LALM 2.1.31 in lineage and publish the correction as the next versioned runtime event. No production deployment or server restart is required for such a runtime-hot correction.
