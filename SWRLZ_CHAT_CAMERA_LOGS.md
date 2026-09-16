# §wyrlz Chat Camera Logs — Runtime Observation Runbook

**Purpose:** Persistent instructions for future ChatGPT/§wyrlz engineering sessions on where the Chat/Whole Conversation Camera is implemented, where its live observations actually appear, and how to inspect those observations correctly.

## Core distinction

The GitHub repository contains the **camera instrumentation/source code**. It is used to understand what the cameras are programmed to capture and how the telemetry is emitted.

GitHub is **not** the primary store for live Chat camera observations. Do not search for a `/logs/` directory and assume that repository files contain the user's current production Chat captures.

The actual live observations are emitted by the running production system and are inspected through **Vercel production runtime logs**.

```text
GitHub camera/instrumentation source
        ↓
running production Chat / server / LALM
        ↓
structured camera + telemetry records
        ↓
Vercel production runtime logs
        ↓
filter/correlate by requestId, threadId, engine/version, event
```

## What GitHub is for

Use the repository to inspect the implementation and contracts that determine what is captured. Relevant files can evolve, so search current source rather than relying only on this list. Historically important surfaces include:

- `runtime/web/chat_account_state_sync_v1.js` — browser-side Whole Conversation Camera/account-state instrumentation and debug submission.
- `runtime_hot/r39_engine_v*.py` — LALM/R39 structured telemetry and camera records such as `SWRLZ_R39_TELEMETRY` and `SWRLZ_R39_CAMERA`.
- Chat debug/client-debug routing and middleware on `main` — receives/records browser diagnostic events.
- `runtime_pages/manifest.json` and Chat runtime loaders — establish which current runtime assets are live.

Before diagnosing, fetch the current runtime manifest and current source/version authorities. File names and revisions may advance.

## What Vercel runtime logs are for

Use Vercel production runtime logs to answer questions about **what actually happened in a live Chat turn**.

When the Vercel connector/tooling is available, retrieve runtime logs for the current production deployment/project and search the relevant time window. Correlate records using concrete identifiers rather than visual timing alone.

High-value correlation fields include:

- `requestId`
- `threadId`
- canonical message IDs
- canonical revision/state transitions
- engine/LALM version and hot revision
- camera event/route
- history message count / bounded history metadata
- terminal state
- prefill/decode/TTFT/latency telemetry
- repetition/social-route diagnostics when relevant

A request ID is normally the strongest join key for following one turn across browser camera events, canonical server commits, middleware, and R39/LALM telemetry.

## Recommended diagnostic workflow

1. Read `SWRLZ_PROJECT_START.md` and the required project documents first.
2. Read this runbook before diagnosing Chat behavior from logs.
3. Fetch current `runtime_pages/manifest.json`, relevant Chat instrumentation, current R39 hot engine/loader, and affected version authorities.
4. Determine the current production deployment/project from Vercel rather than assuming an old deployment ID is still current.
5. Pull Vercel production runtime logs for the narrowest useful time range around the user's test.
6. Find the turn's `requestId` and `threadId` when available.
7. Trace the same request through canonical USER commit → history/context preparation → LALM/R39 route → camera/telemetry → terminal ASSISTANT commit/failure.
8. Compare runtime evidence with repository source. Source explains intended behavior; logs prove observed behavior.
9. If diagnosing a visual Mask defect, combine logs with a screenshot/user observation when useful. Logs prove state/transport behavior; screenshots prove what the user actually saw.
10. Do not claim production acceptance merely because source code looks correct. Require live runtime evidence for production-behavior claims.

## Camera versus screenshot

The Whole Conversation Camera is **structured diagnostic telemetry**, not a literal screenshot camera. It captures bounded conversation/turn state and selected diagnostic metadata according to its current contract.

A user screenshot is different evidence:

- **Camera/runtime logs:** request IDs, state transitions, canonical revisions, routes, history, latency, terminal state, telemetry.
- **Screenshot:** actual rendered Mask/UI, geometry, theme, spacing, flash/flicker, controls, readability.

For server/Brain problems, prefer logs/camera evidence first. For visual Mask problems, use both when possible.

## Important anti-confusion rule

Never say that live camera output was found "in the GitHub logs" unless a repository artifact explicitly contains an exported capture. The normal distinction is:

- **GitHub:** instrumentation and engineering source of truth.
- **Vercel runtime logs:** live production observations.

If Vercel runtime-log access is available, use it before claiming the live camera evidence cannot be inspected.

## Evidence discipline

Do not infer a live result from source alone. Do not infer the responsible component merely because two changes occurred around the same time. Correlate concrete runtime records.

When reporting a diagnosis, separate:

1. **Source fact** — what the current code is designed to do.
2. **Runtime fact** — what production logs show actually occurred.
3. **User-visible fact** — what the user observed or a screenshot demonstrates.
4. **Diagnosis** — the explanation supported by those facts.

This distinction prevents the camera, Mask, server/body, or Brain from being blamed merely because it is near the failure.

## Short memory aid

```text
Need to know what the camera CAN capture?  → GitHub source.
Need to know what the camera DID capture?  → Vercel runtime logs.
Need to know what the user SAW?             → screenshot / direct UI observation.
```
