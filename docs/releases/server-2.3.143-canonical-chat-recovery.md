# Server 2.3.143 / Web Chat 1.5.20 — canonical Chat recovery

## Scope

Runtime-hot Chat delivery/state recovery only. No stable deployment, restart, or LALM inference change.

## Problem

The v50/v51 experimental runtime loaders left the browser showing the standalone base Chat shell and, on some clients, failed to finish enhancement hydration. The legacy browser conversation namespace `swrlz.vercel.chat.v1` could also resurface stale standalone threads such as the pre-migration greeting test.

## Changes

- Removed `web/chat_runtime_loader_v1.js` from the active `/chat` manifest route.
- Restored the known-good canonical main-Chat style/script graph from manifest v47, retaining the current Mask/Human/Brain-safe files.
- Restored stable same-origin manifest-versioned asset delivery.
- Added `web/chat_legacy_state_retirement.js` as the first runtime Chat script.
- The retirement gate removes `swrlz.vercel.chat.v1` once when it exists, records `swrlz.chat.legacy-state-retired.v1`, and reloads once so stale standalone thread state cannot remain in memory on the active page.
- The experimental loader source remains in repository lineage but is inactive.

## Architecture

Mask/Human/Brain ownership is unchanged:

- Chat relays factual input/context and presents output.
- Server owns operational authority/execution.
- LALM 2.1.44 owns interpretation/reasoning/semantic acceptance.

## Authorities

- Server Runtime: 2.3.143
- Web Chat: 1.5.20
- LALM Engine: unchanged at 2.1.44
- Manifest: 52

## Deployment

NONE. Runtime-hot source only. No restart.
