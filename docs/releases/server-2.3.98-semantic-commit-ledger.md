# §wyrlz Server Runtime 2.3.98 — Semantic Commit Ledger

## Authorities

- Server Runtime: `2.3.97 -> 2.3.98`
- LALM Engine: `2.1.34 -> 2.1.35`
- LALM revision: `2.1.35-hot-semantic-commit-ledger-v25`
- Web Chat: `1.4.80 -> 1.4.81`
- Source branch: `runtime`
- Deployment: `NONE`
- Restart: `NONE`

## Why this event exists

The previous committed-output event successfully made visible assistant text append-only and stopped destructive response replacement. The next acceptance run exposed a separate semantic problem: syntactically coherent but incorrect content could still be committed as final output. Examples included exceeding an explicit `at most 4` retrieved-message limit, repeating `Output:` headings, inventing a fixed lexical score/percentage, and completing without the requested runnable Python implementation while the server still described coding checks as passed.

The same camera evidence also showed RMCCA transport was still not captured on the real request path (`canonicalRequestPrepared=false`, `rmccaCarrierAttached=false`), so this event adds an explicit canonical transport proof/fallback layer rather than assuming the previous wrapper executed.

## LALM Engine v25

`runtime_hot/r39_engine_v25.py` preserves v24 and adds a request-derived requirement ledger.

Detected obligations include:

- maximum retrieved-older-message count,
- recent-window count,
- runnable-code requirement,
- Python-code requirement,
- architecture-first ordering,
- example requirement,
- prompt-prefill explanation requirement.

The ledger is appended to the response directive as a compact hard-obligation contract. At terminal completion, v25 validates the actual generated response. If mandatory requirements remain unmet, the engine emits a requirement-guard status and a `FAILED` terminal event instead of falsely reporting successful completion.

The existing v24 batching, hard coding ceiling, degeneration guard, native quantized execution, and continuity behavior remain underneath v25.

## Web Chat semantic committed output v2

`web/chat_committed_output_v2.js` replaces the active v1 committed-output layer while retaining the same core invariant: visible text is the append-only final copy.

Before a staged chunk becomes visible, v2 additionally checks:

- retrieved-older numeric list limits,
- duplicate structural headings,
- unsupported percentage claims when the user did not supply a percentage,
- fabricated fixed lexical-score values in lexical-scoring requests,
- known internal-control labels such as `Output Budget`, `Coding Mode`, and bare `DELTA`,
- malformed/repetitive output.

The semantic guard records rejected staged content in message metadata and leaves committed visible text unchanged.

At terminal completion, the browser independently evaluates the same high-value requirements. If the server returns `COMPLETED` while required runnable code/example/prefill/window obligations are missing, Chat converts that terminal state to `FAILED` while preserving the visible committed response for inspection.

## RMCCA transport proof guard

`web/chat_rmcca_transport_guard.js` is inserted between canonical context preparation and the background transport wrapper.

It wraps the public canonical `preparePayload` path and records which preparation path ran:

- `canonical-prepare`,
- `build-envelope-fallback`, or
- `clock-fallback`.

If the ordinary canonical preparation path fails to produce a cognitive envelope, the guard reconstructs one from the canonical context object's own envelope/clock functions. It does not introduce a competing task router. Diagnostic receipts are attached to the assistant context camera so the next acceptance log can identify the exact transport path.

## Manifest

Runtime page manifest advanced from v18 to v19.

Active Chat ordering now includes:

1. incremental stream renderer,
2. `chat_committed_output_v2.js`,
3. user-time context,
4. canonical context,
5. `chat_rmcca_transport_guard.js`,
6. single-visible-generation background transport,
7. context camera.

The previous committed-output v1 file remains in repository lineage but is no longer active in manifest v19.

## Concurrency evidence

Immediately before assigning versions, runtime authorities were re-read and remained:

- Server Runtime `2.3.97`,
- LALM Engine `2.1.34`,
- Web Chat `1.4.80`.

No concurrent version movement was observed.

## Rollback

Rollback can restore:

- `runtime_hot/r39_engine.py` to the v24 entrypoint,
- `runtime_hot/manifest.json` to revision `2.1.34-hot-polished-first-continuity-v24`,
- runtime page manifest v18,
- active committed-output script back to `web/chat_committed_output.js`,
- removal of `chat_rmcca_transport_guard.js` from the active manifest.

Historical v25/v2/guard files should remain as lineage even after rollback.

## Acceptance targets

The next fresh benchmark should demonstrate:

- one original generation branch unless the request dies before visible text,
- `committedOutputV2=true`,
- `outputVisibilityPolicy=append-only-final-copy-semantic`,
- no fifth retrieved-older list item when the limit is four,
- no repeated `Output:` placeholder headings,
- no unsupported fixed percentage or fixed lexical score claim,
- required runnable Python code present before successful completion,
- `requirementLedgerPassed=true` on successful completion,
- RMCCA camera fields showing canonical preparation path and an attached cognitive envelope,
- batch prefill behavior unchanged from the proven v22-v24 path.
