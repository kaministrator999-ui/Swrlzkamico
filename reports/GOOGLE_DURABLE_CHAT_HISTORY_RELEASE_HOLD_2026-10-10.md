# §wyrlz Google-owned durable chat history — v195 candidate handoff

**UTC 2026-10-10 — SOURCE COMPLETE / CI VERIFIED / NOT DEPLOYED**

## Root cause, directly inspected
The live `hf_space/station.py` currently maps `_hf_accounts` and `_sessions` to in-process Python dicts. Although the separate GitHub OAuth tokens and source-project snapshots are already encrypted in Upstash Redis, full conversations and Google login cookie sessions are NOT saved there. On any Hugging Face Space restart, previous process-local conversations are lost.

## Source
- Starting approved release source: v195 `feature/lyric-native-reader-planner-fallback-v195`, SHA `933533e00d603e60044e86a58595ac415a8523c3`.
- Canonical review branch `feature/google-durable-chat-history-v195-integration`, draft [PR #80](https://github.com/kaministrator999-ui/Swrlzkamico/pull/80). Original candidate PR #79 based on v194 was superseded by v195 integration.
- New `hf_space/account_chat_store.py`: encrypted account-owner keys, 7-day encrypted Redis Google session, no-TTL complete account chat snapshot, 2.2MB raw limit (explicit error, no silent truncation), Redis Lua EVAL version CAS. Uses existing Space Upstash REST and SWRLZ_GITHUB_ENCRYPTION_KEY secrets. No new app/provider config.
- `hf_space/station.py`: restored verified Google login, stable same-owner session after process restart, full message/thread/pin/artifact catalog restore, durable mutation/send/completion, confirmed persistence before terminal response, logout revocation, account export reflects durable tier; anonymous state remains volatile.
- Existing v195 `chat/§wyrlz/index.html`, `hf_space/lfm2_700m_engine.py` and lyric planner files preserved byte-for-byte.

## Tests
- [GitHub account CI #38021475553](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38021475553): **SUCCESS** on latest source, checks Google login restore/revoke, encryption, account isolation, revision CAS collision, full message restore after simulated process restart and account wiring.
- [HF Candidate Offline Validation #38021479030](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38021479030): **SUCCESS** on latest source.
- Upstash REST EVAL Lua scripting is supported by official Upstash REST Redis documentation; live Redis calls, production session restore, multi-instance behavior and browser UI remain unverified.

## Release HOLD — requires user backup first
**Do not deploy yet.** The existing server has never persisted past chat transcripts; a release cannot reconstruct already-lost process-local threads. Ask user to open the current browser Chat and use **Download dragon Chat JSON** before the next Space deployment. That export is a backup, not an implemented in-app import. If earlier process-local chats are already gone, only previously downloaded exports may survive.

After user backup/explicit approval, recheck other branches and guarded deployment nonce, deploy through existing `main:.deploy/HF_SPACE_REQUEST.txt`, verify rollback snapshot, record final Space SHA, then do live login → multiple thread messages → reload/log out/log back in → re-deploy → thread/message reconstruction. Verify users cannot read each other's history. Advance independent version authorities and Roadmap FINISHED only after actual release evidence.

## Known limitations to resolve after first smoke test
- Active/queued inference is NOT durable; a restarted generation cannot be resumed; only prior accepted prompts and completed replies persist.
- The first candidate stores a bounded whole-account snapshot (2.2MB plaintext) rather than a scalable per-thread/append-only log. Overflow blocks writing explicitly; extend with sharded records and pagination for large long-lived archives.
- No legacy `swrlz-dragon-chat.json` import pathway in Chat UI yet; address migration separately when desired.
