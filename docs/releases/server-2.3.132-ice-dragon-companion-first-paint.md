# Server 2.3.132 — Ice Dragon companion first-paint stabilization

## Authorities

- Server Runtime: `2.3.132`
- Web Chat: `1.5.10`
- Runtime manifest: `43`
- Source branch: `runtime`

## User-visible goal

Keep the assistant companion permanently beside the §wyrlz name/time plate, use the user-supplied blue/white Ice Dragon artwork instead of the green emoji/legacy companion, and remove the stale pre-layout flash seen briefly on refresh.

## Changes

- Added `web/themes/ice-dragon/assets/companion-kami-128.jpg`, a 128×128 display derivative of the user-supplied square Ice Dragon companion image. It is used only for the small UI avatar surface; the full source artwork remains user-provided input.
- `ice-dragon-response-layout-v1.css` now owns a deterministic raw-GitHub companion URL and reapplies `background-image` after later theme CSS, preventing a later `background` shorthand from erasing the avatar.
- The green dragon emoji fallback is retired from the assistant identity surface.
- `ice-dragon-art-loader-v17.js` no longer asynchronously reconstructs/repaints a competing companion image. It retains legacy wallpaper cleanup and compatibility API behavior while companion ownership is static CSS.
- `chat_response_layout_v1.js` marks the normalized assistant layout ready after its first structural pass. Ice Dragon assistant rows remain hidden only during that tiny normalization window, preventing refresh from visibly showing the old avatar-above-name arrangement before the forum plate is formed.
- Existing `Activity log → companion/name/time → response` composition is preserved.

## Root cause

Two independent transitions were visible. First, assistant DOM normalization happened after the base Chat markup could paint, creating a short stale-layout flash on refresh. Second, the companion had multiple owners: the async art hydrator/cached legacy preview and later CSS shorthand could replace or clear the image after it appeared. This produced the observed repeated load/disappear behavior and exposed the emoji fallback.

## Concurrency reconciliation

The event baseline initially observed Server `2.3.130` / Web Chat `1.5.9`. Before version assignment, the authoritative files were re-read and Server had advanced independently to `2.3.131` while Web Chat remained `1.5.9`. This event therefore reconciled from the new authority and assigned Server `2.3.132` / Web Chat `1.5.10` rather than overwriting the concurrent Server event.

## Deployment / restart

- Vercel deployment: **NONE**.
- Server restart: **NONE**.
- Current `vercel.json` has Git deployment disabled and the affected files are runtime-owned hot assets.

## Verification

- Repository binary asset creation succeeded and was attached to the `runtime` branch.
- Version and manifest authorities were updated using fresh SHAs.
- Manifest 43 was published for cache/source revision invalidation.
- Live/browser visual acceptance remains to be confirmed by mobile refresh screenshot after propagation.
