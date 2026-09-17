# Server 2.3.259 — R39 v75 programming continuation semantics

**Status:** runtime-hot source complete; production hydration verified; deterministic continuation/semantic acceptance 5/5; authenticated post-v75 user-turn acceptance pending.  
**LALM Engine:** `2.1.87` / `2.1.87-hot-programming-continuation-semantics-v75`.  
**Chat:** `1.5.76` preserved from concurrent work; unchanged by this event.  
**Deployment / restart:** NONE performed.

## Triggering live evidence

After Server 2.3.257's runtime-hot canonical-history policy was bootstrapped in production, three authenticated coding paths isolated the remaining Brain-owned defects.

- Fresh-thread base request `web:mu65ooeu:5610839912042721028` correctly stayed standalone/lightweight and completed the original even/odd Python program.
- Fresh-thread continuation `web:mu65t03i:30386169343835364035` proved canonical history + v74 first-hop routing: two history messages were selected, the assistant code anchor was high-confidence, `projectContext=none`, `architectureDepth=lightweight`, and the prompt compacted to 596 rendered tokens. The generated edit nevertheless renamed `even_odd` to `evenodd`, omitted the top-level function call, and added an unrequested `while True` retry loop while still passing the old artifact gap checker.
- Old-thread continuation `web:mu65y61e:3993695763349477977` proved legacy history recovery: the hot policy merged 2 current-index + 4 legacy-index records and selected 4 canonical messages with a high-confidence assistant anchor. v74 then classified the edit-of-an-edit as `projectContext=existing` / normal depth, inflated the prompt to 3,883 tokens, and timed out after 300 seconds. This localized the remaining defect to continuation provenance rather than Server history delivery.

## Architecture reconciliation

The Human/Server remains the authority for authenticated durable history and the runtime-hot history policy remains its read-only reconstruction seam. Those paths are now live verified and are not changed here.

The remaining defects belong to the Brain/LALM programming edge:

1. **artifact provenance across edit chains** — a second follow-up must inherit the original standalone/project context rather than classifying the immediately preceding deictic request in isolation;
2. **runnable edit semantic preservation** — a code mutation must preserve existing callable names and runnable entrypoints unless the user explicitly requests restructuring, and must not silently add retry-loop behavior.

v75 extends the existing v74 route and the existing v27 bounded artifact-repair owner; it does not create a second persistence, routing, or repair authority.

## Runtime change

`runtime_hot/r39_engine_v75_overlay.py` overlays pinned v74 with:

- bounded artifact-chain traversal back to the first non-deictic programming origin;
- explicit project/repository promotion as an intentional provenance boundary;
- propagation of `continuationDepth` and original project context across edit-of-edit turns;
- a compact continuation directive requiring requested-scope edits while preserving runnable behavior;
- Python AST signatures for prior runnable artifacts;
- semantic gaps for unrequested callable-name loss, lost runnable entrypoint calls, loss of top-level execution, and newly introduced `while True` retry loops when retry behavior was not requested;
- integration with the existing v27 one-pass repair payload rather than another repair system;
- bounded `v75-enter` cameras that log route/semantic counts only.

The active hot entry hydrates pinned v74 first, then applies the pinned v75 overlay and fail-closes unless the v75 self-test passes.

## Verification

Static syntax checks passed before publication.

Production runtime-hot sync loaded the new `r39_engine.py`, and `/api/lalm/status` reports:

- `hotServerVersion=2.1.87`;
- `hotRevision=2.1.87-hot-programming-continuation-semantics-v75`;
- `interactiveReady=true`;
- `v74Preserved=true`;
- `programmingContinuationProvenance=true`;
- `runnableEditSemanticGate=true`;
- `unrequestedRetryLoopGate=true`.

The deterministic v75 suite passed 5/5:

1. multi-hop standalone continuation remains lightweight;
2. explicit project promotion remains existing-project work;
3. missing prior entrypoint is rejected;
4. unrequested retry loop is rejected;
5. minimal error-catching edit that preserves the prior runnable program is accepted.

A normal authenticated user continuation after v75 activation is still required before calling the new behavior user-turn/live accepted.

## Concurrency

Event entry observed Server `2.3.257`, LALM `2.1.86`, Chat `1.5.75`. During runtime hydration another event advanced Server to `2.3.258` and Chat to `1.5.76` while LALM remained `2.1.86`. This event preserved that concurrent lineage and assigned only Server `2.3.259` plus LALM `2.1.87`.

## Lineage

- v75 overlay: `8a92721addbeb6709b132f826404e805d8e35029`
- hot entry: `00a38f0b22976dd959101a0462d041b1bd161a65`
- manifest: `1ccbfbdf4acf3b0cee8f4be987c4625d11e34b12`
- Server authority: `bfcfdcd72ac5eeb59dfb515986cfd99b4a7f5123`
- LALM authority: `a6aa1a51caf87f5795cadda06030d3547cbbd9d6`
