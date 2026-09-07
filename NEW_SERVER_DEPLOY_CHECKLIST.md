# Server 2.2.0 deploy checklist

## Before deploy

- [x] Server source version advanced to `2.2.0`.
- [x] Chat remains frozen at `1.3.26` for this architecture release.
- [x] Dedicated Server UI added at `/server/`.
- [x] Dedicated LALM UI added at `/lalm/`.
- [x] Scoped LALM hot-sync contract staged.
- [x] Native direct-quantized backend build remains wired through `requirements.txt -> -e . -> setup.py`.
- [x] Release record and control-plane V2 contract added.

## Vercel deployment

- [ ] Promote the prepared Server 2.2.0 source to the deployment branch when quota is available.
- [ ] Deploy/redeploy once.
- [ ] Confirm `/api/health` reports Server `2.2.0`.
- [ ] Open `/server/` and confirm Server UI `1.0.0`.
- [ ] Open `/lalm/` and confirm LALM UI `1.0.0`.
- [ ] Open `/api/chat` and confirm Chat remains `1.3.26`.
- [ ] Confirm `/api/server/status` reports deployment commit/instance/capabilities.
- [ ] Confirm `/api/lalm/status` reports engine source, hot revision, model SHA, and native backend availability without forcing model verification.
- [ ] Run `POST /api/lalm/verify` and confirm R39 verification receipt.
- [ ] Confirm native backend is `AVAILABLE`; if not, inspect the Vercel build log for the editable package/native extension build.

## Scoped hot acceptance

- [ ] Trigger `POST /api/control/hot/sync?scope=lalm&branch=dev`.
- [ ] Confirm response contains `chatTouched: false`.
- [ ] Confirm only `web/lalm.html` and `runtime_hot/r39_engine.py` are listed in the LALM scope receipt.
- [ ] Refresh `/api/chat` and confirm Chat version/source did not change.
- [ ] Refresh `/lalm/` and confirm the LALM/runtime revision can change independently.

## Routing acceptance

- [ ] `/api/control/route?client=chat` -> target `/api/chat`.
- [ ] `/api/control/route?client=lalm` -> target `/lalm/`.
- [ ] `/api/control/route?client=server` -> target `/server/`.
- [ ] `/route?client=chat` redirects to Chat.
- [ ] `/route?client=lalm` redirects to LALM.

Once these pass, routine R39/LALM engineering should use the LALM plane and scoped hot sync rather than changing Chat or redeploying the base server.
