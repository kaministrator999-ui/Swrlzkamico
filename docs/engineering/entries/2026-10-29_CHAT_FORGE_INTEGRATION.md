# Chat side panel, shared Google account and scoped §E editing

Mode: IMPLEMENT. Lifecycle: BRANCH_ACTIVE. Status: implementation verified locally; exact-source CI/publication pending.

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
