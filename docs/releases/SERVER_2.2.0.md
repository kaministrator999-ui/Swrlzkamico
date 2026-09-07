# §wyrlz Server 2.2.0

Date: 2026-09-07

## Release intent

Split infrastructure/server operations, LALM/R39 engineering, and Chat UX into independent control planes so model/runtime work no longer requires Chat UI mutation.

## New routes

- `/server/` — Server control/status/router page.
- `/lalm/` — dedicated R39/LALM runtime page.
- `/api/server/status` — non-model-loading server receipt.
- `/api/lalm/status` — non-blocking LALM engine/readiness receipt.
- `POST /api/lalm/verify` — explicit model verification.
- `/api/control/route?client=...` — route decision receipt.
- `/route?client=...` — browser redirect helper.
- `POST /api/control/hot/sync?scope=lalm|server|all` — scoped runtime mutation.

## Hot boundary

`scope=lalm` updates only `web/lalm.html` and `runtime_hot/r39_engine.py` and returns `chatTouched: false`.

`scope=server` updates only `web/server.html`.

The legacy `/api/hot` route remains for compatibility, but ordinary R39 iteration should move to the LALM scope after 2.2.0 is deployed.

## Chat boundary

Chat remains at **1.3.26** for this server release. No Chat version bump is required because the Chat protocol and Chat UX are not changed by the control-plane split.

Future R39/native/prefill/decode work advances the LALM/runtime revision, not the Chat revision, unless Chat behavior itself changes.

## Native inference

2.2.0 preserves the compiled direct-quantized R39 backend introduced in 2.1.18 and the Python/NumPy reference executor as correctness/fallback oracle.

## Deployment note

The new Python routes and native extension require one base Vercel deployment. They are fully staged on `dev` so the eventual server promotion/deploy does not require another architecture edit.

After that deployment, ordinary LALM page/engine updates can be hot-synced independently of Chat.
