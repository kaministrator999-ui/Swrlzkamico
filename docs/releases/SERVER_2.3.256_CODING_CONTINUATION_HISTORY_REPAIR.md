# Server 2.3.256 — Coding continuation history + proportional routing repair

## Status

**Split activation state.**

- Overall Server event: `2.3.256`
- LALM Engine: `2.1.86`
- LALM revision: `2.1.86-hot-programming-artifact-continuation-v74`
- Chat: `1.5.75` unchanged
- Stable Server history compatibility: **source complete on `main`; production deployment required; activation pending**
- LALM v74: **runtime-hot published and production hydration verified**
- End-to-end same-thread continuation acceptance: **pending stable Server deployment**
- Deployment / restart: **NONE performed by this event**

## Triggering evidence

After the live-verified v73 standalone Python response, the same thread sent:

`Can you add a error catch to that code?`

Production request `web:mu62vyb6:41632918973548127832` proved two connected failures before inference:

1. `CHAT_HISTORY_CANONICALIZED` reported `historyMessages=0` even though the request was in the same thread and the deictic phrase `that code` referred to the immediately preceding assistant code artifact.
2. With no code artifact available to cognition, the v66 programming classifier routed the short follow-up as `projectContext=existing`, `changeClass=fix`, `architectureDepth=normal`, `architectureReconciliation=true`, `diagnostics=true`, and `toolEvidenceRequired=true`.

Because that route was not standalone/lightweight, v69 context compaction did not activate. The rendered prompt expanded to 3,599 tokens / 18,724 characters, and the stable Vercel function timed out during prefill after 300 seconds. Reconnect/resume attempts reused the same request ID and could not repair the missing canonical context.

## Architecture reconciliation

This event has two canonical owners and keeps them separate:

- **Human/Server — canonical conversation history:** server-owned Redis message indexing and canonical history reconstruction.
- **Brain/LALM — programming continuation cognition:** interpreting a deictic modification of a previously generated standalone code artifact proportionally.

The browser/Mask is not made authoritative for conversation history. v73 inference/sampling is preserved; the repaired n-gram path is not the cause of this failure.

## Root cause — stable Server history

The currently deployed stable source commit `88eed351f6e768d3da544a5cd0c69aeb8f17545e` writes canonical message/thread/job indexes with the older Redis key names:

- `messages`
- `activeJobs`
- `threads`

The canonical `RedisRestChatStore` reader uses the newer key family:

- `message_index`
- `active_jobs`
- `thread_index`

The individual durable message records therefore existed and terminal persistence could succeed, while `list_messages()` looked in a different sorted-set index and returned no canonical history. That exactly matches the production `historyMessages=0` observation.

Current `main` already writes the newer key family. This event additionally adds a backward-compatible history bridge so already-written legacy-indexed messages are not stranded.

## Stable Server repair

`api/canonical_redis_state.py` on `main` now:

- preserves the current `message_index` / `active_jobs` / `thread_index` writer;
- reads both current `message_index` and legacy `messages` indexes for canonical history;
- resolves each indexed ID back to the server-owned durable message record;
- deduplicates by `message_id`, preferring the record with the latest `updated_at` if both indexes contain it;
- sorts the merged records canonically before applying the existing history filters;
- continues to exclude the current request, empty records, and `STREAMING` / `FAILED` / `CANCELLED` assistant state;
- emits only bounded count telemetry through `history-legacy-index-bridge`; no private transcript text is logged;
- does **not** promote browser/client history to authority.

Stable Server source commit: `a1667599d03585f4fb068afc485b5b79bdb34263`.

This file is outside the runtime-hot source map and therefore requires an explicit production deployment to activate. No deployment was requested or performed.

## LALM v74 repair

Immutable `runtime_hot/r39_engine_v74.py` loads live-verified v73 and changes programming-route classification only. Inference, sampling, coding completion, bounded repair, and v73's NumPy namespace repair remain inherited unchanged.

v74 adds a bounded programming-artifact continuation bridge:

- detects deictic references such as `that code`, `this script`, `the previous function`, and related forms;
- searches recent canonical user/assistant history for the nearest assistant code artifact and its preceding programming request;
- inherits that prior programming context when the current turn is a genuine continuation;
- preserves a prior standalone artifact as `projectContext=none` and `architectureDepth=lightweight` rather than promoting it to an existing repository/project;
- treats requests to **add error handling** as a feature/hardening request, not proof that an existing project is broken;
- still classifies an actual `fix/debug/repair` request as a fix and keeps diagnostics armed, but standalone artifact fixes remain lightweight and do not require project tooling;
- preserves explicit existing-project/repository language as `projectContext=existing`, including architecture reconciliation and tool evidence requirements where appropriate.

Deterministic hydration self-tests cover:

1. standalone `add an error catch to that code` continuation;
2. standalone `fix the bug in that code` continuation;
3. explicit existing-repository fix remains project-scoped;
4. direct standalone program + error-handling request remains lightweight;
5. unrelated non-programming input remains inactive.

v74 fail-closes hydration if those tests do not pass.

## Verification

### LALM v74 — live hydration verified

A fresh production `/api/chat` load hot-fetched v74 source commit `58bfd905d0d3281b6adc1669ca8482cd04cc300c` and emitted:

- `hotServerVersion=2.1.86`
- `hotRevision=2.1.86-hot-programming-artifact-continuation-v74`
- `v73Preserved=true`
- `programmingArtifactContinuation=true`
- `proportionalErrorHandlingFeature=true`
- `selfTest=true`

The active hot entry additionally verified the response-contract bridge, gap checker, repair payload, candidate generator, programming profile, camera, and inherited n-gram sampler remained callable.

### Stable Server history repair — activation pending

The compatibility reader is committed on `main`, but the current production deployment still points to stable commit `88eed351f6e768d3da544a5cd0c69aeb8f17545e`. End-to-end canonical history recovery therefore cannot be truthfully labeled live until an explicitly approved production deployment activates the stable Python change.

## Acceptance target after deployment approval

Using the same authenticated thread pattern:

1. generate a small standalone code artifact;
2. send `Can you add an error catch to that code?`;
3. `CHAT_HISTORY_CANONICALIZED` must report prior server-owned history rather than zero;
4. if legacy records are involved, `history-legacy-index-bridge` may report bounded counts without text;
5. v74 must report an inherited standalone/lightweight artifact continuation (`projectContext=none`, `architectureDepth=lightweight`, no architecture reconciliation, no tool-evidence requirement);
6. v69 lightweight compaction should activate;
7. the request should modify/restructure the prior code directly instead of entering project architecture ceremony;
8. terminal assistant output should complete normally.

## Versions / lineage

Version gate before assignment:

- Server `2.3.255`
- LALM `2.1.85`
- Chat `1.5.75`

No concurrent authority advance was observed before assignment. This event therefore owns Server `2.3.256` and LALM `2.1.86`; Chat remains unchanged.

Lineage:

- stable Server compatibility source (`main`): `a1667599d03585f4fb068afc485b5b79bdb34263`
- v74 immutable LALM source: `58bfd905d0d3281b6adc1669ca8482cd04cc300c`
- v74 hot entry: `dc79a648600aec4accd453a5b72cf79bde100f80`
- v74 manifest: `9fdf1dff84be8650f28c924d978c0de9a679d131`
- LALM authority: `7cc3579b4d392aa51550faf4ae50d4e9c1070945`
- Server authority: `a627c8fbf74feb3edb7d3b296f902b8ed64db864`

## Deployment boundary

The runtime-hot LALM selection required no Vercel deployment or restart. The stable Server history repair **does** require a production deployment because `api/canonical_redis_state.py` is not runtime-hot. That action remains gated on explicit user approval.