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


## Verified actual live Space (2026-11-14)

The production Space is **not** using the repository's `api/durable_redis_store.py`
directly. Its running `station.py` delegates user login and encrypted chat
history to `account_chat_store.py` and the shared
`github_connection._redis(c, *args)` REST gateway. Its source credentials
are stored privately as `UPSTASH_REDIS_REST_URL` and
`UPSTASH_REDIS_REST_TOKEN`, and Aiven is configured as `SWRLZ_VALKEY_URL`.

Production evidence:

- Secret key presence confirmed without reading secret values:
  GitHub run 43646343321 (initial) and 43646616301 (source key audit).
- First read-only live TLS probe deployed to the **same** Space at revision
  `18812f52ccdb40da5faded7ebdb8ac31c83f0661`.
- Live probe completed: TLS/Valkey PING, SET/GET and EVAL all successful;
  Upstash REST PING returned HTTP **403**, so source data cannot currently be
  verified or migrated through that REST connection.
- An optional, **dormant**, native Redis-protocol adapter was installed in
  the actual `github_connection.py` at Space revision
  `cca069b30df86f4214138a3bfcdbb9331579f16e`.
  `SWRLZ_REDIS_BACKEND` was absent at deployment, therefore the existing
  Upstash provider remains selected. The exact prior gateway file was saved
  as a private GitHub Actions rollback artifact (run 43647599433).
- The older Hugging Face `manual-hf-space.yml` packaging workflow has
  known source-layout drift and **must not** be run to deliver this adapter.

**Cutover remains blocked:** retrieve and verify the original encrypted
accounts, chat snapshots, indices, and their TTLs first. Aiven is still
empty of user records except the deleted test probe key. Do not manually set
`SWRLZ_REDIS_BACKEND=valkey` until data parity is proven.

Potential offline source recovery: Upstash provides an administrative
`Backups > Backup & Export > Export` RDB operation, although access under
the currently restricted free tier must be verified. Keep RDB backups
private. Never paste Redis passwords or raw session values into GitHub.
