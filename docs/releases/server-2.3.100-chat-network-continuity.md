# Server 2.3.100 — Same-generation network continuity

Status: **prepared; stable deployment pending explicit approval**

## Authorities

- Server Runtime: `2.3.99 -> 2.3.100`
- Web Chat: `1.4.82 -> 1.4.83`
- LALM Engine: unchanged (`2.1.36` / v26)

## Problem observed

A phone network handoff (for example cellular -> Wi-Fi) can break the browser's HTTP stream while local R39 is still computing. The previous browser continuity layer treated that socket failure as a failed request or a one-shot retry. That is the wrong ownership model for long generations.

## Architecture

### Stable server generation owner (`main`)

`api/chat_resume_sessions.py` adds a per-`requestId` local generation session.

- R39 generation runs in a daemon generation-owner thread independent of an individual browser StreamingResponse subscriber while the worker remains alive.
- Events are retained in a bounded ordered replay buffer (maximum 4096 events).
- Completed sessions remain available for 30 minutes on the warm worker.
- A reconnect sends the same `requestId` plus `resumeAfterSeq`.
- The server reuses the original generation session and returns only events with `seq > resumeAfterSeq`.
- Reusing a requestId with a different canonical payload is rejected with HTTP 409 rather than silently generating a different answer.
- Response headers advertise `X-SWRLZ-Generation-Session: resumable-v1` and `X-SWRLZ-Replay-Through-Seq`.
- Explicit user cancellation still arms the existing local cancellation path.

`api/index.py` installs the session owner and advertises stable Server `2.3.100` plus capability `chat-resumable-generation`.

### Runtime browser continuity (`runtime`)

`web/chat_background_resume_v2.js` is internally upgraded to continuity version 3 while preserving the existing hot asset path.

When the initial server response advertises `resumable-v1`:

1. Core Chat receives one logical browser `ReadableStream` for the whole answer.
2. A network read failure does not reach core `sendMessage()` as a terminal error.
3. The continuity layer enters `RECONNECTING`, waits for connectivity, and reconnects to the same request with the last accepted sequence.
4. Duplicate sequence events are dropped.
5. Events that already existed when the reconnect attached are treated as backlog.
6. Backlog DELTA events are presented at 24 ms per DELTA so the user sees a fast but smooth catch-up animation instead of an instantaneous text jump.
7. Once the replay reaches `X-SWRLZ-Replay-Through-Seq`, presentation naturally returns to live generation timing.
8. User Stop/Cancel still aborts the logical stream and the server generation.

If the stable server does **not** advertise `resumable-v1`, the runtime wrapper returns the original response unchanged; it does not fake a resume by regenerating the answer.

## Safety / truth properties

- Same requestId = same generation lineage.
- No fresh-answer regeneration is used for transport recovery.
- Already committed visible output remains append-only.
- A mismatched reconnect payload is rejected instead of merged.
- This contract is warm-worker scoped. If the Vercel worker itself is destroyed, recurrent model state cannot be reconstructed from this replay buffer and the client must preserve the committed partial rather than invent continuity.

## Deployment boundary

The browser half is runtime-hot, but the generation-session owner is stable API infrastructure on `main`. Full functionality therefore requires a stable deployment.

No `.deploy/REQUEST.txt` mutation was made and no deployment or restart was triggered in this event.
