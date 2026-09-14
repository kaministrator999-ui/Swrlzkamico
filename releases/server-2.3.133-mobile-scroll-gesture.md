# Server 2.3.133 / Web Chat 1.5.11

## Event
Mobile transcript drag/scroll responsiveness correction.

## Baseline
- Server Runtime: 2.3.132
- Web Chat: 1.5.10
- Runtime manifest: 43

A same-version authority SHA change was detected during release, so Server and Web Chat authorities were re-read before assigning the next versions.

## Change
Added `web/chat_scroll_gesture_v1.js` and published it in manifest v44. The transcript now explicitly uses native vertical touch panning, contained overscroll, native momentum scrolling and automatic (non-smooth) scroll behavior. During an active touch drag and a 260 ms post-release momentum handoff window, capture-phase scroll handling blocks the stream-follow re-evaluation listener from re-locking the viewport against the user's finger or browser inertia.

## Preserved behavior
- Stream-follow remains available after the manual gesture/momentum window settles.
- Ice Dragon canonical wallpaper and companion first-paint remain unchanged.
- Activity → companion/name/time → response composition remains unchanged.
- Google user identity, account/theme settings, turn integrity, transcript continuity and context capacity remain unchanged.

## Versions
- Server Runtime: 2.3.133
- Web Chat: 1.5.11
- Runtime manifest: 44

## Verification
Repository/runtime wiring complete. Mobile tactile acceptance remains pending user refresh/testing. No explicit Vercel deployment or restart was required for this runtime-hot event.
