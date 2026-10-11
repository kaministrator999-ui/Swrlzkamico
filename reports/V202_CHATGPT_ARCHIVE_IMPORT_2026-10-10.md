# v202 — encrypted Google-owned ChatGPT conversation import

**Date:** 2026-10-10 US Central / 2026-10-11 UTC.
**Status:** deployed to existing Hugging Face Space; actual user ZIP import and end-user mobile acceptance pending.
**Canonical source:** `feature/google-chatgpt-archive-import-v202`, `e1e2793b851ea8b1113b8438a16d3c71ea62d055` based on accepted v201 `ffb9a9777f878b911b01e2a18c003f7123b43ce2`.
**Review:** [draft PR #91](https://github.com/kaministrator999-ui/Swrlzkamico/pull/91).

## User-requested behavior

The existing §wyrlz Chat Settings receives a **ChatGPT imports** pane. Verified Google-account users may select an official ChatGPT conversation-export ZIP, upload it in ordered 256 KiB chunks and receive live progress while server-side, selected-branch user/assistant text conversations are saved in independent encrypted per-conversation Redis records. A later export merges by original ChatGPT conversation ID and message ID, adding only missing messages and preserving earlier data and existing titles when the reimport is older. Reimports of the same export are idempotent. Indexed imported conversations are viewable in the settings pane, and can be explicitly deleted individually or all-at-once, without altering native §wyrlz chats. No imported text is inserted into LALM prompts/training, public documents or GitHub.

## Engineering ownership

- `hf_space/chatgpt_archive.py`: separate Google-derived archive namespace, Fernet encryption, account validation, per-thread optimistic Redis CAS, incremental message union, per-user index, constrained ZIP/JSON/parser, read/list/delete, no silent truncation
- `hf_space/chatgpt_upload_session.py`: bounded temporary single-account ZIP staging, chunk-size/offset enforcement, stale-upload cleanup
- `hf_space/station.py`: authenticated account and same-origin CSRF guard, streamed import completion and archive endpoints, existing account and native session preserved
- `chat/§wyrlz/assets/chatgpt-archive-import-v1.js`: optional settings panel, chunk upload progress, private read-only archive browsing and deliberate deletion
- `scripts/prepare_hf_space.py`: packages new asset through the existing HF source staging path
- `hf_space/test_chatgpt_archive_import_v202.py`: synthetic account isolation, chunking, malformed ZIP, duplicate/newer/older export merge and deletion tests
- Existing GitHub-account and offline HF candidate workflows extended; no new infrastructure or deployment mechanism

## Privacy and import evidence

User-provided local ZIP (~54.6 MB, 27 `conversations-xxx.json` files) was analyzed in the conversation only; **raw export, private messages, ZIP and attachment contents were not committed to GitHub, uploaded as CI artifacts, or uploaded to the production Space**. Approximately 2,608 unique conversation IDs were identified; 52 text-empty/unsupported selected-branch conversations are reported as skipped. The real ZIP has not been imported into any user's account. Images, attachments, audio, hidden reasoning, and regenerated alternative branches are not imported by this version. Imported conversation history is read-only and separate from native Chat model context.

## Static and deployment proof

- [GitHub account / new archive regression #38104650846](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38104650846) **SUCCESS** on exact candidate SHA
- [HF candidate offline #38104650819](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38104650819) **SUCCESS** on exact candidate SHA
- [HF candidate PR #38104653415](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38104653415) **SUCCESS** on exact candidate SHA
- [Guarded HF deployment #38104708520](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38104708520) **COMPLETED/SUCCESS** via `main:.deploy/HF_SPACE_REQUEST.txt` trigger `35661f9ecf4c7b3c8d001a641a03de8f068dd60c`, `SOURCE_REF=feature/google-chatgpt-archive-import-v202`, fresh nonce `2026-10-10-v202-chunked-google-history-import-001`
- Exact deployed Space revision **`d5d79c6eed41ad3a8e8fb51eddc63cecfac426bd`**; prior revision preserved for rollback **`dfd7986e5a84bd2097342cb12003dfecc82dfc9d`**. `hf-release-checkpoint` artifact #11689133467 records `verificationState=DEPLOYED_UNVERIFIED`, `knownGood=false` pending runtime/mobile acceptance. No second Space or Vercel deployment.
- Initial CI failed when an obsolete assertion expected the former one-request import endpoint after chunked transport was introduced. The assertion was corrected and both CI suites rerun successfully. Earlier failures remain visible in Actions history.

## Registered version resolution

- Repository Work **1.0.140 → 1.0.141** (`runtime:versions/repository-work.txt`, commit `c1215317ecf53ed4f5ffefa3c74eb5a23fa63bbc`)
- Server Runtime **2.3.352 → 2.3.353** (`runtime:versions/server-runtime.txt`, commit `1695da345378782801170496392551d0c471a816`)
- Web Chat **1.5.95 → 1.5.96** (`runtime:versions/web-chat.txt`, commit `cb813dde057e57c15d11572080eb8b913bfa31ea`)
- Google Account **1.0.9 → 1.0.10** (`runtime:versions/google-account.txt`, commit `ffdee1816a69a57f92e54d4f17f9247da9bb00a5`)
- LALM Engine **2.1.180**, Online Research **1.0.30**, Deployment Control **1.0.41**, Runtime Manifest **152**, and `runtime:VERSION.txt` unchanged. Version files/registry read back post-mutation.

## Honest remaining verification

Production upload success is verified; actual signed-in Chat settings presentation, 55 MB/2,608-conversation upload, account-specific Redis storage quota/throughput, archive list/read/delete from Android, refresh/relogin persistence and newer export reimport against that actual user account remain **UNVERIFIED**. Independent HTTP probe of the new HF Space could not be completed from the current tool environment. The user must choose the private ZIP in their authenticated Chat Settings (it was not automatically transmitted).

The current implementation is a **first read-only archive**, not restoration into native Chat threads or automatic use as inference context. Any later promotion/replay/search interface must be separately governed and user-authorized.
