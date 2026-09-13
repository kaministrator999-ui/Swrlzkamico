# Server Runtime 2.3.114 — First-paint response presence repair

## Event

- Server Runtime: 2.3.114
- Web Chat: 1.4.97
- Source branch: `runtime`
- Deployment required: no

## Problem

The base Chat UI could render an empty streaming assistant bubble as `Connecting to §wyrlz` before the staged response-presence overlay took ownership. The response-presence layer carried richer labels, but the bubble renderer read the base phase label rather than `message.meta.workLabel`, so the first visible frame could remain the legacy connecting label.

## Repair

`web/chat_response_presence.js` is now response-presence v3. It:

- treats `swurlz`, `swrlz`, and `swyrlz` as display aliases of `§wyrlz`;
- retries initial presence arming when the assistant message has not been discoverable yet;
- promotes any live assistant message left in legacy `CONNECTING` to `📥 §wyrlz is receiving your message…`;
- writes the staged presence label directly into the visible empty-response bubble after render;
- re-applies the visible work label after DOM re-renders, so the base phase renderer cannot reintroduce `Connecting to §wyrlz` while the response is waiting;
- preserves event-driven progression through reading, context connection, thinking, shaping, writing, checking, reconnecting, and catch-up states.

## Invariant

The waiting bubble is owned by the staged §wyrlz response-presence contract from the first visible frame. `Connecting to §wyrlz` is no longer an acceptable steady-state waiting label for a live request.
