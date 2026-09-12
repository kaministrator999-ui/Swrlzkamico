# Server v2.3.70 — RMCCA first-send receipts + natural identity framing

Date: 2026-09-12

## Outcome

This event closes the observability gap exposed by the fresh identity test and strengthens identity response framing without adding a presentation-layer suppression hack.

## Evidence that triggered the event

- Fresh thread user request: `What's your name?`
- Model output was factually correct but under-framed: `§wyrlz`.
- Raw and display text matched, proving the old leading-name suppression was no longer responsible.
- The context camera still reported `authority=unknown`, `envelope=none`, and `RMCCA=not-captured` on an initial send with no recovery attempt.
- The failure mode matched request preparation occurring before the assistant placeholder existed, causing message-local annotation to miss the first-send cognitive receipt.

## Changes

### Canonical RMCCA context

- `web/chat_context_canonical.js` now keeps a bounded request-ID keyed pending cognitive receipt for initial sends.
- The receipt records cognitive authority, canonical envelope ID, directive ID, history provenance, prompt size, and RMCCA cognitive-clock diagnostics before the request leaves Chat.
- If an assistant message already exists, the receipt attaches immediately. Otherwise it remains pending for the stream camera to attach when the matching assistant message appears.
- Pending receipts expire after ten minutes.
- Canonical envelope advanced to `swrlz-rmcca-context-v2`.
- Cognitive policy advanced to `rmcca-cognitive-policy-v3-natural-identity`.
- Identity detection now also recognizes phrasing such as `What should I call you?`.
- Identity response policy now explicitly requires a natural first-person conversational answer such as `I'm §wyrlz.` or an equivalent, and explicitly rejects a bare `§wyrlz` label unless the user specifically requests only the label.

### Camera continuity

- `web/chat_context_camera.js` now attempts to hydrate the pending cognitive receipt on every first matching stream event and again at terminal completion.
- Camera continuity summary now reports whether a first-send receipt was attached.
- This allows a clean initial request to prove RMCCA ownership without requiring a recovery event.

## Module state

- Server runtime: `2.3.70`
- Web Chat: `1.4.64`
- LALM engine: `2.1.26` unchanged

## Concurrency guard

- Work began from authoritative Server `2.3.69` / Chat `1.4.63`.
- Immediately before version assignment both authorities were re-read.
- They remained unchanged, so the event safely advanced to Server `2.3.70` / Chat `1.4.64` using the fresh authority SHAs.

## Verification / acceptance gate

- Production deployment: NONE requested.
- Server restart: NONE requested.
- Runtime-only Chat/model-context update.
- Next clean identity test should show a natural contextual identity answer rather than a bare label.
- Camera should show:
  - `cognitiveAuthority=chat_context_canonical`
  - `canonicalEnvelopeId=swrlz-rmcca-context-v2`
  - `firstSendReceiptAttached=true`
  - RMCCA topology `identity-answer`
  - reference frame `identity-context`

## Relevant lineage

- Canonical context / identity framing: `53253034318d076c64a4cebd981a0ccfa07d21bc`
- Camera first-send receipt bridge: `a66d2007d488e428926a4983799c6bf36e3c8ce2`
- Server version authority: `f1ac6dcc53fd6a9b9d61e134e6b93e28761a1e4d`
- Chat version authority: `7711a90a00c9690c3c1fb48c47941983663fc45f`
