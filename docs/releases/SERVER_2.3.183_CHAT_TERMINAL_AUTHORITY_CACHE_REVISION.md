# Server 2.3.183 — Chat terminal authority + runtime asset revision

**Web Chat:** 1.5.42  
**Runtime manifest:** 107  
**Deployment:** NONE  
**Restart:** NONE  
**Path:** runtime-hot

## Incident

Fresh Android browser reproduction after Server 2.3.182 still showed completed assistant turns rendering `No committed assistant text was received.` The prior source repair existed on `runtime`, but the cooperative Chat loader derives all functional-child cache keys from the loader URL revision. The manifest revision had not advanced after terminal-integrity v2 was authored, so a browser/CDN could continue requesting the old terminal-integrity asset under the unchanged revision.

A second authority defect existed in turn-integrity v3.1: `terminalConfirmed=true` was enough for stream terminal authority even when the terminal snapshot contained no assistant text. Terminal-integrity v2 intentionally permits an empty `completed-awaiting-text` snapshot while waiting for canonical text, so turn-integrity could prematurely settle that empty state as a completed response.

## Change

- Turn-integrity advances to v3.2 and requires non-empty terminal text before stream terminal authority is accepted.
- Transcript terminal authority likewise requires non-empty canonical assistant text before terminal UI settlement.
- Terminal authority metadata now identifies terminal-response-integrity-v2.
- Runtime manifest advances from 106 to 107. The cooperative loader receives the new revision and therefore requests its functional children, including terminal-integrity v2 and turn-integrity v3.2, under a new cache key.
- The existing terminal-integrity v2 and same-tab monotonic reconciliation remain in place; this event makes their intended revision deterministic for a fresh Chat load and closes the empty-terminal authority hole.

## Intended invariant

A completed marker without assistant text is not sufficient evidence for the Mask to settle a successful assistant response. Non-empty assistant text must be present in canonical/transcript or matching terminal evidence before terminal UI authority can finalize the turn. Once non-empty completed text exists, later empty snapshots may not downgrade it.

## Verification

Repository mutation completed on `runtime`. Authoritative versions were re-read at the commit boundary and remained Server 2.3.182 / Web Chat 1.5.41 before assignment. They were advanced to Server 2.3.183 / Web Chat 1.5.42. No Vercel deployment or restart was performed. Live browser reproduction remains required before production acceptance is declared.
