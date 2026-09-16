# Server 2.3.192 — Redis Canonical Chat Storage Foundation

Date: 2026-09-16
Status: staged; not deployed

## Event
Canonical Chat persistence foundation moved away from direct whole-account Vercel Blob ownership toward the existing durable Redis REST architecture.

## Stable infrastructure
Merged PR #16 to `main` at merge commit `fb6965a95ee6ae2c7813405cc98675d5db5b6ff7`.

Changed stable API modules:
- `api/durable_redis_atomic.py` — atomic Redis generation creation.
- `api/canonical_redis_state.py` — canonical Chat adapter preserving browser/server message IDs and atomic begin/finish semantics.
- `api/chat_turn_state.py` — explicit canonical backend selector: `redis`, `blob`, or `auto`.

The Redis pre-generation transaction atomically commits the user message, assistant placeholder, generation job, active-job membership, thread update, and indexes. Request ID is the idempotency claim. Generation remains fail-closed if the selected durable backend cannot commit.

## Configuration required before production activation
- `SWRLZ_REDIS_REST_URL`
- `SWRLZ_REDIS_REST_TOKEN`
- optional `SWRLZ_REDIS_PREFIX` (default `swrlz:v1`)
- `SWRLZ_CHAT_CANONICAL_BACKEND=redis`

## Deployment state
No production deployment was triggered by this event. Current Vercel project state reported Git deployment disabled (`live: false`). A manual production deployment is still required after Redis configuration is present.

## Version authority
Overall Server advanced from 2.3.191 to 2.3.192. No unrelated module version was advanced.

## Verification
Repository verification: merged source is present on `main`; Server authority is 2.3.192 on `runtime`.
Production verification: pending Redis configuration + manual deployment + live Chat test.
