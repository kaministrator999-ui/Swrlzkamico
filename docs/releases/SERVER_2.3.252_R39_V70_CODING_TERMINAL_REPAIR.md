# Server 2.3.252 — R39 v70 coding terminal + fence repair hardening

**Status:** runtime-hot source complete; v70 live-hydrated; deterministic repair acceptance passed; authenticated coding-turn completion acceptance pending.  
**Server Runtime:** `2.3.252`  
**LALM Engine:** `2.1.82` / `2.1.82-hot-coding-terminal-repair-v70`  
**Chat:** `1.5.75` unchanged by this event  
**Deployment / restart:** none.

## Triggering evidence

The authenticated v69 standalone Python test used request `web:mu5xxfum:6088402523056499266`. The v69 context repair itself passed: lightweight programming routing activated, nine Brain-owned policy records were compacted to one, rendered prompt size fell from the earlier 3,839-token baseline to 444 tokens, and inference prefetched 656 tokens. The old render-path `NameError` did not recur.

After successful prefill, however, the first coding candidate emitted only an opening Python fence and reached a terminal after roughly two decode steps. The existing v27 requirement owner correctly detected `runnable-code` as missing and launched its one bounded correction pass. That repair also failed to produce runnable code; the final visible combined prefix consisted of duplicated Python fence/opening fragments and the request terminated failed. The same request reported zero reconnects, so worker handoff was not involved.

Production evidence did not emit the old `DEGENERATION_GUARD` phase for that request. Existing logs also did not expose which terminal source v27 received from its lower generator, leaving a bounded observability gap at the candidate-terminal boundary.

## Architecture reconciliation

This remains a Brain/LALM defect. Chat correctly relayed and persisted the failed model output, and the continuity path was not implicated.

The canonical semantic acceptance/repair owner already exists in the inherited v27 lineage. v70 therefore extends that owner rather than introducing a second repair subsystem. v69 lightweight context compaction remains unchanged except for one compact coding instruction that forbids ending after only an opening language fence.

The lower v17 generation loop already consults the dynamic response-contract gap helper before accepting EOS. v70 preserves that design and hardens the active global completion boundary specifically for an empty/bare code-fence coding candidate.

## What v70 changes

Immutable `runtime_hot/r39_engine_v70.py`:

- preserves the full v69 programming/context-compaction lineage;
- hardens `_response_contract_gaps` so a coding response that is empty or only an opening `python`/`py` fence always retains `complete-code`, plus `requested-explanation` when applicable;
- extends the existing v27 `_repair_payload` path rather than replacing it;
- when the first candidate is only an opening Python fence and `runnable-code` is missing, removes that incomplete assistant fence from repair-history conditioning and instructs the correction pass to continue inside the already-visible fence instead of emitting another opener;
- keeps the final response append-compatible by asking the repair to close the existing fence once, then provide the requested brief explanation;
- adds a bounded `coding-candidate-terminal` camera around v27's existing first/repair candidate generator boundary;
- the camera records only terminal classification/count metadata: pass kind, terminal type/reason class, delta count/chars, max observed decode step, degeneration-guard observation, fence count/bare-fence state, and completion-gap booleans; it does not log response text;
- adds a bounded `coding-fence-repair-normalized` camera when the malformed opening-fence repair normalization activates;
- fails hydration closed if the inherited v27 repair/generator/completion contracts are unavailable.

## Deterministic acceptance

The v70 hydration self-test verifies:

- the probe is classified as coding + explanation;
- a bare opening Python fence has `complete-code` and `requested-explanation` gaps;
- the fence-continuation repair activates for `runnable-code`;
- the incomplete assistant fence is removed from repair-history conditioning;
- the repair prompt explicitly continues inside the existing visible fence.

The live self-test additionally revealed that the inherited pre-v70 gap checker already returned both `complete-code` and `requested-explanation` for the bare fence. Therefore the original early terminal was not caused by the completion gap helper accepting the fence as complete. The remaining lower terminal source is now observable through `coding-candidate-terminal` on the next real coding turn.

## Verification truth

### Source complete

- immutable v70 source published;
- runtime hot entrypoint points to immutable v70;
- runtime hot manifest selects revision `2.1.82-hot-coding-terminal-repair-v70`;
- LALM authority advanced `2.1.81 → 2.1.82`;
- Server authority advanced from the concurrency-checked `2.3.251 → 2.3.252`;
- Chat remains `1.5.75`.

### Live runtime verified

Production `/api/lalm/status` reports:

- `hotServerVersion=2.1.82`;
- `hotRevision=2.1.82-hot-coding-terminal-repair-v70`;
- `interactiveReady=true`;
- `v69Preserved=true`;
- `codingBareFenceCannotComplete=true`;
- `v27FenceContinuationRepair=true`;
- `codingCandidateTerminalCamera=true`;
- `codingTerminalSelfTest.ok=true` with every check passing.

### End-to-end acceptance pending

The next authenticated standalone coding turn must prove one of two acceptable paths:

1. the first candidate proceeds past the former two-step malformed-fence terminal and completes runnable code + explanation; or
2. if the lower generator still terminates early, `coding-candidate-terminal` identifies the terminal source and the normalized v27 repair continues inside the existing fence and completes successfully.

If the second repair still fails, the new candidate-terminal camera supplies the exact next diagnostic boundary without logging private response content.

## Concurrency

At the final version gate the canonical runtime authorities were Server `2.3.251`, LALM `2.1.81`, and Chat `1.5.75`. No affected authority moved before assignment. This event therefore owns Server `2.3.252` and LALM `2.1.82`; Chat is intentionally unchanged.

The main roadmap was behind the runtime authorities and must be reconciled as historical/reporting state rather than treated as a competing version owner.

## Lineage

- v70 immutable source: `d35c55aed8a1d83550e6639af70759fe0b310554`
- v70 hot entrypoint: `83ab61aba5ca46f858684130a008f557cec176dd`
- v70 manifest: `1244d12d607302154b1047f6c9b0f57baecdbeb3`
- LALM `2.1.82` authority: `8412b52261d389525539a5c0df21b3d877deca0e`
- Server `2.3.252` authority: `7b9487e7304f512fb020128f033022265b08e840`
