# Server Runtime 2.3.51

Date: 2026-09-11

## Module state

- Server Runtime: 2.3.51
- Web Chat: 1.4.46
- LALM Engine: 2.1.25 (unchanged)

## Change

Corrected turn-intent isolation and conversation-prefix stability after the 2.3.50/1.4.45 test exposed that internal social-turn guidance was being appended directly to user prompt text. That internal text leaked into model output and contained programming vocabulary, causing a plain social greeting to be misclassified as a coding request and arming the coding completion contract.

Chat now keeps the user's prompt text clean, stores intent only as request metadata, strips legacy injected intent markers from recovered/history user turns, and uses one stable response directive across turns. This preserves exact user semantics and improves the chance that same-worker conversation checkpoints share an exact token prefix for incremental prefill reuse.

Background/reload recovery remains enabled and authenticated. If a Vercel worker changes, the same request can still be resumed or regenerated and reconciled against saved partial output; however recurrent-state checkpoints remain worker-local, so a new worker may still rebuild prefill from zero until a durable shared context store is introduced.

## Failure / attempt history

The 2.3.50 / Chat 1.4.45 implementation embedded `[[SWRLZ_TURN_INTENT:...]]` guidance directly into prompt/history text. In the acceptance log, `Hey 👋` leaked the internal marker into the generated response and the engine classified the turn as coding, armed code obligations, and generated hundreds of unrelated tokens.

## Verification state

- Source update committed to `runtime`.
- Version authorities advanced to Server Runtime 2.3.51 and Web Chat 1.4.46.
- LALM Engine unchanged at 2.1.25.
- Production/browser acceptance test required after runtime propagation.
- No Vercel deployment requested.
- No server restart requested.

## Relevant lineage

- Turn-intent isolation fix: `dd2c7593250f203f96af4ce1cf5b345a3535acc8`
- Server version authority: `15276d08a3ebe29cb2e5053ebde8923692d8cbad`
- Chat version authority: `eabdfe94167e3a18d998ea32b036d864d53c9582`
