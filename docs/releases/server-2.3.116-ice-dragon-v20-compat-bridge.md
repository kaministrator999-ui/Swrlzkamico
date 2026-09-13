# Server Runtime 2.3.116 / Web Chat 1.4.99 — Ice Dragon v20 compatibility bridge

Live evidence showed the runtime manifest source lagging at manifest 31, which still loads wallpaper v20 even after manifest 32/v21 were committed. To make both stale and current manifest paths converge, v20 now directly paints the same exact repository-root PNG used by v21, with centered cover geometry and no binary live-source bridge. This preserves the explicit failure evidence from the 503 binary proxy and removes stale-manifest dependence from browser acceptance. Runtime-hot; no stable deployment required.
