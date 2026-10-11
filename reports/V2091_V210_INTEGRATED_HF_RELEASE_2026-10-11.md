# v209.1 native Chat persistence + v210 GitHub capabilities — integrated HF release

Date: 2026-10-11. Single existing Hugging Face Space: `kamiloki/Swyrlz`. This report records an engineering release, **not** successful private-user acceptance.

## What prompted the corrective release

The owner confirmed native §wyrlz conversations **still did not save** after published v209 browser synchronization. The prior store serialized the entire verified-Google native conversation history into one encrypted Redis value, rejecting raw JSON above 2,200,000 bytes. Older conversations could remain readable while further saves failed. This was a verified code defect consistent with the report, **not proof of the exact private-session failure code**. A final assistant persistence error could also attempt an additional failing write, making incomplete persistence harder to diagnose. Imported ChatGPT archive records (2,556 threads observed earlier) remain stored separately; their background message tally is not a native Chat save operation.

Separately, the owner requested request-scoped GitHub read/write capabilities: use granted OAuth scopes and observed repository access, never assume access merely because owner controls the repo; explain denied vs unverified permissions and clearly state that OAuth grants require interactive user approval, never silently acquiring read or write authorization.

## One combined source rather than colliding releases

- Published v209 source: `fix/native-google-chat-cross-browser-20261011@4fe3ede62a198f841adc30b1b673e2ae28ec7ed0`.
- Native persistence corrective source: `fix/native-chat-capacity-v2091@9fecf01937b83d2b2082e311189e4ec9c005994d` in [draft PR #101](https://github.com/kaministrator999-ui/Swrlzkamico/pull/101).
- Initial v210 GitHub source stayed isolated in [PR #102](https://github.com/kaministrator999-ui/Swrlzkamico/pull/102).
- Integrated publishable source: `feature/github-capabilities-v210-v2091-integrated@4db31fb5a8470e3784ee04c97dcaf871728af1b4`, tracked in [draft PR #103](https://github.com/kaministrator999-ui/Swrlzkamico/pull/103), built on v209.1. Original branches/PRs remain independent; do not merge or deploy the initial v210 branch over the storage fix.
- Clean-room Chat source version `1.1.05`.

### Native Chat data contracts

Existing verified Google identity and Redis snapshot CAS key remain the sole native Chat authority; old Fernet-encrypted v1 snapshots load with no forced mutation. New snapshots use bounded zlib-compressed Fernet encryption (inline or independent encrypted-value chunks). A new revision becomes visible only after all chunks are confirmed and the same owner-specific manifest CAS commits successfully; missing or tampered chunks fail closed. Raw size and chunk-count bounds remain; no unbounded or silently truncated storage promises.

The Station prevents its failing final assistant save from being disguised as a durable completion or recursively retried as an additional save; Chat displays an unsaved-response warning while allowing the transient answer to be copied. No user archive deletion, import reset, plaintext logging, model retraining, alternate persistent store, or automatic data migration occurred.

### GitHub consent contracts

The Google-owner encrypted OAuth link remains separate from ChatGPT's own GitHub plugin authorization. GitHub commands are request-anchored. `@GitHub permissions` reports verified capabilities; repository reads require observed actual access, and unknown permission failures are labeled unverified, not fabricated missing scopes. Optional repository writes require both granted scope and effective repo permissions, an explicit first proposal and a second one-time confirmation, followed by fresh permission verification. No self-granted OAuth, arbitrary file editing, PR merging, repository deletion, or automatic deployment authorization.

## CI evidence at the **exact integrated source**

- [GitHub/Google account and persistence CI #38166008958](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38166008958): **SUCCESS**.
- [HF candidate offline #38166012949](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38166012949): **SUCCESS**.
- [Mobile integrity #38166013025](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38166013025): **SUCCESS**.
- Prior independent v209.1 tests exercised native history greater than the old 2.2 MB cap, a real Station `/send` synthetic request, account Redis save, cache clear/restart, same-thread readback, legacy-record loading, missing/tampered encrypted chunks, CAS conflict rejection and owner isolation. v210 tests cover effective permission and OAuth-consent boundaries. All are synthetic; none inspected owner transcripts or confirmed owner browser behavior.

## Guarded production publication

- Existing `main:.deploy/HF_SPACE_REQUEST.txt` requested **one** exact integrated source SHA `4db31fb5a8470e3784ee04c97dcaf871728af1b4`, nonce `2026-10-11-v2091-v210-combined-github-consent-and-chat-save-001`.
- [GitHub Actions HF release #38171052805](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38171052805): terminal **SUCCESS**. Request authorization, source pinning, package checks, original model validation, R39 reconstruction, 700M smoke test, existing Space snapshot and upload succeeded.
- New published Space revision: `e77d03f2263bd3be1734fe32aeda16c3ce74c6a9`.
- Previous rollback checkpoint revision: `5a4e2286c6ff1a567680331485d836fd07d4938e`.
- Release checkpoint artifact `hf-release-checkpoint` ID `11713578138`: `knownGood=false`, `verificationState=DEPLOYED_UNVERIFIED`. No signed-in acceptance has yet been performed.

## Atomic runtime version authority

Commit `runtime@25bfb1a3375c023b80616e99f77500a0d19a9556` atomically updated and read back:
| Registered module | Before | After |
|---|---|---|
| Repository Work | 1.0.149 | **1.0.150** |
| Server Runtime | 2.3.361 | **2.3.362** |
| Web Chat | 1.5.100 | **1.5.101** |
| Google Account Architecture | 1.0.13 | **1.0.14** |
| LALM Engine / Station | 2.1.186 | **2.1.187** |

Remaining registered modules — Runtime Manifest 152, Stream Contract V2, Online Research 1.0.30, Deployment Control 1.0.41, others — remain as previously registered. Native APK modules remain UNASSIGNED. Versions and successful publication alone do not establish live correctness.

## Owner acceptance to close behavioral validation

1. Open `https://kamiloki-swyrlz.hf.space/` in two Android browsers. Verify both display the **same signed-in Google account**, not just a local profile name.
2. In Browser A, start a **small non-sensitive** conversation, wait for a completed assistant response and reload. Confirm the new conversation and its messages remain.
3. In Browser B, reload; confirm exactly the same new thread without importing or resetting the 2,556-thread archive. Create another small thread in Browser B. Reload each browser and check both threads and saved export.
4. If failure persists, capture the visible safe `CHAT_SAVE_FAILED`, 409, 413, 503, or login status/error receipt; **do not share cookie, OAuth code, access token or private transcript**. Distinguish an oversized owner snapshot, stale user identity, transient service outage and observed permissions rather than assuming one cause.
5. Separately use GitHub Settings `Check permissions` and explicit Chat `@GitHub permissions`. Any write test must be specifically chosen and confirmed by the owner; reading access never silently escalates.

**Final tier state:** SOURCE/CI VERIFIED; GUARDED HF PUBLICATION SUCCESS; VERSION AUTHORITIES RECONCILED; USER LIVE NEW-CHAT SAVING AND OAUTH ACCEPTANCE PENDING. No known-good promotion.
