# Server v2.3.71 — RMCCA social participation + recovery lineage stabilization

Date: 2026-09-12

## Triggering evidence

A fresh `Hey 👋` camera log exposed three independent failures:

1. The model correctly classified the turn as brief-social but still generated meta-commentary (`This is a friendly greeting`) instead of participating naturally.
2. The camera reported `authority=unknown`, `envelope=none`, `first-send receipt=n/a`, and `RMCCA=not-captured`; recovery later reported `canonicalEnvelopePreserved=false`.
3. After an instance change/recovery, raw model capture concatenated text from two generation branches while the visible reconciler correctly kept one coherent displayed response. That made `modelText` unsafe as canonical history.

## Changes

### RMCCA social participation policy

- Advanced the cognitive policy to `rmcca-cognitive-policy-v4-social-participation`.
- Advanced the canonical envelope to `swrlz-rmcca-context-v3`.
- Social/greeting topology now explicitly requires direct participation: greet back, match conversational energy, and continue naturally.
- The policy explicitly forbids meta-descriptions such as `This is a friendly greeting`.
- Greeting cues now contribute to the social domain and conversational reference frame.

### Canonical request transport hardening

- Canonical preparation now degrades safely instead of silently disappearing if history analysis or clock diagnostics fail.
- The canonical layer exposes envelope validation and preserves a request-ID keyed receipt until terminal completion.
- Background transport verifies that the outgoing payload has the current canonical envelope and retries canonical preparation if validation fails.
- Initial-send and recovery camera metadata now records canonical preparation state, envelope identity, transport errors, request attempt, and generation branch identity.

### Recovery-safe canonical model text

- Each generation attempt now has a branch identity (`requestId:branch-N`).
- Recovery increments the branch and records which branch is active.
- The context camera resets raw capture when generation moves to a new branch instead of concatenating original and regenerated streams.
- On terminal completion, `modelText` is taken only from the winning generation branch and is marked `canonicalModelTextSource=winning-generation-branch`.
- This keeps visible reconciliation and canonical history aligned after restart/recovery.

## Concurrency reconciliation

- Transaction baseline: Server `2.3.70`, Chat `1.4.64`.
- Immediately before version assignment, both authorities were re-read and remained unchanged.
- Safe assignment: Server `2.3.71`, Chat `1.4.65`.
- LALM engine remains `2.1.26`; no R39 engine source was changed.

## Verification / deployment state

- Runtime source updated on branch `runtime` only.
- Production deployment: NONE requested.
- Server restart: NONE requested.
- Acceptance remains camera-driven.

Expected next greeting receipt:

- `cognitiveAuthority=chat_context_canonical`
- `canonicalEnvelopeId=swrlz-rmcca-context-v3`
- `firstSendReceiptAttached=true`
- `RMCCA topology=social-participation`
- `referenceFrame=conversational`
- `canonicalEnvelopePreserved=true` if recovery occurs
- one `winningGenerationBranchId`
- `modelText` contains only the winning branch, with no duplicated pre-recovery prefix
- generated greeting participates naturally rather than describing itself

## Relevant lineage

- Canonical RMCCA v4 / resilient envelope: `6968b1489732df12609556d5a80e23305e9ff497`
- Background canonical transport + branch lineage: `623c4ece6b2595a796c51130d5cea8df8e8fa0cb`
- Branch-aware context camera: `70863beab2cd9ad2463a6568137dda3073e135d1`
- Server version authority: `0ef58926f166f1d5aee8aeb4560cf50244887e15`
- Chat version authority: `134bc2ef18c76739a779ccc9d223d7ae3cea75c0`
