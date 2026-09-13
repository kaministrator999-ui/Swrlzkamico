# Server 2.3.123 / Web Chat 1.5.3 — canonical chat shell

## Scope

Runtime-hot Web Chat visual architecture only. No LALM/server inference contract changes.

## Changes

- Moved the Ice Dragon wallpaper owner from `.messages` to the full `.workspace` so the same artwork sits behind both transcript and composer.
- Made `.messages` transparent.
- Made `.composer-shell` and `.composer-box` translucent blurred glass so the wallpaper remains visible behind the input region.
- Kept the readability fade attached to the full `.message-stack`, covering long/error content instead of only the scroll viewport.
- Increased welcome subtitle contrast over bright wallpaper regions.
- Changed frontend-first boot to default/persist Ice Dragon when no saved preference exists and paint the canonical workspace immediately from the exact repository PNG or the locally cached preview.
- Added `web/themes/ice-dragon/ice-dragon-shell-v1.css` as the final shell override.
- Bumped runtime manifest to v36 for cache invalidation.

## Authorities

- Server runtime: 2.3.123
- Web Chat: 1.5.3
- Manifest: 36

## Verification

Repository writes completed successfully. Browser visual acceptance remains pending user refresh on the live chat. Existing turn-integrity, transcript-continuity, context-capacity, and response-polish scripts were preserved in the manifest.
