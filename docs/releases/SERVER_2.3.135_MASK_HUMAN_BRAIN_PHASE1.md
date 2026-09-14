# Server 2.3.135 — Mask / Human / Brain migration, Phase 1

## Release identity

- Overall Server Runtime: `2.3.135`
- Web Chat: `1.5.13`
- LALM Engine: `2.1.43`
- LALM revision: `2.1.43-hot-brain-owned-interpretation-v33`
- Runtime manifest: `45`
- Source branch: `runtime`
- Deployment: **NONE**
- Restart: **NONE**

## Purpose

Begin enforcing the documented Mask / Human / Brain architecture in live runtime behavior:

- Chat/Mask relays user text, bounded history and factual approved context.
- Server/Human continues to own transport, sessions, continuity, authorization and execution boundaries.
- LALM/Brain owns interpretation, task classification, RMCCA reasoning, temporal interpretation, response planning and semantic acceptance.

## Phase 1 changes

### Chat / Mask

`web/chat_context_canonical.js`
- Removed browser RMCCA domain/role/topology classification.
- Removed browser-generated RMCCA cognitive policy directives.
- Removed `swrlzCognitiveContext` as a client interpretation authority.
- Retained canonical prompt/history relay and diagnostic receipts.
- Added factual relay contract `mask-factual-relay-v1`.

`web/chat_rmcca_transport_guard.js`
- Retired browser fallback reconstruction of RMCCA cognitive envelopes.
- Guard now ensures browser cognition is not reintroduced and records LALM ownership.

`web/chat_rmcca_transport_trace_v2.js`
- Converted diagnostics from cognitive-envelope/carrier validation to factual-relay tracing.

`web/chat_temporal_personality.js`
- Removed client-authored direct-time/personality response directives.
- Retained profile utility access only.

`web/chat_turn_integrity_v1.js`
- Removed social greeting and temporal response steering.
- Retained factual request-time receipts and terminal UI reconciliation.

### LALM / Brain

`runtime_hot/r39_engine_v33.py`
- Added explicit brain-owned interpretation boundary.
- Ignores retired browser `swrlzCognitiveContext` envelopes.
- Ignores browser `turnIntent` labels.
- Drops legacy RMCCA history carriers before inference.
- Neutralizes known legacy browser cognitive-response directives from cached clients.
- Preserves approved factual temporal context.
- Derives morning/afternoon/evening/night from the approved local clock inside the LALM boundary.
- Keeps task classification, RMCCA interpretation and semantic acceptance inside R39.

`runtime_hot/r39_engine.py`
- Hot entrypoint now pins the corrected v33 source commit.

### Runtime delivery

`runtime_pages/manifest.json`
- Advanced to manifest `45` so versioned immutable Chat assets resolve the new architecture instead of remaining on the previous browser cache revision.

## Concurrency reconciliation

Event-entry authorities were:
- Server Runtime `2.3.133`
- Web Chat `1.5.11`
- LALM Engine `2.1.42`

At the required pre-version commit boundary, concurrent work had advanced:
- Server Runtime to `2.3.134`
- Web Chat to `1.5.12`
- LALM Engine remained `2.1.42`

This event therefore reconciled from the newest authorities and assigned:
- Server Runtime `2.3.135`
- Web Chat `1.5.13`
- LALM Engine `2.1.43`

No stale planned version was written.

## Intentionally preserved

- Ice Dragon presentation/theme and response layout.
- Google/account/session surfaces.
- transcript synchronization and shared continuity.
- resumable generation/reconnect behavior.
- terminal response integrity.
- context-capacity/thread storage behavior.
- stream framing and server authorization boundaries.

## Remaining migration work

This is Phase 1, not the end of the cleanup.

Known browser-side legacy cognition still to be removed in later versioned events:
- `chat_background_resume_v2.js` still contains a legacy lightweight `turnIntent` classifier. R39 v33 now explicitly ignores that label, so it no longer owns model interpretation, but the browser code should be deleted/simplified in Phase 2.
- `chat_user_time_context.js` still computes a convenience `daypart` field for its local receipt. R39 v33 ignores that interpretation and derives daypart from the approved clock internally; the client field should be retired in Phase 2.
- `chat_committed_output_v3.js` still performs substantial semantic requirement/code validation in the browser. That needs a separate stream-semantics migration so committed-output presentation remains stable while requirement interpretation/acceptance moves entirely into the LALM.

## Verification required before close

- Re-read Server/Chat/LALM authoritative version files.
- Confirm live manifest reports version 45 from GitHub contents authority.
- Confirm a hot R39 worker reports LALM `2.1.43` / v33 before claiming the engine live.
- Exercise representative greeting/time/general/coding turns after propagation.

## Deployment state

No stable infrastructure, deployment workflow, API loader, authentication boundary or Vercel build configuration changed. This event uses the existing runtime hot-update path and requires no production deployment or restart.
