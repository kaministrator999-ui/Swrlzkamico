# §C tool capability + accepted-offer recovery — governed scope (2026-11-16)

## User-observed failure
- §C previously researched a public song and agreed to rewrite an original remix. After the user answered "Yes please", its next response claimed it could not browse the live web, contradicted its own earlier verification, and requested the user paste a published hook.
- The local model's pretrained assumption about its available tools must never override the real runtime. Prior source evidence and the agreed task should survive a short affirmative follow-up.
- Preserve the distinction between internal reference context and the user-visible finished original remix. Do not reproduce published source lyrics just because a research tool retrieved them.

## Architecture and control
- **Source:** actual Hugging Face `kamiloki/Swyrlz` 9B/700M owner, not §E Forge or Vercel.
- Existing outermost `lfm2_700m_engine.py:generate_events` remains the single orchestration entrypoint. The new pure `api/tool_capability_recovery_v1.py` is a bounded helper, not a competing research service or a new account/history store.
- Keep existing `api.online_research.research` as the only additional public HTTP search owner, and the existing browser/server research and source-event contracts.
- Keep already verified structured current-turn research evidence rather than searching again; never assume an earlier assistant utterance is itself verified research.
- Before model generation: turn a direct short yes to an immediately preceding rewrite offer into the accepted actionable task, preserving both recent critique and older named song identity.
- After model generation: **only for research-sensitive requests or accepted pending offers**, buffer draft text and terminal events. If the model falsely claims no search capability, or blocks the accepted creative rewrite on a user-provided published hook, perform one bounded public reference search, inject tagged source evidence and a truthful capability correction, and generate once more.
- Do not publish rejected first-draft text. Preserve unrelated non-text source/activity/route events. Preserve normal streaming on ordinary chat; no extra model pass when the draft succeeds.
- Native Stop takes precedence before, during and after bounded recovery. No retries after cancellation; one extra retrieval and one regeneration maximum.
- Search queries must come from the public task or bounded named song metadata, not private account history. Private data/agentic code changes keep their existing dedicated routes.
- On failed retrieval, disclose missing sources rather than fabricate a tool failure, successful verification, or source details.
- Feature kill switch `SWRLZ_TOOL_CAPABILITY_RECOVERY_ENABLED=0` restores the preexisting flow without changing model weights.

## Testable boundaries
- Unit tests in `tests/test_tool_capability_recovery_v1.py`: ordinary chat bypass, accepted-task continuity, lyrics transformation source separation, source reuse, one-pass research and regeneration, provider unavailable, second hallucination fail-closed, Stop, privacy, critique vs rewrite, false positives, and failed generation.
- GitHub branch preflight additionally fetches the exact live Space revision, checks a unique outermost wrapper anchor, Python-compiles candidate engine and helper, checks byte checksums; no publication in preflight.
- Production can be published only via the existing `.deploy/HF_SPACE_REQUEST.txt` -> `hf-space-request.yml` -> `manual-hf-space.yml` guarded `tool-capability-recovery-v1` scope; immutable source SHA, backed-up live code, CAS Space commit, byte-exact readback, bounded rollback on unexpected readback failure. Never trigger a full old HF package to add this feature.
- Prior adaptive-public-research PR #429 remains **draft / not deployed** because the actual HF environment returned zero attributable sources in some tests. This patch does not claim to solve provider reliability or fabricate search receipts.

## Release / future phases
- This record begins as **source/static tested; production activation and real guest/user behavioral confirmation pending**. Assign actual SHA, workflow run and deployed Space revision only after observed results; do not backfill with guesses.
- Subsequent §C improvements: normalize capability descriptors across search, image, voice, code, and account actions; strengthen relevance/freshness and source coverage in the actual HF environment; persist valid research provenance per thread without duplicated private history; richer answer validation and self-correction for mathematics, code, music and factual claims; dedicated quality/latency and cancellation regression scenarios across all tools.
- No weights, §E engine, user credentials, archived conversations or Vercel changes in this phase.

## Observed publication and live acceptance (2026-11-16 UTC)
- Source PR #442 merged; canonical release [#43811020463](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43811020463) passed. Exact original live revision `a72f505a00557ecd7218e6e68fff1fc2baad9e8a` became byte-verified new revision `971de186d00ff0d59494e2cabaeb8b181d17bbbc`. Guarded source publication did not modify weights, auth or §E.
- Live read-only guest probe [#43811718996](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43811718996) PASSED against RUNNING exact new revision. Fictional-song critique turn completed after 99.9s with an affirmative rewrite offer. Follow-up `Yes please` completed after 158.9s with a 1,817-character new composition containing verse and chorus/hook, no false inability to browse, no demand for published lyrics, and no native HTTP500. Source/test PR #444 merged. Both turns used isolated anonymous guest Station state, no user account.
- Historical tests: initial live probe failed harness import (before model); second probe did not receive a qualifying offered rewrite; both remain recorded. Third run passed. This proves *one* accepted-offer scenario, not reproducibility across every prompt or semantic quality of song/flow.
- A real failure-triggered public search and replacement-generation path has eleven deterministic tests but **not yet a live forced-capability-hallucination acceptance**. Public-research coverage and provenance deficits in draft PR #429 remain open. Never mark the entire tool makeover done from this evidence.
- Follow-on workstream is [issue #443](https://github.com/kaministrator999-ui/Swrlzkamico/issues/443) covering server capability registry, retrieval and source provenance, creative/coding/vision/voice reliability and cross-tool quality gates.
