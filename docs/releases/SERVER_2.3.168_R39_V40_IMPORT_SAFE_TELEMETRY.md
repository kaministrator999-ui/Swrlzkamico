# Server 2.3.168 — R39 v40 import-safe telemetry repair

**Status:** source published; live acceptance pending fresh runtime hydration/send
**Server Runtime:** 2.3.168
**LALM Engine:** 2.1.51
**R39 revision:** 2.1.51-hot-import-safe-server-telemetry-v40
**Deployment:** NONE
**Restart:** NONE

## Trigger evidence

Fresh Chat request `web:mu2zfkvx:27966982442496927954` canonically committed USER state at revision 142 and terminal FAILED assistant state at revision 143 with zero response bytes. No `SWRLZ_R39_TELEMETRY` records were emitted for that request.

A direct production `/api/chat/status` receipt then reported `mode=LOCAL_R39`, `engineSource=unavailable`, and blocker `R39_ENGINE_IMPORT_FAILED`. This moves the defect boundary ahead of generation: the v39 hot engine was failing during import, so its `generate_events` telemetry wrapper was never reachable.

## Root-cause correction

R39 v39 isolated v37 in a synthetic `types.ModuleType` to prevent the prior shared-global recursion defect. That synthetic module was executed without first being registered in `sys.modules`. Inherited Python code can resolve module/class metadata through `sys.modules` while source is executing; an unregistered synthetic module therefore creates an import-time compatibility failure before inference starts.

R39 v40 preserves the isolated namespace but registers it in `sys.modules` before executing the pinned v37 source chain. If execution fails, the temporary registration is removed and the exception remains visible. Inference semantics remain v37; the server telemetry wrapper remains observation-only and does not log prompt/history/generated response text or credentials.

## Authority baseline

Immediately before assignment:
- `VERSION.txt` SHA `30ffd037ef7f75ed16e8781923e09145718f4ecf`
- Server Runtime `2.3.167`, SHA `8499343ed685f3c3480f02d44e994292c0efa426`
- LALM Engine `2.1.50`, revision `2.1.50-hot-recursion-safe-server-telemetry-v39`, SHA `a516bd9900f469855cbd387af7f6a61c57fc7756`

No concurrent authority change was observed before assignment.

## Source lineage

- v40 source commit: `5890e74e9dd2b77339d0ac300ebbd07832b84121`
- hot entrypoint commit: `956230ccc7e23c99ac18e1b4aa436de38bc91cd2`
- hot manifest commit: `915e65aaba0b54d1a28255392b77485669933979`
- LALM authority commit: `23f7c40b3b0dfb96eb006c1b3fc3ce00d57dc9fd`
- Server authority commit: `f34dc4d194063131b60dc5a2e13f996d00451e87`

## Acceptance criteria

After runtime hydration:
1. `/api/chat/status` resolves `engineSource=runtime-override` and reports hot revision `2.1.51-hot-import-safe-server-telemetry-v40` rather than `R39_ENGINE_IMPORT_FAILED`.
2. A fresh request emits `SWRLZ_R39_TELEMETRY inference-start` for its requestId.
3. No `telemetry-wrapper-exception` or `RecursionError` occurs.
4. Prefill/decode/first-delta/engine metrics are reported when the inherited engine emits those stages.
5. The canonical assistant terminal is COMPLETED with non-empty response text and a revision increment.
6. RequestId-first browser/server terminal correlation remains coherent.

If any acceptance criterion fails, the failure remains lineage and the next correction receives another Server/LALM version event.
