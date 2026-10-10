# Google-owned GitHub project-thread continuity · source and release handoff

**UTC:** 2026-10-10  
**Result:** SOURCE / CI VALIDATED + GUARDED SPACE UPLOAD SUCCEEDED; REAL GOOGLE-OWNED MULTI-TURN ACCEPTANCE PENDING.

## Why
Live user feedback requested §wyrlz to keep the factual state behind the rich §tart handoff *throughout the same Chat thread*: what project was read, which GitHub revision and module versions were authoritative, what was completed, what might still need acceptance. Rendering alone was insufficient; the model must actually receive this evidence again on later related turns.

## Work and ownership
- New `hf_space/project_thread_memory.py` provides account+thread-keyed, encrypted bounded **project evidence snapshots** in existing Upstash Redis. Keys are SHA256 of a server-verified Google ID and thread ID; payload encrypted with the configured Fernet key. 90-day TTL. No GitHub OAuth tokens, prompt transcripts, private chain-of-thought or full repository file bodies are deliberately stored in this tier.
- `hf_space/github_connection.py` emits a `PROJECT_CONTEXT` receipt after source-pinned, read-only §tart retrieval. The receipt is tied to the same pinned GitHub SHA, branch, startup path, source-read list, registry versions, Roadmap completed heading and potential pending heading as the visible response.
- `hf_space/station.py` binds the verified evidence to the active account-owned thread, persists it after successful response, reloads it for relevant follow-ups and passes a bounded `projectThreadEvidence` field to the model. Account-isolated session export now checks subject; DELETE_THREAD requests deletion of its project evidence record.
- `hf_space/lfm2_700m_engine.py`, `hf_space/qwen_coder_engine.py`, `hf_space/original_engine.py` consume bounded evidence on relevant turns. This is source *data*, never repository instruction permission or live status proof. Accepted R39 not modified. The v194 Chat UI/lyric reader is byte-for-byte preserved.
- This feature does **not** make entire Chat conversation history or Google session cookies durable across process restarts. The existing in-process thread catalog remains authoritative until separately migrated. A standalone encrypted project snapshot does not make an otherwise-lost thread navigable in UI. Future continuity work must explicitly address per-user durable threads/ledger and active repository action orchestration; do not mislabel this as full ChatGPT parity.

## CI and release receipts
- Original source review: [PR #76](https://github.com/kaministrator999-ui/Swrlzkamico/pull/76).
- Integration on current deployed v194: [PR #77](https://github.com/kaministrator999-ui/Swrlzkamico/pull/77), code SHA `52db3986c81dd061d7f3e5639737ae714f565d57`.
- [GitHub account+project memory CI #38018692105](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38018692105) **SUCCESS**; source/replay/account tests include encrypted tenant isolation, tampering, thread isolation, provenance and model-route assertions.
- [HF Candidate Offline #38018707661](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38018707661) **SUCCESS**.
- [Lyric Ocean #38018707538](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38018707538) **SUCCESS**.
- [Guarded Hugging Face #38018770558](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38018770558) **SUCCESS** against exact source `52db3986c81dd061d7f3e5639737ae714f565d57`, target existing `kamiloki/Swyrlz`. Predeploy Space revision `601b76c65bc76e9a21411af5adf5218a3ac26d38` preserved; new revision `88ef87b43da107ce1633b7338b61bf0980e41f67`. Publication checkpoint `DEPLOYED_UNVERIFIED`.
- Independent runtime module versions: Repository Work **1.0.130**, LALM Engine **2.1.173**, Server Runtime **2.3.344**; Web Chat unchanged from v194 **1.5.93**.

## Required live acceptance
1. User logs into Google and connected GitHub; creates/opens a thread.
2. Request `Read §tart` for selected repository and inspect completed source handoff.
3. Follow up *in the same thread*: ask for pinned source commit, current known project version/remaining gate **without rerunning §tart**; inspect actual model-generated answer for grounding, relevance, and honest non-current status.
4. Check actual session export includes `projectContext` scoped to thread and avoids tokens.
5. Switch threads and Google accounts; verify snapshots do not cross boundaries.
6. Delete thread and verify account-scoped Redis source snapshot is removed; simulate storage failure/revocation; check fail closed/no false persistence claims.
7. Separate full durable conversation history and iterative GitHub investigation engine need independent architecture/spec, code, test and release work. `PROJECT_CONTEXT` does not authorize GitHub write operations.

**Never classify source publication as completed user-visible memory or activity-ledger acceptance without this live proof.**
