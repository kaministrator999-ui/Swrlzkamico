# Server 2.3.158 — Phase 2A server-owned Chat state

**Overall Server:** 2.3.158  
**Web Chat:** 1.5.28  
**Web Frontend:** 1.0.4 unchanged  
**Runtime manifest:** 96  
**Stable deployment:** pending explicit/manual action

Phase 2A removes signed-in browser message snapshots from canonical ownership once the stable mutation API is deployed. The runtime sync is compatibility-gated until then.

## Runtime behavior

- Pre-Phase-2A stable API: retain compatibility merge/PUT behavior.
- Phase-2A stable API detected: remote state hydrates the browser cache; browser message/stream saves no longer upload canonical snapshots.
- Thread create/rename/pin, deletion, selection, and message bookmark changes are translated to narrow server mutations.
- Hydration defers during an active local assistant stream.
- Generation request identity attachment remains intact.

## Stable ownership contract prepared on main

- `swrlz-chat-account-mutation-v1`
- server state authority
- whole-snapshot PUT retired after deployment
- deletion tombstones preserved across canonical turn commits

## Lineage

- main `1f3db794ca5ebda4ac07b6357c9901e12807ff9d`
- main `ae39d874e9ac0e15a9bf46e6b33416bea9940df5`
- runtime `7cfd9569e120f4a9d1e98069a2457acdf3795403`
- runtime manifest `7e2ddb3ad71a1039b97ab635295c4a65dda9e817`
- Server authority `87bb91cab20dcb090706866bfac5d0acc28dce14`
- Web Chat authority `a8dd70681e5e47f8f60ce3b74deab98473bb6c8f`

No deployment or restart was performed by this event.
