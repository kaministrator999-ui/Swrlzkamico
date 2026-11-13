# §C 9B acknowledgment latency experiment — 2026-11-13

Status: **Rejected and rolled back**, keep existing 18-thread live source.

## Source and purpose
- Existing Space: `kamiloki/Swyrlz`, resident Qwen3.5-9B Q4_K_M.
- Cgroup quota: 16 effective CPUs; deployed model threading 18 decode / 18 batch.
- Goal: prevent simple praise, such as `Good job!`, from incurring unnecessary latency.
- Current v4 classifier already treats a bare `good job` as social chat; adding the phrase is not an actual fix.
- Existing native `cache_prompt=True` stays enabled. No weights, hardware, billing, authentication, saved history, or §E changes.

## Trial 1: verification-path finding
- Live source candidate `677ab7c7d3717936d760dbaf74c9e18f6a3dc1ee` reduced model-inference history for bare acknowledgments.
- Synthetic bare praise responses often started in ~0.4–0.5s and finished in ~1.6–6.5s on the already optimized system.
- The live test incorrectly required diagnostic keys `ackFastRoute` and `ackHistoryCompacted` in the NDJSON streaming endpoint. Station does not project those keys.
- The trial was rejected; exact previous source restored at HF revision `1d522612e73ae740d29dc3dba3796ddf05a11b77`.
- Correct telemetry source for future tests: the request's own cookie-scoped `/api/lalm_station/sync` snapshot, `activeGeneration.contextBudget`; compare `requestId` before reading.

## Trial 2: matched four-turn first-text regression gate
- Baseline source: `1d522612e73ae740d29dc3dba3796ddf05a11b77`.
- Candidate source: `a5961018c39f96f59a49042b76c9b82eb199d07b`.
- Same synthetic conversation sequence: greeting; friendly follow-up; `Nice!`; `Good job!`.
- Baseline final turn: 6 preceding inference messages, **1.14s first text**, **5.80s total**.
- Candidate final turn: 4 preceding inference messages, **3.39s first text**, **9.05s total**.
- First text was ~2.97× slower; total turn ~1.56× slower.
- Acceptance test detected the regression and **rolled back exactly** to prior source, HF rollback revision `bd5ea5c14fae1a1815385441018f4230affcc6de`. Warm 9B readiness at unchanged 16 CPU quota / 18 decode / 18 batch was verified.

## Engineering lesson
- Do **not** assume that fewer historical tokens means faster continuous conversation. Changing the prompt prefix may interfere with native cache reuse; this was **not separately proven** as the cause here.
- Preserve stable system prompt composition, cache reuse, streaming behavior, per-request tokenizer cache, and the working CPU/thread plan.
- For future optimization, compare matched **time to first visible text**, prompt tokens, native cached/evaluated tokens, and total latency under both warm and cold conditions; keep only measured wins. Avoid source repairs, identities, user memory, and normal project-follow-up regression.
- Record unsuccessful experiments as evidence; never claim an unmeasured improvement or deploy a regression.
