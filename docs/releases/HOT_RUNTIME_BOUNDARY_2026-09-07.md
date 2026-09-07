# R39 Hot Runtime Boundary — 2026-09-07

Status: active on non-deploying `dev`.

Production server remains the stable Vercel boundary. R39 performance/tuning work is now owned by `runtime_hot/r39_engine.py` and is intended to reach the running server through `/api/hot/sync?branch=dev` without promoting `main` or redeploying Vercel.

## Boundary

Stable server owns:
- FastAPI routing and mount topology;
- authentication/session/security contracts;
- hot-loader contract and bundled fallback;
- NDJSON stream contract / Truth Firewall;
- deployment configuration.

Hot R39 runtime owns:
- bounded matvec/dequant batch policy;
- small decoded tensor caching;
- local prompt/prefill policy;
- runtime profiling/tuning knobs;
- future inference experiments that can be expressed through the stable R39 executor ABI.

The bundled `swyrlz/r39_inference.py` remains the correctness/reference fallback. The hot engine patches the stable ABI at runtime and exposes `HOT_REVISION` in model inspection receipts.

## Flow

`edit dev/runtime_hot/r39_engine.py -> POST /api/hot/sync?branch=dev -> invalidate hot engine -> next LOCAL_R39 request uses new runtime`

No Vercel redeploy is required for this class of tuning.

A server redeploy is required only when the change crosses below the hot-runtime contract (routing, auth, loader, middleware, deployment config, or an executor ABI change that the hot file cannot express safely).

Current hot revision: `2.1.16-hot-boundary-v2`.
