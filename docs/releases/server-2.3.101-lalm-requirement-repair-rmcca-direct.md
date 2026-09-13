# Server Runtime 2.3.101 — requirement-enforced repair + RMCCA direct transport

## Versions

- Server Runtime: 2.3.100 -> 2.3.101
- LALM Engine: 2.1.36 -> 2.1.37
- LALM revision: `2.1.37-hot-requirement-repair-rmcca-direct-v27`
- Web Chat: 1.4.83 -> 1.4.84

## Runtime changes

- Added `runtime_hot/r39_engine_v27.py` and activated it through the hot entrypoint/manifest.
- v27 converts the requirement ledger into artifact acceptance checks, including Python AST syntax validation, required recent-window semantics in code, retrieved-older caps in code, lexical-score implementation checks, and unsupported-percentage completion checks.
- v27 performs at most one bounded correction pass inside the same generation session before reporting final failure.
- Added `web/chat_committed_output_v3.js` and activated runtime page manifest v21.
- Committed Output v3 keeps requested code fences private until the complete artifact passes requirement-aware validation. Rejected rough code never enters user-visible final-copy text; a valid repair artifact can become the first visible code artifact.
- Broadened unsupported measurement cleanup so percentage claims are sanitized before visibility when the user supplied no measured percentage.
- Batched/vectorized prefill remains unchanged.

## Stable server preparation

- Added `api/chat_rmcca_passthrough.py` on `main`.
- Prepared stable Server 2.3.101 entrypoint to install validated first-class RMCCA/time-context passthrough after resumable-session normalization.
- Direct `swrlzCognitiveContext` becomes the primary transport. The compact history carrier remains a compatibility fallback.

## Evidence motivating this event

The preceding benchmark correctly parsed `recentWindow=6`, `maxRetrievedOlder=4`, runnable Python, example, and prefill-explanation requirements, but generated code failed to implement the six-message recent window and invented an unsupported 70% prefill claim. The final guard caught the missing recent-window requirement only after generation. The context camera also reported `RMCCA=not-captured`.

## Deployment boundary

- Runtime v27 and Web Chat 1.4.84 are runtime-hot and require no stable deployment.
- The direct RMCCA preservation module and stable Server 2.3.101 entrypoint are prepared on `main` but are **not deployed by this event**. Production deployment requires explicit user approval.

## Rollback

- Restore `runtime_hot/r39_engine.py`/manifest to v26 and runtime page manifest v20 to return to LALM 2.1.36 / Web Chat 1.4.83.
- Stable rollback is removal of the `chat_rmcca_passthrough` install and Server 2.3.101 version change before any production deployment.
