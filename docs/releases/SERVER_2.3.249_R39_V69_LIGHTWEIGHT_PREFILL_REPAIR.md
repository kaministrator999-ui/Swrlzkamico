# Server 2.3.249 — R39 v69 lightweight programming prefill repair

**Status:** runtime-hot source complete; immutable v69 published and selected by the hot entry/manifest; fresh-worker activation and user-turn performance acceptance pending.  
**Server Runtime:** `2.3.249`  
**LALM Engine:** `2.1.81` / `v69`  
**Chat:** `1.5.74` unchanged by this event  
**Deployment / restart:** none.

## Triggering production evidence

The first authenticated standalone programming test after v68 used request `web:mu5vbli6:11914080611097954501` and asked for a small Python even/odd program.

The production cameras proved the Phase 1 programming router itself behaved correctly:

- `v68-enter` executed;
- `programming-mode` classified `projectContext=none`;
- `architectureDepth=lightweight`;
- no architecture reconciliation, diagnostics, project coaching, or repository/tool evidence was requested;
- the request was therefore correctly treated as standalone lightweight coding.

The same request exposed two independent prefill defects and one existing continuity boundary:

1. the LALM payload contained nine internally injected system-policy records totaling about 16.8k characters despite canonical Chat history containing zero prior messages; the rendered prefill reached 3,839 tokens at roughly 10–11 tokens/s;
2. the bounded prefill render camera emitted `render-error: NameError` before inference, although generation continued;
3. a later reconnect on another worker re-entered the same request and restarted inference because model/KV state is worker-owned rather than durably checkpointed across workers.

## Architecture reconciliation

### Context ownership

The nine apparent history records were not canonical user conversation history. They were Brain/LALM-owned copied-payload system policies layered by the v46–v66 reasoning wrappers. Canonical Chat history remained server-owned and reported zero prior messages. The repair therefore belongs in the LALM internal context compiler, not Chat persistence.

v69 compacts only recognized §wyrlz internal system policies and only when the existing programming classifier reports an active task with `projectContext=none` and `architectureDepth=lightweight`. It replaces those redundant long policies with one bounded `SWRLZ_LIGHTWEIGHT_PROGRAMMING` marker.

User/assistant dialogue is preserved exactly. Unknown system messages are preserved rather than treated as §wyrlz-owned policy. Non-lightweight requests are unchanged.

### Render-camera namespace

The v42 bounded render camera still called historical bare-global `_get_model`, while the canonical implementation lives at `_impl._get_model`. v69 restores the compatibility alias to that canonical owner and preserves the existing history cleaner.

The old v36 token-exact rendered-prompt trace also depends on `_get_model`. Restoring the alias without further action would resurrect raw prompt-token logging. v69 therefore explicitly retires that legacy trace while preserving the current bounded render/count/timing camera. This aligns diagnostics with the project-wide privacy/observability contract.

### Reconnect / worker handoff

No Chat continuity code changed. Existing continuity releases explicitly define detached model state as worker-memory: same-worker reconnect replays/follows the existing generation, while replacement-worker recovery may regenerate from the start because no durable cross-worker KV/inference checkpoint exists. v69 reduces the cost of such regeneration for standalone lightweight coding but does not falsely claim cross-worker compute checkpointing.

## v69 behavior

Immutable `runtime_hot/r39_engine_v69.py`:

- preserves the v68/v66 programming classifier and permission boundaries;
- marks only standalone lightweight programming turns for compaction;
- compacts recognized internal system-policy records at the final pre-inference boundary;
- applies the same compact view to the bounded rendered-prompt camera;
- preserves all user/assistant dialogue and unknown system records;
- makes compaction idempotent;
- bridges `_get_model` to `_impl._get_model`;
- keeps the legacy raw prompt token trace retired;
- emits bounded `lightweight-context-compaction` and `lightweight-context-applied` cameras containing counts/character totals only;
- reports that cross-worker compute checkpointing remains false.

A hydration self-test verifies the model accessor/history-cleaner contracts, dialogue preservation, unknown-system preservation, recognized-policy compaction, one compact marker, idempotence, and non-lightweight no-op behavior.

## Verification truth

### Source complete

- immutable v69 source published;
- active hot entrypoint targets that immutable source;
- hot manifest revision is `2.1.81-hot-lightweight-programming-prefill-v69`;
- LALM authority advanced `2.1.80 → 2.1.81`;
- Server authority advanced from the concurrently observed `2.3.248 → 2.3.249`.

### Live activation pending

The production worker reachable during closure was already warm on v68 before v69 publication and continued reporting `2.1.80`/v68. That is consistent with instance-local hot-engine residency and does not prove v69 failure or success. A fresh or explicitly hot-refreshed worker must report v69 before live activation is claimed.

The next authenticated standalone programming turn should provide the decisive acceptance evidence:

- `v69-enter` with `lightweightProgramming=true`;
- no `render-error` camera;
- `lightweight-context-compaction` / `lightweight-context-applied` with `dialoguePreserved=true`;
- materially reduced `afterMessages`, `afterChars`, and rendered/prefill token count relative to the v68 baseline of 9 internal records / ~16.8k chars / 3,839 tokens;
- normal code response completion;
- if a worker handoff occurs, no claim of exact compute continuation unless durable checkpoint evidence exists.

## Concurrency

This event began while the main roadmap still displayed Server `2.3.241`, but runtime authorities advanced through several independent Chat/runtime events. Immediately before version assignment the canonical runtime authorities were Server `2.3.248`, LALM `2.1.80`, and Chat `1.5.74`. Those intervening events were preserved. Only LALM and overall Server advanced in this event.

## Lineage

- v69 immutable source: `a47edea4867c8082baddf27b04182430dc92fb31`
- v69 hot entrypoint: `6003557b9868996b3f7c71cce7694e95680d3d32`
- v69 manifest: `1a48de48a50735e331cbc689fb5f88ce516993da`
- LALM `2.1.81` authority: `a081434edb9ac5582494e62ec5e8e48c031ad669`
- Server `2.3.249` authority: `78e2852532cee133a26eb69888961fa58f651609`
