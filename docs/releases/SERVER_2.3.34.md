# Server v2.3.34 — Mobile Header Fit + Faster First Paint

Date: 2026-09-11

## Module state

- Server Runtime: v2.3.34
- Web Chat: v1.4.29
- LALM Engine: v2.1.23 (unchanged)
- LALM UI: unchanged
- Stream contract: unchanged
- Google Account architecture: unchanged

## Why this release exists

User browser evidence showed that the narrow mobile top bar still clipped the right-side controls, and the Chat boot path was still intentionally hiding the entire document until the account dock had been mounted. The live runtime manifest also still requested an older responsive-polish stylesheet even though those rules had already been consolidated into the active mobile viewport correction layer.

## Chat presentation changes

- Narrow mobile widths now hide the compact status pill from the top bar so the theme selector, camera, settings, title, and menu can fit without cutting off the right edge.
- The mobile theme selector is reduced slightly at very narrow widths and top-bar spacing is tightened.
- Existing LALM status remains available from the sidebar, so removing the duplicate top-bar status indicator on narrow phones does not remove status access.
- Existing Ice Dragon styling, camera behavior, sidebar behavior, composer geometry, code artifacts, account state, and streaming semantics remain unchanged.

## Initial-loading optimization

- The final Chat stylesheet now forces the body visible immediately instead of waiting for `#swrlzAccountDock` to exist, removing an unnecessary all-page hidden first-paint gate.
- Off-screen sidebar thread rows use `content-visibility: auto` with an intrinsic row size so the browser can skip unnecessary initial paint/layout work for long thread lists.
- Responsive/card rules previously duplicated in `chat_responsive_polish.css` are already consolidated in `chat_mobile_viewport_fix.css`.
- The runtime manifest no longer loads the redundant `chat_responsive_polish.css`, removing one stylesheet request from every Chat boot while preserving the historical file in repository lineage.

## Verification / deployment

- `web/chat_mobile_viewport_fix.css` updated on the `runtime` branch.
- `runtime_pages/manifest.json` updated to remove the redundant responsive-polish stylesheet from `/chat`.
- `versions/server-runtime.txt` advanced to `2.3.34`.
- `versions/web-chat.txt` advanced to `1.4.29`.
- Production deployment: NONE.
- Server restart: NONE.
- Path: runtime-hot only.
- Final browser acceptance remains screenshot-driven for the user's Android viewport.

## Relevant lineage

- Mobile header + first-paint stylesheet: `cfb5a657dd5294c2b2f62d9256493425fae8f6cb`
- Runtime manifest boot-chain reduction: `6c5cc12a55a64a4f8b75a9453e6421a25b296d8e`
- Server Runtime version authority: `2e4f73aa509ee970ddd7f200cedcefbcc0deed06`
- Web Chat version authority: `60d1f20cf7b36d552939544172e0acccf016f9d9`
