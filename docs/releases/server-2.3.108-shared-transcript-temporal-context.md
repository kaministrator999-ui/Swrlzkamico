# Server Runtime 2.3.108 — Shared Transcript + Permission-First Temporal Context

## Event summary

This event finishes the serverless transcript-continuity issue identified before the temporal-context discussion and adds permission-first device time context to Chat/LALM.

## Versions

- Server Runtime: 2.3.108
- Web Chat: 1.4.90
- LALM Engine: 2.1.38
- LALM revision: `2.1.38-hot-permission-temporal-grounding-v28`
- Runtime manifest: v26

## Shared transcript continuity

Stable `main` is prepared for Server 2.3.108 with `shared-private-blob-v1` transcript checkpoints.

- Active model/KV generation remains owned by the worker that started the request.
- Generated assistant transcript position is checkpointed to private Vercel Blob.
- A different worker can answer `/api/chat/transcript` from the shared checkpoint instead of returning `GENERATION_SESSION_NOT_FOUND` merely because it lacks the local Python session dictionary.
- A remote worker does not start a duplicate generation when a durable active owner already exists.
- Browser transcript sync remains fail-closed: no legacy event-replay path is treated as successful transcript continuity.
- When a shared transcript is being served by another worker, Chat can follow shared checkpoints until terminal state or until the owner stream becomes available again.
- `/tmp` is not transcript authority.

Stable deployment of 2.3.108 is **pending explicit production approval**. Production remains on the previously deployed stable server until that approval occurs.

## Permission-first temporal context

The existing `chat_user_time_context.js` behavior previously attached device-local time automatically. Web Chat 1.4.90 replaces that behavior with explicit user consent.

### Consent states

- Allow device time: device local clock + IANA timezone are attached to each request.
- Not now: temporal context remains off; a future reminder is allowed after a cooldown.
- Don't ask again: temporal context remains off and automatic reminders stop.
- The Chat settings dialog always provides controls to enable/disable the feature later.

### Reminder behavior

- First decline: approximately one-week cooldown.
- Multiple declines: approximately one-month cooldown.
- `never` reminder preference suppresses automatic prompts.

### Profile location fields

City, state/region, and country fields are present for future profile context but `useForTemporalResolution` is forced false in this event. They are not used to resolve a timezone and no online location/timezone analysis is attempted.

### LALM temporal policy

R39 v28 treats approved temporal metadata as grounded context and uses it only when conversationally relevant. If approved metadata is absent, the LALM is instructed not to infer or claim the user's current local hour/daypart and not to use morning/afternoon/evening/night greetings unless the user supplied sufficient temporal information in conversation.

## Runtime activation

The following runtime-owned pieces are live without a stable server redeploy:

- permission-first `web/chat_user_time_context.js`
- shared-transcript-aware `web/chat_transcript_sync.js`
- R39 hot v28 entrypoint and overlay
- runtime manifest v26

The shared private transcript store itself is stable-server infrastructure and becomes active only after Server 2.3.108 is deployed.

## Verification

Live production status after the runtime update reports hot LALM `2.1.38` / `2.1.38-hot-permission-temporal-grounding-v28`, including:

- `permissionAwareTemporalGrounding=true`
- `timeSpecificClaimsRequireApprovedContext=true`
- `deviceTimeConsentOwnedByChat=true`
- `profileLocationTemporalResolution=false`

The live device-time asset is served from the GitHub `runtime` branch with no-store runtime-source headers.
