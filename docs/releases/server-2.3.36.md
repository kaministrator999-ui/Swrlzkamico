# Server v2.3.36 — 2026-09-11

## Modules

- Server Runtime v2.3.36
- Web Chat v1.4.31
- LALM Engine v2.1.25
- LALM UI unchanged
- Stream contract unchanged

## User-visible objective

Correct the streaming-generation presentation and tighten programming-response completion after the camera log showed an empty assistant card during prefill, delayed Activity visibility, an unwanted `§wyrlz` self-introduction/signature, and a coding response that incorrectly passed verification despite containing no code.

## Chat changes

- Keep the active assistant card mounted during prefill and generation.
- Show the current prefill/generation phase inside the empty response area instead of presenting a blank box.
- Keep the Activity log visible and update it live while the response is still being prepared/generated.
- Continue to replace the response card only once at final completion so rich markdown/code-artifact formatting can be applied without repeated whole-card flashing.

## LALM changes

- Assistant name is treated as identity metadata, not ordinary greeting/signature text.
- The stable model-facing directive was shortened to reduce first-turn prompt/prefill overhead while retaining completeness and programming guidance.
- Programming-response verification now requires recognizable programming syntax rather than accepting prose that merely contains words such as `function`.
- Fahrenheit/Celsius verification continues to require a valid conversion formula when that specific task is requested.
- EOS deferral remains armed while required code/explanation/consistency obligations are missing.
- Existing progressive prefill checkpoints, adaptive output budgets, speculative next-turn warmup, and detached generation remain active.

## Failure evidence addressed

The acceptance log for the preceding release showed:

- 168 fresh prefill tokens and 54.26 s prefill before the first visible model delta;
- raw assistant text containing only `§wyrlz`, prose, and another `§wyrlz`;
- no C++ code despite the response contract requiring code;
- the prior verifier incorrectly reporting that coding consistency checks passed.

## Verification / deployment state

- Runtime-only update; no stable `main` infrastructure change was required.
- Production deployment: NONE requested.
- Server restart: NONE requested.
- Acceptance requires live `/api/lalm/status` to report LALM v2.1.25 and live Chat to serve the updated incremental-stream asset from the `runtime` branch.
- Browser acceptance remains required for the exact Android streaming behavior and black-flash regression.

## Relevant lineage

- Chat live-stream update: `38d5ce8a88092b9fae84edbdc9b8a44b1f6505c6`
- LALM engine update: `f2c46eb9c8c929c60a8bf7ba9915026ef5708730`
- LALM version authority: `e587cd98de6507d0bc9d0e28fffb5608f244c5df`

## Rollback

Runtime loader backups remain the operational rollback mechanism for hot Chat/LALM source. Reverting this release should restore both the previous stream renderer and LALM engine together so the Chat/LALM behavior stays version-consistent.
