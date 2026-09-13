# Server Runtime 2.3.99 — Requirement-Driven Planning + RMCCA Transport Trace

## Versions
- Server Runtime: 2.3.98 -> 2.3.99
- LALM Engine: 2.1.35 -> 2.1.36
- LALM revision: `2.1.36-hot-requirement-plan-rmcca-trace-v26`
- Web Chat: 1.4.81 -> 1.4.82
- Runtime page manifest: 19 -> 20

## Why this event exists
The v25 benchmark correctly detected unmet requirements at terminal validation, but the model still spent most of its output budget on prose and never produced the requested runnable Python implementation. The same benchmark also showed the browser context camera still reporting no captured RMCCA envelope/carrier.

## LALM change
`runtime_hot/r39_engine_v26.py` layers over the pinned v25 source and turns the existing requirement ledger into an ordered execution plan before generation:
1. brief architecture explanation,
2. runnable artifact early,
3. example after the artifact,
4. prompt-prefill explanation last.

For coding requests, explicit numeric requirements such as recent-window size and maximum retrieved-older count are repeated inside the artifact phase so the implementation must enforce them rather than merely mention them in prose. The planner explicitly shortens commentary before sacrificing the runnable artifact.

## RMCCA transport change
`web/chat_rmcca_transport_trace_v2.js` is loaded after `chat_background_resume_v2.js` and wraps the final browser stream-fetch boundary. It records envelope/carrier state before and after canonicalization, preparation path, fallback use, serialized body size, and any outer transport error. It also canonicalizes the outgoing request at that final boundary before forwarding it into the existing wrapper chain.

The trace is designed to distinguish whether RMCCA is absent before the final wrapper, lost during canonicalization, or present in the serialized body but later absent from server-side inference receipts.

## Preserved behavior
- v22 batched/vectorized prefill remains untouched.
- v25 semantic committed-output validation remains active.
- Single-visible-generation continuity remains active.
- No `main` changes.
- No deployment request.
- No server restart.

## Verification before publication
- `r39_engine_v26.py` syntax compiled successfully locally.
- `chat_rmcca_transport_trace_v2.js` passed `node --check` locally.
- Version authorities were reread after runtime mutations and remained Server 2.3.98 / LALM 2.1.35 / Web Chat 1.4.81 before assignment.

## Rollback
Rollback is a new versioned event. Restore the previous hot entrypoint/manifest revision and remove the v20 trace script from the active runtime page manifest while retaining these files and this record as lineage.
