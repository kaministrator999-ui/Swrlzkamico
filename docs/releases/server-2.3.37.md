# Server 2.3.37 — Live Code Artifact Streaming

Date: 2026-09-11

## Module state

- Server Runtime: **2.3.37**
- Web Chat: **1.4.32**
- LALM Engine: **2.1.25** — unchanged
- LALM UI: unchanged
- Stream contract: unchanged

## User-observed problem

A successful coding response was generated as plain streaming text first, then transformed into the polished Code Artifact container only after generation completed. This created a visible presentation snap: the user watched one layout during generation and a different layout after completion.

The acceptance log also confirmed that the underlying response itself was now correct and complete: it emitted a fenced C++ block, used the correct Fahrenheit-to-Celsius formula, handled user input, explained both the conversion function and `main`, and passed strict coding checks.

## Change

- Chat now recognizes fenced code while an assistant message is still streaming.
- As soon as the first fenced-code marker arrives, the already-mounted assistant bubble is promoted in place into the normal Code Artifact hierarchy.
- The artifact header, file metadata, code workspace, file tab(s), copy controls, and Details section are maintained during generation instead of being created only after completion.
- Code text is updated inside the existing live code pane; the whole conversation and assistant article are not rebuilt for each token.
- Additional fenced code blocks can become additional live file tabs in the same artifact.
- Explanatory prose after the code fence is streamed into the artifact's Details area while generation continues.
- On completion, Chat synchronously applies the canonical finished-artifact decorator before replacing the live article, preventing a one-frame fallback to raw markdown/code between the streaming and completed presentations.

## Verification state

- Runtime source was updated on the `runtime` branch.
- Canonical version authorities advanced to Server Runtime 2.3.37 and Web Chat 1.4.32.
- LALM Engine remains 2.1.25 because no inference behavior changed in this event.
- Final visual acceptance remains browser-driven: confirm that the artifact shell appears during generation, code grows inside it live, Details appears as explanatory prose begins, and completion does not visibly restyle the response.

## Deployment state

- Production deployment: **NONE**
- Server restart: **NONE**
- Path: runtime-hot only

## Relevant lineage

- `web/chat_code_artifacts.js` — synchronous finished-artifact decorator exposed for the streaming handoff.
- `web/chat_stream_incremental.js` — live code-fence parsing and in-place artifact streaming.
- `versions/web-chat.txt` — 1.4.32.
- `versions/server-runtime.txt` — 2.3.37.
