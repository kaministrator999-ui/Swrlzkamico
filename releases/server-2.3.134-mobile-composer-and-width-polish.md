# Server 2.3.134 / Web Chat 1.5.12

## Event
Mobile composer reading mode, wider response layout, and balanced user identity polish.

## Baseline
- Server Runtime: 2.3.133
- Web Chat: 1.5.11
- Runtime manifest: 44
- `VERSION.txt`: unchanged registry format and ownership routing

The Server and Web Chat authorities were re-read immediately before version assignment. They still matched the captured baseline, so the next valid authorities were assigned as Server 2.3.134 / Web Chat 1.5.12.

## Change
- The Ice Dragon assistant response starts 26 px from the left edge on mobile instead of the prior 52 px offset, giving the response substantially more usable width while retaining a small visual gutter beneath the companion identity plate.
- User messages now use a smaller companion-style identity treatment: the signed-in/custom avatar remains authoritative, while the user name receives a restrained frosted plate, Ice Dragon brand typography, blur, shadow, and tighter visual pairing with the avatar.
- User message width is increased so the bubble uses the screen more efficiently without touching the physical viewport edge.
- The mobile composer now has a small chevron handle immediately above the input. Tapping it collapses the complete composer below the viewport, leaving only the handle and expanding the transcript reading area.
- A manually collapsed composer automatically slides back into view when the user later scrolls downward into the conversation tail. The reveal is armed only after the transcript has moved away from the tail, preventing an immediate self-reopen when the user intentionally collapses it at the bottom.
- The existing native touch/scroll gesture guard remains the single scroll-interaction owner; the new tail-reveal check runs inside that same capture path before the existing stream-follow suppression logic.

## Preserved behavior
- No LALM cognition, response generation, server routing, authentication, Google identity ownership, transcript persistence, context capacity, wallpaper ownership, or assistant companion source changed.
- No new competing scroll listener layer or composer backend was introduced.
- Runtime manifest remains v44 because only already-loaded runtime assets changed.
- Web Frontend remains 1.0.3; this event changes Chat presentation/interaction rather than frontend boot/cache architecture.

## Versions
- Server Runtime: 2.3.134
- Web Chat: 1.5.12
- Web Frontend: 1.0.3 unchanged
- Runtime manifest: 44 unchanged

## Deployment / restart
NONE. This is a runtime-hot Chat event using assets already served by the deployed runtime loader. No Vercel deployment or restart was requested or performed.

## Verification
- Repository source updates completed for the canonical Ice Dragon response-layout CSS, mobile viewport CSS, and existing mobile scroll-gesture controller.
- Version authorities were revalidated before assignment and advanced without a concurrent authority conflict.
- Post-version authority verification and live/mobile visual acceptance are recorded separately during closeout. The user should refresh the current `/chat` page and test the collapse/reveal gesture on the target phone.

## Source lineage
- Response width + user identity CSS: `a21125d5381b2ff1b7e16f5266da3163fe852e44`
- Mobile composer dock CSS: `95983351a7699b468b3d2578c60027f5f06568cf`
- Composer collapse/tail-reveal + preserved gesture guard: `01ffc1421efc1a1802cdbc388d8707218d3f673f`
- Server authority: `1becf71cf28a2bb1307212c0e526215655a1dd63`
- Web Chat authority: `0943a3d3d039a024de5ef24eee27da16f49e01aa`
