# §WYRL§ Engine v11.532 — project account-save receipts

Date: 2026-11-20. Scope: correct the shared full-project account save and preserve project identity when a save response is uncertain. The Little Glitch Dragon modeling mission remains blocked and has not started.

## Defect and correction

The composed source exposes a defect in the v11.529 full-project save path. `se371PreviousSaveCloud()` is the raw native v11.486 writer captured before the checked v11.371 facade. A durable write can succeed while that raw function returns `undefined`. The v11.529 caller requires `=== true`, so it reports `ACCOUNT_SAVE_UNCONFIRMED` after the write. Bypassing the checked facade also skips its account ownership/revision preflight and persisted account-link handling, risking a duplicate project on a later save.

This corrects the facade description in the historical [v11.529 account-save note](PROJECT_LIBRARY_ACCOUNT_FIX_V11_529.md). The historical note remains intact as release history; its description alone is not evidence that the composed save chain was correct.

v11.532 invokes `se488PreviousAccountSave()`, the existing checked native facade captured before the separate v11.488 model-asset dispatcher. It retains the native versioned project serializer, authenticated §Chat bridge, account ownership check, compare-and-set revision preparation and account-link persistence. Before a startup save refreshes its local snapshot, it reads the existing local project row so the persisted account ID and revision are restored rather than overwritten by an unlinked snapshot.

## Durable acknowledgement and uncertain outcomes

The full-project RPC dispatch now records a small pending receipt in the existing local project store before sending `cloud.save`. It contains the local project identity, target account project ID when known, expected revision and SHA-256 of the exact dispatched bytes. Failure to persist this receipt prevents the account write. A durable acknowledgement must return the expected project identity and exactly the next revision before the checked native route accepts it.

Every checked native project-save route shares acknowledgement cleanup at the existing account-link persistence boundary. The §Chat, My Projects and immersive full-project account save retain their common v11.529 entry point. The standalone model-asset save remains a separate operation.

An RPC error can follow a real server commit. A pending receipt therefore blocks another write until the outcome is verified:

- For a known account project ID, authenticated `cloud.list` and `cloud.load` must confirm that same ID, exactly `expectedRevision + 1`, the same local project identity and the exact dispatched bytes by SHA-256. Recovery accepts this already committed revision without sending another write.
- A new project's first request can lose its acknowledgement before the remote ID is known. Recovery requires explicitly opening the saved project through the authenticated account library to supply that ID. The engine does not search by project name or guess a matching project.
- A missing account project, changed revision, different bytes or unavailable verification leaves the outcome unknown and blocks blind replay. The local copy remains available. A read failure before dispatch permits retry because no account write was attempted.
- If the project/account changes after receipt preparation but before dispatch, cleanup removes only matching receipt metadata in an atomic transaction over the latest local row. It preserves newer local autosave content.

The UI distinguishes an unknown acknowledgement from a confirmed account save. Repeated clicking is not evidence of a successful save and must not create another project or revision while the original outcome is unknown.

## Source changes and verified local identity

The append-only source change consists of:

- [runtime/project_account_save_receipt_v11_532.js](../runtime/project_account_save_receipt_v11_532.js): receipt preparation, verification, recovery and atomic cleanup inside the existing authenticated project closure.
- [patches/v11_532_project_account_save_receipt.py](../patches/v11_532_project_account_save_receipt.py): targeted save-chain repair and v11.532 release identity.
- [tests/project_account_receipt_v11_532.cjs](../tests/project_account_receipt_v11_532.cjs): regression coverage using the actual native writer, wrappers, revision preparation and receipt code.

Canonical assembled HTML: **509 ordered patches; 10,996,103 bytes; SHA-256 `62ac2d3c524a6dd58d6ba4a826cadbb8455a0bd90d2fc2a03aa0c90643c6e382`**. Deploy marker: `V11_532_PROJECT_ACCOUNT_SAVE_RECEIPT`.

**BUILD PASS / STATIC VERIFICATION PASS:** the canonical full 509-patch source build, inline JavaScript parse, focused tests against the actual assembled save chain, four relevant prior persistence units and integrity checks for all 78 packaged assets pass locally.

The local static-delivery package receipt records:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| Packaged HTML | 682,477 | `2b4e077ff5c73daa39db5bb5ea113db0a519d2a12f9b8cf07d5df7fcca0aac07` |
| Compact module | 9,479,837 | `4d794e8a05314607acfe2a2ca6355e13a00e3d74a60369b4f8a0ff0e4725616c` |
| Source module | 10,313,657 | `a8a954815acb83d1b7b9acd71996d917fe8765ed5546a0518ae80823189b7f3e` |

Packaging uses esbuild 0.25.12 with whitespace-only compaction. The local generated receipt is `/dev/shm/dragon-engine532/SOURCE.json`. These local build/package results are distinct from repository publication and the served release. Delivery and live account acceptance remain pending; the release owner will record source/deployment commits and exact hosted receipt verification here when confirmed.

## Verification evidence

**SOURCE IMPLEMENTED / STATIC VERIFICATION PASS:** focused composition tests pass against the actual assembled save chain. Only DOM, IndexedDB transport and authenticated RPC are harness boundaries; the native save function, wrappers, revision preparation and receipt verification are exercised from source. The historical chain is retained as a negative control: it performs one durable backend write and still returns `ACCOUNT_SAVE_UNCONFIRMED`.

The corrected-chain assertions cover:

- A confirmed first project save followed by a second save to the same remote ID with an advancing revision and no model-asset dispatch.
- The other checked native save route, persisted link cleanup and startup restoration when both in-memory link maps begin empty.
- Native rolling revision preparation, account ownership preflight and stale-revision rejection before a write.
- Lost acknowledgements for existing and new projects, persisted uncertainty across restart, explicit authenticated account-open recovery and zero write replay during recovery.
- Exact-byte mismatch rejection, local receipt-store failure before dispatch, account/project changes before dispatch, newer autosave preservation and disconnected behavior.
- Continued reachability of the separate model-asset save dispatcher.

These are source/harness results. They made no live account writes and do not establish a successful authenticated transfer, deployment, browser save/reopen or owner acceptance.

## Runtime and mission status

**RUNTIME NOT TESTED / FOLLOW-UP REQUIRED:** an actual verified-account save/reopen round trip is blocked. The workspace proxy returns HTTP 403 for `kamiloki-swrlz-forge-moba.static.hf.space`; access to the live engine is unresolved. The available browser profile has not yielded a verified §Chat account; the account-check UI reports unverified. The original browser profile was preserved while a clone was inspected. A connected badge alone is not a verified account-save receipt.

The six-view dragon reference is visible inline, but the original PNG/JPEG file is not exposed to the workspace despite being resent. There is no claim of an imported reference, a newly created project, a §C-constructed dragon, model screenshots or any new project/model/account write for this mission.

The requested ownership remains: **§C is the sole modeler inside live §E; Codex supervises the mission and repairs general capability gaps.** Once access, reference-file availability and account verification are resolved, §C must create the model through the live engine, save frequently at meaningful checkpoints, verify the account project ID/revision and reopen it before progress is described as durably saved.

The separate §Chat native-continuity repair is pending in its own checkpoint. This engine save repair does not establish that repair's completion, verified account access or dragon modeling progress.

## Acceptance still required

1. Publish the verified source and follow the existing separate `DEPLOY_REQUEST.json` delivery workflow; confirm the served version/hash against the local receipt before claiming deployment.
2. In a verified §Chat account, save a deliberately named test project, record its account project ID and revision, make a small native edit, save again and confirm one project with an advancing revision.
3. Reopen that same account project after a fresh engine session and verify native project content/history and its persisted account link. Save again to confirm the same remote identity survives startup.
4. Resume the Little Glitch Dragon mission only when the live engine, original six-view image file and verified account are available. Keep §C's modeling and verified account-save checkpoints inspectable.

The change preserves the existing engine architecture, providers, authentication transport, model-asset API, project history, geometry, UVs, rigging and saved projects. It does not replace the engine or implement dragon-specific geometry.
