# Server 2.3.153 — Chat message receipt post-redirect ownership

## Scope

Correct the private Chat message receipt so it is emitted at the mounted Chat action owner that handles the request after `/api/chat` redirects to `/api/chat/`.

## Baseline

- Server authority at event entry: `2.3.152` (`runtime/versions/server-runtime.txt`).
- Web Chat authority: `1.5.26`; unchanged by this stable server diagnostics event.
- Production evidence before the event showed `POST /api/chat -> 307 -> POST /api/chat/ -> 200` while no `SWRLZ_CHAT_MESSAGE` receipt appeared.
- Vercel Git deployment is disabled. The production deployment workflow runs on explicit workflow dispatch or a `main` push changing `.deploy/REQUEST.txt`; neither was triggered by the code commits in this event.

## Change

- Added `api/chat_message_receipt.py`.
- Installed the receipt hook from `api/index.py`.
- The hook wraps the mounted Chat `_post_action` owner, after Vercel/FastAPI mount routing has resolved the trailing-slash request and before generation begins.
- The existing authenticated Chat-ingress check remains required.
- Receipt records retain the existing structured fields and add `receiptBoundary=MOUNTED_CHAT_POST_ACTION`.
- Ordinary runtime logs remain private operational diagnostics; this event does not create a public prompt-log endpoint.

## Lineage

- New receipt module commit: `1f8a2d48a516e846eb11118c3f0e1e1f1ef435d4`
- Stable entrypoint install commit: `710c1d74d0416377f2500ab927f7fb1c3542d1bc`
- Runtime Server authority event commit: `44298f335e7d43b7203789b144f7121f7851b26d`
- Server version: `2.3.153`

## Deployment state

**Not deployed.** No `.deploy/REQUEST.txt` mutation and no explicit Vercel deploy action was performed. Applying this stable API/diagnostics change to production requires an approved production deployment.

## Verification state

Repository wiring is complete. Live verification is pending production deployment. Required live proof after deployment:

1. Send a new authenticated Chat message.
2. Confirm `/api/chat -> /api/chat/` may still redirect normally.
3. Confirm one `SWRLZ_CHAT_MESSAGE` record appears with `receiptBoundary=MOUNTED_CHAT_POST_ACTION` and the expected request/thread/message metadata.
4. Confirm generation still starts and completes normally.
