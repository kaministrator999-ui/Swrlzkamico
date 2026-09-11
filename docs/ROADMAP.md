# §wyrlz Server Roadmap

## Current release

**Server v2.3.9**

This is the current runtime development release. Stable deployed infrastructure remains Server v2.3.3 until a future stable-infrastructure deployment changes it.

### Module state

- **Chat v1.4.9** — Chat now resolves display versions through the per-module version-file index instead of a shared value registry.
- **LALM UI v1.0.0** — unchanged in this release; now has its own canonical version file.
- **LALM engine v2.1.18** / revision `2.1.18-hot-boundary-v9-effective-receipt` — unchanged; now has its own canonical version file.
- **Server UI v1.0.0** — unchanged; now has its own canonical version file.
- **Admin Web v1.0.0** — initial canonical version-file enrollment; behavior unchanged.
- **Google Account architecture v1.0.0** — initial canonical version-file enrollment; behavior unchanged.
- **Client APK / Server APK** — version authorities reserved as `UNASSIGNED` until their actual artifacts/source versions are verified.

## Server v2.3.9 — 2026-09-10

### Changed

- Replaced the single value-bearing root `VERSION.txt` with an index that maps stable module IDs to independent canonical files under `versions/`.
- Added dedicated version authorities for Server runtime, Server UI, Web Chat, stream contract, LALM UI, LALM engine, Admin Web, Google Account architecture, Client APK, and Server APK.
- Existing unversioned structures were enrolled with explicit baselines where the repository has an identifiable structure; APK entries remain `UNASSIGNED` rather than inventing versions for artifacts that are not verified in this repository.
- Changed Chat version presentation so it reads the root index and then fetches the specific Server runtime, Chat, stream-contract, and LALM version files needed for display.
- Advanced Chat from `v1.4.8` to `v1.4.9` because its version-resolution behavior changed.
- Advanced overall Server from `v2.3.8` to `v2.3.9` because this is a new runtime development event.
- No LALM behavior, Admin behavior, Google account behavior, Server UI behavior, or APK artifact behavior changed in this event.
- Kept the implementation entirely on `runtime`; no stable-infrastructure deployment or server restart is required.

### Architecture rule established

- Every independently evolvable structure gets its own canonical version file.
- `VERSION.txt` is an index of module IDs to version-file paths, not a duplicate list of version numbers.
- A display or update checker fetches only the module file(s) it needs.
- New structures must receive and register a version authority when they enter the project lifecycle.
- Installed clients may compare their local version against the hosted canonical module file to decide whether an update is available.

### Verification state

- `VERSION.txt` now points to per-module files rather than embedding component version values.
- `versions/server-runtime.txt` reports `2.3.9`.
- `versions/web-chat.txt` reports `1.4.9`.
- Chat reads its displayed Server runtime / Chat / Stream / LALM versions from the corresponding per-module files.
- Existing module values were preserved where already established; unverified APK versions were not fabricated.
- **Deployment:** NONE required.
- **Server restart:** NONE.
- Final browser verification: reload Chat after runtime propagation and confirm the footer reflects the per-module files.

## Server v2.3.8 — 2026-09-10

### Changed

- Added the repository-level `VERSION.txt` canonical version registry for components that expose version information.
- The registry contains the authoritative Server runtime, Server UI, Chat, Stream, LALM UI, and LALM engine version/revision values.
- Changed Chat version presentation so it fetches the registry instead of keeping duplicate Chat/Stream/Server/LALM version constants in `web/chat_version.js`.
- Advanced Chat from `v1.4.7` to `v1.4.8` because the user-facing version-source behavior changed.
- Advanced overall Server from `v2.3.7` to `v2.3.8` because this is a new server runtime development event.
- LALM UI, Server UI, and LALM/R39 engine source were not changed, so their versions remain unchanged.
- This establishes the same source-of-truth pattern needed for future update checks: clients and UI surfaces can retrieve the hosted registry and compare the relevant installed/local version against the authoritative available version.
- Kept the work entirely on `runtime`; no stable-infrastructure deployment or server restart is required.

### Failure / history

- The previous Chat footer mixed an authoritative deployed Server status value with a separately maintained runtime development version, producing a confusing `Server v2.3.3` display while the runtime release lineage had advanced.
- The deeper architectural issue was duplicate version ownership: components had version values in code while other surfaces fetched or repeated those values independently.
- Server 2.3.8 replaces that pattern with one canonical repository registry that consumers fetch when they need version information.

### Verification state

- `VERSION.txt` exists on the runtime branch and contains the current component version registry.
- `web/chat_version.js` no longer owns hardcoded Chat/Stream/Server/LALM display version constants; it fetches and parses the canonical registry.
- Runtime Server version source advanced to `2.3.8`.
- Chat version advanced to `1.4.8`.
- No LALM UI or engine source was changed.
- **Deployment:** NONE required.
- **Server restart:** NONE.
- Final browser verification: reload Chat and confirm the footer reflects the registry values and no longer presents the deployed infrastructure version as the runtime release version.

## Server v2.3.7 — 2026-09-10

### Changed

- Corrected the main Chat page status indicator so its status dot and label are driven by the authoritative `/api/lalm/status` readiness state instead of the separate upstream bridge-configuration state.
- The main Chat indicator now agrees with the sidebar: ready local LALM state is shown as green **LALM ready**, warming state remains amber, and an unavailable/error state is red.
- Kept the correction in the canonical runtime-owned `web/chat_version.js`, avoiding another dependency on the separately propagated enhancement asset.
- Bumped Chat from `v1.4.6` to `v1.4.7` because the user-facing Chat status behavior changed.
- Bumped overall Server from `v2.3.6` to `v2.3.7` because this is a new server runtime development event.
- LALM UI and LALM/R39 engine versions remain unchanged because their source/behavior did not change in this event.
- Kept the change entirely on `runtime`; no stable-infrastructure deployment or server restart is required.

### Failure / history

- The sidebar and main Chat status indicator had diverged because they were evaluating different status concepts. The sidebar was already reading `/api/lalm/status`, while the main indicator was evaluating upstream bridge configuration.
- The live screenshot demonstrated the resulting mismatch: the sidebar showed **Local LALM ready** with a green indicator while the main Chat status remained amber.
- This release unifies the user-facing status presentation around the authoritative local LALM readiness result without changing the underlying LALM engine.

### Verification state

- `runtime/web/chat_version.js` now reads `/api/lalm/status` and applies the same ready/warming/error state to both the sidebar indicator and the main Chat status pill.
- Server version source advanced to `2.3.7`.
- Chat version source advanced to `1.4.7`.
- No LALM UI or engine source was changed.
- **Deployment:** NONE required.
- **Server restart:** NONE.
- Final browser verification: reload the live Chat page and confirm the main status dot and sidebar dot remain visually synchronized when local LALM readiness is green.

## Server v2.3.6 — 2026-09-10

### Changed

- Fixed `web/chat_enhancements.js` so its local LALM status updater no longer installs a `MutationObserver` that observes the same DOM nodes it rewrites.
- The previous observer could repeatedly trigger itself because `paint()` changed `#nodeTitle` / `#nodeDetail`, which generated new mutation records and re-entered the observer. This is the likely cause of the Chat page appearing stuck/loading while the LALM indicator itself showed ready.
- Replaced the observer with a bounded 15-second status poll and guarded text writes so unchanged values do not create unnecessary DOM mutations.
- Bumped Chat from `v1.4.5` to `v1.4.6` because the user-facing Chat runtime implementation changed again.
- Bumped overall Server from `v2.3.5` to `v2.3.6` because this is a new server runtime development event.
- LALM UI and LALM/R39 engine versions remain unchanged because their source/behavior did not change in this event.
- Kept the correction entirely on the `runtime` branch; no stable infrastructure deployment or server restart is required.

### Failure / history

- Server 2.3.4 added local LALM readiness handling to `web/chat_enhancements.js`.
- Server 2.3.5 moved authoritative readiness presentation into `web/chat_version.js` after production asset propagation for the separate enhancement asset was found stale.
- Inspection of the 2.3.4 enhancement implementation exposed a self-triggering `MutationObserver`: it watched `#nodeTitle` and `#nodeDetail`, then its own `paint()` function wrote to those nodes. That creates a recurring mutation cycle and can monopolize browser work.
- Server 2.3.6 records this as a new corrective runtime event rather than rewriting the earlier release history.

### Verification state

- The production LALM backend remains independently verified as `interactiveReady: true` and `warmModelResident: true`; the defect isolated here is browser-side Chat behavior, not LALM readiness.
- `web/chat_enhancements.js` now contains no `MutationObserver`; its updater performs a direct status fetch and bounded polling.
- `web/chat_version.js` canonical Chat version/status source is now Chat `v1.4.6` in `runtime`.
- Runtime commits:
  - `34f57ab433226fa0a0a8f47e929ae17dbc0ce19a` — enhancement observer-loop fix.
  - `4952fef7519946b8b04dece24077d3353df737ae` — canonical Chat version/status bump to v1.4.6.
- **Deployment:** NONE required.
- **Server restart:** NONE.
- Final browser verification remains required: reload the live Chat page and confirm it remains responsive instead of appearing stuck/loading while the green **Local LALM ready** indicator remains stable.

## Server v2.3.5 — 2026-09-10

### Changed

- Moved the authoritative local LALM status presentation into `web/chat_version.js`, the canonical Chat version/status asset that was verified live after the 2.3.4 runtime update.
- The Chat sidebar now directly queries `/api/lalm/status` and displays:
  - **Local LALM ready** when `interactiveReady` is true.
  - **Local LALM warming** while readiness is not yet established.
  - **Local LALM unavailable** when the status probe reports an error or cannot be reached.
- Bumped Chat from `v1.4.4` to `v1.4.5` because the Chat runtime implementation changed again.
- Bumped overall Server from `v2.3.4` to `v2.3.5` because this is a new server runtime development event.
- LALM UI and LALM/R39 engine versions remain unchanged because their source/behavior did not change.
- Kept the correction entirely on the `runtime` branch; no stable loader/infrastructure deployment is required.

### Failure / history

- Server 2.3.4 correctly identified the root cause and added the status override to `web/chat_enhancements.js`, but production verification showed that asset still serving the older 519-byte runtime content while the canonical `chat_version.js` had already propagated to Chat `1.4.4`.
- Rather than depend on the separate enhancement asset's propagation state, Server 2.3.5 places the same status correction in the canonical version/status asset already confirmed live.
- This preserves the versioning rule: the incomplete 2.3.4 attempt remains recorded; the next corrective attempt receives a new Server and Chat version.

### Verification state

- Production `/api/lalm/status` was verified to report `engineSource: runtime-override`, `interactiveReady: true`, `warmModelResident: true`, native backend availability, and the expected R39 model identity.
- Production `/live/assets/chat_version.js` was verified serving Chat `1.4.4` after the 2.3.4 merge, proving that the runtime branch hot path is active for that canonical asset.
- The status presentation is now implemented in that verified-live asset and will query the same authoritative LALM endpoint directly.
- **Deployment:** NONE required.
- **Server restart:** NONE.
- Final user-side verification: reload Chat and confirm the sidebar indicator is green with **Local LALM ready** instead of **Local inference pending**.

## Server v2.3.4 — 2026-09-10

### Changed

- Corrected the Chat sidebar's local inference status so it is sourced from the authoritative `/api/lalm/status` readiness object.
- A ready local R39 worker now displays **Local LALM ready** with a green indicator and the resident/native-backend detail.
- A warming worker displays **Local LALM warming** rather than incorrectly implying that local inference is simply pending configuration.
- An actual LALM status error displays **Local LALM unavailable** with an error indicator.
- Bumped Chat from `v1.4.3` to `v1.4.4` because the user-facing Chat status behavior changed.
- Bumped overall Server from `v2.3.3` to `v2.3.4` because this is a new server runtime development event.
- LALM UI and LALM/R39 engine versions were intentionally left unchanged because their behavior/source did not change in this event.
- Kept the change entirely inside runtime-owned Chat assets so the existing hot-runtime path can serve it without a Vercel deployment or server restart.

### Root-cause clarification

The previous screenshot's **Local inference pending** label was not evidence that R39 itself was unready. The live production `/api/lalm/status` response was verified with `interactiveReady: true` and `warmModelResident: true` while reporting `engineSource: runtime-override`. The base Chat page was instead using the absence of an upstream SERVER bridge to choose the misleading local-inference label.

Server 2.3.3's startup-warm path therefore remains valid; this 2.3.4 event corrected the Chat presentation layer. Its first asset implementation was not deterministically visible in the final production verification path, so the follow-up correction is recorded as Server 2.3.5 rather than silently rewriting 2.3.4.

### Failure / history

- Server 2.3.3 startup warm was initially interpreted as unsuccessful because the Chat sidebar continued to display **Local inference pending**.
- Direct production status verification showed the LALM/R39 engine was actually ready and resident, isolating the remaining defect to Chat status presentation rather than model warming.
- No LALM engine failure occurred in this update.
- No stable-infrastructure change was made.

### Verification state

- Current production `/api/lalm/status` was queried directly before the fix.
- Verified production response reported `engineSource: runtime-override`, `interactiveReady: true`, `warmModelResident: true`, and the expected R39 model identity.
- `runtime/web/chat_enhancements.js` was updated to consume `/api/lalm/status`, but production verification found the older asset content still being served.
- `runtime/web/chat_version.js` was updated from Chat `v1.4.3` to `v1.4.4` and was verified live.
- Runtime branch remains the live application source of truth.
- **Deployment:** NONE required for these runtime-owned changes.
- **Server restart:** NONE.

## Server v2.2.8 — 2026-09-10

### Changed

- Fixed mobile Chat sidebar stacking so the background Chat interface is dimmed while the sidebar remains bright above the scrim.
- The targeted CSS change is in `web/chat_enhancements.css` and removes the mobile `.app` stacking context that trapped the sidebar beneath the root-level scrim.
- Bumped Chat from `v1.4.2` to `v1.4.3` because user-facing Chat behavior/visuals changed.
- Bumped Server from `v2.2.7` to `v2.2.8` because a server runtime event occurred.
- Chat version rendering now retrieves:
  - Server version from `/api/server/status` → `version`.
  - LALM UI version from `/api/lalm/status` → `uiVersion`.
- Added mandatory version/roadmap rules to the runtime update guide and the project hotfix rules so future module updates preserve lineage and do not require duplicate hardcoded display values.

### Failure / history

- The original sidebar fix was committed as runtime commit `2b4bed5d175368278834a8d086b03537577fcfea` before the new version/roadmap contract was formalized.
- This release record retroactively closes that runtime event into the versioned Server v2.2.8 / Chat v1.4.3 lineage rather than erasing the earlier commit history.
- No LALM failure occurred in this update.

### Verification state

- Runtime source was fetched before the targeted CSS and version-source edits.
- `runtime` remains the live application source of truth.
- No Vercel deployment was created for the runtime Chat fix.
- No server restart was performed for the runtime Chat fix.
- The updated Chat version source was committed and can resolve live Server/LALM status versions automatically.
- Live browser verification remains the final user-side check for the visual sidebar result.

## Mandatory roadmap/version law

Every server runtime development event gets a new overall Server version, including a failed attempt.

Every module actually changed gets its own version increment in that Server event.

Every independently evolvable structure must have one canonical version file registered by stable module ID in root `VERSION.txt`. This includes server runtime, web interfaces, LALM components, protocol contracts, admin surfaces, account/auth architectures, APK clients, desktop clients, and future modules/pages/services that evolve independently.

A changed module updates its own version file in the same release event. A module that did not change does not advance simply because another module or the overall Server advanced.

Consumers must read the relevant module version file rather than copy another component's version into local code. The root `VERSION.txt` maps IDs to version-file paths and must not duplicate their version numbers.

Every event must update this roadmap/release lineage with:

1. Server version.
2. Affected module versions.
3. What changed.
4. Failed attempts, if any.
5. Verification state.
6. Relevant commit lineage.

## Roadmap direction

### Server

- Preserve runtime hot-update/no-redeploy workflow for runtime-owned application changes.
- Keep stable infrastructure changes isolated to `main` and the deployment boundary.
- Maintain complete Server release lineage.
- Treat root `VERSION.txt` as the version-authority index and `versions/*.txt` as module-owned version authorities.

### Chat

- Continue user-facing Chat/runtime fixes as targeted runtime hot updates.
- Fetch each displayed version from that module's canonical version file.
- Keep Chat status presentation tied to `/api/lalm/status`, not upstream bridge configuration.
- Preserve stream, request, session, and Truth Firewall boundaries.

### LALM

- Continue R39/native inference work independently of Chat where the user-facing Chat protocol is unchanged.
- Keep LALM UI and engine revision/version in their own canonical version authorities.
- Preserve correctness/reference fallback while native runtime work evolves.

### Clients / update checks

- Each independently released APK/client receives its own version file.
- A client carries its installed version locally, fetches its hosted canonical version file, compares versions, and follows its update policy when a newer/different version is available.
- Never assign an artifact version without verified source/artifact evidence; reserved entries remain `UNASSIGNED` until established.

## Version ownership map

| Module | Canonical version file | Consumers |
|---|---|---|
| Server runtime | `versions/server-runtime.txt` | Chat, status surfaces, update checks |
| Server UI | `versions/server-ui.txt` | Server/admin status surfaces |
| Web Chat | `versions/web-chat.txt` | Chat display, diagnostics, update checks |
| Stream contract | `versions/stream-contract.txt` | Chat and diagnostics |
| LALM UI | `versions/lalm-ui.txt` | Chat and LALM surfaces |
| LALM engine | `versions/lalm-engine.txt` | LALM status and diagnostics |
| Admin Web | `versions/admin-web.txt` | Admin UI/status/update checks |
| Google Account architecture | `versions/google-account.txt` | account/login diagnostics and release tracking |
| Client APK | `versions/client-apk.txt` | Android client update check |
| Server APK | `versions/server-apk.txt` | Android server update check |

**Rule:** root `VERSION.txt` is an index only. Each structure owns one canonical `versions/<module>.txt`. Displays and update-check consumers fetch the owner; they do not maintain a second copy.

**Update-check pattern:** local installed version → fetch root index → fetch relevant module version file → compare → apply the module's update policy only when an update is indicated → verify the resulting installed version.
