# §wyrlz Clean Vercel SERVER Transplant

Server revision: **2.1.1**  
Chat revision: **1.0.0**  
Checkpoint: `INT-VERCEL-CHAT-001A`

This repository is the clean unified §wyrlz Vercel SERVER. It preserves the R39 transport/runtime workbench, mounts the R299-derived web chat bridge at `/api/chat`, and presents the Admin workbench with the Dragon Jester visual system.

Included:
- one unified FastAPI/Vercel entrypoint at `api/index.py`;
- `/api/health`, `/api/admin`, `/api/lalm`, and `/api/chat`;
- exact repaired R39 size/SHA verification and Forge chunked transport reconstruction;
- ZIP-wrapper support for `lalm§wyrlz.zip` containing the verified R39 `.gz`;
- hot Gate 5 execution with R39 load/verification inside the same invocation;
- binary-safe Admin file manager/viewer/editor with chunked large-file upload/download;
- responsive Dragon Jester Admin dashboard with the same underlying Admin actions and IDs;
- full structured Admin error receipts in the visible diagnostics console instead of collapsing failures to a generic message;
- browser-local chat threads and evidence export;
- V2 NDJSON streaming bridge with strict DELTA/RESET/terminal semantics;
- independent fail-closed `SWRLZ_WEB_CHAT_TOKEN`;
- proof-bound Android SERVER upstream headers injected only on the server side.

## Runtime boundary

All API behavior is rooted in the single `api/index.py` FastAPI application. `/api/chat` is mounted additively from `api/chat.py`, so Admin, health, LALM, Gate 5, and chat share the same deployed function definition. Vercel `/tmp` remains ephemeral and instance-local. Gate 5 therefore calls `ensure_r39()` in the same invocation before executing the live verifier.

The proven R39 path is:

`Forge chunks -> wrapper ZIP -> nested verified R39 gzip -> raw R39 -> SHA-256 -> Gate 5 readiness`

Authoritative raw R39 SHA-256:

`65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee`

## Admin workbench

Open `/api/admin`. Admin actions require `SWRLZ_ADMIN_TOKEN` through `x-swrlz-admin-token`. The workbench supports runtime state, R39 load/verify, Gate 5 execution, directory browsing, arbitrary binary upload, text editing, media/PDF/binary preview, SHA-256, rename/delete, folder creation, runtime logs, and response-safe chunked downloads.

Revision 2.1.1 changes presentation and observability, not the proven backend boundaries. The Admin workbench now uses the Dragon Jester visual language: neon blue/violet glass panels, responsive dashboard/navigation, explicit status tiles, dedicated Admin/LALM/Gate 5 sections, runtime console, and direct Chat navigation. Existing control IDs/actions are retained so the underlying file, runtime, upload/download, auth, LALM, and Gate 5 plumbing remains intact. Failed Admin API calls now preserve the complete structured JSON receipt in the visible console, including safe auth diagnostics such as `authConfigured`, `tokenReceived`, and `receivedLength` when provided by the server.

## Web chat

Open `/api/chat`. The browser chat token is deliberately separate from Admin:

- `SWRLZ_WEB_CHAT_TOKEN` — browser-to-Vercel chat token, minimum 16 characters;
- `SWRLZ_CHAT_UPSTREAM_URL` — reachable HTTPS SWRLZ SERVER gateway for live chat;
- `SWRLZ_CHAT_UPSTREAM_NODE_ID` — registered proof-bound CLIENT node ID;
- `SWRLZ_CHAT_UPSTREAM_DEVICE_PROOF` — server-side proof for that node;
- `SWRLZ_CHAT_UPSTREAM_BEARER` — optional outer gateway bearer;
- `SWRLZ_CHAT_UPSTREAM_IDLE_TIMEOUT_SECONDS` — optional 10–290 second upstream idle timeout.

The browser submits only `x-swrlz-chat-token`. Device proof and optional gateway bearer never enter HTML, local storage, thread exports, or browser-visible responses.

When no live upstream is configured, chat is intentionally status-only: it reports the current local R39 boundary and does **not** fabricate assistant DELTAs. Current Gate 5 proves container/integrity readiness, not one-token inference.

## Forge transport

The durable model source is the committed `lalm§wyrlz.transport.json` plus `.transport/...` chunks. `.transport/**` and preserved large archives stay excluded from Vercel function bundles. Missing chunks are streamed from the deployment Git source and verified before reconstruction.

Optional transport overrides:
- `SWRLZ_R39_TRANSPORT_MANIFEST`;
- `SWRLZ_REPO_ROOT`;
- `SWRLZ_R39_URL`;
- `SWRLZ_GITHUB_REPO_OWNER` / `SWRLZ_GITHUB_REPO_SLUG` / `SWRLZ_GITHUB_REF` for the current loader.

## Verification

The chat overlay carries a deterministic source verifier:

```bash
python scripts/verify_vercel_chat.py
```

It checks the 2.1.1 unified mount/theme markers, source compilation, Admin diagnostics preservation, chat page safety invariants, truthful local no-inference behavior, required integration files, and Vercel transport exclusions.

See:
- `SWRLZ_VERCEL_CHAT_README.md`;
- `docs/contracts/SWRLZ_VERCEL_CHAT_BRIDGE_V1.md`;
- `docs/checkpoints/INT-VERCEL-CHAT-001A_CHECKPOINT.md`;
- `SWRLZ_VERCEL_CHAT_CHANGELOG.md`.

## Revision history

2.0.5 unified the API runtime and colocated Gate 5 with R39 load/verify. 2.0.6 added response-safe chunked large-file downloads. 2.0.7 hardened Admin token normalization and diagnostics. 2.1.0 added the R299-derived Vercel chat bridge/UI without removing the proven Admin, R39 transport, or Gate 5 behavior. **2.1.1 restyles the existing Admin workbench into the responsive Dragon Jester dashboard and preserves structured failure diagnostics without changing R39/Gate 5/chat runtime contracts.**
