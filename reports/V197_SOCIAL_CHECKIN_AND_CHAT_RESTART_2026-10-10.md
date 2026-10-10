# §wyrlz · v197 friendly greeting guidance and Google conversation restart test

**Date:** 2026-10-10  
**Status:** SOURCE VALIDATED + GUARDED EXISTING HF SPACE PUBLISHED; LIVE V197 GREETING QUALITY AND POST-DEPLOY GOOGLE THREAD RESTORATION STILL UNVERIFIED.

## User-reported observations
After v195 account-owned encrypted chat history was deployed, the user shared a screenshot of a short conversation. Both their `Hey how are you` user bubble and a completed §wyrlz reply remained visible after a browser refresh and signing out/back into Google. This establishes live **refresh/login** continuity but, by itself, did **not** establish persistence across a new server process.

The 700M model's answer repeated phrases like "I'm here, I'm here", described AI assistant purpose rather than answering, and asked "how's your chat with §wyrlz?" as though §wyrlz was a different entity. User requested better replies and another guarded deployment to test chat survival after process replacement.

## Change and lineage
- Source: `feature/social-checkin-v197-persistence-restart` at exact commit `96c6d0547707349f7a99baf4b1e5c3627e155c3e`, [draft PR #82](https://github.com/kaministrator999-ui/Swrlzkamico/pull/82).
- Based on v196 `feature/research-assisted-lyrics-v196` SHA `e5652a54b6ac3167e3be0a319929e6af5f60363d`; preserves v196 lyric research/cache, v195 encrypted account-owned chat persistence, GitHub OAuth/read-only §tart, project snapshot memory, Chat UI and operational control.
- Adds `hf_space/social_checkin.py` pure bounded full-message greeting intent detector and model **style hint**, NOT a fixed canned answer. Two example *tones* guide spontaneous first-person, concise, friendly responses to "how are you?" while avoiding ontology lectures, redundant phrases or third-person assistant identity. Does not trigger on code/song requests.
- `hf_space/lfm2_700m_engine.py`, `hf_space/qwen_coder_engine.py`, `hf_space/original_engine.py` receive social style hint only for short greetings. Stock-original uses compact instruction. No GGUF weight updates/fine-tuning.
- Regression tests `hf_space/test_social_checkin_v197.py` confirm positive greeting recognition, negative non-greetings, bounded guidance and unchanged account chat model-route source contracts.

## CI and release receipts
- [GitHub account/greeting #38023378212](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38023378212) **SUCCESS** exact source.
- [HF Candidate Offline Validation #38023380877](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38023380877) **SUCCESS** exact source.
- [Lyric Ocean Corpus Integrity #38023380963](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38023380963) **SUCCESS** exact source.
- [Guarded HF Space Deploy Request #38023443715](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38023443715) terminal **SUCCESS**. Existing target Space `kamiloki/Swyrlz` prior revision `17f9b48b6861e65085d11cee4549259aa81605f3` snapshotted for rollback. New published revision `759e05a253157bc7a6ef8f729ba8c2d8c362b9a9`. Deployed source exactly `96c6d0547707349f7a99baf4b1e5c3627e155c3e`. Checkpoint `DEPLOYED_UNVERIFIED`, not claim of user-visible quality or persisted chat state.
- Independent versions: Repository Work **1.0.134**, LALM Engine **2.1.176**, Server Runtime **2.3.348**; Web Chat **1.5.94** unchanged.

## Required LIVE acceptance
1. User opens `https://kamiloki-swyrlz.hf.space/` AFTER v197 Space is running. Under the same Google account, verify pre-v197 "Hey how are you" thread is still in Chat sidebar and BOTH user and assistant messages are intact; refresh again. This is the **first deployment restart** persistence proof.
2. Open fresh chat and ask `Hey how are you?`. Evaluate naturalness (brief direct answer, first-person §wyrlz, no repetitive "I'm here", no "how's your chat with §wyrlz", appropriate friendly reciprocity). Compare actual output against the screenshot; source-only prompts do not guarantee model competence.
3. Send a follow-up to that greeting and verify conversation continuity; sign out and back in to the same Google identity and verify both new thread messages remain. For longer reliability, repeat at next normal guarded deployment.
4. Distinct users must not share conversations; active in-flight inference remains process-local and whole-account snapshot has 2.2MB limit. These are separate from simple greeting style and should not be marked resolved by this publication.

**Do not assert full ChatGPT-style memory, actual GGUF training, conversation recovery from previously lost server-only sessions, or live model-quality acceptance without user evidence.**
