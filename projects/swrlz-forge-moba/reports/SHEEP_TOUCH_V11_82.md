# Mobile Sheep Tag controls v11.82

The owner requested building icons arranged like MOBA skills in the bottom right, a left movement joystick, and a building ghost above the finger. This extends the native HUD, placement system and game loop rather than creating a separate controller or saved actor layer.

Five custom inline SVG illustrations decorate the existing native building buttons. Costs, permissions, toggled build mode, raised-route availability and original commands remain native. Round targets form a right-side arc with the house as the largest button; active state has a mint ring and costs sit on small gold badges. A top-left minimap and compact score free the center. Unit actions, selling/upgrades, camera controls and archive actions remain in a closable drawer, using temporary DOM placeholders that restore their original positions on desktop/Stop. The editor footer hides only during mobile Sheep Tag play. Safe-area insets and compact portrait/landscape rules preserve button access.

The left joystick has pointer capture, a dead zone and proportional strength. It supplies transient native move orders from the controlled unit update, preserving regular animation/velocity, live collisions, traffic, rescue and combat. Short swept targets prevent an unexpected long detour; axis sliding permits movement along walls. Unit speed is restored after each update. Release/cancel/lost capture/blur/hidden page/pause/winner/resize/Stop clear ownership and owned movement, leaving no autorun. A held joystick does not create a new clock or teleport the unit. Wisp updates scale time by stick strength, retaining 0.35 m/s maximum drift and the existing return leash; a waiting wolf cannot move.

Native touch aim now uses a viewport-dependent 72–112 px lift, with a dotted line from the touch to the actual snapped footprint. Terrain solving, legality checks, placement tint and release command still use one target. The existing touch pointer set now contains viewport placement fingers only, so the joystick can own an independent first thumb while a nonprimary second thumb aims. Two placement fingers still invalidate the build gesture. Invalid footprints, cancellation and controls under a release cannot create a house. A stationary finger release reuses the last visible world footprint while the camera moves, then native placement revalidates it. The normal camera pass updates the ghost while following/moving; resizing cancels held input. Mouse placement and the full desktop command bar remain unchanged.

Targeted native CPU tests cover full/half analog speed, restored rule speed, wall collision without crossing or detouring, release stopping, slow wisp crawl and leash, waiting wolves, and the existing sanctuary/fog/narrow-lane behavior. Real Chromium touch tests use independent CDP touch IDs to verify movement/release, two-thumb preview/commit equality, 72+ px separation, simultaneous steering and aiming with camera following, exact commit after browser touch events settle, cancel/pause/Stop, accessible drawer controls and original desktop behavior. Responsive checks include 412×915, 915×412, 360×915, 320×915 and 568×320; screenshot review checks the playfield and control layout. These are browser layout checks; physical-device acceptance remains with the owner.

```sh
python scripts/verify_v11_82_release.py --output /tmp/sheep-touch
node --check /tmp/sheep-touch-module.mjs
SWYRL_TEST_HTML=/tmp/sheep-touch/index.html node scripts/test_sheep_touch_cpu_v11_82.mjs
# Serve that package locally, then:
SWYRL_TEST_URL=http://127.0.0.1:8795 node scripts/test_sheep_touch_v11_82.mjs
```

The baseline freezes all 259 preceding patch/runtime files and 49 assets. Release sealing verifies ordered lineage, exact generated HTML, runtime/build/marker consistency, original heroine JSON and unchanged saved map/artwork. The final separate DEPLOY_REQUEST.json identifies the source commit and seal; terminal production success and exact served HTML/SOURCE/all-assets verification are required before reporting the release live.
