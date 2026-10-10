# §wyrlz Google-owned conversation history — guarded release handoff

**Date (UTC):** 2026-10-10.

## Outcome and scope
**Source verified / unit CI successful / full HF offline CI successful / guarded Space upload successful / private live-account persistence acceptance PENDING.**

Live user observation: repeated continuous Hugging Face deployments left no old thread history worth backing up. User explicitly confirmed that no legacy accessible chats needed preservation, lifting the export-first hold. Earlier deleted process-local conversations cannot be recovered retroactively.

Current Space: `kamiloki/Swyrlz`; exact released source `4b81dea857f55daee0f688201a937286adbfd58d`, `feature/google-durable-chat-history-v195-integration`, draft review [PR #80](https://github.com/kaministrator999-ui/Swrlzkamico/pull/80).

Guarded deploy workflow [#38021816054](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38021816054) terminal SUCCESS. Previous HF revision `0f18e6619bbaa1f3b0ddd321fa68011f4770ea82` snapshot retained as rollback. New HF revision `f8223ea42faabdbcb91cf4159f2de839de758f98` published. Checkpoint truth `DEPLOYED_UNVERIFIED`: uploading the source does not independently prove that a real signed-in Google account reloads persisted chats after restart.

## Implementation
- `hf_space/account_chat_store.py` owns encrypted account chat snapshots (whole-account, 2,200,000-byte plaintext limit; errors on overflow, no implicit TTL), per-account compare-and-set revision (atomic Upstash Redis EVAL), and encrypted 7-day session-cookie verification via the already configured `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`, `SWRLZ_GITHUB_ENCRYPTION_KEY`. These secrets remain server-side.
- `hf_space/station.py` now resolves verified Google sessions from Redis instead of `_hf_accounts`, rehydrates the account's thread catalog/message history after process replacement, stores each material state revision before presenting success, and protects against stale revisions. Anonymous sessions remain process-local. New message/assistant completion, pins, thread operations, diagnostics and exports are included.
- The deployed branch began from approved v195 native lyric reader source SHA `933533e00d603e60044e86a58595ac415a8523c3`; `chat/§wyrlz/index.html`, `hf_space/lfm2_700m_engine.py`, native lyric reader and story-planner logic remained unchanged from v195.
- Source CI [Google account and persistence #38021545880](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38021545880): SUCCESS.
- Full candidate CI [#38021548935](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38021548935): SUCCESS.
- Runtime version authorities advanced: Repository Work 1.0.132; Server Runtime 2.3.346; Google Account Architecture 1.0.9. LALM Engine, Web Chat and unrelated modules unchanged.

## Required live acceptance
1. User opens the Space after redeploy, signs into Google again if older process-local session vanished.
2. Sends a message in a **new** chat and waits for final assistant message.
3. Refreshes: verify same thread, both messages, title and current-thread selection.
4. Logs out and back into same Google account: verify the same history. Test second Google account cannot see first user's history.
5. When feasible, restart Space or perform next normal guarded deploy, sign back in: verify the exact same thread and message history exists.
6. Confirm pinned messages/renames/deletes persist and account export reports `encrypted-google-account-redis`.
7. Future work: 2.2MB/account snapshot cap needs chunked/sharded per-thread scalable storage; queued/in-flight inference is not durable and no retroactive import/recovery for old process-local messages.

**Do not claim ChatGPT-equivalent lifelong chat memory or completed multi-instance endurance without these checks.** Account history persistence is separate from bounded GitHub project snapshots and from model attention/context windows.

