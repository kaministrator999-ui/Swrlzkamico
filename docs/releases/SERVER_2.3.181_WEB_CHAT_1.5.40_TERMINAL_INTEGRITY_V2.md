# Server 2.3.181 / Web Chat 1.5.40 — Terminal Integrity v2

## Scope
Runtime-hot Chat Mask repair for completed assistant text oscillating between the canonical non-empty server transcript and an empty terminal-integrity snapshot.

## Evidence
Production conversation-camera captures showed completed assistant messages with non-empty canonical text while `terminalIntegrity.terminalSnapshot.text` was empty and `terminalConfirmed=true`. Subsequent reconciliation could therefore restore the empty snapshot over valid committed text.

## Fix
- Terminal Integrity contract advanced to `terminal-response-integrity-v2`.
- Empty terminal snapshots are never authoritative restoration evidence.
- A completed non-empty canonical/visible assistant message promotes its text into terminal evidence when the prior snapshot is empty.
- Reconciliation is monotonic: non-empty completed text cannot be replaced by an empty terminal snapshot.
- Non-empty disagreements merge conservatively instead of allowing destructive empty downgrade.
- Camera/client diagnostics emit promotion/preservation events for future tracing.
- Genuine failed/cancelled turns are not converted into successful completed text.

## Versions
- server-runtime: 2.3.181
- web-chat: 1.5.40
- stream-contract: unchanged
- lalm-engine: unchanged

## Deployment
NONE.

## Restart
NONE.

This is a runtime-hot Web Chat change and does not require a Vercel deployment or server restart.
