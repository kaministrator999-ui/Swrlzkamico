# Server 2.3.83 — Ice Dragon clean source/cache reset

Status: source implementation complete; browser acceptance pending.

Affected modules:
- Server Runtime 2.3.83
- Web Chat 1.4.75
- Web Frontend 1.0.2

Deployment: NONE
Restart: NONE

What changed:
- Removed the browser-generated 4320x7680 WebP promotion path because it enlarged the 864x1536 source without adding detail and could preserve a visually poor derivative.
- Advanced Ice Dragon persistent Cache Storage and local-preview keys to generation v2 so earlier wallpaper cache entries are ignored rather than reused.
- Added Ice Dragon loader v17, which uses the verified 864x1536 source tier directly, persists that source, and seeds a fresh v2 local preview for subsequent frontend-first refreshes.
- Advanced the runtime page manifest to v14 and the frontend boot contract to v3.

Why:
User-visible wallpaper quality remained poor after cache/8K promotion work. The new event removes the misleading upscaled tier and forces a clean source generation so testing occurs against the actual source rather than stale derived cache content.

Verification:
- Repository source/authority verification required after commit.
- Live runtime manifest/loader verification required.
- Final browser visual acceptance remains user-visible.
