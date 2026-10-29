# Chat side panel, shared Google account and scoped §E editing

Mode: IMPLEMENT. Lifecycle: ACCEPTED_WITH_FOLLOW_UP / DEVICE_TEST_PENDING. Status: source, documentation and authorized publication completed.

The user explicitly requests the full existing Chat as a §E pop-out side menu,
shared Google identity/history/settings, account-owned §E Save/Load, and AI editor
access only while Chat is operating inside §E. Implementation and the existing
governed release paths are authorized; no extra permission is waiting.

## Baseline and prior work

Use accepted Chat f925e2012ed7ece820e3272700bc6619846c2085, observed RUNNING at
HF48515f7fc6e8cb7b4450725320e8fed64fb886e6. Current §E source is main225650ceee808706dd5a73b0c66978e73b00775c,
v11.167, observed static Space RUNNING at88d461787534b7d6ffa37ab536b69cc324cf5376.
Its199-patch reconstruction is6,962,001bytes/SHA256ffcc4a8b9c7902a8c2b673347ad6093219a81a2e562688c6b172a47c5dbd2412;
historical final manifest/request seals are null, not independently sealed PASS.
Reseal only the changed successor. Preserve all68 assets and existing native/LAN
work. Swrlzing-core remains unchanged at310ce70ae77815c82161d43c5cd0f6bb8e3d4812.

The unaccepted starter/reviewer experiments remain at99a7aa401a27719bc25bd8129aed3a15eb2fffd8
on their original branch, REPAIR_REQUIRED and not deployed. Neither7B nor14B
self-review established reliable acceptance. No weights/default/hardware change
is included in this integration.

## Architecture reconciliation and documentation impact

Chat already owns verified Google subjects and encrypted CAS history. §E is a
static native editor with local/download saves and an exposed native agent API.
There is no current embed bridge. HF Chat returns profile.version0 without its
frontend's expected profile endpoint, so shared settings require an actual
encrypted owner-scoped implementation. Do not reuse legacy random-user-ID stores.
Real native scenes can exceed70MB raw; project storage must be independent of
the Chat snapshot and must never truncate levels/geometry/workspace files.

Follow [the integration contract](../CHAT_FORGE_EMBEDDING.md). Documentation
impact: account/storage/auth trust, Chat surface and inference tool capability,
§E UI/native actions, schema/transport, diagnostics, source integrity, independent
release lanes, version authorities, known limitations and handoff. Constitution
source was not present at the specified path; no missing authority is invented.
Current canonical routers, §E AGENTS/RELEASE_PROCESS and related owners govern.

Integration source branch starts at accepted Chat and imports exactly the current
main §E project/workflow/router. It does not merge the whole divergent Chat tree
into main. Fresh narrow writes preserve concurrent main work; no force pushes.
Chat API/UI release and separate §E final-trigger release retain their existing
gates. Versions are read afresh at their owning commit boundaries, not reserved.

## Verification and disposition

Read-only source audits and fresh HF metadata establish the baseline only.
Implementation, source tests, controlled two-origin browser/identity/storage
tests, source packages and terminal deployment evidence are pending. Real user
Google login and owner-device editor acceptance remain distinct from controlled
credentials and local tests. The cloud environment currently blocks direct §E
host requests with403; its two canonical hostnames have been saved in the
environment draft, awaiting product Review/Save/Publish. Independent work continues.

No new feature, source package or live integration is claimed complete by this
entry. Next gate: implement the bounded canonical owners and verify their combined
account/action boundaries. Approval waiting: NOT APPLICABLE within requested scope.

## Implemented source checkpoint

Full canonical Chat iframe and Google popup broker are implemented, together with
same-owner history, encrypted CAS profile Save, separate multipart native project
Save/Load, native editor leases, fixed typed Qwen plans, actual host receipts and
native Undo/Redo. Standalone Chat cannot acquire a native context from request
flags or history. Account changes, panel/document closure, thread/project changes,
root-login revocation and expiry fail closed. Settings bootstrap version0 remains
unsaved until explicit Save; saved user/companion fields guide inference with
speaker separation. A scoped CSP permits the existing HF wrapper and two §E
origins; the sign-in popup cannot be framed.

New source owners: `forge_embed.py`, `account_profile_store.py`,
`forge_project_store.py`, `brain_forge.py`, `forge_chat_actions.py`; Station/router
and both existing model engines integrate them. Canonical Chat owns
`forge-embed-v1.js`, `forge-connect.html` and its existing UI. §E appends
`v11_169_chat_account_panel.py` and `runtime/chat_account_panel_v1.js`, using real
native handlers. Literal native names remain text in the mobile inspector.
Production staging copies the canonical popup/broker exactly. The existing Chat
candidate workflow admits this integration branch and runs focused new checks;
the separate §E workflow adds only package/request identity validation, with no
broad game/browser suite.

Fresh main advanced to9c21f2ac90388d92d036ddfe856ca2d605c2a49e during implementation.
Its v11.168 Quest panel and exact seals are preserved. §E successor v11.169 has201
ordered patches,68 unchanged asset identities,6,995,656 HTML bytes and SHA256
`6e71a18f0279827ab876b78204437565e5d923818cc8052138919feecdf967d7`.
Historical v11.84 release-history generation reads the current manifest patch
list; reconstruct with the final manifest on disk before measuring. A cached
v11.167 fixture has older history bytes and cannot stand in for the final seal.
A fresh complete package matches the successor seal and verifies all68 assets.

## Bounded verification and repairs

- Repository offline workflow replay:120 commands PASS, zero failures,143s.
  Existing installed browser/dependencies substitute only installation. This
  working-tree replay precedes final focused fixes; exact committed CI is pending.
- New controlled auth/storage/native/Station tests and profile tests pass,
  including exact70MiB native preservation, concurrent CAS, failure recovery,
  owner isolation, invalid/replayed credentials, cancellation/revocation,
  standalone denial, per-embed event visibility and secret-free export.
- Canonical served-composition Chat passes real Chromium desktop1440x900 and
  mobile390x844: shared fixture history, settings first Save/default model,
  private bearer, native sideband and revocation, no horizontal overflow/errors.
- Actual native §E Chromium fixture passes desktop/mobile mesh add, exact literal
  text/material/position, native Undo/Redo, real scene actor and Undo, project
  scope, responsive sibling aside, Escape/focus and hidden-host denial. Cached
  baseline r1/r2 bytes are distinguished; final whole-source replay is pending.
- Existing GitHub source-change/Station tests46 PASS; drawer/IME, live cue,
  scroll reuse and Chat update dialog regressions pass. Announcement now includes
  this feature and preserves265 prior recorded entries.
- Actual pinned Qwen7B r1 produced a semantically correct fenced JSON plan which
  the strict transport rejected; retain REPAIR_REQUIRED r1. Constrained JSON
  decoding repaired that transport. R2 and final R3 passed two synthetic exact
  add/rename/transform plan cases and two nonmutation routing cases. CPU r3 first
  plan ~98s, so latency remains material. These are typed-plan results, not
  comprehensive project/model or real editor execution acceptance. No generated
  model JavaScript runs in the host. No model weights/default/hardware changed.

Controlled tests exposed and repaired prompt contamination by native labels,
executor admission leaving a queued generation stuck, an external-store lookup
on every25ms stream poll, and native mobile label HTML interpolation. Diagnostics
use bounded codes/random correlation IDs/counts, with camera OFF/ON parity; never
private account/history/settings/project content or credentials.

## Documentation impact and evidence boundary

Updated: this checkpoint, integration contract, root Roadmap event, Chat overview,
programming architecture, account runbook, diagnostic camera contract, update
history contract/feed, §E README/SPACE_README/Roadmap/Start, exact source manifest
and minimal release verifier. Strict legacy streamV2, activation manifest,
existing provider permissions and Swrlzing-core sandbox remain unchanged. This is
an additive Station NDJSON sideband, not a legacy stream protocol revision.
Documentation gate: source/current behavior PASS; release receipts will be added
when observed, without treating source checks as publication or user acceptance.

Current disposition: IMPLEMENTATION_VERIFIED / release pending. Source commit,
canonical source ZIP/checksum, exact remote CI, both workflow outcomes and live
identities remain to be recorded. Real Google sign-in, deployed Redis writes,
two-browser same-account continuity and owner-device UX are pending; the owner
signs in directly, with no passwords/codes in Chat. Source rollback preserves the
accepted Chat SHA and prior §E request/sealed source; storage namespaces are
additive and previous project/history pointers survive failed writes. Cleanup
may remain journaled after a confirmed save (`cleanupPending:true`). Account
embed credentials remain RAM-only and reconnect after reload/expiry.

Approval waiting: NOT APPLICABLE. Publication remains explicitly authorized.
Next gate: exact committed candidate CI, canonical packaging and the existing
separate guarded publication lanes, then record actual outcomes.

## Exact candidate publication request

Source `e4dee084f57788c3c6edc16381203d34ebc0c7e1`, exact [candidate CI](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40928848556) SUCCESS. Full final §E HTML6,995,656/SHA2566e71a18f0279827ab876b78204437565e5d923818cc8052138919feecdf967d7 passed actual native desktop/mobile Chromium with no page errors (controlled Chat/lease fixture). Final native inference functions match captured R3 exactly; final stricter routing/action guards revalidate all captured plans. This main commit requests only the existing Chat guarded lane; §E source and its separate final trigger follow after the backward-compatible backend is published. Real Google/deployed-store/device acceptance pending.

## Pre-publication §E account-switch correction

Initial source e4dee084f57788c3c6edc16381203d34ebc0c7e1 passed exact CI40928848556 and Chat guarded workflow40929174874. Chat Space upload5058110eccab6ec8965f550998eb0645609785ba reached RUNNING; public route acceptance is being observed. A final host review found cloudRefs and visible cloud project metadata could remain after account changes, causing a safe server rejection when a new account attempted Save with another account’s project reference. The unreleased §E host now clears those IDs/revisions/list on the existing account-change signal, while ordinary thread changes retain the project revision. Local work stays local and no account data is copied. CPU and actual native-browser tests cover this correction. Chat/backend/inference files are byte-identical to published e4; no second Chat deployment is required for this host-only correction.

Current unreleased §E v11.169 seal:201 patches,68 assets,6,995,807 bytes, SHA2561c484cf4f627a87c95d720d11fabfe1fb9005f114c2a7712b67f7474222a3d84. Earlier6,995,656-byte source and immutable r1 package remain prior-candidate evidence, not rewritten. Exact successor CI, r2 source overlay package and §E final-only request follow.

## UPDATE FINISHED — publication and handoff receipt

Current release: Chat **1.5.158**, Google account architecture **1.0.18**, LALM
**2.1.204**, Server runtime **2.3.441**, Repository Work **1.0.241**. Exact prior
values and changes were committed with the runtime Roadmap in
`9ba69e6255acfd5f47ad49b576b40519591165bc`. Manifest152, strict streamV2, deploymentcontrol1.0.41 and
other owners remain unchanged. This is registered source/runtime evolution,
not model training or real-account acceptance.

- Accepted Chat source `e4dee084f57788c3c6edc16381203d34ebc0c7e1`;
  [exact CI40928848556](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40928848556) SUCCESS;
  [guarded deployment40929174874](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40929174874) SUCCESS.
  Space `5058110eccab6ec8965f550998eb0645609785ba` observed RUNNING with matching
  runtime revision and immutable source provenance. Public popup/broker return
  byte-identical200; anonymous profile/projects and forged editor lease return401.
- §E application candidate `51d3d44aa3c5ac85f65cf83e0505dd7442c3c6b1`;
  [exact CI40930279362](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40930279362) SUCCESS.
  Main source34eed0839902dae96941fed1ab0cff9e9cf4a10a and first final-request-only
  commit77d7c9cf8c59e3cc5a3fba3a2713ba3993e6c52b deployed via40930867494 SUCCESS.
  Docs-only6a53f242f2739f0348f962564ba6c1ec24c41a36 repaired the HF README's release
  evidence link without changing HTML/version; separate final-request-only
  commitf9ad333f4382ee4db1f7148c4e21f13a50054529 published through
  [deployment40931411290](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40931411290) SUCCESS.
  Final static Space `6fdc0351b04c6b27a5f65b6c4402dfb259b61a72` RUNNING. HF stored HTML/SOURCE receipt
  agrees: **v11.169 /201 patches /68 assets /6,995,807 bytes /SHA256
  1c484cf4f627a87c95d720d11fabfe1fb9005f114c2a7712b67f7474222a3d84**.
- Chat/backend/inference source is byte-identical between these two candidate
  commits; only the unreleased §E account-reference correction differed. No
  second Chat upload or model change was needed. Existing separate release lanes
  and concurrent v11.168 Quest implementation were preserved.
- Final exact native Chromium source passes desktop/mobile including native
  mesh/actor edits, Undo/Redo, exact hostile-looking labels, scoped permissions,
  account-switch metadata clearing and no page errors. Canonical Chat desktop/
  mobile, saved-profile/owner isolation,75 controlled backend tests and source
  model plan probes pass within their recorded bounds. Source CI ran the real
  workflow including adjacent regressions. No broad game suite was dispatched.

Canonical source overlay: `chat-forge-integration-source-r2.zip`, **1,389,782bytes**,
SHA256 **7bc4681c289b2331a34330f3c4ba758e96f83067a88c675932fb6ab95ef3555a**.
It carries43 full changed sources/docs, exact reconstruction patch/manifest and
public synthetic evidence. Applying to the recorded composite baselines proves
the entire Git tree `dbba295b36805eaa5f8452a78b2c58a7c9a3309b`. This is an overlay
requiring existing repository baselines, not a full standalone app or model
redistribution. Immutable r1 (`cda812e421fc6687c5f0b4b7c273b97a9932b3a67e1461e9bca1b436e8560337`)
remains prior-candidate evidence. Delivery files are in
`/workspace/cloud-setup/deliverables`; the final handoff adds current release
receipts without rewriting source archives.

Documentation gate PASS. Source/package/CI/promotion/build/HF runtime observations
are recorded separately. Direct static-host access remains denied by the cloud
network policy; the static Space/runtime and stored HTML receipt are confirmed
through the allowed HF API, with exact local/native Chromium acceptance. No
claim of a live hosted browser, actual Google login, deployed private project
write/read or physical Android/Quest UX is made. These remain owner acceptance:
open §e, choose § Chat → Sign in with Google, connect the same account as standalone
Chat, verify history/preferences, Save/Load a native project and request a native
edit then Undo. The user signs in directly; no passwords or codes are collected.

Current disposition **ACCEPTED_WITH_FOLLOW_UP / DEVICE_TEST_PENDING** for this
bounded integration. Earlier broad starter/editor/long-form model failures remain
REPAIR_REQUIRED and were not promoted by native-plan tests. CPU planning latency
and RAM-only reconnect behavior remain known limits. No weights/default/hardware
change; Swrlzing-core remains310ce70ae77815c82161d43c5cd0f6bb8e3d4812.
Approval waiting: NOT APPLICABLE; authorized publication is finished. Next gate:
real-account and owner-device acceptance, with any new defect handled as its own
bounded successor. Environment configuration is separately saved for Review and
Publish; a draft is not a published environment snapshot.
