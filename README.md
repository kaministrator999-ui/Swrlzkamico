# §wyrlz Clean Vercel SERVER Transplant

Server revision: **2.1.3**  
Chat revision: **1.2.0**  
Checkpoint: `INT-VERCEL-CHAT-001A`

This repository is the clean unified §wyrlz Vercel SERVER. It preserves the R39 transport/runtime workbench, mounts the R299-derived web chat bridge at `/api/chat`, presents the Admin workbench with the Dragon Jester visual system, and adds a runtime-published web workspace under `/live/*`.

Included:
- one unified FastAPI/Vercel entrypoint at `api/index.py`;
- `/api/health`, `/api/admin`, `/api/lalm`, `/api/chat`, and `/live/*`;
- exact repaired R39 size/SHA verification and Forge chunked transport reconstruction;
- ZIP-wrapper support for `lalm§wyrlz.zip` containing the verified R39 `.gz`;
- hot Gate 5 execution with R39 load/verification inside the same invocation;
- binary-safe Admin file manager/viewer/editor with chunked large-file upload/download;
- responsive Dragon Jester Admin dashboard and engineering control plane;
- browser-local chat threads, response evidence, trace export, retry/fork, context inspection, stream camera, thread search, generation controls, and Send to Workbench;
- V2 NDJSON streaming bridge with strict DELTA/RESET/terminal semantics;
- independent fail-closed `SWRLZ_WEB_CHAT_TOKEN` with runtime override support;
- Admin-authenticated runtime Chat token set/change/generate/clear controls;
- proof-bound Android SERVER upstream headers injected only on the server side;
- runtime web publishing from `/tmp/swrlz-admin/web` to `/live/*` with safe path handling, MIME detection, index resolution, and no-store responses;
- Live Web manager, capability registry, health/release status, instance-change warnings, web snapshots/rollback, activity timeline, and promote manifests;
- `dev` branch deployment suppression so incremental work does not trigger Vercel production deployments.

## Runtime boundary

All API behavior is rooted in the single `api/index.py` FastAPI application. `/api/chat` is mounted additively from `api/chat.py`; `api/chat_extensions.py` augments presentation/diagnostics without changing the Truth Firewall. Admin, health, LALM, Gate 5, chat, and live web publishing therefore share the same deployed function definition. Vercel `/tmp` remains ephemeral and instance-local.

The proven R39 path is:

`Forge chunks -> wrapper ZIP -> nested verified R39 gzip -> raw R39 -> SHA-256 -> Gate 5 readiness`

Authoritative raw R39 SHA-256:

`65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee`

## Admin workbench

Open `/api/admin`. Admin actions require `SWRLZ_ADMIN_TOKEN` through `x-swrlz-admin-token`. The workbench supports runtime state, R39 load/verify, Gate 5 execution, directory browsing, arbitrary binary upload, text editing, SHA-256, rename/delete, folder creation, runtime logs, response-safe chunked downloads, Live Web publishing, runtime Chat-token management, snapshots, rollback, activity receipts, capability discovery, health state, release receipts, and promote manifests.

The Admin page never reads secret Chat-token values back. A generated token is returned once to the authenticated Admin caller so it can be copied into Chat. Runtime Chat-token precedence is runtime override first, then deployment environment fallback.

## Runtime web workspace

Admin uploads and edits under:

`/tmp/swrlz-admin/web`

are exposed through:

`/live/*`

Examples:

- `/tmp/swrlz-admin/web/chatv2/index.html` -> `/live/chatv2/`
- `/tmp/swrlz-admin/web/tools/tokenizer.html` -> `/live/tools/tokenizer.html`

Directory requests resolve `index.html`. Runtime web paths are confined to the dedicated web root, reject traversal/symlink escape, use detected MIME types, and are served with no-store headers. The runtime workspace is ephemeral and instance-local; durable accepted changes still belong in GitHub.

See `docs/contracts/SWRLZ_RUNTIME_WEB_WORKSPACE_V1.md` and `docs/contracts/SWRLZ_CONTROL_PLANES_V1.md`.

## Web chat

Open `/api/chat`. The browser chat token is deliberately separate from Admin:

- `SWRLZ_WEB_CHAT_TOKEN` — browser-to-Vercel chat token;
- `/tmp/swrlz-admin/runtime/web-chat-token.txt` — optional runtime override;
- `SWRLZ_CHAT_UPSTREAM_URL` — reachable HTTPS SWRLZ SERVER gateway;
- `SWRLZ_CHAT_UPSTREAM_NODE_ID` — registered proof-bound CLIENT node ID;
- `SWRLZ_CHAT_UPSTREAM_DEVICE_PROOF` — server-side proof for that node;
- `SWRLZ_CHAT_UPSTREAM_BEARER` — optional outer gateway bearer;
- `SWRLZ_CHAT_UPSTREAM_IDLE_TIMEOUT_SECONDS` — optional 10–290 second upstream idle timeout.

Chat 1.2.0 adds operational evidence drawers, retry/fork actions, thread filtering, bounded context inspection, optional bounded generation controls, a stream camera, trace export, runtime-mode/instance status, and an Admin-authenticated Send to Workbench action. These additions keep operational evidence outside assistant prose. Only committed `DELTA.text` is assistant content.

When no live upstream is configured, chat remains intentionally status-only and does **not** fabricate assistant DELTAs. Current Gate 5 proves container/integrity readiness, not one-token inference.

## Development / release flow

Incremental source work occurs on `dev`. `vercel.json` disables Vercel deployments for that branch. `main` remains the production/release branch. Finished, validated batches are promoted to `main` deliberately.

Runtime page iteration can bypass source deployment entirely after the runtime-web release is live:

`Admin upload/edit -> /tmp/swrlz-admin/web -> /live/* -> refresh`

## Forge transport

The durable model source is the committed `lalm§wyrlz.transport.json` plus `.transport/...` chunks. `.transport/**` and preserved large archives stay excluded from Vercel function bundles. Missing chunks are streamed from the deployment Git source and verified before reconstruction.

Optional transport overrides:
- `SWRLZ_R39_TRANSPORT_MANIFEST`;
- `SWRLZ_REPO_ROOT`;
- `SWRLZ_R39_URL`;
- `SWRLZ_GITHUB_REPO_OWNER` / `SWRLZ_GITHUB_REPO_SLUG` / `SWRLZ_GITHUB_REF`.

## Verification

Run:

```bash
python scripts/verify_vercel_chat.py
python scripts/verify_runtime_web.py
python scripts/verify_control_planes.py
```

See:
- `SWRLZ_VERCEL_CHAT_README.md`;
- `docs/contracts/SWRLZ_VERCEL_CHAT_BRIDGE_V1.md`;
- `docs/contracts/SWRLZ_RUNTIME_WEB_WORKSPACE_V1.md`;
- `docs/contracts/SWRLZ_CONTROL_PLANES_V1.md`;
- `docs/checkpoints/INT-VERCEL-CHAT-001A_CHECKPOINT.md`;
- `SWRLZ_VERCEL_CHAT_CHANGELOG.md`.

## Revision history

2.0.5 unified the API runtime and colocated Gate 5 with R39 load/verify. 2.0.6 added response-safe chunked large-file downloads. 2.0.7 hardened Admin token normalization and diagnostics. 2.1.0 added the R299-derived Vercel chat bridge/UI. 2.1.1 restyled the Admin workbench into the responsive Dragon Jester dashboard. 2.1.2 added the runtime-published `/live/*` web workspace, runtime chat-token override, and dev-branch deployment suppression. **2.1.3 turns Chat and Admin into paired control planes: Chat gains evidence/fork/retry/context/stream diagnostics, while Admin gains runtime Chat-token generation/change controls, Live Web management, capability/health/release state, instance warnings, snapshots/rollback, activity receipts, and promote manifests.**
