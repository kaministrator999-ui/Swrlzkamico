# Server 2.3.254 — R39 v72 coding inference failure-detail camera

## Status

**Source complete / static verified / superseded diagnostically by v73 before live v72 candidate evidence.**

- Overall Server event: `2.3.254`
- LALM Engine: `2.1.84`
- Revision: `2.1.84-hot-coding-inference-failure-detail-v72`
- Chat: `1.5.75` unchanged
- Deployment Control: `1.0.8` unchanged
- Deployment / restart: **NONE**

## Triggering evidence

The authenticated v71 coding request `web:mu5zycye:4201205958924473599` proved that both the first coding candidate and its bounded repair terminated as `FAILED / inference-failed` after exactly two decode steps and nine visible characters. The v71 terminal camera correctly separated this from EOS, completion-gap acceptance, degeneration, Chat transport, and the v70 fence-normalization path, but it intentionally collapsed the underlying base-generator exception into a coarse `inference-failed` class.

That left one real observability gap: the base v17 generator already included a bounded Python exception type/message in its `FAILED` event, but v70/v71 did not preserve that detail at the candidate boundary.

## Architecture reconciliation

This was a **Brain/LALM diagnostics event**, not another generation or repair owner. v72 preserved v71/v70/v69 response semantics and wrapped the existing v27 candidate-generator boundary only to retain the already-produced terminal failure classification.

No Chat persistence/transport, server operational authority, deployment infrastructure, or programming completion semantics changed.

## Change

v72:

- hydrates immutable v71;
- wraps the inherited `_V24_GENERATE_FOR_V27` candidate boundary used by both first-pass and bounded-repair generation;
- emits bounded `coding-inference-terminal-detail` evidence for failed/cancelled candidates;
- records only failure category, Python exception type, and a short sanitized detail preview;
- logs no prompt, response body, secret, or hidden reasoning;
- preserves the original candidate event unchanged;
- includes a deterministic parser/self-test for the bounded failure-detail contract.

## Verification

The v72 source, hot entry, manifest, and module authorities were published. Its diagnostic behavior was source/static verified. A fresh authenticated v72 candidate failure was not observed before source inspection of the inherited sampler exposed the deterministic two-token cause directly; v73 therefore superseded the diagnostic-only edge while preserving v72 in its lineage.

## Lineage

- v72 source: `3c41765183650793ad6c4c552c2d2a2cc5db6056`
- v72 hot entry: `0447348f81d1d3b9b00e50a06327fd103dcb459a`
- v72 manifest: `bafb39d94fee30e98c2904b26eb6ce1963d5839e`
- LALM authority: `6d065f71b7b0215a69cf68fe243cd3a931a55461`
- Server authority: `261ca08045078516aa37750b8ae07c2103d0e312`

## Outcome

v72 closed the observability gap without changing generation semantics. The subsequent v73 event identified and repaired the actual inherited two-token decode fault rather than adding another semantic workaround.
