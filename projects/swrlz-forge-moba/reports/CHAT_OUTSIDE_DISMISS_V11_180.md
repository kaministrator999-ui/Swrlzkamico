# §E v11.180 Chat outside-tap slide-away

Owner intent: selecting anywhere outside Chat closes the side panel with an offscreen slide and keeps the editor interaction intact.

Implementation: scroll-free side-panel translation (translate3d) with opacity transition and reduced-motion override. Click and pointerdown listeners are installed once in the existing native Chat mount. They exclude all Chat descendants and the Chat toggle. Cross-origin iframe pointer events are contained in the iframe and are not misclassified as outside. Main/secondary mouse interactions and multipointer corner cases are guarded.

Lifecycle: opening clears any pending close timer and stale animation frame, shows the existing iframe, restores accessibility and marks the panel visible; closing reuses revoke() of the temporary authorized native editor lease, immediately removes interaction/focus, animates, and hides without unmounting iframe. No synthetic pointer events or preventDefault. Outside close does not steal focus from the editor; explicit close restores focus to Chat toggle.

Focused test: projects/swrlz-forge-moba/tests/test_v11_180_chat_outside_dismiss.cjs. Source rebuild and integrity: projects/swrlz-forge-moba/scripts/verify_v11_180_release.py.

Exact source: 212 patches / 68 assets / 7,066,690 HTML bytes / sha256 befd3604d7614483eff73ef958c9652204ba3aeed4533f01a4b6204b9212ea60. Live-host status is established independently by the final deployment Actions run.
