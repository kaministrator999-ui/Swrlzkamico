# INT-VERCEL-CHAT-001A Checkpoint

Date: 2026-09-06  
Target: unified SERVER **2.1.0** / chat **1.0.0**  
Android source contract: `SERVER_CFv2.1.134` / `R299`

## Accepted source boundary

Vercel SERVER baseline:

- repository: `kaministrator999-ui/Swrlzkamico`;
- branch: `main`;
- baseline commit: `0375f42f57d1e4df000a53a6ec02659bb7a6a5df`;
- baseline implementation: SERVER 2.0.7.

R299 Android source archive supplied for integration:

- archive: `SERVER_CFv2.1.134_SWRLZ_CANDIDATE_R299.zip`;
- recorded source SHA-256: `d54cf84feebddba1524c69fe601c97e759c59a8c870f5199f43051a988414a3a`.

Chat overlay source:

- archive: `SWRLZ_VERCEL_CHAT_v1.0.0_R1.zip`;
- purpose: additive Vercel web chat and bridge derived from the R299 SERVER chat contract.

## Pre-mutation evidence

SERVER 2.0.7 was already proven live on the correct Vercel deployment boundary:

- Admin token authentication accepted;
- Forge transport reconstructed 54 GitHub chunks;
- wrapper ZIP and nested R39 gzip were accepted;
- raw R39 size `233637480` bytes;
- raw R39 SHA-256 `65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee`;
- Gate 5 return code 0;
- container/header integrity checks passed;
- 176 declared integrity records and 176 parsed records;
- required sections 3, 4, and 5 registered;
- `oneTokenReady:false`;
- `interactiveReady:false`;
- blocker `SECTION_PAYLOAD_LOCATION_AND_INFERENCE_WIRING_PENDING`.

The integration therefore must not fabricate local inference output.

## Impact/dependency map

Requested change: web chat interface integrated into the current Vercel SERVER.

Documented intent -> visible behavior -> implementation boundary -> validation:

1. Preserve proven Admin/R39/Gate 5 behavior -> existing `/api/admin`, `/api/lalm`, `/api/health` continue to exist -> keep `api/index.py` as the unified application and mount chat additively -> verify version/routes/source references.
2. Add R299-style chat -> responsive `/api/chat` page with browser-local threads and streaming UI -> `web/chat.html` + `api/chat.py` -> verify page source invariants and mount.
3. Keep answer text distinct from operational state -> only DELTA enters assistant body -> strict V2 NDJSON validation -> verify RESET/DELTA/terminal semantics in source.
4. Do not expose Admin or device credentials -> independent browser token and server-only upstream proof -> `SWRLZ_WEB_CHAT_TOKEN` plus upstream environment variables -> verify examples/docs and source non-disclosure boundary.
5. Respect current inference truth -> status-only local mode until one-token wiring exists -> STARTED/STATUS/FAILED without DELTA -> source verifier and runtime status endpoint.

## Integrated changes

- added `api/chat.py`;
- added `web/chat.html`;
- added `api/__init__.py`;
- mounted chat at `/api/chat` from `api/index.py`;
- advanced unified SERVER version 2.0.7 -> 2.1.0;
- added Admin `OPEN CHAT` entry point;
- added separate chat environment template;
- synchronized root README, chat guide, contract, checkpoint, and changelog;
- preserved existing model transport and Vercel large-file exclusions.

Primary integration commits include:

- `70f184649dee3207dfb07e6503f692b59e23333c` — chat bridge;
- `2f9f5adfc7362aa7268abfd6a1a5ce6e4c9e3b7e` — SERVER 2.1.0 mount/version;
- subsequent commits synchronize source accounting and documentation.

## Validation boundary

The supplied chat package passed its deterministic local verification before mutation, including:

- static package checks;
- safe chat UI checks;
- unified SERVER mount;
- truthful local boundary;
- simulated proof-bound upstream stream/cancel;
- content manifest.

After GitHub integration, repository source is rechecked for version, mount, chat files, environment names, and stale version references. A Vercel deployment is still required to establish live deployment evidence.

## Non-claims

This checkpoint does not claim:

- Vercel deployment success for SERVER 2.1.0 until redeployed;
- local R39 token generation;
- live reachability of a proof-bound upstream;
- proof acceptance by an Android SERVER until observed;
- production scaling or multi-instance stream durability.
