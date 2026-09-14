# Server 2.3.144 / Web Chat 1.5.21 — main Chat phased bootstrap

## Scope
Runtime-hot Web Chat startup and legacy browser-history retirement only. No stable deployment, restart, or LALM cognition change.

## Wallpaper Ethics correction
The previous Chat route required the browser to hydrate the full enhancement graph before startup could settle. Manifest revisions also version-busted the entire graph, making mobile startup appear stuck. This event removes that all-or-nothing startup dependency instead of layering another visual workaround over it.

## Changes
- Added `web/chat_runtime_loader_v2.js` as the single manifest-injected startup entry.
- Manifest v53 no longer injects the full CSS/JS graph as parser-blocking route assets.
- Bootstrap v2 starts visual styles concurrently through the same-origin `/live/assets/` contract.
- Main-mask essentials load first and emit `swrlz:main-chat-ready` without waiting for continuity/diagnostic/code helper layers.
- Noncritical runtime helpers load during idle time after main Chat is ready.
- Background helper failures remain diagnostics and no longer convert an otherwise usable Chat into a page-load failure.
- `web/chat_legacy_state_retirement.js` advanced to v2 and removes obsolete browser conversation state from:
  - `swrlz.vercel.chat.v1`
  - `swrlz.vercel.chat.v2.migrated`
  - every `swrlz.vercel.chat.v2.account.*` key
- The retirement gate reloads at most once when old Chat state was actually removed.
- Authentication/session tokens, Google profile preferences, theme preferences, and other non-conversation settings are not deleted.

## Architecture
Mask/Human/Brain ownership is unchanged. Chat remains presentation/factual relay, Server remains authority/execution, and LALM 2.1.44 remains cognition authority.

## Authorities
- Server Runtime: 2.3.144
- Web Chat: 1.5.21
- LALM Engine: 2.1.44 (unchanged)
- Runtime manifest: 53

## Verification
Repository writes completed. Live runtime verification is required before visual acceptance; user-device visual acceptance remains authoritative for the final UI result.
