# §C Upstash 10 GB free-tier bandwidth incident — 2026-11-14

## Scope and status

Upstash rejected the live `PING` request with HTTP 403 while its free
10 GB/month quota was reported exhausted. The exact Upstash Usage traffic
series and per-command byte totals were **not** available through the
connected Hugging Face/GitHub integrations. A 403 response on its own does
not prove the causal quota or individual bandwidth consumers.

Aiven Valkey was tested from the actual Hugging Face runtime with TLS,
SET/GET, and Lua EVAL. The opt-in native gateway deployed in
`github_connection.py` was activated as a fresh database with
`SWRLZ_REDIS_BACKEND=valkey` and passed both native command checks and
the account HTTP endpoint. GitHub Actions run **43651400200** records
the live acceptance. No Upstash records were copied, deleted or modified
during the cutover. Existing Google sessions stored only in Upstash will
not automatically persist to Valkey; a new Google login may be required.

## Confirmed source-level bandwidth amplification

These are findings from the **actual running Hugging Face Space**
(`kamiloki/Swyrlz`), not the older canonical repository's alternate
`api/durable_redis_store.py` implementation:

1. `chat/§wyrlz/index.html`, approximately line **4402**, polls
   `/api/lalm_station/sync` every **2 seconds** while visible and idle.
2. `station.py:_refresh_account_chat`, approximately lines **307-342**,
   allows external Redis reads every **10 seconds** per cached account
   session. Browser focus, export and account mutation can force an
   immediate refresh. It checks the session's active generation status,
   so in-flight generation itself may temporarily suppress refresh.
3. `account_chat_store.load_chat`, approximately lines **169-185**,
   reads the complete encrypted account chat record, then decodes all
   encrypted chunks. This replays **full history**, not a small revision
   or conditional `not modified` response.
4. `account_chat_store._decode_native_chat`, approximately
   lines **113-148**, makes an extra Redis GET **per chunk** when the
   compressed encrypted snapshot exceeds the inline envelope limit.
   Constants: `CHAT_CHUNK_BYTES=640_000`,
   `CHAT_MAX_RAW=32_000_000`, `CHAT_MAX_CIPHER=40_000_000`,
   `CHAT_MAX_CHUNKS=64`.
5. `account_chat_store.save_chat`, approximately lines **188-222**,
   recompresses/encrypts the **entire** account-thread collection for
   every committed mutation and writes one or more chunks, then a
   CAS manifest. It is not an append-only/delta write.
6. `account_chat_store.load_login` and other account-oriented routes
   add additional small Redis requests. Archive import, archive
   recall and account profile operations also use the shared Redis
   gateway. These are candidate secondary contributors; no evidence
   yet proves a continuous archive import loop.

A continuously active session reading only **100 KB** of compressed
history every 10 seconds moves approximately **864 MB/day** before
accounting for request overhead or other reads/writes. An **~1 MB**
encrypted history snapshot at that same interval moves **~8.64 GB/day**.
These are *illustrative upper-rate estimates* (the actual read pattern,
compression, active generation time, multiple replicas and HTTP payload
accounting vary), not observed metering. More browser tabs, devices,
active workers or forced refreshes can increase traffic. The 2-second
HTTP response itself may also duplicate complete projected chat state,
which adds browser/network traffic distinct from Upstash egress.

## Root-cause confidence

- **Confirmed architectural cause/risk:** repeated full-history reads
  and whole-history rewrites rather than conditional revision checks or
  incremental persistence.
- **Plausible dominant usage driver:** sustained polling while long code
  outputs made encrypted history larger.
- **Not yet proven:** exactly how many bytes/commands Upstash charged,
  whether another request loop coincided with the spike, or which account
  consumed the most egress. Those require the Upstash **Usage** time
  series/logged command sizes from the affected period.

## Corrective design (not deployed)

1. Keep the 2-second local UI/status cadence, but make the Redis
   reconciliation request **revision-first**. Read a small monotonic
   account revision marker and download/decrypt the full encrypted
   history **only if its revision differs**. Update the marker and
   canonical manifest **atomically** in the same Lua CAS to guarantee
   correct concurrent-writer behavior. Include a safe legacy-missing
   marker fallback, and tests for fail-closed errors and multiple
   workers. Do **not** skip freshness checks just to save bandwidth.
2. Send conditional `not modified` or revision-only responses from
   `/api/lalm_station/sync` when no projection change is needed.
   Preserve navigation, focus, background generation, reconnect and
   cancellation behavior.
3. Measure aggregate Redis commands, request bytes and response bytes
   **per operation class**, without logging credentials, user text,
   thread IDs, or raw payloads. Capture rolling totals and unexpected
   spikes. Do not add a Redis write per metric update.
4. Consider bounded incremental persistence for chat messages rather
   than rewriting the entire history on each committed mutation,
   provided CAS, ownership, chunk integrity, and recovery are preserved.
5. Test with ~0 KB / 640 KB / 1 MB / multiple-chunk histories and two
   account sessions across separate workers; compare request/response
   byte counts at the old and new implementations.

The migration itself is complete as a fresh-start **Aiven** deployment.
This report does not claim the future low-bandwidth redesign is already
implemented.
