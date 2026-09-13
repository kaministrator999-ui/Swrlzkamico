# Server Runtime 2.3.111 — Terminal Integrity + Temporal Context Non-Relay

Date: 2026-09-13
Branch: `runtime`

## Changed modules

- Server Runtime: `2.3.111`
- Web Chat: `1.4.93`
- LALM Engine: `2.1.40` / `2.1.40-hot-temporal-context-nonrelay-v30`
- Runtime page manifest: v29

## Terminal response integrity

A stream-confirmed `COMPLETED` response is now monotonic browser evidence for that request. `web/chat_terminal_integrity.js` snapshots the accepted visible response at terminal completion and preserves it if a later foreground, pageshow, reconnect, transcript, or generic network error attempts to downgrade or erase that completed message.

The guard also snapshots already-visible committed text before the page backgrounds. If late network-state churn clears the message body, the previously committed visible text is restored rather than replaced by an empty failure bubble. Foreground/online events still ask the existing strict transcript continuity layer to reconcile unfinished generations; terminal preservation does not create a legacy replay fallback.

## Temporal context non-relay

R39 v30 replaces the older raw `User local time: <date> <time> <daypart> <timezone> UTC<offset>` model-facing string. Approved device time remains available for reasoning, but raw date, IANA timezone, and UTC offset are explicitly classified as internal grounding metadata.

For direct current-time questions, the model receives a human-readable local clock anchor and daypart. It must not list or echo the raw temporal context record. Date, timezone, or UTC-offset details are surfaced only when the user explicitly asks for them or asks for temporal debugging/context details.

## Deployment boundary

This event changes only runtime-hot sources and runtime-owned browser assets. It does **not** deploy the stable Vercel server. Stable production remains on its existing deployed server version until a separate deployment is explicitly approved.
