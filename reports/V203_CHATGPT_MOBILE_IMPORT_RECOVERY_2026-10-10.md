# v203 — Mobile-safe ChatGPT ZIP importing: browser interruption repair

Date: 2026-10-10 (America/Chicago)
Source: `feature/google-chatgpt-archive-import-v202`, final candidate `b98abc7572be719eb4a31509a19f63159f641e77`
Space: `kamiloki/Swyrlz`
Published Hugging Face revision: `5ba3d56c81003ceb89cb1d4af34de84b72a0b4a1`
Prior revision/rollback: `d5d79c6eed41ad3a8e8fb51eddc63cecfac426bd`
Guarded deployment: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38107249882 — **SUCCESS**
Google account/incremental import CI: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38107171325 — **SUCCESS**
Hugging Face candidate CI: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38107171298 — **SUCCESS**
Candidate HF workflow repeat: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38107174048 — **SUCCESS**
Deployment receipt: artifact `hf-release-checkpoint` ID `11689613536`, marking `DEPLOYED_UNVERIFIED`.

## Live failure report

The user successfully uploaded the 54.6 MiB August 30 ChatGPT ZIP in v202 and saw roughly twenty conversations indexed every 3–5 seconds until approximately 1,300 messages/threads were processed. They switched from §wyrlz Chat to the ChatGPT Android app and back. Progress stopped and disappeared on the client, with no durable in-UI completion receipt.

The root cause was the v202 `/api/chatgpt_archive/complete/{upload_id}` design: enumeration, encrypted per-conversation Upstash writes, and progress lived inside one long-lived streamed HTTP response. Browser teardown/suspension could cancel the response and cleanup the temporary ZIP. Earlier Redis commits were individually durable but the client had no restoration of progress state after navigating away. Sequential 256-KiB POST chunks created roughly ~210 requests for a ~55 MiB export.

## Repair

- `hf_space/chatgpt_import_job.py`: a new detached per-verified-Google-account job worker starts on ZIP completion, returns HTTP 202 immediately, keeps compact job progress/status under a user-hashed Redis key (7-day expiry). Account-scoped Redis claim and in-process exclusion prevent racing simultaneous imports. The import continues on the host even when the client closes the browser connection. A stale receipt is reported as interrupted, not falsely complete.
- `hf_space/station.py`: authenticated `GET /api/chatgpt_archive/status` includes the authoritative archive `storedTotal`; `GET /api/chatgpt_archive/upload/{upload_id}` reports a verified owner's temporary upload offset. New complete endpoint initiates server-owned work. Mutating DELETE and new upload init are denied while an account import is actively running. Existing CSRF/Origin checks maintained.
- `hf_space/chatgpt_upload_session.py`: chunks enlarged to 2 MiB, opaque owner-scoped upload progress; identical retransmitted chunks acknowledged after an interrupted network receipt.
- `chat/§wyrlz/assets/chatgpt-archive-import-v1.js`: after selecting ChatGPT imports in Settings, refresh persisted job state and current archive total. During processing, poll every three seconds while that pane is active; returning to the page reconnects. Show terminal completion/error/interrupted receipt and current stored total; render total even for old v202 partially completed imports. Persist only the upload ID/file-size/name/last-modified marker locally and resume transport from server-declared offset when the user reselects the same ZIP; actual ZIP file bytes are never placed into browser storage.
- `hf_space/test_chatgpt_archive_import_v202.py`: verifies 202 detached acceptance, complete status after HTTP response closes, authoritative stored count, duplicate retry acknowledgments, owner isolation, encrypted per-message deduplication and data retention.

## Limits and recovery

- Previously saved user/assistant text messages are encrypted in Redis and remain available even when the old v202 stream ended. No private user's actual saved count could be read without their signed-in session; approximately 1,300 displayed as processed is **not** proof that exactly 1,300 persisted.
- The old v202 completed transport ZIP may already have been deleted when its streaming request was cancelled. Retrying requires selecting the original file again; deduplication skips already-stored IDs.
- Detached workers and staging files are independent of browser/tab lifetime but are still process-local: a Hugging Face Space restart or crash can interrupt the job. Persisted conversation records and the progress receipt survive; on next login an interrupted job can be retried with the same file safely. This release does **not** implement restart-persistent object storage or a fully durable external job queue.
- The read-only ChatGPT import archive remains separate from native §wyrlz Chat threads and from LALM memory/training; no automatic injection of private imported contents.
- The 2,608 original unique conversation IDs include 52 selected-branch empty/non-text-only threads intentionally counted as unsupported; most 2,556 text-bearing threads can be imported if the server's encrypted store accepts all records. End-to-end full 55 MiB owner import and Android navigate-away acceptance remain to be verified on the deployed app.
- Deployment workflow validated and published the candidate, **not** an authenticated end-to-end live 2,608-conversation import.

## Module version impact

- Repository Work: `1.0.141 → 1.0.142`
- Server Runtime: `2.3.353 → 2.3.354`
- Web Chat: `1.5.96 → 1.5.97`
- Google Account Architecture: `1.0.10 → 1.0.11`
- LALM Engine, Online Research and Deployment Control unchanged.
