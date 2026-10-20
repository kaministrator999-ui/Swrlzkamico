# §wyrlz Chat v290 — Live reply shimmer and tail

## Owner and scope

Canonical source: `chat/§wyrlz/index.html` on the exact v289 production source lineage. This is **UI-only**; no LALM weights, GitHub permissions, Station API, saved-message schema, or §E/Forge artifacts change.

## Behavior

The existing `stationGeneration` event stream is the **only authority** for a live reply. While `g.terminal===false`, the active `.station-live-message` receives `data-response-live="true"`, a low-contrast cyan/violet sheen inside its existing assistant body, and a small indicator at the end of the active message. Before any first text token, the tail says **Preparing response**; after the first token it says **Still responding** and three subtle dots animate.

The signal remains present across long stalls, Qwen source analysis and provider work until the actual Station terminal flag arrives; it does not infer progress, percent complete or successful output. On `g.terminal=true` (COMPLETE, FAILED, CANCELLED), the live-tail DOM is removed immediately, the shimmer CSS selector no longer matches, and historical committed messages are rendered without any live attribute/tail. The existing v238 activity timeline, telemetry status, source response anchor, widgets and preserved historical DOM stay unchanged.

## Accessibility and performance

The tail contains readable text and a three-dot animation marked decorative to assistive technology. The pre-existing station activity status remains accessible. Only **one currently active** response can shimmer; CSS gradients are low-opacity, limited to the response card and pointer-events none. No JS animation timer, per-token DOM rebuilding, global shimmer, oversized SVG or full-screen blur introduced. CSS disables motion for explicit `motion-off`/`motion-reduced` and the operating-system `prefers-reduced-motion` setting unless explicitly overridden by `motion-full`. Reduced-motion users retain a visible static cue. High contrast retains readable text and a clearer boundary.

## Tests

- `tests/test_chat_live_response_cue_v290.cjs` uses a synthetic real browser Station snapshot: pre-token, active streaming, Android 390px card, no overflow, reduced motion, a real active-to-terminal transition and historical hydration. COMPLETE, FAILED and CANCELLED use the same audited `g.terminal` condition; this fixture does not simulate unsupported new-request transitions without a send ACK.
- Existing v170 response-start anchor and v287 scroll DOM reuse tests remain required.
- `.github/workflows/chat-live-response-cue-v290.yml` runs Node syntax, static contract and Chromium in the exact Chat document.
- A green browser test is independent of later signed-in Android user acceptance.
