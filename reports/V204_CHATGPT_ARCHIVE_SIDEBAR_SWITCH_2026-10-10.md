# v204 — Imported ChatGPT conversations in the Chat sidebar

Date: 2026-10-10 (America/Chicago)

- Existing source base: `feature/google-chatgpt-archive-import-v202` at `b98abc7572be719eb4a31509a19f63159f641e77` (v203).
- Candidate/source: `feature/chatgpt-archive-sidebar-v204` at **`cf59320f169c1ae56efb0abb3b743ae165f4ae7a`**.
- Draft [PR #93](https://github.com/kaministrator999-ui/Swrlzkamico/pull/93), base `feature/google-chatgpt-archive-import-v202`.
- Google account/import CI: [#38109505024](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38109505024) — **SUCCESS**.
- HF candidate CI: [#38109505099](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38109505099) — **SUCCESS**.
- Guarded HF deployment: [#38109538281](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38109538281) — **SUCCESS**.
- Space: `kamiloki/Swyrlz`; published revision **`ea37fbeb7c71a90da2227f85cbcc90bdf7e30f83`**.
- Safe rollback Space revision: `5ba3d56c81003ceb89cb1d4af34de84b72a0b4a1`.
- Release checkpoint artifact `hf-release-checkpoint`, ID `11690853181`, reports `DEPLOYED_UNVERIFIED`. Publication verified via guarded workflow; live Android UI acceptance still pending.

## Requested design

User successfully imported an August 30 archive from ChatGPT: 2,608 unique threads in the original ZIP; app reports 2,556 saved text-bearing threads and 52 unsupported non-text selected branches. Those imported conversations did not appear in the native Chat sidebar because v202/v203 stored them in a separate, encrypted account-owned read-only archive accessible only through Settings. User requested a small 📄↑ document-with-arrow control just to the right of the CHATS label in their Android slide-out navigation. The button should toggle which conversation list the drawer displays.

## Implemented

- `chat/§wyrlz/assets/chatgpt-archive-sidebar-v204.js` adds a small, keyboard-accessible, `aria-pressed` document/up-arrow SVG toggle directly beside the existing CHATS title in the same drawer. Tapping enters **Imported chats**, tapping again restores **Chats**. The existing + New chat action is hidden only while browsing the archive.
- Imported listings are paginated at 30 conversations per request using **existing authenticated read-only** `GET /api/chatgpt_archive/list?offset=...&limit=30`. This loads only a bounded page from the 2,556 archived threads rather than duplicating them into the native `/api/lalm_station/sync` snapshot. Pagination uses Newer/Older controls and shows server-reported total. No client-held massive catalog.
- Selecting an imported row fetches the owner-scoped `GET /api/chatgpt_archive/thread/{id}`, closes the drawer, and displays its original saved user/assistant text in the **main conversation viewport**. Messages are rendered using `textContent` and `white-space:pre-wrap` (untrusted imported HTML remains literal). Rendering is progressive in batches of 100 messages via user-activated Show next messages so a long thread does not flood the DOM.
- In Imported mode the native `#messageList`, new-chat button, composer and jump-to-latest are hidden, **not deleted**. Returning to native restores the previous local thread navigation, chat composer and Station state. Background Station synchronization remains owned by native Chat.
- Account sign-out clears imported presentation, network responses are guarded against stale cross-view completion, and no private imported body text is copied into a test fixture, repository, model prompts, native chats or new storage layer. The prior Settings → ChatGPT imports upload/progress/delete interface is unchanged.
- The small new adapter is loaded by `hf_space/station.py` after the existing ChatGPT import settings script and shipped by `scripts/prepare_hf_space.py`. No change to account-auth owners or per-conversation encrypted storage endpoints.
- `tests/test_chatgpt_archive_sidebar_v204.mjs` uses synthetic DOM/fetch stubs to validate button accessibility, imported list and read-only thread opening, safe markup rendering, native view preservation, Google unauthorized gating, and no client mutation API calls. CI runs Node syntax, this regression and existing v203 archive/account/HF candidate suites.

## Release and version ownership

- Repository Work `1.0.142 → 1.0.143`.
- Web Chat `1.5.97 → 1.5.98`.
- Server Runtime `2.3.354 → 2.3.355` following successful guarded HF deployment.
- Google Account Architecture remains `1.0.11`: existing verified Google account and archive API contract reused unchanged.
- LALM Engine, Online Research, Deployment Control unchanged.

## Acceptance boundary

Workflow tests/packaging and guarded production publication succeeded. **Owner must reload /chat/§wyrlz on Android**, open sidebar, use 📄↑ to open imported conversations, choose a thread and switch back. Success of real tapping, responsive layout and live endpoint retrieval has not yet been demonstrated from the deployed phone, and is not claimed.

**No ZIP re-upload required**: the data from v203 remains encrypted and separately indexed. Imported threads are read-only; continuing them as native §wyrlz messages or injecting them as LALM model context is not part of this release.
