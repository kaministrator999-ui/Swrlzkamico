# Server 2.3.166 — R39 v39 telemetry recursion correction

## Trigger
Fresh production acceptance request `web:mu2v03yw:14225086002855917144` on 2026-09-15 reached R39 v38 server-log telemetry but failed before inference completion.

## Evidence
Vercel runtime logs showed:
- `inference-start` under engine 2.1.49 / v38
- `CHAT_GENERATION_STARTED`
- `telemetry-wrapper-exception` with `errorType=RecursionError` at 693 ms
- `inference-end` with `terminalSeen=false`
- canonical assistant terminal persisted as FAILED at account-state revision 132.

The same request proved the new stdout telemetry transport itself was visible in Vercel logs.

## Root cause
v38 executed the complete v37 source into v38's own `globals()`. v37's `generate_events()` resolves its base generator through the global name `_BASE_GENERATE`. After v37 loaded, v38 assigned `_BASE_GENERATE = generate_events` to wrap v37. That assignment changed the global name seen by the already-defined v37 wrapper, making it call itself recursively.

## Correction
R39 v39 loads the pinned v37 source into an isolated `types.ModuleType` namespace and captures `_v37.generate_events` / `_v37.inspect_engine`. v37 therefore retains its own independent globals and its own base-generator alias. v39 wraps those isolated functions without mutating their namespace.

## Authority
- Server Runtime: 2.3.166
- LALM Engine: 2.1.50
- Hot revision: `2.1.50-hot-recursion-safe-server-telemetry-v39`
- Runtime branch only; no production deployment or restart requested.

## Safety / architecture
Telemetry remains observation-only. It logs request correlation, phases, timing, token counts, throughput, batching/fallback counters and terminal lifecycle. It does not log prompt text, history text, generated response text, credentials, cookies, authorization values, or other secret-bearing request fields.

## Acceptance criteria
A fresh Chat turn must show one request-correlated sequence containing `inference-start`, prefill/decode lifecycle, engine metrics when emitted by the underlying adapter, a terminal event/summary, and `inference-end terminalSeen=true`, with no `telemetry-wrapper-exception` or RecursionError. Canonical Chat turn persistence must terminate COMPLETED for a successful inference.
