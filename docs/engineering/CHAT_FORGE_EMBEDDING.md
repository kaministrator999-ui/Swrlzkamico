# Chat in the §E workspace

Status: published 2026-10-29 through the existing Chat and §E lanes; source/runtime evidence is recorded in the checkpoint. Real Google/deployed-store/owner-device acceptance remains pending.

The user explicitly requests integration of the existing Chat and §E products.
Their source/deployment lanes remain separate. Chat owns Google identity,
account history, settings, model inference and encrypted account storage. §E
owns its live editor, native project format, transactions and local/offline work.
The embedded surface composes the existing complete Chat UI; it is not another
conversation implementation or another account database.

## Baselines and ownership

- Accepted Chat source: `f925e2012ed7ece820e3272700bc6619846c2085`, observed RUNNING
  at HF revision `48515f7fc6e8cb7b4450725320e8fed64fb886e6`.
- §E source: main `225650ceee808706dd5a73b0c66978e73b00775c`, v11.167,
  199 ordered patches and68 assets. Its null final seals are historical; the
  changed successor must carry actual rebuilt bytes/hash and matching identity.
- Integration branch starts at accepted Chat, imports only that exact canonical
  §E project/deployment owner, and preserves the unaccepted starter experiment
  separately at `99a7aa401a27719bc25bd8129aed3a15eb2fffd8`.
- Chat publishes through its existing main request/guarded workflow. §E publishes
  through a separate final `DEPLOY_REQUEST.json`-only main commit and its own
  package/upload workflow. No new hosting service or production trigger.

## Required behavior

1. A responsive, keyboard-accessible §E aside opens the full canonical Chat in
   an isolated Chat-origin iframe. Closing it preserves Chat state but revokes
   live editor authority. Local §E work remains available without sign-in.
2. A §E Google sign-in button uses the existing Chat-origin sign-in, then loads
   the same verified Google owner's Chat history and explicitly saved settings.
   No guessed email/user-ID migration or duplicate history store.
3. User-initiated account Save/Load preserves the exact native project snapshot,
   including levels, workspaces, files, editor metadata and geometry. Cloud
   failures preserve local work and previous stored revisions.
4. AI editor operations require a currently visible, connected §E host, a live
   server lease, the correct account/session/thread/project and fresh native
   preconditions. Standalone Chat, URL flags and historical messages grant none.
5. Only typed, allowlisted native operations execute. No model JavaScript,
   arbitrary method dispatch, eval, new provider permission or implicit deploy.
   Results are described only after actual host receipts.

## Browser and account transport

Chat origin is `https://kamiloki-swyrlz.hf.space`. Allowed §E parent origins are
exactly `https://kamiloki-swrlz-forge-moba.static.hf.space` and
`https://kamiloki-swrlz-forge-moba.hf.space`. Tests may inject explicit local
origins in controlled fixtures; query parameters cannot change the allowlist.

The protocol identifier is `swrlz-forge-chat-v1`. Every initial window message
checks exact origin AND source window AND current host/channel nonce. After
handshake use a private transferred MessagePort. Messages have a bounded type,
request ID, host ID and channel ID. A parent never receives account bearer tokens,
Google ID tokens, Chat history or settings merely to host the iframe.

The iframe generates an in-memory PKCE verifier and sends its S256 challenge to
the Chat backend with the allowed parent/host/channel binding. The backend
creates a short-lived pairing record and returns a Chat-owned login URL carrying
only the random pair ID. The parent opens that URL on an explicit sign-in click.
The popup reuses the existing Google client/origin and server-verified account
cookie. It must verify its expected §E opener handshake before offering an
explicit connection action. Same-origin POST approval binds the pair to the
verified Google principal and parent login; client-supplied owners are ignored.

The original iframe exchanges its verifier against the approved pair. Redemption
is atomically single-use, expiry-checked and fails without changing the record
on an incorrect verifier. The returned short-lived embed credential remains
only in Chat-origin memory. API authentication resolves the same `google:<sub>`
and checks parent-login revocation. Cookies are not weakened globally. A scoped
partitioned-cookie resume may be added only with equivalent owner/audience tests;
RAM authentication is the fallback when third-party cookies are blocked.

All native Chat transports, streaming, account/profile APIs and downloads must
use the credential only for exact Chat-origin protected API paths. Never attach
it to Google, external GitHub, assets or arbitrary URLs. Native Export navigation
needs an authenticated fetch/blob download adapter. Logout clears scoped state
and revokes active tools; account switches cannot hydrate another owner's data.

Pair API owner: `hf_space/forge_embed.py`, installed by Station:

- `POST /api/forge/embed/pair`: parentOrigin, hostId, channelId, challenge.
- `GET /api/forge/embed/pair/{pairId}`: public binding/readiness only.
- `POST /api/forge/embed/pair/approve`: legacy verified Google cookie,
  same-origin guard and the popup/opener binding; never a claimed user ID.
- `POST /api/forge/embed/pair/exchange`: pairId, verifier, hostId, channelId;
  returns account session credential/user only after atomic redemption.
- `POST /api/forge/embed/logout`: revoke the embed session and its capabilities.

`resolve_account(request)` returns a verified `(session_id, user)` only for its
own credential class; an invalid supplied credential fails closed, without
silently falling back to a different cookie owner. Station retains the existing
legacy account resolver for Google login/pair approval. `require_embed(request)`
also supplies the immutable parent/host/channel binding for editor authorization.

## Shared settings

`hf_space/account_profile_store.py` uses the existing account encryption key and
Redis transport under `swrlz:google:profile:v1:<SHA-256 of verified owner>`.
The encrypted record includes the exact verified `google:<subject>` owner and
schema; decrypt/read rejects mismatched owners, invalid schemas or malformed
settings without substituting defaults. It does not register the legacy
random-user-ID account router or guess a migration from emails/display names.

The module exports `load_profile(owner)`, `save_profile(owner, body)` and
`install(app, authenticate, write_guard)`. Authentication callbacks return the
existing verified `(session_id, user)` tuple; the module uses `user.id`, never an
owner supplied in the body. Synchronous and asynchronous callbacks are supported.
The mutation guard must return `None`/`True` or raise; a `False` result denies the
write. Blocking storage calls run outside the async request loop.

- `GET /api/account/profile` returns
  `{ok:true, profile, durable:true, saved:profile.version>0}`.
- `PUT /api/account/profile` requires `application/json` and the current integer
  `version`, plus any of `displayName`, `preferences`, `modelPreferences`,
  `uiPreferences` and `companionProfile`. It returns
  `{ok:true, profile, durable:true, saved:true}` only after confirmed atomic CAS.
- Returned profile fields are `display_name`, `preferences`,
  `model_preferences`, `ui_preferences`, `companion_profile`, `version` and
  `updated_at`. The first five request fields map to these snake_case fields;
  nested settings retain their existing frontend names.

Missing settings return a fresh, complete version0/default profile with
`updated_at:0`, without creating a record. `durable:true` means the backend is
available; `saved:false` means the user has not saved a profile. Opening or
previewing settings does not save them. Explicit Save at version0 creates
version1; later saves increment the version. Omitted nested fields retain their
current values, while explicit empty strings/null clear fields where supported.
An atomic comparison checks both the expected version and exact prior ciphertext;
a stale or concurrently replaced record returns409 and preserves the winner.
Unknown storage acknowledgements return503 without claiming a confirmed save.

Known nested settings include general Enter-to-send/personality, user
pronouns/role/communication/output style, proposal policies, default model/effort/
response length, UI density/glass/motion/font scale/accessibility and companion
identity/style fields. Unknown keys, invalid enums/types, duplicate JSON keys,
nonfinite numbers and out-of-bound text are rejected. Request/profile JSON is
bounded to32,768 UTF-8 bytes and the encrypted envelope to65,536 bytes; input is
never silently truncated. Versions are safe JSON integers through2^53−1.
Reads and writes return `Cache-Control: private, no-store`.

Station's account/me and Google-login responses include the actual profile and
backend availability. Saved model/user/companion preferences are the shared
settings source where those fields apply. Stored preferences never grant live
editor, provider-write or deployment authority.

## Cloud projects

`hf_space/forge_project_store.py` stores native projects independently of Chat
snapshots and source-code archives. The iframe acts as the authenticated cloud
broker: an explicit §E Save transfers native UTF-8 bytes, optionally compresses
them with gzip and uploads bounded chunks. It does not send full snapshots to
inference. Load requires explicit user selection and returns the exact native
bytes for the existing `loadScene` path, preserving levels, workspaces, files,
editor metadata and geometry. Local/download paths remain available on failure.

The API owner exports `install(app, authenticate, write_guard)` with the same
verified-account and mutation callback contracts as shared settings. Every key
is selected from the authenticated Google owner, hashed under
`swrlz:google:forge:v1:{<owner hash>}`; the hash tag keeps catalog and part keys
in the same Redis Cluster slot for atomic publication. Encrypted records bind the owner,
schema, upload nonce and part identity. Project/upload IDs from another owner's
namespace return404 and cannot select another owner's keys.

Exact endpoints and bodies:

- `GET /api/forge/projects` returns `{projects, limits}`. Each metadata entry is
  `{id,name,revision,rawBytes,rawSha256,encodedBytes,encodedSha256,updatedAt}`;
  listing contains no scene bodies, native files or chunk credentials.
- `POST /api/forge/projects/uploads`, with JSON
  `{name,projectId?,expectedRevision,codec,rawBytes,rawSha256,encodedBytes,encodedSha256}`,
  returns `{uploadId,projectId,partBytes,parts,expiresAt}`. IDs are32 lowercase
  hexadecimal characters; digests are64 lowercase hexadecimal characters.
  `codec` is `identity` or `gzip`. A new project omits `projectId` and uses
  `expectedRevision:0`; replacing a stored project supplies its ID/current
  revision. Names contain1–160 visible characters. Identity sizes/digests must
  agree. Unsupported fields are rejected.
- `PUT /api/forge/projects/uploads/{uploadId}/parts/{index}` requires raw
  `application/octet-stream` bytes at the zero-based index and exact planned
  part size. It returns `{index,bytes,sha256,confirmed:true}`. Repeating the same
  confirmed bytes is idempotent; different bytes at that index return409.
- `POST /api/forge/projects/uploads/{uploadId}/commit` accepts `{}` (or an empty
  body), not a revised upload plan. It returns
  `{project:<metadata>,durable:true,cleanupPending:<boolean>}` after publication.
  A retry after an unknown transport outcome can return `alreadyCommitted:true`
  for the still-current revision without publishing another revision.
- `DELETE /api/forge/projects/uploads/{uploadId}` cancels only that staged upload
  and reclaims its indexed parts; it never deletes a current project.
- `GET /api/forge/projects/{projectId}` streams the original native JSON bytes,
  with `X-SWRLZ-Project-Revision`, `X-SWRLZ-Project-SHA256`, an attachment filename
  and private/no-store caching. It validates every stored chunk and raw digest.
- `DELETE /api/forge/projects/{projectId}?expectedRevision=<current integer>`
  explicitly removes that revision and returns
  `{ok:true,projectId,deletedRevision,cleanupPending}`. Stale revisions return409.

Bounds are96MiB raw,64MiB encoded gzip (identity may use96MiB),512KiB per part,
64 projects,4 pending uploads and256MiB total reserved encoded project/upload/
cleanup bytes per owner. Uploads expire after3,600 seconds; commit receipts are
bounded to16 entries with86,400-second expiry. Catalog plaintext is at most256KiB
and cleanup journals are bounded to16 entries. Exceeding a bound reports an error
without truncating native data or advancing the saved project revision.

The encrypted catalog is the single atomic CAS publication point. A staged
upload indexes its plan before parts can be written; each part and its catalog
receipt are written in the same atomic transaction. Commit verifies all parts,
encoded/raw lengths and SHA-256 hashes, bounded single-stream gzip decompression,
finite/duplicate-free JSON and the native `engine/version/project/editor/scene`
envelope including `scene.actors`. It publishes an immutable upload nonce and
incremented project revision only if the expected prior catalog/project remains
current. Staging changes catalog bookkeeping, but failed/partial commits do not
advance the published project revision or replace its previous manifest.

Old revisions and cancelled/expired uploads remain indexed in cleanup journals
until every deletion and journal CAS is confirmed. A confirmed commit may return
`cleanupPending:true`: the new revision is durable while reclamation remains
journaled for retry. An unconfirmed commit returns an error, preserves recovery
metadata and never claims success. These rules prevent silent old-pointer loss
and unindexed persistent chunks after known failure paths.

Controlled verification:13 profile tests and15 project-store tests passed,
including concurrent CAS writers, two-owner isolation, unknown transport outcomes,
cleanup failure recovery and exact preservation of an approximately70MiB native
snapshot. These tests use an atomic in-memory storage fixture; real Google,
deployed Redis and owner device acceptance remain separate evidence gates.

## Active-editor capability

Account access and live editor access are distinct. The authenticated iframe
requests a one-use presence ticket bound to its account session and current
thread/project/host/channel. Only a POST from the exact §E browser Origin may
activate it. This creates a separate short-lived host capability which cannot
read Chat data. Host-only endpoints have narrow Origin CORS, no wildcard or
credentialed general account CORS. Missing/mismatched Origin fails closed.

- `POST /api/forge/embed/presence`: iframe account auth; binding/context ticket.
- `POST /api/forge/embed/host/activate`: §E Origin + one-use presence ticket.
- `POST /api/forge/embed/host/heartbeat`: host capability, current bounded context.
- `POST /api/forge/embed/host/close`: revoke host/lease/pending batches.
- `POST /api/forge/embed/host/batches/{id}/take`: atomically take exact canonical
  operations once, requiring active host capability and execution nonce.
- `POST /api/forge/embed/host/batches/{id}/finish`: submit actual native receipts.

Heartbeat runs only while the panel and document are visible. Closure, navigation,
project/account/thread change and expiry revoke tool authority. Server deadlines
bound lost/disconnected clients. Neither browser visibility nor client receipts
are cryptographic device attestation; the enforceable claim is an authenticated,
Origin-bound active-host session plus native client guards, not physical presence.

Station validates capability against its actual authenticated request and new
generation identity. It passes a server-produced trusted context to Brain/router;
no client `inForge`, `trusted`, saved history or model plan can create that context.
Full projects stay in §E/cloud storage; inference receives a bounded read-only
scene/selection/workspace summary with actual object IDs and preconditions.

Native operation names/types are fixed against real §E native handlers. Model
Atelier supports `mesh.add/set/select/duplicate/remove`; the scene supports
`sceneactor.add/transform/select/rename`; both support `editor.undo/redo` through
native history. Adds use sphere/box/cone/cylinder or approved wall/rock/bush/
crystal/pedestal prefabs. Batches contain at most16 operations; names max100,
position/rotation absolute100, scale greater than0.005 through20, colors exactly
#RRGGBB and material matte/silk/gloss/metal/emissive. All referenced IDs must be in
the original bounded snapshot; no new-target reference in the same batch.
Undo/Redo runs in its own batch. Workspace file editing/grouping, arbitrary
JavaScript/methods, general HTTP, provider writes, cloud deletion and deployment
are outside this native tool surface. The host repeats shape/target/epoch/mode
checks and preserves native history. UI names use literal text nodes.

The model proposes typed operations; server validates intent, shape, scope and
limits and registers a batch. Chat sends only the public batch ID and binding to the host. The host alone receives a private one-use receipt nonce from its authenticated take call.
The host takes server-canonical operations, executes the native allowlist, then
posts receipts. Final response is grounded in those receipts; missing/expired/
partial/rejected operations cannot become a successful completion.

## Native project creation and active-project context — v11.175 candidate

Status: implementation candidate with focused backend/development-browser evidence and a measured engine source seal. Exact sealed-browser verification, final-source CI, publication and real-model/device acceptance remain separately classified in the [project workflow checkpoint](entries/2026-10-30_CHAT_FORGE_PROJECT_WORKFLOW.md). The existing published integration above is retained; this section does not claim the successor is live.

The current human request may ask Chat to create a named native §E project from blank or from a reusable starter. The sole creation operation is `{op:"project.create",starterId,name}`. It must occupy its own one-operation batch. `name` is literal text of1–100 characters under the existing native name constraints; `starterId` must identify an entry in the current live `context.starters` catalog. Unknown fields, unsupported starter IDs, a missing catalog or mixed create/edit batches are rejected. A host without this advertised capability cannot be silently treated as supporting it; adding a mesh is not a substitute for creating a project.

A bounded explicit-command resolver handles only a fully specified current human creation request with one exact advertised starter ID/name and one quoted literal `named`/`called` project name. It produces the same validated `project.create` batch and requires the same native receipts; it does not bypass authorization. It rejects extra content clauses and compound create-plus-edit requests rather than silently dropping them, and never chooses a fuzzy/default starter or invents a name. Other requests retain the semantic typed planner and clarification path. Actual pinned Qwen7B planner probes r1/r2 both redundantly clarified an already supplied name and remain REPAIR_REQUIRED; this reliable command route is an orchestration improvement, not model-weight or general planning acceptance.

The bounded live context adds `project.template`, `project.sourceStarterId`, `dirty`, optional `activeLevel:{id,name}` and `starters:[{id,name,kind,workspace}]`. The catalog contains at most16 unique known entries; the candidate engine advertises11 native blank/starter choices. Existing current project identity, workspace, selection, actual object counts, target summaries and epoch remain authoritative. Metadata is untrusted data, never an instruction or authorization. Full native project files, source snapshots and account histories do not enter inference context. A fresh context is obtained before each authorized native request, so a manual project switch or the newly created project replaces the preceding project reference. The embedded `beforeSend` handshake retries only `EDITOR_CONTEXT_CHANGED`, with at most3 fresh context/ticket/activation attempts. It rechecks account epoch, thread, authentication and visibility after awaits; other errors are not retried and native preconditions are not relaxed.

### Independent copies and local preservation

Native creation calls the existing blank/starter loaders and stamps the editable copy with a new persistent instance ID, the accepted literal `projectName` and `sourceStarterId`. The canonical starter identity is retained where specialized native tools require it; the project instance ID identifies the user's independent copy. Level bundles receive a project-specific root. Starter builders/defaults remain reusable and are not overwritten by work on the copy. Editable workspace draft keys and export ownership prefer the persistent instance ID; clone loading suppresses legacy canonical draft hydration, preventing another copy or an older starter draft from contaminating the new copy.

Before switching, a complete native recovery snapshot of the preceding workspace must commit to this browser's IndexedDB project store. Storage unavailability, quota or transaction failure stops creation before the native starter builder. A new-project snapshot must then commit before success is reported. A loader or new-save failure attempts to reopen the preceding snapshot and restore its prior dirty/history/Undo state. If reopening itself fails, the operation reports the saved recovery-copy condition instead of claiming the active workspace was restored.

**My Projects → On this device** exposes local saved copies independently of the account project library. IndexedDB schema2 keeps complete project bodies and metadata in separate stores; listing reads at most1,000 metadata entries without loading all saved native bodies. A selected load reads that project body. Native edits to identified projects schedule local autosave after350ms. Autosave failure is visible and retains native file Save/Load as a recovery path. Local storage is scoped to this browser origin; clearing browser data can remove these copies. It is not an account backup or a cross-device sync guarantee. Explicit **Save to account** remains the existing separately authenticated cloud operation with its own durable revision receipt.

### One transition, then fresh authority

A successful native receipt contains `{op:"project.create",ok:true,changed:true,projectId,name,starterId,previousProjectId,localSaved:true}`. The returned project ID is the newly opened instance, not the starter identity. The server permits changed-project completion only for this sole successful operation and checks the resulting context's project ID, literal name and source starter. Ordinary edit batches still reject a project change. Missing, failed, stale or inconsistent receipts cannot become a creation success.

After the transition's finish is accepted, the host closes the old lease. Reading that already sealed terminal receipt is limited to its original generation and still-live same-owner session; it does not reactivate the old host or authorize edits in the new project. A subsequent user turn obtains fresh current context and a new project-bound lease. No create-and-edit chain can target guessed new objects inside the creation batch.

Standalone Chat still has no native editor authority. Closing/hiding the host, account/thread changes, expiry and all existing exact-Origin/private-port/server-bound checks retain their enforcement. Creating/opening and saving a copy on this device do not save it to Google, the cloud, GitHub or production; Chat must use the actual receipt wording and keep those actions separate.

## Evidence, privacy and delivery

Diagnostics report correlation IDs, operation names/counts, reason codes,
revisions and hashes; never tokens, Google credentials, private history/settings
or full projects. Cameras OFF/ON must have equal functional outcomes. Explicit
profile/cloud writes and local editor changes retain their own permissions.

Required tests include two-owner isolation/CAS, pair replay/wrong audience/
verifier/expiry, cookie-blocked transport, profile bootstrap/roundtrip, chunk
failure/large native snapshot preservation, strict window/port checks, revoked/
stale/standalone tool denial, actual native operation receipts/Undo, and desktop/
mobile sidebar behavior. Mocked Google tokens are controlled tests, not real
Google sign-in acceptance. §E production workflow remains package/upload only;
no unrelated game suites or automatic hosted browser marathons.

Current release/source evidence is authoritative in [the checkpoint](entries/2026-10-29_CHAT_FORGE_INTEGRATION.md#update-finished--publication-and-handoff-receipt). The host clears cloud project IDs/revisions and its visible cloud list on account-change revoke; ordinary thread changes preserve the current account reference.
