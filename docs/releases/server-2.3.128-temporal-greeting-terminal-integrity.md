# Server Runtime 2.3.128 / Web Chat 1.5.8 — Temporal Greeting + Terminal UI Integrity

## Problem
A simple social greeting at an approved local evening time could still produce a contradictory greeting such as `Good morning!`. The previous social-opener directive only said that a fitting time-of-day greeting was appropriate; it did not bind the approved request-time daypart as a fixed factual anchor. Separately, the browser could continue displaying `Analyzing request` and the Stop button after a terminal response if transcript terminal metadata lagged behind the existing terminal-response-integrity receipt.

## Changes
- `web/chat_turn_integrity_v1.js` advances internally to `turn-integrity-v2`.
- Social greetings now attach approved request-time `localTime` and `daypart` as fixed facts when available.
- Any time-of-day greeting must agree with that daypart; contradictory dayparts are explicitly forbidden.
- Without approved local-time context, the response must not invent a morning/afternoon/evening/night greeting.
- Terminal UI authority now accepts either strict verified transcript terminal state or the existing `terminal-response-integrity-v1` completion receipt.
- Terminal authority retires stale active/Stop state, normalizes the phase to `COMPLETE`, clears stale network errors, and settles the activity log to `Response complete`.

## Invariant
Approved request-time temporal context is a factual constraint, not stylistic inspiration. A greeting may omit time-of-day wording, but if it uses one, it must agree with the approved request-time daypart.

Terminal completion is monotonic and must retire stale active-generation UI regardless of whether transcript terminal metadata or stream-terminal integrity evidence arrives first.
