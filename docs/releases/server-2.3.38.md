# Server 2.3.38 — Live Code Artifact Streaming Correction

Date: 2026-09-11

## Module state

- Server Runtime: **2.3.38**
- Web Chat: **1.4.33**
- LALM Engine: **2.1.25** — unchanged
- LALM UI: unchanged
- Stream contract: unchanged

## Why this follow-up exists

Server 2.3.37 introduced live Code Artifact construction while an assistant response is still streaming. Review of that first implementation found two presentation-state defects before final browser acceptance: live tab actions could use an earlier captured stream value, and the live artifact did not yet expose the same complete controls as the finished artifact.

## Correction

- Live file-tab selection now always uses the latest streamed response state instead of an older captured snapshot.
- The artifact remains mounted while code grows inside it.
- Live artifact controls now match the completed artifact more closely: Copy all, Export all, per-file Copy, and per-file Download are available during generation.
- Multi-file tabs continue to appear as additional fenced code blocks arrive.
- Explanatory prose streams into the nested Details area after the code block closes.
- Finalization synchronously applies the canonical finished-artifact decorator before the completed assistant article replaces the live article, avoiding a raw-markdown presentation frame at completion.

## Verification state

- Runtime source updated on the `runtime` branch.
- Canonical authorities are Server Runtime 2.3.38 and Web Chat 1.4.33.
- LALM Engine remains 2.1.25 because inference behavior was not modified in this event.
- Source-level verification complete.
- Final mobile/browser visual acceptance remains pending user test: the artifact should appear as soon as the model begins a fenced code block, fill live, add Details while prose arrives, and remain visually coherent when generation completes.

## Deployment state

- Stable deployment required: **NO**
- Server restart required: **NO**
- Path: runtime-hot only

## Relevant lineage

- `web/chat_stream_incremental.js` — corrected live tab state and live export/download controls.
- `web/chat_code_artifacts.js` — canonical completed-artifact decorator exposed for synchronous final handoff.
- `versions/web-chat.txt` — 1.4.33.
- `versions/server-runtime.txt` — 2.3.38.
