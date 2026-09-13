# Server Runtime 2.3.96 — polished-first continuity

## Authorities

- Server Runtime: 2.3.95 -> 2.3.96
- LALM Engine: 2.1.33 -> 2.1.34
- LALM revision: `2.1.34-hot-polished-first-continuity-v24`
- Web Chat: 1.4.78 -> 1.4.79
- Runtime web manifest: 16 -> 17
- Source branch: `runtime`
- Deployment: NONE
- Restart: NONE

## Acceptance evidence that motivated the event

The long coding/retrieval benchmark proved batched prefill was healthy (~11 prompt tok/s on 96-token native blocks), but exposed five remaining defects: repeated recovery branches, RMCCA transport not visible in the camera, completion-budget extension beyond the advertised 448-token coding ceiling, malformed Markdown/`alt` degeneration, and streaming code-artifact decoration before the answer was terminal.

## LALM v24

`runtime_hot/r39_engine_v24.py` layers over pinned v23 and preserves the v22 batch/native execution path.

Changes:

1. Rephrases control policy so internal labels such as `Coding Mode`, `Output Budget`, `Response Budget`, and `Priority` are explicitly non-user-facing.
2. Parses explicit numeric message constraints such as `at most N retrieved older messages` and reinforces them before generation.
3. Lets a substantial response with a balanced code block accept EOS instead of forcing hundreds of extra tokens for `complete-code` / `code-explanation-input-mismatch` warnings.
4. Detects repeated `alt` fragments, empty Markdown-fence bursts, malformed fence loops, and low-entropy repetition before emitting the triggering chunk.
5. Enforces the automatic coding ceiling at decode step 448 in the outer stream controller, so the underlying completion verifier cannot extend to 512/576.
6. Keeps batched-prefill/native kernels unchanged.

## Chat continuity v2

`web/chat_background_resume_v2.js` replaces the old background-resume + recovery-overlay pair in the live manifest.

Policy:

- while the original browser stream/controller is still alive, background/foreground transitions do not start a second generation;
- if a stream ends after any visible assistant text, that exact partial is committed and automatic regeneration stops;
- only a request that ended before its first visible assistant token gets one safe retry;
- after that retry, no repeated branch loop is allowed;
- the canonical RMCCA/time carrier is attached in the active transport layer before the request is stored/sent, so the same body used for recovery also contains the carrier;
- context-camera metadata records the carrier and the `single-visible-generation` continuity policy.

## Streaming artifact stability

`web/chat_stream_artifact_stability.js` disconnects the eager artifact observer and decorates code only when:

- the assistant message is `complete`; and
- Markdown fences are balanced.

While streaming, blank/incomplete `pre` elements are hidden instead of becoming empty code-artifact cards. This prevents the visible response from morphing through empty boxes while tokens are still arriving.

## Runtime manifest

Manifest v17:

- replaces `web/chat_background_resume.js` with `web/chat_background_resume_v2.js`;
- removes `web/chat_recovery_integrity.js` from the active script chain;
- adds `web/chat_stream_artifact_stability.js` immediately after code-artifact support.

The superseded runtime files remain in repository history for rollback/lineage.

## Verification before publication

- `r39_engine_v24.py` passed local Python syntax compilation.
- `chat_background_resume_v2.js` passed `node --check`.
- `chat_stream_artifact_stability.js` passed `node --check`.
- Version authorities were re-read after runtime mutations and still read Server 2.3.95 / LALM 2.1.33 / Web Chat 1.4.78 before assignment, so this event had no detected concurrent-version collision.

## Rollback

Rollback can restore:

- `runtime_hot/r39_engine.py` to the v23 entrypoint / v23 manifest revision;
- runtime web manifest 16 to restore the old background-resume + recovery-integrity chain.

Do not delete the v24/v2 source files during rollback; they are durable lineage evidence.
