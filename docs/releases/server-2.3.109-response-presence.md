# Server Runtime 2.3.109 / Web Chat 1.4.91 — Stage-aware §wyrlz response presence

## Scope
Runtime-only Chat presentation update. No Vercel deployment is required.

## Changes
- Added `web/chat_response_presence.js`.
- Replaced the generic response placeholder experience with stage-aware presence labels driven by the actual stream phases.
- Initial pre-network stages: `§wyrlz received your message…`, `§wyrlz is reading your message…`, `§wyrlz is understanding your request…`.
- Stream stages map to preparing context, thinking, composing, writing, checking, reconnecting, catch-up, and terminal states.
- Added display-only brand normalization: `swurlz`, `swrlz`, and `swyrlz` render as `§wyrlz` in ordinary UI text.
- Raw conversation text, stored history, input/textarea values, code blocks, and preformatted technical content are not rewritten by brand normalization.
- Manifest advanced to v27.

## Preserved contracts
- `generation-transcript-v1` remains strict/fail-closed.
- `resumable-v1` transport remains unchanged.
- Permission-first device temporal context remains unchanged.
- This event changes presentation only and does not alter model generation or networking semantics.
