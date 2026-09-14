# Server 2.3.141 — Chat parallel runtime hydration

**Status:** runtime-hot complete  
**Overall Server:** `2.3.141`  
**Web Chat:** `1.5.18`  
**LALM:** unchanged at `2.1.44`  
**Deployment:** NONE  
**Restart:** NONE

## Problem

After the Mask/Human/Brain cleanup, the Chat page could remain visibly stuck on the base shell while the full Ice Dragon interface and enhancement layers had not yet appeared.

The stable live-source injector emits every manifest script as a normal parser-blocking `<script src=...></script>` tag. Every manifest revision also changes the `?v=` revision on every asset URL. A new manifest therefore forced the browser to walk the entire runtime enhancement script chain under new immutable URLs before the full interface finished hydrating.

The base boot guard intentionally keeps the shell usable while enhancement hydration is incomplete, so the user could see a partial interface for an unacceptable amount of time.

## Correction

Manifest v50 now injects only `web/chat_runtime_loader_v1.js`.

The runtime loader:

- captures the native browser `fetch` before later Chat wrappers are installed;
- starts all existing runtime enhancement asset fetches concurrently;
- executes the fetched classic-script sources in the exact established dependency order;
- preserves the current Chat enhancement graph and ownership boundaries;
- exposes `parallel-fetch-ordered-exec-v1` hydration diagnostics;
- emits a visible hydration-failure event rather than silently pretending the full interface loaded.

This avoids a stable-server deployment while removing the serial runtime-hydration bottleneck.

## Architecture boundary

This is delivery mechanics only.

- Chat remains the Mask: factual relay, presentation, continuity and client capabilities.
- Server remains the Human/Body: operational authority, routing and execution.
- LALM remains the Brain: interpretation, reasoning and semantic acceptance.

No cognition was added back to Chat.

## Lineage

- Runtime loader creation: `23301dabb31e1ebf7550485c3449aac93d5ec8a0`
- Manifest v50 activation: `04631588456ea37bbb38d829c10c9fa049df9fd5`
- Server version authority: `f304f563fb566e999ac135290c86aac56457ff5f`
- Web Chat version authority: `152015d72da8e654c0a2302ce3444595543a2d1a`

## Rollback

Rollback can restore the manifest v49 script list. No durable user-data migration is involved.
