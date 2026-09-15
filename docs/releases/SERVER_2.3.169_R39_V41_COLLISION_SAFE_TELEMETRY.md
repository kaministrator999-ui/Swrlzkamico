# Server 2.3.169 — R39 v41 collision-safe telemetry correction

**Status:** source published; live acceptance pending
**Server Runtime:** 2.3.169
**LALM Engine:** 2.1.52
**R39 revision:** 2.1.52-hot-collision-safe-server-telemetry-v41
**Deployment:** NONE
**Restart:** NONE

## Failure lineage preserved

Server 2.3.168 / LALM 2.1.51 attempted to preserve v37 wrapper globals by executing v37 in a registered synthetic module. Production `/api/chat/status` still reported `engineSource=unavailable` and `R39_ENGINE_IMPORT_FAILED` after hot hydration, so 2.3.168 remains a failed correction event.

## Correction

v41 removes the extra synthetic-module import boundary. It loads the pinned v37 source into the normal hot-engine namespace after deterministically renaming only v37's `_BASE_GENERATE` and `_BASE_INSPECT` aliases. The pinned v37 source is required to contain exactly two references to each alias; otherwise loading fails closed with `R39_V37_ALIAS_CONTRACT_CHANGED`.

This prevents the v38 recursion mechanism without changing the inherited module/import environment that older working R39 revisions expect. The server-log telemetry remains observation-only and excludes prompt/history/generated response text and credentials.

## Authority baseline

Immediately before this event:
- `VERSION.txt` SHA `30ffd037ef7f75ed16e8781923e09145718f4ecf`
- Server Runtime `2.3.168`, SHA `95b6e837d3ad834fea48915db12eda368f04533f`
- LALM Engine `2.1.51`, revision `2.1.51-hot-import-safe-server-telemetry-v40`, SHA `98b5718bc118953c8f3a1a6618b688c1e0137bf8`

## Source lineage

- v41 source commit: `1b75ca5c46c1f67f19fb4a4f145722aa13718840`
- hot entrypoint commit: `76bd3b068f0eb8a78820f37ed46ccd58045450e7`
- hot manifest commit: `87a7fa46d77bb13f4d084f388b68fe14af84e796`
- LALM authority commit: `ef4aca55b757b45085718a943deca928c69f522b`
- Server authority commit: `082c3bfc3d7e36605f7346d852b2d31330830813`

## Acceptance

1. Production status resolves `engineSource=runtime-override` and hot revision `2.1.52-hot-collision-safe-server-telemetry-v41`.
2. Fresh Chat request emits `SWRLZ_R39_TELEMETRY inference-start`.
3. No RecursionError or telemetry-wrapper exception.
4. Prefill/decode/first-delta and available engine metrics are observable.
5. Canonical assistant terminal is COMPLETED with non-empty text.
6. Browser/server requestId and message identity remain coherent.
