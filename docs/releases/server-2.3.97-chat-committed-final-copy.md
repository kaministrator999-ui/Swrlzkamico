# Server Runtime 2.3.97 — Committed Final-Copy Streaming

## Scope

Runtime-hot Chat event only. No `main` mutation, deployment request, or restart.

## Versions

- Server Runtime: `2.3.96` → `2.3.97`
- Web Chat: `1.4.79` → `1.4.80`
- LALM Engine remains `2.1.34-hot-polished-first-continuity-v24`

## User-visible invariant

Anything visible in the assistant response is committed final output. Raw model deltas are not authoritative UI state.

The active Chat path now uses a private staging tail before visibility:

`raw DELTA -> private staging -> coherence/degeneration/control-leak gate -> commit -> message.text -> UI`

`message.text` is the append-only final-copy buffer. Once text enters it, automatic recovery or rendering must not remove or replace it.

## Changes

- Added `web/chat_committed_output.js`.
- Manifest advanced to v18 and loads the committed-output gate immediately after incremental stream rendering.
- Removed the terminal-only artifact-stability overlay from the active manifest because it conflicted with the final-copy-in-progress invariant.
- Prose commits at coherent sentence/paragraph/line boundaries instead of exposing raw token fragments.
- Code commits at complete line boundaries while an open fenced artifact is in progress.
- Known internal control-label leakage is filtered before visibility.
- Repetitive/malformed staged tails are discarded before they can enter the visible response.
- Terminal staging is committed only if coherent; an unfinished final code fence may be presentation-closed and recorded in message metadata.
- Existing single-visible-generation recovery from Web Chat 1.4.79 remains active and now persists only committed text.
- Existing RMCCA carrier transport remains active.

## Preserved architecture

- Batched/vectorized R39 prefill remains unchanged.
- LALM v24 generation controls remain unchanged.
- Stable server/API/deployment files remain unchanged.
- Runtime branch remains the durable live source of truth.

## Acceptance targets

A repeated long coding benchmark should show:

1. Visible response text grows monotonically and never rewrites earlier visible content.
2. Rough token fragments do not appear and then disappear.
3. Code artifacts may appear while being written, but committed code lines remain the same lines in the final artifact.
4. Recovery after visible text preserves the exact committed partial rather than regenerating it.
5. Exported/camera `message.text` matches the visible committed response.

## Rollback

Rollback consists of restoring manifest v17 (removing `web/chat_committed_output.js` and restoring the previous active script sequence) and returning Server Runtime/Web Chat authorities to the prior release through a new versioned correction event rather than erasing this lineage.
