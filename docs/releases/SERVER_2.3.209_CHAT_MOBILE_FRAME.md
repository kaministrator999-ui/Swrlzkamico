# §wyrlz Server 2.3.209 — Chat mobile frame authority

Date: 2026-09-17

## Versions

- Overall Server Runtime: 2.3.209
- Web Chat: 1.5.58
- Google Account Architecture: unchanged at 1.0.8

## Event

Improved the runtime-owned Web Chat mobile frame without changing the stable authentication boundary. The runtime viewport stylesheet now treats the Android visual viewport as the outer Chat frame and places consistent gutters on Chat content rather than subtracting width from the workspace itself. This removes the prior nested workspace/message/composer width reductions that could produce asymmetric left/right framing.

The same runtime authority now provides the Ice Dragon visual hierarchy requested for Chat: bright ice-white primary content, muted steel-blue secondary/metadata text, and cyan interactive icons/actions with clearer hover/focus treatment.

The signed-in Google profile-photo behavior remains owned by the existing runtime account identity module and continues to use safe Google display claims; Google OAuth boot order and stable token/session verification were intentionally unchanged.

## Source lineage

- Runtime baseline before event: `630a54b39faf75201b892cf5d506682a4256e918`
- Chat frame/style change: `bf4643b71c00e51432fcd50c50ad88276e83c7c8`
- Server version authority: `4131ba476fd7dfd69548a080e5cf9b66537728f5`
- Web Chat version authority: `5960e7c6fe9e7d9dc2079c3da20243d157cce7e7`

## Deployment state

Runtime Chat changes use the established runtime-hot path and require no explicit Vercel deployment or server restart. The user explicitly approved this main-branch release-record commit even if the connected Vercel Git integration automatically creates a deployment from it. No manual `Deploy to Production` action is part of this event.

## Verification state

Repository source and canonical version authorities were re-read around the event and advanced from Server 2.3.208 / Web Chat 1.5.57 to Server 2.3.209 / Web Chat 1.5.58. Production visual acceptance remains pending a fresh mobile Chat reload/screenshot; source correctness is not treated as proof of rendered acceptance.
