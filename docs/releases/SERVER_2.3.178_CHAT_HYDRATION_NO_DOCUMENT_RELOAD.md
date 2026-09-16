# Server 2.3.178 — Chat canonical hydration without document reload

## Versions
- Server Runtime: 2.3.178
- Web Chat: 1.5.38
- Runtime page manifest: 106

## Problem
Production Chat could visibly refresh/reboot after account-state hydration. Audit found an explicit `location.reload()` in both compatibility and server-authority hydration paths whenever a newly applied canonical revision differed from the session's previously applied revision. Because the full Chat runtime loader, functional asset chain, Ice Dragon theme, wallpaper, and account synchronization initialize on document boot, this reload presented as a complete Chat/interface refresh.

## Change
`web/chat_account_state_sync_v1.js` advances to account-state sync contract v5. Canonical hydration now writes the authoritative state to the browser cache and emits an in-document hydration/adoption signal. The already-loaded same-tab canonical reconciler observes the cache change and adopts it into the live Mask. No hydration path calls `location.reload()`.

Mutation-result hydration uses the same in-place path. Active request deferral, requestId-first terminal correlation, server authority, diagnostic overlay preservation, and Whole Conversation Camera behavior remain intact.

## Audit findings
- `web/chat.html` has a `storage` event handler that can call `render()` for cross-tab state changes; this is an in-document reconstruction, not document navigation.
- `web/chat_same_tab_canonical_reconcile_v1.js` can call `render(false)` only for visually non-equivalent canonical state; equivalent snapshots are quiet adoptions.
- `web/chat_background_resume_v2.js` listens to `pageshow`, visibility, and online events to resume the same generation, but does not navigate/reload the page.
- `web/chat_boot_guard.js` only reveals the existing booted document and does not reload it.
- The direct document reload discovered in account-state hydration was therefore a concrete root cause for full runtime/theme bootstrap recurrence.

## Lineage
- Account-state sync change: `637ae4112a523e9856daa3f6628904be618d86eb`
- Server Runtime authority: `1368f2fdaabf8313d57b6eeaea7818de8afa61d2`
- Web Chat authority: `984c5f403c26a05b45b4dde1d404b24d710b85b5`
- Manifest 106: `2a840af2698e3a35facf0eb33febbda460cd023e`

## Deployment / restart
NONE. Runtime-hot path only. Git-based Vercel deployment is disabled in the current stable configuration.

## Verification
Repository/source verification complete. Live manifest/source propagation and user-visible behavioral acceptance remain to be checked after runtime propagation. A successful acceptance should show canonical hydration/reconciliation without a new document boot/runtime-loader sequence.