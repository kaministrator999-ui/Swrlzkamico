# §E v11.476 — Account-first startup, last workspace and Page Down

## Startup behavior

§E displays its account gate over the initial native editor. The existing §Chat
Google identity bridge is warmed without exposing its tokens to the engine.

Order: verified Google session → cloud/local project list → a checked default project
(if one exists) → otherwise last successfully loaded saved project → its native studio
and Model Studio camera position/projection → working editor.

The default checkbox uses the existing `SWYRL_ENGINE_SAVED_DEFAULT` owner and remains
independent of recent history. Session reference stores only source, saved project ID,
studio and camera geometry in localStorage; no Google credentials or project bytes.
The existing loader and dirty-state/revision conflict recovery remain authoritative.

The local fallback remains available when §Chat cannot be reached. No online service
or sign-in is required to open an already downloaded project. A failed local/cloud
restore does not silently overwrite the active scene.

## Page Down / SIGNAL LOST

When §Chat never answers its account handshake, the §E static page displays a
full-screen animated SIGNAL LOST screen. It includes scanlines, independently moving
portal geometry, glitch text and energy rings with a reduced-motion fallback.
There are two real controls: Reconnect to §C and Continue in §E offline. The latter
opens the local project where available or the existing local workspace.

No claim is made that the §C server can replace Hugging Face's own
`503 Service Unavailable` page while its application is not running.
The outage screen is hosted by the independent §E static Space.

## Acceptance gates

- 453-patch deterministic source build with exact HTML SHA-256 receipt
- Native startup and account bridge syntax/static invariants
- Browser phone and desktop-site touch layouts: entry gate, offline full-screen
  viewport coverage, reduced-motion compliance, real buttons and offline exit
- Original modeling, toolbars, projects, Undo and XR modes remain unchanged
- Real Google OAuth, cross-device cloud saves, and physical Moto / Quest acceptance
  remain owner-device checks and are not implied by a mocked browser test
