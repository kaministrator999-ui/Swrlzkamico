# Server Runtime 2.3.105 — Proactive Foreground Resume + Live Work Status

## Versions
- Server Runtime: 2.3.105
- Web Chat: 1.4.87
- LALM Engine: unchanged
- Deployment: NONE (runtime-hot)

## Problem
A browser/app background or network handoff could leave the visible response appearing stalled even while the resumable server generation continued. The composer/response status could also remain on a generic “Connecting to §wyrlz” message instead of following actual inference work.

## Changes
- `web/chat_background_resume_v2.js` advanced internally to continuity version 4.
- Added proactive same-generation resume nudges on `visibilitychange` (foreground), `pageshow`, and `online`.
- Foreground resume cancels only the current browser reader, never the server generation or user request; the next connection resumes with the same `requestId` and `resumeAfterSeq`.
- Preserved 24 ms replay pacing for missing DELTA events so backlog catches up visibly instead of teleporting.
- Added user-facing work-phase mapping so visible status follows request progress: analyzing, preparing context, writing response, checking response, reconnecting, catching up, and completion/error.
- Raw server phase remains available in `message.meta.rawPhase`; the user-facing phase is stored separately through the existing message state.
- Kept the `resumable-v1` server contract and append-only committed-output architecture unchanged.

## Evidence basis
The conversation camera showed a network drop after prefill block 864/893, followed by successful same-generation reconnect, completion of prefill, and continued decode through at least step 128. The browser continuity state reported one reconnect and returned to `state=live`, proving server generation survived while the visible UI appeared stalled.

## Concurrency/version reconciliation
Immediately before assigning versions, runtime authority had independently advanced to Server Runtime 2.3.104 while Web Chat remained 1.4.86. This event therefore used the next non-conflicting authorities: Server Runtime 2.3.105 and Web Chat 1.4.87.

## Rollback
Restore the prior `web/chat_background_resume_v2.js` content and advance authorities in a new corrective event; do not erase this lineage.
