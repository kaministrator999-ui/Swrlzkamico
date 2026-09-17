# Server 2.3.253 — R39 v71 coding-terminal camera-contract namespace repair

**Status:** runtime-hot source complete; v71 live-hydrated; camera-contract self-test live verified; authenticated coding-turn terminal acceptance pending.  
**Server Runtime:** `2.3.253`  
**LALM Engine:** `2.1.83` / `v71`  
**Chat:** `1.5.75` unchanged by this event  
**Deployment / restart:** none.

## Triggering state

Server 2.3.252 / LALM 2.1.82 v70 added bounded `coding-candidate-terminal` and `coding-fence-repair-normalized` cameras around the existing v27 first-candidate + bounded-repair owner. v70 also normalized repair conditioning for a candidate that consists only of a bare opening Python fence.

During closure, the v70 source had already been activated, but its generic global `_CONTRACT` name shared the same exec-based namespace as older hydrated layers. A nested inherited source reassigned `_CONTRACT`, so v70 camera functions could resolve the wrong contract identifier even though the underlying terminal/repair behavior remained intact.

## Architecture reconciliation

This is a Brain/LALM compatibility/instrumentation defect, not a new coding-repair subsystem. v70 remains the semantic repair owner. v71 extends only the camera-contract namespace boundary so the existing terminal instrumentation can be trusted on the next authenticated coding turn.

No Chat persistence, transport, prefill compaction, response semantics, deployment infrastructure, or tool execution authority changes in this event.

## Repair

`runtime_hot/r39_engine_v71.py`:

- hydrates immutable v70;
- introduces the unique `r39-v71-coding-terminal-camera-contract-v1` authority;
- restores the global contract value after nested lineage hydration because v70 camera functions resolve that global dynamically;
- recomputes the v70 coding-terminal self-test after the namespace repair;
- fails hydration if the self-test contract does not resolve to the v71 camera contract;
- preserves v70 generation/repair behavior unchanged;
- emits a bounded `v71-enter` camera before delegating to v70.

## Verification

### Source / authority

- immutable v71 source is selected by the runtime hot entrypoint;
- runtime manifest revision is `2.1.83-hot-coding-terminal-camera-contract-v71`;
- LALM authority is `2.1.83` / v71;
- Server authority is `2.3.253`;
- Chat remains `1.5.75`.

### Live runtime

Production runtime logs show fresh workers fetching v71 and hydrating the inherited v70→v69→v68 lineage successfully. v71 emitted `hydrate-ok` with:

- `hotServerVersion=2.1.83`;
- `v70Preserved=true`;
- `cameraContractNamespaceRepair=true`;
- `selfTest=true`;
- `selfTestContract=r39-v71-coding-terminal-camera-contract-v1`.

The active hot entry also reported revision `2.1.83-hot-coding-terminal-camera-contract-v71` with response contract, response-gap helper, repair payload, candidate generator, programming classifier, and camera callable.

### Remaining acceptance

No authenticated post-v71 coding generation has yet emitted `coding-candidate-terminal`. The next normal lightweight runnable-code request is the correct acceptance surface. Its camera should reveal the first candidate's actual terminal type/reason class, delta count/characters, maximum decode step, degeneration-guard state, bare-fence state, and completion-gap state without logging response text.

If the v70 repair succeeds, the turn should complete normally. If it still fails, those bounded facts identify the lower terminal source for the next repair without another speculative patch.

## Concurrency / failure lineage

The v71 source/entry/manifest had already been published and live-hydrated while canonical module authorities still reported Server `2.3.252` / LALM `2.1.82` v70. The restarted repair session treated that as an incomplete governed event rather than overwriting it. After re-reading current authorities and confirming no newer version assignment, the event was closed as Server `2.3.253` / LALM `2.1.83`.

## Lineage

- v71 immutable source: `b1bfa7eaec5eec7b21b020a7f8d7ec423416d5ab`
- v71 hot entry activation: `b25858e67b8b3e7801134263a695034194c68402`
- v71 manifest selection: `e03dd747c54c6cf8c4bf3d7128821550771da704`
- LALM `2.1.83` authority: `23b4728072a5808bb0dc88d1309b1c9144bd32a9`
- Server `2.3.253` authority: `6b75f7c9fdb9ca7220683c35dc4ac27c5e882642`
