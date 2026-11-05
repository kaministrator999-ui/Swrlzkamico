# §E v11.274 — Browser viewport Nerd Stats

A single lightweight, optional, user-toggled debug HUD is available in the Game Engine, Model Atelier, Particle Studio, and Materials & Textures studio browser viewports. Toggle it using the small **▥ Nerd Stats** viewport button or **F3** on desktop. It starts hidden and resets to hidden when switching studios.

The HUD reuses the already-running diagnostics and Three.js renderer. It updates on an 800 ms timer only; it does not create another WebGL canvas, frame callback, or scene mutation.

It displays available approximate browser **requestAnimationFrame** cadence FPS/frame time, real Three.js renderer draw calls, rendered triangle and point counts, GPU *object* counts (textures and geometries; these are not GPU memory bytes), optional Chrome JS heap estimate, canvas dimensions, and active disposable stress-test particle/triangle counts. Do not conflate callback FPS with GPU timing. Model Atelier uses its own renderer's existing stress diagnostics when open.

The existing **Sheep Tag browser live-game Nerd Stats** and the three-page **Quest 2 VR metrics panel (left joystick L3)** are unchanged. This browser editor HUD hides during immersive WebXR. Native emitter limits, gameplay AI, input mappings, multiplayer authority, project files, and particle test geometry are untouched.

Validation: exact rebuilt source hash/bytes; inline JavaScript syntax; manual owner testing of button placement, toggle, and HUD readouts with 100, 118,600 and high particle loads in Particle Studio; verify no controls or view navigation are obstructed. VR metrics still require physical Quest 2 acceptance.
