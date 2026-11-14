# Aiven Valkey storage adapter — staged, not a live cutover

The application uses Redis for canonical authenticated users, profiles, lore,
threads, messages, job state, and recovery checkpoints. The original Upstash
REST storage remains the **default**. Aiven Valkey requires a native TLS
Redis-protocol connection, not Upstash's HTTP REST endpoint.

## Activation (after a verified migration)

Use the existing Hugging Face Space `kamiloki/Swyrlz`. Configure via its
private secret/variable management (never in GitHub source, screenshots,
chat messages, or frontend JavaScript):

- `SWRLZ_VALKEY_URL` — **secret**: the complete Aiven `rediss://`
  Service URI, including password; do not convert to plain `redis://`.
- `SWRLZ_REDIS_BACKEND=valkey` — explicit backend selection.
- `SWRLZ_REDIS_PREFIX` — leave at `swrlz:v1` unless deliberately
  migrating to a different key namespace.

Without `SWRLZ_REDIS_BACKEND=valkey`, the existing
`SWRLZ_REDIS_REST_URL` and `SWRLZ_REDIS_REST_TOKEN` remain authoritative.
An invalid or missing Valkey URI **fails closed**; it will not silently
switch storage providers.

## Mandatory before changing production backend

1. Keep both databases, all original credentials, and current deployment
   rollback references intact. Do not delete or clear Upstash data.
2. Inventory the existing Redis keys and schema from Upstash; determine
   whether its traffic quota currently prevents reads.
3. Migrate the complete `swrlz:v1` namespace (including user/identity
   associations, sorted-set scores, sets, strings and relevant TTLs).
   Include chat state, identity, message records, thread indexes, jobs,
   and nonexpired generation checkpoints. Avoid copying credentials to
   plaintext output or shared artifacts.
4. Compare source/destination **key counts by type**, indexed referents,
   selected account history, identities, and TTL behavior. New Valkey
   starts empty: simply switching the backend can make accounts and
   conversations *appear* missing.
5. Test a nonproduction read/write session, Google sign-in, account
   identity preservation, chat history, new generations, cancellation,
   resume/checkpoints, Redis Lua atomic updates, and reconnection.
6. Only after successful parity verification and user-approved cutover,
   switch the HF environment to `valkey` and perform the gated HF
   deployment/acceptance process. Roll back by restoring the previous
   backend selection and exact HF release.

This PR deliberately makes **no live database or HF secret changes**.
Test the transport locally with
`python -m unittest tests.test_valkey_adapter_contract`.

## Notes

- Redis-compatible operations such as `EVAL`, `SET NX`, `ZADD`,
  `ZRANGEBYSCORE`, and `SETEX` run through the same existing
  `_command` interface, keeping canonical chat transaction logic intact.
- TLS certificate verification stays required. TCP pools are reused.
- The Aiven service itself still has resource/fair-use limits; this
  adapter is not a claim of unlimited throughput.
- Aiven reference: https://aiven.io/docs/products/valkey/howto/connect-python
