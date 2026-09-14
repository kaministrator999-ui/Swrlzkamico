# Server 2.3.142 — Chat direct runtime asset delivery

**Overall Server:** `2.3.142`  
**Chat:** `1.5.19`  
**LALM:** unchanged  
**Manifest:** `v51`  
**Deployment:** NONE  
**Restart:** NONE

## Purpose

Correct the partial/very-slow Chat hydration observed on mobile after the Mask/Human/Brain cleanup.

## Root cause

The prior runtime path reduced parser blocking but still caused the browser to request the full Chat enhancement set through the Vercel live-source bridge. That meant many revisioned asset requests each incurred the Vercel-to-GitHub source hop.

## Correction

- `/chat` now receives only one runtime loader through the Vercel live-source bridge.
- The manifest no longer injects the full stylesheet list itself.
- The loader applies the saved/default Ice Dragon theme marker immediately.
- Runtime CSS and JS are loaded directly from the GitHub `runtime` source using the manifest revision as a cache-busting token.
- Styles are requested concurrently.
- External scripts are inserted with `async=false`, allowing overlapping downloads while preserving execution order.

## Architecture

This changes delivery only. It does not move cognition back into Chat.

- Chat / Mask: relay + presentation.
- Server / Human: authority + execution.
- LALM / Brain: interpretation + reasoning.

## Lineage

- Loader correction: `2739d9d0d02721da49882a820b141f0f725dc3e9`
- Manifest v51: `8abad155606627086cf046b5702f22b441fa2a5f`
- Server 2.3.142: `0de1408cc850c8959ff120946dbba4b537690e05`
- Chat 1.5.19: `49d728834aca99e09d644ef3344073fa8e41b03e`
