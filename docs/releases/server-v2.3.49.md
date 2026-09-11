# Server v2.3.49 — 2026-09-11

## Module state

- Server Runtime: **v2.3.49**
- Web Chat: **v1.4.44**
- LALM Engine: **v2.1.25** unchanged

## Changes

- Added deterministic per-turn intent classification in the Chat request layer: `social`, `coding`, or `general`.
- Social turns now carry an explicit no-unrelated-code instruction so a greeting or emoji cannot inherit programming behavior from a prior/general coding directive.
- Coding-only guidance is attached only to turns that actually contain programming intent.
- Replaced the long mixed-purpose Chat response directive with one compact stable directive shared by every turn.
- User turns in both `prompt` and `history` are normalized deterministically with the same intent annotation. This keeps the rendered conversation prefix byte/token-stable across later turns so the existing LALM conversation checkpoint matcher can reuse the previous recurrent state instead of missing because the current request was decorated differently from historical copies.
- Background-resume requests pass through the same normalization path, preserving the existing authenticated reconnect/replay behavior.
- Existing recovery reconciliation, bounded activity history, code-artifact rendering, and LALM engine behavior remain otherwise unchanged.

## Failure / evidence addressed

- Camera evidence showed a plain `👋` turn generating an unrelated Python `greet()` snippet and explanation.
- The same log showed follow-up turns reporting `cached 0`, indicating that conversation-prefill checkpoints were not being reused for that worker/request lineage.
- This release targets both causes at the Chat payload boundary without changing the deployed stable server or LALM engine.

## Verification state

- Source updated on `runtime`.
- Version authorities advanced to Server Runtime `2.3.49` and Web Chat `1.4.44`.
- LALM Engine remains `2.1.25`.
- No Vercel deployment or server restart is required for this runtime-hot Chat revision.
- Browser acceptance still required: refresh once, then test a fresh social turn followed by another turn in the same thread and inspect the Activity log for a conversation checkpoint hit (`reused N token(s)`) rather than `cached 0` when the request stays on a worker with the cached state.

## Relevant lineage

- Chat intent/cache normalization: `0e4a42c71bcf6421a986bb58d02ebc2d193c59aa`
- Server Runtime version authority: `8724ff27137d116f58d31d7a4af069415c91b2e5`
- Web Chat version authority: `5d7446ef6835b5c3ec417ec5e9bb0a93413a80ae`
