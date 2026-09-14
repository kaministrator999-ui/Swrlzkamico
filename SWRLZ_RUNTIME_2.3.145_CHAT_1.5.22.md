# §wyrlz Runtime 2.3.145 / Web Chat 1.5.22

Date: 2026-09-14
Branch: `runtime`
Deployment: none required
LALM engine: unchanged at 2.1.44

## Problem

Android Chrome could render the Chat shell and then appear frozen for an extended period. Manifest v53 moved many helpers out of the critical phase but still scheduled the full background graph within 900 ms and appended that graph in one burst. The theme path also had two heavyweight image hazards: first-paint boot could hydrate legacy base64 companion art from localStorage, and wallpaper v21 performed a second `Image()` probe using a distinct cache-busting URL after the wallpaper had already been assigned.

## Correction

- Added `web/chat_frontend_boot_v2.js`.
  - Removes legacy companion/adult preview keys without reading or decoding them.
  - Does not request the large wallpaper during first paint.
  - Leaves the main Chat shell immediately usable.
- Added `web/chat_runtime_loader_v3.js`.
  - Critical phase is intentionally tiny.
  - Functional helpers load serially after a 1.6 second settling window.
  - A browser yield occurs between every functional helper.
  - Decorative theme hydration is delayed until after the functional layer settles.
- Added `web/themes/ice-dragon/ice-dragon-wallpaper-v22.js`.
  - One canonical delayed wallpaper paint.
  - No `Image()` probe.
  - No second cache-busting asset URL.
- Manifest advanced to v54 and now injects only loader v3 for `/chat`.

## Ownership rule

The Chat mask may present status, theme, layout, controls, and accepted output. It must not monopolize the browser main thread during startup. Heavy decoration is subordinate to an interactive Chat surface.

## Acceptance target

On mobile, `/chat` should become interactive immediately after the base shell paints. Later functional/decorative hydration must not create a prolonged page freeze. Production delivery must show manifest revision 54 before this event is considered live.
