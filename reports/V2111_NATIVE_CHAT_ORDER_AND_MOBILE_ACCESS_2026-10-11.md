# v211.1 — Native Chat newest-first ordering and mobile drawer accessibility

Date: 2026-10-11. Canonical existing HF Space: `kamiloki/Swyrlz`.

## Owner-discovered defects

The signed-in Android §wyrlz Chats drawer presented native conversations in their unsorted Redis insertion order. Newly created chats appeared near the bottom. The native Chat JSON export had the same thread-array order. The imported ChatGPT archive is a distinct system whose listing already uses `ZREVRANGE` (newest-first) and was not changed.

A second mobile screenshot/report showed the bottom chat rows becoming visually overlapped or inaccessible by the Versions control after the tall account/GitHub panel. In the v211 source a fixed-height flex sidebar contained a nested capped `max-height:36dvh` scrollable thread list plus a flex footer `margin-top:auto`, leaving too little usable space in Android's viewport. These are confirmed source/layout flaws. **Neither defect alone proves every previously missing native chat was durably stored.**

## Targeted change and retained authority

The published v211 `feature/github-model-guided-progress-v211@4da362e9f89339b37017c0a8aeba65948008f7d2` was the exact base for the isolated and deployed [draft PR #107](https://github.com/kaministrator999-ui/Swrlzkamico/pull/107), branch `fix/native-chat-mobile-sidebar-access-v2111@2284fccb589625449fc83405e170fcd428864834`.

- Canonical clean-room Chat `chat/§wyrlz/index.html`: make the **entire drawer** a single `100dvh` scrollport including Google/GitHub account card, all native chat rows, and Versions at the end. Remove capped nested chat list; respect Android bottom safe area. Versions no longer sits over unreachable bottom rows; user can scroll to it normally.
- Native list view: pinned conversations first; others ordered by most recent actual message timestamp, then optional updatedAt and createdAt, with deterministic ID tie ordering. Unsaved new draft remains first. Sort a copy of the source array only.
- Station `/api/lalm_station/export`: present native thread list in the same pinned/newest-first order without changing conversation message order or persisted Redis insertion order. Other export fields unchanged.
- Chat source version `1.1.06 → 1.1.07`; diagnostic camera and original stale HTML metadata version aligned.
- **No Redis writes/migrations**, no deletion/reimport of ChatGPT archive, no modification of Google account, selected model weights, v211 inference/GitHub tool logic or explicit permission/confirmation safeguards.
- Older v210-based [PR #105](https://github.com/kaministrator999-ui/Swrlzkamico/pull/105) was source-only and was **not deployed** over v211. This integrated v211-based patch preserves newer behavior.

## Tested candidate and CI

All on exact source `2284fccb589625449fc83405e170fcd428864834`:

- [Google/account CI #38173174329](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38173174329): **SUCCESS**. Includes authenticated Station export endpoint and storage-immutability regression, plus separate Node deterministic newest-first/unchanged-source-array and mobile drawer CSS/markup invariant tests.
- [Hugging Face candidate #38173202771](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38173202771): **SUCCESS**.
- [Mobile UI integrity #38173202808](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38173202808): **SUCCESS**.

These are source and synthetic UI tests, not physical Android touchscreen acceptance.

## Single guarded production release

- Existing `main:.deploy/HF_SPACE_REQUEST.txt` requested **one** approved release from exact SHA `2284fccb589625449fc83405e170fcd428864834`, nonce `2026-10-11-v2111-native-chat-scroll-and-newest-first-001`, commit `52a84d0be271ed2626a0856264bc6f2da3522060`.
- [Guarded HF workflow #38173292795](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38173292795) terminal **SUCCESS**. Source pin, existing Space predeploy snapshot, package/lyric/R39/kernel/700M smoke, and upload/revision capture all passed.
- New `kamiloki/Swyrlz` Space revision: `6c06b10f6328da082ead77a77c1d1b690495bb17`.
- Previous rollback Space revision: `e5760d09a5e30a5ba1cfba3b52c28a4127248e49`.
- Terminal release checkpoint artifact: `hf-release-checkpoint` ID **11714418503**; `knownGood=false`, `verificationState=DEPLOYED_UNVERIFIED`. Source/CI/deployment is verified; actual private-account mobile behavior is still awaiting live owner confirmation.

## Runtime registry reconciliation

Atomic commit `runtime@216715faab329508881b41231e0e6ea0f5062e7a`, all affected modules re-read:

| Module | Prior | New |
|---|---|---|
| Repository Work | 1.0.151 | **1.0.152** |
| Server Runtime | 2.3.363 | **2.3.364** |
| Web Chat | 1.5.102 | **1.5.103** |
| LALM Engine / Station | 2.1.188 | **2.1.189** |

Google Account 1.0.14 remains unchanged; all unrelated registered modules (Online Research, manifest, Stream Contract, §E/animation, native APK reservations etc.) unaffected.

## Owner acceptance

1. Open `https://kamiloki-swyrlz.hf.space/` after new published revision loads and expand the Chat drawer on Android.
2. The newest unpinned native conversation should appear first below pinned chats, not at the bottom. Check the list while account/GitHub panel is expanded, scroll down through **all** chats, and confirm the Versions block appears only after the last row and does not intercept taps.
3. Create a small new conversation, reload the browser, and check that it appears at the top (unless pinned threads exist). Repeat from the same authenticated Google account in another browser. An export should list native threads in the same order while messages within each thread are chronological.
4. If a thread still disappears after reload, treat that as a **separate native persistence failure** with safe `409/413/503` or `CHAT_SAVE_FAILED` status evidence; don't assume the ordering correction cured it. Preserve older encrypted native messages and the imported archive without resets.

**Final project tier state:** UI SOURCE/CI VERIFIED / GUARDED HF PUBLICATION SUCCESS / REGISTRY RECONCILED / USER ANDROID TAP/RELOAD ACCEPTANCE PENDING. Never mark known-good on a release receipt alone.
