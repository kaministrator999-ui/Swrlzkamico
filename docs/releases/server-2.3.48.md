# Server v2.3.48 — authenticated background recovery

Date: 2026-09-11

## Module state

- Server runtime: 2.3.48
- Web Chat: 1.4.43
- LALM engine: 2.1.25 (unchanged)

## Trigger / failure evidence

The whole-conversation camera log showed pending assistant messages stuck in RECONNECTING with repeated `HTTP 401` recovery failures after the page/background stream disconnected. The original foreground request used Chat authorization headers, but the background resume path rebuilt the POST with only content negotiation headers, so every reattach attempt was unauthorized. The retry loop then alternated reconnect and 401 activity entries, creating hundreds of noisy trace records.

## Changes

- Background/reload recovery now reuses the same authoritative Chat authorization headers as a normal foreground stream request, including `X-SWRLZ-Chat-Token`.
- Recovery still uses the saved request ID/body so an existing detached job can replay, or a replacement worker can regenerate and reconcile against saved partial text.
- HTTP 401 is no longer treated as a hot retry loop. Recovery waits for a valid current Chat token instead of retrying every ~1 second indefinitely.
- Recovery activity history is bounded to prevent runaway reconnect telemetry from bloating message state.
- Reconnect polling is slightly less aggressive while remaining prompt on focus/pageshow/online transitions.
- Instance-change activity wording no longer claims a restart before the replay/regeneration path actually proves what happened.

## Verification state

- Source-level root cause: VERIFIED from the uploaded camera log and current Chat source.
- Runtime source update: COMMITTED on `runtime`.
- Browser acceptance: PENDING user retest after refresh.
- Vercel deployment: NONE requested or required.
- Server restart: NONE requested.

## Relevant lineage

- `web/chat_background_resume.js`: `c00aaa9dce1c38412ed07b4c947600d32a415d77`
- `versions/server-runtime.txt`: `7d334b534680f07c0429658b5598e5842b213f7e`
- `versions/web-chat.txt`: `c8a8d476c691247852f4caffad457de1f4124a35`
