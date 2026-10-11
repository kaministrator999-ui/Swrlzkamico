# v209 — Verified Google native Chat cross-browser persistence reconciliation

Date: 2026-10-11 · Existing hosted application: `kamiloki/Swyrlz`.

## Owner-observed behavior and evidence level

User reported native §wyrlz conversations created in a second Android browser were not appearing or reliably saving in the first browser, while older native threads and the separately encrypted imported ChatGPT archive remained readable. A screenshot of the cumulative imported text-message question showed archive-count progress initially `0 of 0`, then `160 of 2,556`. That progress belongs to a distinct read-only cumulative-message counting worker; it does not mean original/imported threads are being reuploaded or automatically injected into Chat. Cumulative visible-message totals are not equivalent to latest import `addedMessages`.

This event identifies and repairs a **source-level native Chat synchronization defect**. Actual user-specific cause could additionally involve signed-in browser identity, account snapshot size limit or live storage pressure; source and CI cannot prove which condition was encountered by the owner's exact session. No private transcript, login ID or export body was committed.

## Existing architecture reused

- `hf_space/account_chat_store.py` remains the sole verified-Google native Chat encrypted Redis/CAS snapshot owner; owner is derived only from server-verified Google session.
- `hf_space/station.py` retains process-local session/generation projection but now checks durable state on authenticated idle sync, new sends, mutations and exported history, with a bounded remote-read cadence for background polling. Active local generations are not replaced mid-stream; revisions moving backward fail closed.
- `chat/§wyrlz/index.html` requests a fresh account snapshot after login or return to the visible browser, and retains an unconfirmed send's composer draft with a clear notice (including the pre-existing 2.2 MB native snapshot limit).
- `hf_space/chatgpt_archive.py`, imported content, opt-in recall, original/native stored thread bodies and model weights were not mutated. Existing imported-message cumulative count procedure is separate.
- `chat/§wyrlz/VERSION.txt` advanced `1.1.02 → 1.1.03`; clean-room camera ID changed from obsolete `1.0.91` to actual `1.1.03`. No second account storage or competing Chat route.

## Source and validation

- Isolated candidate: `fix/native-google-chat-cross-browser-20261011`, SHA `4fe3ede62a198f841adc30b1b673e2ae28ec7ed0`.
- Base: deployed v208.1 source `feature/private-account-facts-v208` SHA `6a1e55af26dcfe0dc03dafc8e8aa19d251741f36`.
- Review: [draft PR #100](https://github.com/kaministrator999-ui/Swrlzkamico/pull/100). Not merged; deployment used exact candidate branch ref.
- Account/persistence CI [#38162460190](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38162460190) **SUCCESS**, with synthetic separate-worker Google-owner read-after-write, stale CAS overwrite prevention, in-flight generation preservation and cross-account isolation.
- Offline Hugging Face candidate [#38162463967](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38162463967) **SUCCESS**.
- Mobile Chat HTML integrity [#38162463966](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38162463966) **SUCCESS**.
- Early new regression cases failed due to invalid test revision and overly literal source assert, corrected before final green candidate; these are retained in GitHub Actions history and not presented as production failures.

## Guarded terminal release

- Authorized existing request file: `main:.deploy/HF_SPACE_REQUEST.txt`, commit `1ffea8b573ce9ae89ca4084a21c26700059e0dbc`, nonce `2026-10-11-v209-native-cross-browser-preserve-001`.
- [Guarded GitHub HF run #38162562535](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38162562535): **SUCCESS**. Verified source SHA, isolated package, dependencies, R39 reconstruction, 700M budget, auth gate, existing Space snapshot, upload and checkpoint.
- New Space revision: `5a4e2286c6ff1a567680331485d836fd07d4938e`.
- Previous rollback Space revision: `645229dfbc1c4d29329c682458a9e860910a2577`.
- Release artifact: `hf-release-checkpoint` ID `11710098384`, `knownGood=false`, `verificationState=DEPLOYED_UNVERIFIED`.
- Publication succeeded; actual signed-in cross-browser Android persistence remains **owner acceptance pending**, not fabricated.

## Version authorities after real deployment

One lease-guarded atomic `runtime` tree/commit `b5d37fef0ba5eef460c74f98ae772c545239ead3` reconciled five affected registered axes:

| Module | Before | After |
|---|---|---|
| Repository Work | 1.0.148 | **1.0.149** |
| Server Runtime | 2.3.360 | **2.3.361** |
| Web Chat | 1.5.99 | **1.5.100** |
| Google Account Architecture | 1.0.12 | **1.0.13** |
| LALM Engine / Station | 2.1.185 | **2.1.186** |

Stream Contract V2, Runtime Manifest 152, Online Research 1.0.30 and Deployment Control 1.0.41 remain unchanged; CLIENT/SERVER APK registered versions remain reserved/unassigned. Version STATUS=active is declared lifecycle intent, not a substitute for verified live health.

## Exact owner acceptance (Android)

1. Open original existing Space from two browsers; verify both display the **same signed-in Google account** (profile text alone is not proof of identity).
2. In browser A, create a new non-sensitive thread with a distinctive title and wait for a finished assistant reply. Reload browser A. The thread and both messages should survive.
3. Open/refocus browser B while signed into that same Google account; allow ~10 seconds or reload. The exact A thread and messages should appear without importing anything.
4. Create a second new thread in browser B; reload B, then refocus/reload A. Both threads should appear in both browsers. A new session export should contain both.
5. If a draft is restored with a save/storage-limit warning or a revision-conflict error, retain the draft and report the exact non-sensitive error status; do not erase old chats or re-upload the imported archive merely to force refresh.

Do not claim **live fixed** until these checks succeed. Real 2.2 MB snapshot-pressure failures, worker memory concurrency during overlapping model generations, and storage availability require separate evidence if seen. Avoid destructive resets.

**Final project state:** SOURCE STATIC/CI VERIFIED / GUARDED HF PUBLISHED / USER LIVE ACCEPTANCE PENDING.
