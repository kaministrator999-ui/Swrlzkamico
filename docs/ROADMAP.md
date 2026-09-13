# §wyrlz Server Roadmap

## Current release

**Server v2.3.112 / Web Chat 1.4.94 — exact Ice Dragon PNG wallpaper**

**Status: exact supplied artwork wired directly; live browser acceptance pending refresh.**

The Ice Dragon theme now uses the exact repository-root PNG identified by the user (`file_00000000b13c81f5a7f9fe99c0264ef0.png`) without resize, recompression, Base64 reconstruction, or fake 8K generation. The same Git blob is exposed at `web/themes/ice-dragon/assets/ice-dragon-adult-wallpaper.png`, loaded by wallpaper v20, cached under a fresh generation, and rendered with centered `cover` geometry so it fills the whole chat backdrop. Manifest 30 activates the new controller. See [event receipt](releases/server-2.3.112-ice-dragon-exact-png-wallpaper.md).

## Previous release context

The prior roadmap entries remain preserved in Git history. This current-state update intentionally advances only the active frontier while retaining full lineage through release receipts and commit history.

## Mandatory roadmap/version law

Every server development event gets a new overall Server runtime authority when project state changes, including failed attempts.

Every module actually changed gets its own version increment. A module that did not change keeps its version.

`VERSION.txt` is the module-authority router. It maps stable module IDs to their own `versions/<module-id>.txt` files and does not duplicate their values.

Consumers fetch the owning module authority when they need a version for display or update comparison. They do not maintain another module's version manually.

Every event records what changed, affected module versions, failed attempts where applicable, verification state, deployment/restart state, and relevant lineage.

Before version assignment, the authoritative Server and affected-module version files must be re-read and compared to the transaction baseline. If either changed during work, planned version numbers are discarded, current state is reconciled, and the next valid versions are calculated from the newly current authorities. Roadmap updates must use the freshly re-read roadmap SHA and are part of the same guarded release transaction.
