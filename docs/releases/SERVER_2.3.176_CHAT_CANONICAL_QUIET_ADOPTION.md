# Server 2.3.176 — Chat canonical quiet adoption

**Status:** runtime implementation complete; source/version verification complete; user-visible send test pending.

**Server Runtime:** 2.3.176  
**Web Chat:** 1.5.36  
**Deployment:** NONE  
**Restart:** NONE

## Problem

The same-tab canonical reconciler replaced the live Chat state and called the full Chat `render(false)` path whenever the local canonical cache changed. The full renderer rebuilds the thread list and message stack with `replaceChildren()`. During send/canonical acknowledgement this could visually resemble a brief black page refresh or camera shutter even though no browser navigation occurred.

The Whole Conversation Camera itself remains observational and does not navigate or reload the page.

## Change

- Advanced the same-tab reconciler contract from v2 to v3.
- While an active request has not yet reached a canonical terminal assistant state, canonical cache changes are deferred rather than replacing the live streaming Mask.
- Once canonical state can be adopted, the reconciler compares a bounded visual projection of the live and canonical states.
- If the visible conversation is equivalent, canonical state is adopted quietly without invoking the full Chat renderer.
- If visible state genuinely differs (thread/title/pin/message content/state), the existing full render remains available so real server-owned changes are still presented.
- Canonical adoption events now report whether adoption was `quiet` or `render`, and diagnostics count quiet adoptions/deferred active updates.
- Manifest revision advanced from 103 to 104 so the updated runtime Chat asset is cache-busted through the existing runtime loader.

## Architecture

The change stays inside the Mask/presentation synchronization layer. It does not move cognition into Chat, does not weaken server canonical ownership, and does not alter the LALM.

## Baseline and concurrency

At event entry and again at the commit boundary:

- Server Runtime authority: 2.3.175
- Web Chat authority: 1.5.35
- `VERSION.txt` continued routing those modules to their canonical authority files.

No concurrent authority advancement was observed before version assignment.

## Lineage

- Reconciler source commit: `9eb6800aee01cba1a8fff595d254405ce80d35c7`
- Web Chat 1.5.36 authority commit: `58ec83e04aab5ef0796bc812a5790928c2a08be9`
- Server Runtime 2.3.176 authority commit: `079f01062e08ca701508e6613413e0133d860a0c`
- Manifest 104 commit: `876f52337275cdc5723476f958508d129d9e0373`

## Verification

Repository/source verification: PASS.  
Live runtime source/version verification: pending request.  
User-visible send behavior: pending user test.  
No deployment or restart was performed.
