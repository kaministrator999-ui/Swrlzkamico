# Server Runtime 2.3.110 — Contextual Presence + Temporal Personality

## Module versions

- Server Runtime: `2.3.110`
- Web Chat: `1.4.92`
- LALM Engine: `2.1.39`
- LALM revision: `2.1.39-hot-anchored-temporal-personality-v29`
- Runtime manifest: `v28`

## User-visible behavior

Chat no longer relies on a generic `Connecting to §wyrlz` waiting state as its intended visible response-presence experience. The runtime presence layer progresses through concise, expressive stages tied to the actual request lifecycle, including receiving, reading, connecting context, thinking, shaping, writing, checking, reconnecting and catch-up states. The activity log remains the detailed diagnostic authority; the response bubble uses friendlier state text.

Displayed references to `swurlz`, `swrlz`, and `swyrlz` continue to normalize to the canonical brand `§wyrlz`. This release also adds semantic normalization before model request preparation so those spellings mean `§wyrlz` to the LALM as well. Raw stored user text remains unchanged; semantic normalization happens in the outbound request copy.

## Direct current-time response contract

When the user asks a direct question for their own current time and device-time permission is approved:

1. The approved current local time is a fixed factual anchor.
2. If the user has set a Preferred name in the existing account/profile preferences, that preferred name is a second fixed semantic anchor and must be used naturally once.
3. Wording before, between, and after the anchors may express §wyrlz personality.
4. A fitting time-of-day emoji is preferred over a generic waving-hand greeting.
5. Redundant phrasing such as `10:55 AM in the morning` is discouraged; daypart context should be separate and natural when useful.
6. The response remains concise for simple time questions.

The browser-side temporal personality layer reads only the existing Preferred name preference and the already-approved device-time context. It does not activate profile city/state/country timezone resolution.

## Privacy / transparency boundary

- Device-local time remains permission-first.
- If time permission is disabled, current-user-time claims remain disallowed unless the user explicitly provides enough temporal information in conversation.
- City/state/country profile fields remain stored-only for future resolver work.
- Preferred name is read from the user's existing account-scoped/local profile preference only for the direct-time response contract; no name is invented when the preference is empty.

## Files

- `web/chat_response_presence.js` — expressive lifecycle presence + display brand normalization.
- `web/chat_identity_semantics.js` — semantic alias normalization for outbound user prompt/history copies.
- `web/chat_temporal_personality.js` — preferred-name/time anchor contract for direct current-time requests.
- `runtime_hot/r39_engine_v29.py` — LALM-side direct-time personality and fixed-anchor policy.
- `runtime_hot/r39_engine.py` — v29 hot entrypoint.
- `runtime_pages/manifest.json` — runtime application script order/activation.

## Deployment boundary

This release is runtime-owned and does not itself request or trigger a Vercel production deployment. Stable production server changes remain governed separately by explicit deployment approval.
