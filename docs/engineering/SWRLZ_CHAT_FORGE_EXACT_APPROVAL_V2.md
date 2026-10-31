# §C ↔ §E Design Studio v2 — Exact Native Plan Approval

**Status:** source candidate; production publication and owner-device acceptance must be separately verified.
**Module ownership:** §C owns proposal authorization, Chat response and consent; §E alone owns native editor operations/undo and host receipts.

## Why this release exists

v1's "Approve" button sent a fresh natural-language model request. The re-generated plan might differ from the illustrated steps. v2 makes the reviewed list the exact native operation list that the host will receive **only if the original editor snapshot remains valid**. No model gets to re-plan after approval.

This is **not** a claim that the schematic depicts an exact rendered §E mesh, or that the available 16-operation primitive toolset can sculpt, UV, rig or animate. v2 freezes operation data and authorization; the underlying editor and capabilities are unchanged.

## Security protocol / trust boundaries

1. Current human preview/design request enters the existing authenticated Station dispatcher.
2. One constrained model proposes a typed JSON plan. Existing intent guard, project/actor identity check, operation allowlist, numeric bounds and action-specific consent filters validate it.
3. Stage under authenticated live §E owner/session/host/project/thread/contextHash. The encrypted Redis record stores the **exact canonical list**, 64-hex SHA-256 plan digest, random 32-hex public proposal ID and 15-minute-or-shorter expiry. **No batch and no editor mutation** occurs.
4. Chat receives only a bounded presentation widget: schematic, full step fields, plan digest, proposal ID, expiry and a short exact approval command. No host tokens, native receipt nonces, account secrets or privileged operation data flow through the public approval payload.
5. Human clicks "Approve exact plan in §E". Chat submits a NEW user turn containing only \`Approve §e design preview <32 hex>\`. A historical message, widget display, model-generated narrative or client flag is never consent.
6. The Station router recognizes only the full approval phrase when a verified live §E generation is present.
7. The backend loads the server-held encrypted record and checks the **same session, owner, thread, project, parent origin, host identity/channel and exact context hash**. The **original operations** run through native validation again.
8. The atomic Redis transaction updates the proposal from \`offered\` to \`claimed\` AND creates exactly one pending native batch under the current generation. A losing race, changed scene, expired record or replay fails closed; no batch is created in the losing transaction.
9. The active §E host takes the standard native batch using its private origin/host credential. The native host sees exactly the stored operations and existing project/context preconditions. It executes and sends verified receipts through the existing single-use receipt nonce.
10. Chat never claims success before the matching native result is received. Full, partial, rejected, stale and unconfirmed outcomes remain distinct. Once claimed, even a failure is not silently replayable; request a new preview.

## Exactness guarantee and limits

**Guaranteed by server design:** The ordered canonical native operation bytes that §E receives match the validated plan held under the same proposal digest. The approval step does not invoke inference. A clicked proposal can register at most one native batch.

**Not guaranteed by this design:** Pixel-accurate rendering of the 3D blockout, full mesh topology, output correctness beyond the native host's receipt checks, all scene elements absent from the bounded authenticated summary, Undo grouping beyond native undo, atomic multi-operation rollback, or owner acceptance on Android/Meta Quest.

The context digest can only bind what the native host actually sends. Future engine work should add authoritative full-scene revision counters, asset/topology checks and ghost-render diffs so that changes outside the current bounded metadata cannot go unnoticed.

## Public Chat response components

| Component | Data authority | Interaction |
|---|---|---|
| Header/context strip | Current validated host snapshot | Read |
| Schematic | Plan positions/sizes | Isometric, Top and Front views |
| Step scrub | Ordered plan | Inspect first N planned steps |
| Detailed step list | Native typed operations | Expand and review exact fields |
| Plan fingerprint | SHA-256 of canonical operation list | Read-only 12-character display; full digest stays in widget |
| Approval window | Server expiry | Display local end time; reject expired proposals |
| Revision | User text | Draft a new preview, never mutate |
| Approval | Explicit user click | Submit short proposal ID; no client operation payload |
| Status and receipt | Station/host result | Show exact plan receipt or clear stale/expired failure |

The renderer uses \`textContent\` for model-supplied labels and attributes. SVG coordinates are finite/bounded. Browser code cannot invent new operations or native host capabilities. Old v1 cards remain inspectable; they must be re-previewed for v2 exact approval.

## Threat/negative test matrix

- Forged or malformed proposal ID; quoted/reported approval; arbitrary language; unauthenticated Chat → refuse native routing/claim.
- Client-supplied \`operations\` JSON / plan digest does not grant authority.
- Other account or session, host identity/channel, thread, project, or origin → refuse.
- Heartbeat changed snapshot/context hash or closed/hidden §E → refuse; do not silently re-plan.
- Expired proposal or already claimed proposal → 409; no further native batches.
- Concurrent approvals → atomic single winner, seven losers.
- Model/plan error before staging → never emit a native batch.
- Cancelled generation / no active host → existing native gate refuses.
- Receipt absent, inconsistent, partial or unsuccessful → no false complete claim.
- Large 16-step plan → same 16 server-held operations; client approval is always bounded, cannot truncate commands.
- Desktop, mobile, Android desktop-site → no overlay overflow, readable controls, revision and approval behavior preserved.

## Preservation / deployment

The branch is based on the exact merged v1 Chat integration source. No §E engine, Google login provider, account history, LALM weights/defaults, project storage or unrelated gameplay file is modified. Existing sensitive credential/no-secret and signed origin boundaries remain in effect. The guarded Hugging Face existing-Space release must capture prior revision, publish only the validated §C source, and record new Space revision/rollback. Source validation, hosted release, and owner-device acceptance must be tracked as three separate events.

## Deferred work

- Native §E ghost mesh overlay and pixel/geometry comparison.
- Hierarchical model builder, mirrored duplication, instancing, procedural assemblies, booleans and sculpt brushes with their own typed native schema.
- Full-scene monotonic revision and topology/asset fingerprint.
- Transactional undo groups, staged multi-batch projects and graceful partial rollback.
- Material/lighting variants, topology/rigging/animation preview and reusable asset recipes.
- Independent owner Android/Quest touch, keyboard, VR and high-density layout acceptance.

**Source handoff:** \`hf_space/forge_embed.py\`, \`hf_space/forge_chat_actions.py\`, \`hf_space/forge_design_preview_v1.py\`, \`hf_space/model_router.py\`, \`chat/§wyrlz/index.html\`, \`hf_space/test_forge_embed.py\`, \`hf_space/test_forge_chat_actions.py\`, \`tests/test_forge_chat_browser.cjs\`, plus this document.
