# Server 2.3.118 / Web Chat 1.5.1 — Ice Dragon UI polish

Date: 2026-09-13

## Scope

UI-only Ice Dragon theme polish. No LALM, transcript, routing, or wallpaper-source behavior changed.

## Changes

- Moved the dark readability fade from `.messages::after` to `.message-stack::before`, so the fade spans the full rendered message content height, including long error notices, instead of ending at the scroll viewport boundary.
- Made `.composer-shell` and `.composer-box` translucent blurred glass instead of an opaque dark slab.
- Increased `.welcome h2` and `.welcome p` contrast so the copy over bright wallpaper regions remains readable.
- Added a blurred translucent error-notice surface for legibility over the wallpaper.
- Bumped runtime manifest from 33 to 34 so cached theme CSS is refreshed.

## Versions

- Server Runtime: 2.3.118
- Web Chat: 1.5.1
- Runtime manifest: 34
- Ice Dragon wallpaper controller remains v21.

## Verification

Source-level changes are committed on `runtime`. Browser visual acceptance remains pending user refresh/screenshots.

## Deployment

Runtime-hot update; no server redeploy required by this event.
