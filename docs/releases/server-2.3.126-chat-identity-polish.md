# Server 2.3.126 — Chat identity + Ice Dragon polish

## Versions

- Server Runtime: 2.3.126
- Web Chat: 1.5.6
- Runtime manifest: 39

## Scope

Runtime-hot UI-only change. No stable server route, auth boundary, model runtime, collector contract, or deployment contract changed.

## Changes

- Added `web/themes/ice-dragon/ice-dragon-polish-v2.css`.
  - lighter sculpted outer composer glass with rounded top contour;
  - darker inner composer field;
  - lower blur to preserve wallpaper detail;
  - silver-gray monospace context/caption text;
  - ice-blue glass activity/copy/export/action controls;
  - forum-inspired frosted §wyrlz name/time plate joined visually to the dragon companion;
  - subtle themed assistant response border and glass;
  - mobile-fit account settings panel styling.
- Added `web/chat_account_identity_v1.js`.
  - signed-in Google profile picture is used as the user avatar in chat messages when available;
  - the user's saved Chat name is shown in message bylines instead of the generic `You` label;
  - Google name remains the fallback when the account preference requests it;
  - duplicate Preferred-name/Google-name controls are collapsed from the settings UI toward one editable Chat name field;
  - account identity card is shown once in account settings rather than repeating identity as multiple form fields.
- Manifest 39 loads both additions after the established chat/theme pipeline.

## Preserved contracts

- Exact repository Ice Dragon PNG remains the only wallpaper owner.
- No legacy adult-wallpaper fallback was reintroduced.
- Existing transcript continuity, turn integrity, context-capacity, response-polish, and account-scoped browser history behavior remain intact.

## Verification

Static runtime source publication completed. Browser visual acceptance is pending user refresh on the live Vercel endpoint. No server redeploy is required by this runtime-hot UI event.
