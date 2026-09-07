# SWRLZ Vercel Chat Changelog

## SERVER 2.2.0 / Chat 1.3.26 / LALM UI 1.0.0 — 2026-09-07

Changed:
- split the system into independent Server, LALM, and Chat control planes;
- added `/server/` and `/lalm/` dedicated pages;
- added `/api/server/status`, `/api/lalm/status`, `/api/control/route`, `/route`, and explicit `POST /api/lalm/verify`;
- added scoped hot mutation at `POST /api/control/hot/sync?scope=lalm|server|all`;
- `scope=lalm` updates only `web/lalm.html` and `runtime_hot/r39_engine.py` and explicitly reports `chatTouched: false`;
- LALM-scoped verification/hot sync may use the bounded signed browser Chat session while Server/all mutation remains Admin-controlled;
- Chat stays at 1.3.26 because this release changes infrastructure/model ownership rather than Chat protocol or Chat UX;
- the compiled direct-quantized R39 backend remains preferred and the Python/NumPy reference executor remains the correctness/fallback oracle.

Architecture boundary:
- Server owns routing, deployment/base version, instance/capability receipts, and hot control;
- LALM owns R39 engine/model/readiness/native-backend diagnostics and runtime tuning;
- Chat owns conversation UX, request/stream/reconnect behavior, and the Truth Firewall;
- future ordinary R39 tuning must not advance the Chat version unless Chat behavior itself changes.

Deployment boundary:
- 2.2.0 requires one base deployment to establish the new Python routes/native build boundary;
- after that deployment, ordinary LALM engine/page iteration can hot-sync independently of Chat.

## SERVER 2.1.16 / Chat 1.3.13 — 2026-09-07

Changed:
- local R39 reference matvec dequantization batches increased from a 4 MiB target to a bounded 16 MiB target, reducing repeated decode/allocation/BLAS-call overhead while avoiding whole-model dequantization;
- small decoded matrices and vectors are cached per model instance so normalization weights and other small tensors are not repeatedly dequantized on every token;
- the stock Vercel bridge response directive is compacted only on the local R39 prompt path before tokenization, reducing prefill tokens while preserving the Truth Firewall in the stream/event layer;
- the hot R39 engine revision now identifies the `2.1.16-prefill-hotpath` runtime;
- production deployment is recorded as `https://swrlzkamico-o3nu.vercel.app`.

Why:
- the live trace reached `LOCAL_R39` and began a 55-token prefill but only reached `16/55` before the browser stream failed at roughly 153 seconds;
- heartbeats proved the stream remained active, so the dominant failure boundary was reference inference latency rather than route/model-load failure.

Truth boundary:
- this release optimizes the canonical Python/NumPy reference path; it does not claim compiled-backend throughput or guarantee completion inside every Vercel duration limit;
- whole-model dequantization remains prohibited by design in this patch so memory stays bounded.

## SERVER 2.1.15 / Chat 1.3.12 — 2026-09-07

Changed:
- normal same-origin Chat use no longer requires the user to paste or bootstrap a Chat secret through Admin;
- loading `/api/chat` now receives a bounded HttpOnly, Secure, SameSite=Strict session cookie scoped to `/api/chat`;
- the session is signed from the server-side Chat secret and the permanent `SWRLZ_WEB_CHAT_TOKEN` is never exposed to browser JavaScript;
- the legacy explicit Admin session endpoint remains as a compatibility path;
- Chat UI uses a non-secret browser marker only to satisfy the historical base UI token guard; actual request authorization is server-managed by the cookie;
- Bridge Settings is renamed to Chat Settings and the credential field is hidden from the normal UI;
- sending a message no longer opens settings merely because no browser-held Chat token exists.

Security boundary:
- `SWRLZ_WEB_CHAT_TOKEN` remains the server-side root secret;
- the browser receives only a bounded signed cookie, never the root secret;
- manual `x-swrlz-chat-token` validation remains as a fallback compatibility path.

## SERVER 2.1.14 / Chat 1.3.11 — 2026-09-07

Changed:
- Admin-authorized Chat sessions moved from an instance-local in-memory dictionary to stateless signed session tokens;
- any Vercel instance can verify an issued session when the shared signing secret is available;
- Chat stopped forcing the settings dialog open when authorization was missing and instead reported an authorization receipt in place.

## SERVER 2.1.13 / Chat 1.3.6-1.3.10 — 2026-09-07

Added/changed:
- live core pages and Chat assets resolve from GitHub `dev` on request with a short in-instance cache and bundled fallback;
- live reads no longer depend on the `/tmp` copy created by whichever Vercel instance handled `/api/pages` sync;
- `dev`-only Chat version bumps were proven live while the deployed server version remained unchanged (`1.3.7`, `1.3.8`, `1.3.9`, `1.3.10` on Server `2.1.13`);
- Chat settings learned server-side Chat credential state without echoing the secret;
- the stale local-R39 boilerplate panel was replaced by Chat status and model status: route, server/instance, credential/session state, readiness, engine, source, model SHA, and blocker.

Live-page receipt:
- GitHub `dev` is the durable source of truth;
- supported page/UI changes can appear live without `main` promotion, Vercel server redeploy, or `/tmp` synchronization.

## SERVER 2.1.12 / Chat 1.3.5 — 2026-09-07

Changed:
- Admin auth now resolves `SWRLZ_ADMIN_TOKEN` per request instead of relying on an import-time environment snapshot;
- harmless outer whitespace and one matching wrapping quote pair are normalized while identity comparison remains exact and constant-time;
- repaired Page Manager regression where SET ADMIN remained locked despite a valid deployment token.

## SERVER 2.1.11 / Chat 1.3.5 — 2026-09-07

Added/changed:
- Chat operations/status was separated from model inspection so `/api/chat/ops` stays cheap and non-blocking;
- server version and route state can render immediately without loading/inspecting the R39 model;
- introduced Admin-to-Chat ephemeral session bootstrap while retaining the direct Chat-token fallback;
- mobile drawer repair, authoritative status paint, and Chat/server footer receipt remained active.

## SERVER 2.1.10 / Chat 1.3.4 — 2026-09-07

Changed:
- parent UI guards tolerate harmless URL query decoration/tracking parameters;
- live manager/UI paths no longer fall through to stale handlers because of unrelated query keys.

## SERVER 2.1.9 / Chat 1.3.4 — 2026-09-07

Changed:
- `/live/` and Chat UI serving were moved onto the unified parent app boundary;
- Page Manager gained explicit Admin/GitHub/source status receipts;
- mobile drawer stacking and stale bottom status/version behavior were repaired.

## SERVER 2.1.8 / Chat 1.3.4 — 2026-09-07

Added:
- live Page Manager `/api/pages`;
- durable page source on non-deploying `dev`;
- editable runtime copies and optional runtime -> `dev` push-back;
- source-managed Admin, Chat, Chat CSS/JS, live index, and additional `runtime_pages/pages/*` publication;
- server-side GitHub write-token resolution.

## SERVER 2.1.7 — 2026-09-07

Added:
- narrow hot runtime for Chat/R39 overrides under `/api/hot`;
- atomic runtime sync/backups with bundled fallbacks.

## SERVER 2.1.6 — 2026-09-07

Added:
- automatic local R39 initialization path;
- heartbeat STATUS events around blocking engine progress so idle network timeouts do not masquerade as compute hangs.

## SERVER 2.1.5 — 2026-09-07

Changed:
- tokenizer admission became tolerant of producer-specific BPE labels when structural tokenizer evidence is valid.

## Unified SERVER 2.1.4 / Chat 1.3.0 — 2026-09-07

Added:
- canonical SWRLZX v1 header/TOC parser for active physical section locations;
- tokenizer, tensor-directory, and tensor-data payload reconstruction;
- local R39 Python/NumPy reference executor for the supplied LFM2 profile;
- BPE tokenization and incremental UTF-8 decoding;
- recurrent short-convolution and GQA/KV state execution;
- `f32`, `f16`, `bf16`, `q4_0`, `q8_0`, `q4_k`, and `q6_k` tensor readers;
- bounded generation controls and local cancellation checks;
- local `LOCAL_R39` stream route when no upstream URL is configured;
- Gate 5 engine probe that distinguishes physical payload reconstruction from executable one-token readiness;
- source verifier `scripts/verify_r39_inference.py`.

Preserved:
- proof-bound upstream stream/cancel mode and upstream contract validation;
- browser/Admin auth separation and runtime Chat-token override;
- Truth Firewall: only `DELTA.text` becomes assistant prose;
- 2.1.3 Admin/Live Web/control-plane implementation, preserved in `api/server_v213.py` and wrapped by the 2.1.4 release entrypoint;
- R39 Forge transport, exact SHA/size checks, snapshots, activity receipts, capability/release state, and deployment suppression on `dev`.

Truth boundary:
- source-level local inference wiring is complete and verified against the R299 SERVER architecture contracts;
- the executor fails closed on unsupported graph/tensor/profile/quantizer/layout states;
- source verification does **not** claim Vercel latency or live completion within platform limits;
- production readiness requires deployment receipts plus a successful streamed local R39 request.

## Unified SERVER 2.1.3 / Chat 1.2.0 — 2026-09-06

Added paired Chat/Admin control planes: evidence drawers, retry/fork/context diagnostics, stream camera and generation controls on Chat; runtime Chat-token management, Live Web manager, capability/health/release state, snapshots/rollback, activity receipts, and promote manifests on Admin.

## Unified SERVER 2.1.0 / Chat 1.0.0 — 2026-09-06

Checkpoint: `INT-VERCEL-CHAT-001A`  
Baseline: SERVER 2.0.7 at `0375f42f57d1e4df000a53a6ec02659bb7a6a5df`

Initial additive `/api/chat` integration added the R299-derived responsive UI, browser-local threads, V2 NDJSON streaming contract, independent Chat token, proof-bound upstream bridge, Gate 5 verification, Admin Chat entrypoint, contract/checkpoint documentation, and fail-closed local status-only behavior while inference payload locations were still unresolved.
