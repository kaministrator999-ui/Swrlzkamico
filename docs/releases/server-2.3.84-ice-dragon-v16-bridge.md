# Server 2.3.84 — Ice Dragon stale-manifest compatibility bridge

Status: source implementation complete; live verification pending.

Affected modules:
- Server Runtime 2.3.84
- Web Chat 1.4.76

Web Frontend remains 1.0.2.
Deployment: NONE
Restart: NONE

What changed:
- Replaced the old v16 wallpaper hydrator body with a compatibility bridge that immediately loads v17.
- This makes stale live manifest v13 and fresh manifest v14 converge on the same v17 clean-source/cache-generation path.
- No stable API, authentication, LALM, or deployment configuration changed.

Why:
Live verification after Server 2.3.83 showed production still returning manifest v13 and selecting v16 even though runtime already held manifest v14. This bridge prevents that propagation lag from keeping the browser on the retired fake-8K/cache-generation path.

Verification:
- Runtime authority re-read before assignment: Server 2.3.83 / Chat 1.4.75.
- Post-commit authority and live v16 asset verification required.
- Final visual acceptance remains user-visible.
