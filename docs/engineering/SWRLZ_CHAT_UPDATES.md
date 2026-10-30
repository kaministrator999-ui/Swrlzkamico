# Chat update dialog and recorded history

Current announcement: `chat-forge-project-workflow-20261030`, tracked in [the project workflow checkpoint](entries/2026-10-30_CHAT_FORGE_PROJECT_WORKFLOW.md). It explains independent starter copies, visible editor creation, current-project context and the distinction between local recovery and explicit account saves. The preceding editor/project notes and all earlier records remain in history. The original dialog implementation and historical release attempts remain recorded in [their receipt](entries/2026-10-25_EDITOR_PROJECT_COMPLETION.md).

Chat now has a public **Chat updates** button beside its conversation export action in the side menu. A native modal presents the newest notes, then an expandable list of all earlier recorded Chat update entries. This follows the §E engine's exact-version preference pattern without importing the engine's release notes or version numbers.

The checkbox **Don’t show again for this update** saves a browser-local preference under the exact latest update ID. It suppresses that update across reloads and tabs in the same browser. A different latest ID is eligible to appear automatically. Closing without the checkbox dismisses the current update for the tab session. Opening Chat updates manually always works, including when automatic display was suppressed, and lets the user change the preference. Storage failures show a truthful notice; the current tab can still dismiss notes in memory. Escape and Continue synchronously save the actually displayed update ID and preference before closing. Native close events are queued, so relying on that event alone could lose session dismissal during an immediate reload; the close event remains an idempotent fallback. An update fetched at the same time cannot be accidentally marked as already seen. The preference does not change account or conversation data.

The manifest is fetched from the same-origin static Chat asset route with `cache: no-store` on startup, window focus, return to a visible tab, and a bounded two-minute visible-tab poll. Automatic opening waits while generation is busy, a nonempty input/draft has focus, Settings/Work is open, another native modal is open, or the page is hidden. An empty focused composer does not prevent the startup announcement. Manual opening is immediate. Failed fetches preserve previously loaded notes; manual opening exposes a retry action. All note content is rendered using text nodes. No manifest text becomes HTML or executable code.

The dialog uses the browser's modal top layer, an explicit Tab/Shift+Tab wrap, native Escape dismissal, and focus return to the manual opener or visible menu button. Its content scrolls independently of its footer; the checkbox and Continue action remain reachable on a 360 × 640 touch viewport.

## History provenance

`chat/§wyrlz/assets/chat-updates-v1.json` contains the newest stable checkpoint ID and **267 previous recorded entries**:

- 250 records from the full, non-shallow `origin/runtime` history of `versions/web-chat.txt`, preserving each record's actual version, commit date, commit subject and full source commit. Repeated versions and failed attempts remain historical records; they are not silently recast as successful releases.
- 14 earlier Chat entries from `SWRLZ_VERCEL_CHAT_CHANGELOG.md`, preserving the documented version labels/ranges, dates and original recorded notes. These include the initial Chat 1.0.0 entry on 2026-09-06. Historical Vercel references describe past deployments and do not redirect current publication away from the Hugging Face Space.
- The preceding `chat-forge-account-panel-20261029` integration and `editor-project-completion-20261025` records remain source-pinned history.
- The preceding `6240d7151692898b9f30e75675707083ddb7f4cc` Qwen source update, explicitly limited to its recorded cube-viewer proof. It does not claim editor acceptance.

The manifest records the exact registry snapshot commit and each entry's source path/commit. `scripts/build_chat_update_history.py` rebuilds these records from existing repository evidence and refuses to treat a shallow checkout as complete history. “All previous recorded updates” means these available repository records, not invented entries for missing version numbers. The latest checkpoint has an ID rather than an unallocated canonical semantic version; normal release bookkeeping remains authoritative.

## Source surfaces and verification

Canonical ownership is `chat/§wyrlz/index.html` for the menu action and dialog styling; `assets/chat-updates-v1.js` for dialog behavior; and `assets/chat-updates-v1.json` for public notes. `scripts/prepare_hf_space.py` stages both new assets byte-for-byte. Station's existing `StaticFiles` mount serves JSON and JavaScript without a new account endpoint or authorization change. Existing artifact/archive helpers are unchanged.

`node tests/test_chat_updates.mjs` passes in real Chromium. It covers all 267 rendered history entries, hostile-looking text remaining literal, focus wrap/Escape, manual reopening, local suppression across reloads/new tabs, newer-ID reopening, generation/draft deferral, empty-composer startup, fetch failure/retry, mobile layout/touch dismissal, and disabled-storage behavior. It does not substitute for hosted model or live deployment acceptance. Candidate staging/check passes, and FastAPI TestClient reads both new Station static assets with correct MIME types and byte-identical bodies.


## Exact-source CI observation and failure visibility — 2026-10-26

HF candidate run `40234129564` for source `0a1bc4fdf8c5f8e6bdd2c4ee7d7961b75835d8a6` failed its combined browser installation/ZIP/dialog step after all earlier source checks passed. The public checks API exposes a generic exit-one annotation; the full log download redirects to a host outside the current session network policy. The precise failing command is therefore not established by this observation. A local actual Chromium dialog rerun passes; that does not convert the failed CI run into success.

The candidate workflow now separates pinned Playwright/Chromium installation, ZIP browser checks, and dialog browser checks. `scripts/ci_capture_failure.py` streams command output while redacting credential-like environment values and emits a UTF-8-bounded, workflow-escaped failure-tail annotation, readable through the checks API. It preserves the command exit status, executes argument lists without a shell, and never prints the process environment. Three focused tests verify exit/redaction/escaping, successful-command behavior, and size/multiline-credential handling. This is a visibility repair, not an inferred fix to an unidentified browser/install failure. The next exact-source run must establish the actual outcome.
