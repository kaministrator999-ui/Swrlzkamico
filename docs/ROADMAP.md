# §wyrlz Server Roadmap

## Current release

**Server 2.3.132 / Web Chat 1.5.10 — canonical Ice Dragon companion + stable first paint**

**Status: runtime-hot UI update published; mobile visual acceptance pending refresh.**

Manifest v43 locks the assistant companion to a small runtime derivative of the user-supplied blue/white Ice Dragon artwork and removes the competing async companion repaint path. The companion now remains structurally joined to the §wyrlz name/time plate, later theme shorthand can no longer erase its `background-image`, and the green emoji fallback is retired. `chat_response_layout_v1.js` now completes its initial assistant DOM normalization before Ice Dragon assistant rows become visible, eliminating the brief refresh flash where the avatar appeared above the name before moving into the forum-style plate. Existing `Activity log → companion/name/time → response` composition, Google user identity, account/theme settings, canonical wallpaper, turn integrity, transcript continuity, and context capacity remain preserved. The event baseline observed Server 2.3.130 / Web Chat 1.5.9, then correctly reconciled a concurrent Server advance to 2.3.131 before assigning 2.3.132 / 1.5.10. No Vercel deployment or restart was performed. See [event receipt](releases/server-2.3.132-ice-dragon-companion-first-paint.md).

## Previous release context

**Server 2.3.126 / Web Chat 1.5.6 — Ice Dragon forum-glass polish + account chat identity**

Manifest v39 adds `ice-dragon-polish-v2.css` and `chat_account_identity_v1.js` while preserving the canonical exact-PNG workspace wallpaper and the v38 wallpaper lock. The composer uses a lighter sculpted outer glass field with a darker inner input surface, cooler silver-gray context/caption typography, and lower blur so artwork detail remains visible. Assistant identity receives a restrained old-forum-inspired frosted nameplate that visually joins the dragon companion with the §wyrlz name/time, while assistant response bubbles use a subtler themed border rather than a heavy frame. Activity/copy/export/action controls use ice-blue glass instead of flat gray blocks. Account settings are constrained for mobile, duplicate name controls are collapsed toward one editable Chat name, and signed-in Google avatar/name are used for user-message identity instead of the generic `YOU` label when available. Existing turn-integrity, transcript continuity, context-capacity, response-polish, and wallpaper ownership remain unchanged. See [event receipt](releases/server-2.3.126-chat-identity-polish.md).

## Previous release context

**Server 2.3.125 / Web Chat 1.5.5 — canonical wallpaper lock + restrained glass**

The refresh regression was traced to `ice-dragon-art-loader-v17.js`: after the canonical workspace had already painted the intended repository PNG, the legacy adult-art hydrator reconstructed/cached the former 864×1536 JPEG and later painted it onto `.messages`, visually replacing the correct backdrop. That adult wallpaper responsibility is now retired from the art loader; it remains companion-avatar-only and actively clears legacy message-chamber wallpaper state. `chat_frontend_boot.js` no longer reads the stale adult-preview localStorage key and always first-paints the canonical Ice Dragon PNG on `.workspace`. Manifest v38 cache-busts the fix. The composer is rebalanced to the requested layered glass treatment: lighter outer shell blur, darker inner input field, and lower blur on user/assistant bubbles so the artwork remains sharper. Existing Ice Dragon brand styling from manifest v37 and all turn-integrity/transcript/context behavior remain preserved. See [event receipt](releases/server-2.3.125-ice-dragon-wallpaper-lock.md).

## Previous release context

**Server 2.3.124 / Web Chat 1.5.4 — Ice Dragon brand treatment**

Manifest v37 added `ice-dragon-brand-v1.css` and preserved the canonical workspace shell while applying the icy §wyrlz identity treatment to sidebar and assistant byline surfaces. This concurrent update was detected before version assignment and preserved by the 2.3.125 event.

## Previous release context

**Server 2.3.123 / Web Chat 1.5.3 — canonical Ice Dragon shell + glass composer**

**Status: runtime-hot UI architecture published; browser visual acceptance pending refresh.**

The Ice Dragon wallpaper is owned by the full `.workspace` instead of only the `.messages` scroll chamber. This lets the composer region remain genuinely transparent/blurred over the same backdrop instead of revealing a solid dark page behind it. `.messages` is transparent, the full `.message-stack` owns the continuous readability fade so it extends through long/error content, and the welcome subtitle remains high-contrast over bright artwork. `chat_frontend_boot.js` defaults to/persists the Ice Dragon theme when no preference exists, paints the workspace immediately from the direct repository PNG, and marks the canonical frontend shell ready before backend/theme hydration. Manifest v36 adds `ice-dragon-shell-v1.css` as the final theme-shell authority and preserves existing turn-integrity, transcript-continuity, context-capacity, and response-polish scripts. See [event receipt](releases/server-2.3.123-canonical-chat-shell.md).

## Previous release context

**Server 2.3.121 / Deployment Control 1.0.6 — collector storage acceptance**

The prior run confirmed the strong-metadata/weak-delivery ETag mismatch, then stopped at HTTP 401 before a write. This event distinguishes non-readable application credentials and can verify the exact published engine against the existing private store. Production storage acceptance passed: the exact live action saved revision 2 and a new session read confirmed identical content. The exported application credential is redacted, so authenticated browser/API mutation was not verified. Collector remains 1.0.8. No deployment or collection interruption. See [event receipt](releases/server-2.3.121-collector-storage-acceptance.md).

## Previous release context

**Server 2.3.120 / Deployment Control 1.0.5 — bounded collector live verification**

Collector 1.0.8 is confirmed live. This event adds a separate verification job that uses existing credentials privately to save unchanged settings and confirm persistence. Production acceptance is pending the job result. It does not deploy or interrupt collection. See [event receipt](releases/server-2.3.120-collector-live-verification.md).

## Previous release context

**Server v2.3.118 / Web Chat 1.5.1 — Ice Dragon UI polish**

**Status: runtime-hot UI polish published; browser visual acceptance pending refresh.**

The Ice Dragon wallpaper source remains unchanged. This event fixes three presentation issues only: the dark readability fade is owned by the full `.message-stack` so it extends through long/error content instead of stopping at the scroll viewport boundary; the composer shell and input box backing are translucent blurred glass instead of an opaque dark slab; and the welcome subtitle contrast is increased with brighter text and shadowing so the copy beneath “What are we building?” remains readable over bright portions of the artwork. Manifest v34 forces a fresh CSS cache revision. See [event receipt](releases/server-2.3.118-ice-dragon-ui-polish.md).

## Previous release context

**Server v2.3.116 / Web Chat 1.4.99 — exact Ice Dragon PNG with stale-manifest compatibility**

**Status: exact supplied artwork wired directly; stale v20 and current v21 paths both converge on the same PNG; browser acceptance pending refresh.**

The intended Ice Dragon artwork is the exact repository-root PNG `file_00000000b13c81f5a7f9fe99c0264ef0.png`. No resize, recompression, Base64 reconstruction, or fake 8K generation is used. The runtime binary bridge was proven to return HTTP 503 for the copied PNG asset, so current wallpaper v21 requests the exact PNG directly from raw GitHub and renders it centered with `background-size: cover` across the complete chat backdrop. Because the live manifest was still temporarily serving manifest 31 / wallpaper v20, v20 was also converted into a compatibility bridge to the same direct PNG path. This makes stale and current manifests converge instead of showing the old dragon. See [v21 receipt](releases/server-2.3.115-ice-dragon-raw-png.md) and [v20 compatibility receipt](releases/server-2.3.116-ice-dragon-v20-compat-bridge.md).

Server 2.3.113 / Web Chat 1.4.96 copied the exact PNG Git blob into the runtime theme asset path and restored `cover`, but live acceptance exposed that the text-oriented `/live/assets/...` source bridge cannot serve that binary and returned HTTP 503. Server 2.3.115 / Web Chat 1.4.98 therefore bypassed the binary bridge with direct browser loading, and Server 2.3.116 / Web Chat 1.4.99 hardened stale-manifest compatibility.

The prior roadmap entries remain preserved in Git history and release receipts.

## Mandatory roadmap/version law

Every server development event gets a new overall Server runtime authority when project state changes, including failed attempts.

Every module actually changed gets its own version increment. A module that did not change keeps its version.

`VERSION.txt` is the module-authority router. It maps stable module IDs to their own `versions/<module-id>.txt` files and does not duplicate their values.

Consumers fetch the owning module authority when they need a version for display or update comparison. They do not maintain another module's version manually.

Every event records what changed, affected module versions, failed attempts where applicable, verification state, deployment/restart state, and relevant lineage.

Before version assignment, the authoritative Server and affected-module version files must be re-read and compared to the transaction baseline. If either changed during work, planned version numbers are discarded, current state is reconciled, and the next valid versions are calculated from the newly current authorities. Roadmap updates must use the freshly re-read roadmap SHA and are part of the same guarded release transaction.
