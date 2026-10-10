# §wyrlz v199 — Version Literacy and Content-First Chat Release
**Date:** 2026-10-10
**Result:** RELEASED TO EXISTING HUGGING FACE SPACE / SOURCE + CI VERIFIED; LIVE MODEL ANSWERS, PHONE APPEARANCE AND USER ACCEPTANCE PENDING.

## Product decision and observed prior behavior
The user requested general interpretation of versions in conversations, documents and code, accurate project-version recall, and adaptive content-specific presentation. A previous GitHub follow-up ("What were the versions again?") understood its broad topic but mislabeled a source commit as an "initial commit" and inflated the answer with extra historical claims. The mobile Chat also wrapped structured Markdown prose in an unnecessary ornamental `RESPONSE` code-style container.

## Ownership and source lineage
- Existing production hosting remains Hugging Face Space `kamiloki/Swyrlz`; Vercel and new hosting services are out of scope.
- Based on released v198 rap-curriculum source `feature/rap-rhythm-lessons-v198` commit `f39ec28af54b7db1747df354d1772fd1e07c5e41` (Space revision `f412f16a3347eee813a6d8fd0e99205d7917b36a`).
- Isolated candidate: [draft PR #84](https://github.com/kaministrator999-ui/Swrlzkamico/pull/84), `feature/version-literacy-content-layout-v199`, exact committed/published source `710fb30856d8db098f21adc10dc9e118f6b52056`.
- Canonical ownership preserved: `hf_space/project_thread_memory.py` is Google/thread-bound *source snapshot* projection, not chat transcript truth; `hf_space/version_literacy.py` is inference-time concept coaching; canonical renderer is `chat/§wyrlz/index.html`.
- No model checkpoint/weight changes, new external inference, new Redis store, provider credentials or autonomous GitHub writes.

## Implemented
1. **General version literacy**: `hf_space/version_literacy.py` distinguishes component/dependency versions, release tags, prereleases, calendar versions, builds, schema revisions, model checkpoints, commit hashes, and deployments; cues factual recall vs comparison vs history vs explanation. Crucially a pinned source SHA cannot be asserted to be the version's *initial* commit. Injected as bounded generation guidance in LFM2 700M, Qwen coder and 350M fallback routes.
2. **Grounded per-thread followups**: For versions-related prompts `hf_space/project_thread_memory.py` now includes every captured verified module/version/status tuple (up to snapshot contract), rather than the previous four headline modules. It carries runtime registry SHA and a prominent source-not-live limitation. Non-version project questions retain concise salient values. Long-term chat ownership, encryption and session continuity remain with existing Google persistence.
3. **Context-driven Chat content layout**: Removed `wrapMiscResponse()`, which created automatic nested `RESPONSE` framing around Markdown structure. Ordinary paragraphs, lists, tables, headings stay native DOM-safe text. Actual fenced code retains code viewer, syntax-preserving text, copy/download and horizontal scroll with compact restrained styling. Existing original lyrics retain formatted reader plus opt-in compact code view, copy/download; no change to lyrics/research/rap generation logic.
4. **Regression coverage**: `hf_space/test_version_presentation_v199.py`; CI integration in `verify-github-account-v1.yml`; narrowed earlier lyric-specific style tests to their historical CSS sections to permit v199 code viewer evolution. Added v199 push triggers to existing HF candidate/lyric/mobile integrity CI.

## Exact candidate CI evidence
All four tests passed on exact release source `710fb30856d8db098f21adc10dc9e118f6b52056`:
- [GitHub account + version/context + Chat parsing #38027303407](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38027303407): SUCCESS.
- [HF Candidate Offline Validation #38027303341](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38027303341): SUCCESS.
- [Lyric Ocean Corpus Integrity #38027303355](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38027303355): SUCCESS.
- [Mobile Lyric Reader Integrity #38027303431](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38027303431): SUCCESS.
Earlier CI failures from legacy source-boundary phrase and historical CSS test range were diagnosed, corrected and rerun to success. No actual model generated output or Android screenshot was graded by these tests.

## Release: guarded Hugging Face publication
`main:.deploy/HF_SPACE_REQUEST.txt` request nonce `2026-10-10-v199-version-literacy-content-first-001`, request-file commit `4047fc25373649ed49fdf86ff8053455d3f6d3ea`.
[Guarded Hugging Face Space Deploy Request #38027390908](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38027390908): terminal COMPLETED/SUCCESS. Its immutable source commit `710fb30856d8db098f21adc10dc9e118f6b52056` was prepared/validated, and the existing Space was updated. Job log captured:
- Previous Space revision/rollback `f412f16a3347eee813a6d8fd0e99205d7917b36a` (snapshot artifact persisted).
- New uploaded Space revision `e9262360065f84ef6576325e23d1a577a519ab0e`.
The release uses the existing Space; no alternate hosting or bypass of snapshot/rollback guard.

## Canonical version handoff
`runtime:VERSION.txt` remains the only version registry. Post-release module-owned authority updates:
- Repository Work **1.0.135 → 1.0.136**, commit `f9d4f6eb5612ce3a58207dbb82dfc91aa6f460fa`.
- LALM Engine **2.1.177 → 2.1.178**, commit `76ae508280b178d59e080da53f9d7c4b58e5a961`.
- Web Chat **1.5.94 → 1.5.95**, commit `d8789c24e630462b262b424492feef0158dc408e`.
- Server Runtime **2.3.349 → 2.3.350**, commit `a10f36e76410e4d930cf670becc6717492a1b568`.
Online Research, Google Account, deployment-control and other unrelated registered module versions unchanged.

## Live/user acceptance still open
User should reopen the retained Google-owned thread after this deployment and confirm earlier user/assistant chat bubbles persist. After a new `§tart` or GitHub source read, ask:
- `What were the versions again?` — should give a concise, source-grounded module version recap; ask for the full list if desired.
- `Which commit first introduced Server Runtime 2.3.350?` — without actual historical Git evidence, must say the introducing commit is unverified, **not** assign the current inspected source SHA.
- `Compare the LALM Engine and Server Runtime versions` — distinguish separate module identities instead of treating numbers as directly ordered versions.
- Inspect a Markdown list, table, multi-paragraph explanation, syntax-fenced code/copy/download and generated lyrics/collapse on a phone. Should never see automatic ornamental `RESPONSE` frame around ordinary prose.
Behavioral acceptance and visual quality are NOT inferred from green CI or successful source publication.

## Work ownership and continuation
v199 implementation, static tests, version lineage, report and one guarded production publication are complete. No separate inference latency/creativity improvement or learning of weights is claimed. The next relevant owner action is live user screenshot/export evidence for version recall/provenance and formatting; repair from actual regressions with a subsequent isolated branch, preserving v198 rap and encrypted account conversations.
