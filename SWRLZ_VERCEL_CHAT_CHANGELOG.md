# SWRLZ Vercel Chat Changelog

## Unified SERVER 2.1.0 / Chat 1.0.0 — 2026-09-06

Checkpoint: `INT-VERCEL-CHAT-001A`
Baseline: SERVER 2.0.7 at `0375f42f57d1e4df000a53a6ec02659bb7a6a5df`

Added:

- additive `/api/chat` mount on the existing unified FastAPI application;
- R299-derived responsive SERVER chat UI;
- browser-local threads, bookmarks, copy, rename/delete, and JSON evidence export;
- strict `swrlz_llm_stream_v2` NDJSON consumption with DELTA, RESET, terminal state, timing, and operational trace separation;
- independent fail-closed `SWRLZ_WEB_CHAT_TOKEN` boundary;
- proof-bound SWRLZ SERVER stream/cancel proxy with server-side device credentials;
- truthful local R39 status-only behavior when no inference upstream is configured;
- sanitized Gate 5 verification from the chat settings surface;
- Admin `OPEN CHAT` entry point;
- source-lineage, contract, checkpoint, environment template, and source verifier documentation.

Preserved:

- Admin authentication hardening from 2.0.7;
- `/api/health`, `/api/lalm`, Admin file manager and chunked transfers;
- Forge Git-chunk reconstruction and exact R39 integrity contracts;
- same-invocation Gate 5 R39 load/verification;
- Vercel exclusions for `.transport/**` and the preserved large server archive.

Current truth boundary:

- R39 transport, decompression, raw SHA verification, container/header verification, and integrity-table parsing are proven;
- one-token and interactive local inference remain **not ready** with blocker `SECTION_PAYLOAD_LOCATION_AND_INFERENCE_WIRING_PENDING`;
- the chat bridge therefore emits no synthetic DELTA text in local status-only mode;
- live chat requires a reachable proof-bound SWRLZ SERVER upstream until local inference wiring is completed.

Integration commits were written directly to `kaministrator999-ui/Swrlzkamico` on `main`; Vercel deployment remains a separate deployment action.
