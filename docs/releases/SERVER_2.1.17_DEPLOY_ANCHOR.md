# SERVER 2.1.17 deployment anchor

Release transaction: `SWRLZ-SERVER-2.1.17-FINAL-20260907`

This commit is the production deployment anchor for Server **2.1.17** / Chat **1.3.13**.

Production should be deployed from this commit or any descendant, never from an earlier intermediate commit in the 2.1.17 sequence.

Required source receipts at this anchor:

- `api/index.py` declares Server `2.1.17`.
- automatic request-driven hot-runtime hydration from GitHub `dev` is installed.
- `web/chat_admin_session.js` does not own or repaint the Chat version.
- `dev/web/chat_admin_session.js` does not own or repaint the Chat version.
- `dev/web/chat_enhancements.js` owns Chat version `1.3.13` and hides stale legacy version receipts.
- bundled `main/web/chat_enhancements.js` is aligned to the same Chat `1.3.13` behavior as the hot fallback.

Expected production receipt after deployment and refresh:

`Chat v1.3.13 · Server v2.1.17`

The manual Hot Sync control remains a force-refresh/recovery mechanism; normal Chat/R39 hot updates are expected to self-hydrate from `dev` without button presses.
