# 2026-11-05 — §C Vision Auto-Resync & Elapsed Timers v6

**Scope:** canonical §C Chat existing Hugging Face Space `kamiloki/Swyrlz`, owned source branch `fix/chat-embed-mobile-composer-v1-20261103`. No changes to the §E editor, current model checkpoints, Google sign-in, microphone handling, existing v4 JSON vision handoff export, or paid API/hardware.

## Owner screenshot / observed failure
A real image upload reached **Identify visual details** (`ANALYZING`) with image and question correctly shown in the chat viewport. After roughly six minutes, browser code `Date.now()-started>6*60*1000` threw an error stating the analysis was still running on the CPU and telling the user to **Press Send again**. This was a **client-side timeout**, not proof that the native SmolVLM CPU worker had stopped. The user correctly requested continuous automatic resynchronization and an elapsed-time indicator.

## Source implementation
- **Never require manual Send just to recheck an active job.** `chat/§wyrlz/index.html` removes the hard six-minute polling cutoff and continues authenticated status polling while the user keeps the page active and has not explicitly pressed **Stop waiting**.
- **Resync:** temporary polling failures retry against the same job ID. Temporary 5xx/408 network errors and a full local CPU queue trigger automatic backoff/retry; a free Space restart (404 lost in-memory job) triggers re-acceptance of the same attached image/question up to two times. Authentication/real worker failures are still reported rather than ignored. No duplicate Station message is created: existing canonical send remains gated on a successful visual description.
- **Live time display:** two MM:SS counters are visible inside the existing progress card: **Elapsed** total and **Current step**. They update once per second. Server `hf_space/chat_vision.py` now tracks a monotonic job creation timestamp and per-phase start timestamp; the authenticated status response adds `elapsedSeconds` and `phaseElapsedSeconds`. When available, frontend timers anchor to those observed server durations, while pre-upload and post-vision time use local wall-clock elapsed time.
- **No unbounded model parallelism:** existing one-running + one-queued native CPU jobs and short-lived process memory retention stay intact. Stop waiting aborts browser polling but cannot forcibly interrupt native llama.cpp inference. A slow model can still be slow; timers are for diagnosis and transparency, not a synthetic percent or a performance guarantee.

## Verification / deployment receipts
- [PR #379](https://github.com/kaministrator999-ui/Swrlzkamico/pull/379) merged to canonical HF Chat source as squash commit `f38e2d08785ab5fadb4887ad5cac926a05141e61`.
- [HF Candidate Offline Validation #42120509634](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42120509634): focused async owner-scoped local vision, elapsed-timing assertions, job queue and JS/inline composer syntax & auto-resync contracts **PASS**. Overall workflow remains **FAIL** from four pre-existing unrelated `hf_space/test_forge_modeling_lessons_v2.py` §E tests. A legacy lyric-reader test also fails separately on an unchanged source-string expectation; the relevant Android/desktop/widget checks passed.
- Guarded publish requested via `main:.deploy/HF_SPACE_REQUEST.txt` commit `b6f8fca5793b7a89488a2ed5dbce17dc30993e2b`.
- [HF Space Deploy #42120756762](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42120756762) **SUCCESS**: exact source validation, R39/700M protection, previous Space snapshot, immutable rollback checkpoint, Space upload and post-upload checkpoint.
- **Published HF Space revision:** `8040777723164065b3d45b8099bc3a64e6e6b251`; **rollback revision:** `bac1922d8d730786a0bcb2e7244b967db831a639`.
- Runtime lineage versions: Repository Work `1.0.266`, Server Runtime `2.3.457`, Web Chat `1.5.173`. Canonical local HTML contract remains `1.1.22`.

## Acceptance boundary
**DEPLOYED_UNVERIFIED**. Successful upload is confirmed, not actual SmolVLM throughput, completion or resync on the owner's Android device. Refresh §C, reupload the Little Crystal Mage image and watch the new timer while the step is ANALYZING. If it never completes, inspect HF runtime logs to diagnose the native CPU model, process RAM, or inference hang without silently adding a paid provider or increasing hardware costs.
