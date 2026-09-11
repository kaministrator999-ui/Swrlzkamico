# Server Runtime 2.3.42

## Modules
- Server Runtime: 2.3.42
- Web Chat: 1.4.37
- LALM Engine: 2.1.25 (unchanged)

## Change
Ice Dragon generated artwork placement was corrected based on live Android screenshots.

- The juvenile companion artwork now owns the sidebar brand badge, assistant avatars, and the new-chat welcome orb.
- The adult guardian artwork was moved from the body pseudo-element to the actual Chat message chamber so normal app surfaces cannot cover it.
- The old abstract body sigil layer is disabled for Ice Dragon generated-art mode.
- Mobile receives its own adult-background framing while preserving message readability.
- Existing runtime hydration, account-scoped history, responsive geometry, and LALM behavior are unchanged.

## Verification state
- Runtime source updated.
- Browser screenshot acceptance pending.

## Deployment
- Vercel deployment: none required (runtime-hot change).
- Server restart: none required.

## Lineage
- Ice Dragon art placement commit: 5978e8e1b80cf906c19409bd41bca9448e4e6bdd
- Server Runtime version commit: f72e01a0d4293f70a04831048895a2fda4f69017
- Web Chat version commit: 0c705bafc88105c1441d090e18adf37f89577b29
