# Chat–§E project creation and live project context

Mode: IMPLEMENT. Lifecycle: BRANCH_ACTIVE. Status: implementation candidate; focused backend/development-browser evidence recorded, final verification and publication pending.

## Objective and success criteria

The owner requests basic cooperation between §wyrlz Chat and §E: create a new project from blank or a starter, visibly open it in the editor, protect reusable starters and let Chat know the actual project currently open. The first bounded update adds one native creation transition and reliable current-project context before subsequent work. It does not claim general project-building competence.

Success requires an independent named copy, actual editor handoff, confirmed local preservation of preceding work, unchanged starter definitions, bounded fresh context, receipt-grounded completion and fresh authorization for edits to the new project. Standalone Chat remains unable to operate §E. Explicit account save remains separate.

## Baseline and authority inspected

- Mobile repair source: `69c3f8737c5f57ea8e8e0cb9681395847a059a72`, §E v11.174;206 ordered patches,68 assets,7,008,228 generated HTML bytes, SHA-256 `1254e78c5bfd0d55a940f0e7d7c5fd590c325f89d4a45dc893b54f0f76fb9ce4`.
- Published mobile closure: main `5903ed4403b552c7c97395891075fe1d59acdebb`, runtime `2d7ef64` / Repository Work1.0.245; dedicated deploy40986968627 SUCCESS, static revision4d1c5e2a observed RUNNING. See [mobile checkpoint](2026-10-29_FORGE_MOBILE_VIEWPORT.md) for full identities and pending owner-device acceptance. Existing Chat/account/native integration and separate production lanes remain authoritative.
- Engine `AGENTS.md` and `RELEASE_PROCESS.md`, [Chat–§E contract](../CHAT_FORGE_EMBEDDING.md), [Chat overview](../SWRLZ_CHAT_OVERVIEW.md), current [AI runtime architecture](../SWRLZ_PROGRAMMING_LALM_RUNTIME_ARCHITECTURE.md), native bridge and new project-workflow source inspected.
- Requirements come from the owner's current request and prior authorization to implement/publish updates. Repository/runtime module authorities must be read fresh before final version closure; this candidate does not preassign their values.

## Implementation and contract

`project.create` accepts only `op`, `starterId` and literal `name` (1–100 characters under native name constraints). It is the sole operation in its batch. The starter ID must occur in fresh `context.starters`; hosts without a catalog report unsupported capability. The candidate native catalog has11 blank/starter choices, bounded by the server contract to16 unique entries.

A bounded deterministic resolver supports a fully specified current human command with one exact live catalog starter and quoted literal named/called project name. It rejects compound or extra content clauses instead of discarding them; it does not guess a starter/name. The result enters the same native validator, server batch and actual-receipt path. Other requests retain the semantic typed planner and clarification flow.

The native editor uses its existing starter builders, assigning the editable copy a persistent independent instance ID, projectName and sourceStarterId. Specialized native starter identity is retained; level bundles receive a project-specific root. Existing starter definitions remain unchanged. Workspace draft keys/export ownership prefer the persistent instance ID, and starter cloning suppresses legacy canonical draft hydration so one copy cannot contaminate another. The active-project status and fresh context identify the opened copy, current workspace, optional current level, dirty state, actual counts and selection.

A complete preceding native snapshot must commit to local IndexedDB before switching. A new snapshot commits before successful completion. A loader/new-save failure attempts to reopen the preceding copy and restore its previous dirty/history/Undo state; an unsuccessful reopen reports that the recovery copy was saved rather than claiming restoration. IndexedDB schema2 stores metadata separately from complete project bodies; listing reads at most1,000 metadata entries rather than loading every project body. My Projects adds **On this device** with local load/refresh; native edits schedule local autosave after350ms. Browser storage failures are visible; native file downloads remain available. None of this is an account save or a cross-device backup.

The successful native result includes the new project ID, literal name, starter ID, previous project ID and `localSaved:true`. The server accepts the changed-project finish only for this sole successful create with matching resulting context. The host then retires the old lease. Only the original generation and a still-live same-owner session can read its sealed terminal receipt after revocation; no new-project authority follows. The next turn obtains fresh context and authorization. Its embedded beforeSend handshake retries only EDITOR_CONTEXT_CHANGED, at most3 fresh context/ticket/activation attempts, with account epoch/thread/authentication/visibility rechecked after awaits. Other errors are not retried and native preconditions remain unchanged. Ordinary edits retain stale-project rejection.

## Source and documentation impact

Source owners: native `runtime/chat_project_workflow_v11_175.js` and append-only patch; Chat Brain native classification, typed Qwen planner, editor capability/receipt validation and focused tests. The engine source seal is207 ordered patches,68 assets,7,022,679 bytes, SHA-256 `0510e556b49cd94a3d1f89b264c194542476bc26c96169f3c6b8177301d482ff`. Final commits/package identities remain pending.

Documentation impact set: CONTRACT / PROTOCOL; AI / capability; UI / local persistence; CHECKPOINT / release; provenance / source packaging; FORGE / build; known limitations; authority / Roadmap at closure. Updated candidate documents: this receipt, `CHAT_FORGE_EMBEDDING.md`, `SWRLZ_CHAT_OVERVIEW.md` and `SWRLZ_PROGRAMMING_LALM_RUNTIME_ARCHITECTURE.md`. Engine current-release docs/source metadata and root Roadmap/version authorities must be synchronized with the actual final source, measurements and publication evidence before delivery.

Documentation gate: PENDING final source/evidence synchronization. Existing cloud pair/profile/project APIs, security policies, model weights/hardware and unrelated gameplay/LAN behavior are intentionally unchanged unless an independently recorded implementation change requires correction.

## Verification and evidence

Focused check scope: blank/model/starter creation; independent repeated clones and literal labels; unchanged starter source; previous-project recovery and new-save failure; fresh context after manual/native switches; one-operation and allowlist rejection; stale/standalone/closed-host denial; accepted transition followed by old-lease closure and fresh next-turn actions; actual native browser project handoff/local picker/autosave. No unrelated historical game-suite gate is introduced.

- Backend:71 Forge/planner/embed/Station tests PASS (`forge-project-python-all-r2.log`), plus13 adjacent profile tests PASS. Tests include bounded native shape/authority/receipt behavior and explicit-command resolver cases.
- Final Node embedded bridge checks: PASS, including one stale-context refresh followed by success, persistent EDITOR_CONTEXT_CHANGED bounded to3 attempts, closed-panel denial without retry and hidden-during-await rejection. Chat update-popup Chromium: PASS with267 previous updates retained. Backend candidate preparation --check: PASS at its current baseline; exact committed-source CI/preparation remains the publication gate.
- Actual pinned Qwen7B planner probes r1/r2: both TERMINAL_REPAIR_REQUIRED. The exact request supplied Blank Scene and quoted name "My Starter §§"; r1 asked for the name again, and r2 asked to confirm the fully specified request. Neither executed native operations or passed typed-plan acceptance. Immutable `forge-project-planner-7b-r1.json`/`r2.json` and logs retain model/source/driver hashes and outputs. Do not report raw model creation as accepted or imply weights/hardware improved.
- Native development Chromium: PASS recorded for blank/model creation, nonblank Dragon Den with170 actors, namespace/copy isolation, local metadata listing and rollback checks. Exact sealed final desktop-mode/native-browser result: PENDING root verification. Controlled browser evidence is distinct from owner hardware and real Google.
- Exact v11.175 source rebuild:207 patches,68 assets,7,022,679 HTML bytes, SHA-256 `0510e556b49cd94a3d1f89b264c194542476bc26c96169f3c6b8177301d482ff`. Source seal is distinct from native runtime/browser acceptance.
- Canonical source ZIP/checksum/archive reconstruction: PENDING.
- Exact Chat source CI/guarded deployment/runtime provenance: PENDING.
- Separate §E source/request-only deployment and hosted seal: PENDING.
- Real Google/deployed account storage and physical Android/Quest acceptance: DEVICE_TEST_PENDING.

## Provenance, limitations and next gate

Preserve the committed v11.174 mobile source and all v11.170–173 project tabs/dialog/header fixes. The successor appends patch/version lineage; no historical receipt is rewritten into new evidence. Final engine seal, source package/checksum, Chat source identity and actual workflow/runtime receipts must be added before claiming publication.

Local project copies belong to this browser origin and can be removed by browser-data clearing. Account/cloud/GitHub writes do not follow from native creation. General file authoring, unsupported scene operations, model JavaScript execution, external provider changes and deployment are outside this native tool surface. The two raw pinned7B planner failures and existing broad coding/editor competence remain REPAIR_REQUIRED until independently evaluated. Deterministic fully specified command routing is deliberately classified as orchestration, not a successful raw-model re-test.

Current disposition: implement and verify the bounded project transition, synchronize final docs/package, then use the existing authorized separate Chat and §E release lanes. Record actual hosted results and leave owner-device acceptance pending. Approval waiting: NOT APPLICABLE within the existing implementation/publication authorization; no new permission request is introduced by this checkpoint.

## Exact sealed source verification

Generated v11.175 package verifier PASS:207 ordered patches,68 independently hash-checked local assets,7,022,679 bytes/SHA2560510e556b49cd94a3d1f89b264c194542476bc26c96169f3c6b8177301d482ff. Actual native Chromium final receipts project-v175-native-final-r2.json and project-v175-adjacent-final.json BOTH PASS on this exact artifact: desktop1440×1000 primary, phone412×915 regression. Includes literalname, repeatedblank-modelcopies, actualnativefollowupmesh/sceneedits, previous-work+newprojectdurablesaves/localreload/autosave,170-actorDragonDen authoredcontent/levelmetadata, independentcode/documentdrafts evenwithlegacydraftseeded, savedcopyA reload, stale/mixeddenial, beforeloadandafterbuilder storagefailurerecovery, strictoldleasefinish→close, currentcontextaftermanualstarterselection, originalstartertruth and noJSerrors. AdjacentexistingUndo/Redo/account-switch/closed-host checks remain passing. Desktop screenshots inspected.

Failurelineage: earlier harness had a keyword-only Playwright argument mistake and nullable workspace field access, corrected in the runner; one strictcontext→presence handshake legitimately detected changednative state and denied with EDITOR_CONTEXT_CHANGED. Boundedthreeattempt freshcontext/ticket retry applies only that denial in the application frontend and testfixture; no rejected snapshot is reused, all account/thread/visibility guards remain. The final exact rerun passes; prior logs retained. No broad game suites or hosted-browser workflow was dispatched.

Source/contract/currentrelease docs and exact metadata agree: documentation gate PASS. Immutable source overlay/checksum follows committed identity, then existing authorized Chat exactCI/guarded release and separate final-request-only §E deployment. Real Google/private-store/owner-device acceptance remains pending. Raw model planning negatives remain explicitly carried forward; successful native orchestration is not weight training or generalcoding acceptance.
