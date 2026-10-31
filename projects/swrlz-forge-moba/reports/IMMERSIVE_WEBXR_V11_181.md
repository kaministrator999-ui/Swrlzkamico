# §E v11.181 — immersive WebXR doorway and native renderer integration

**Scope:** First end-to-end immersive VR path in the **main §E scene**. The ordinary Quest 2 browser's 2D ray-cursor is different from WebXR controller target ray poses; this change makes a real immersive WebXR session available behind an explicit UI control. This is not the full VR design Studio mapping/Model Atelier tool integration.

**Renderer source of truth:** base HTML uses Three.js 0.169.0 and main renderer new THREE.WebGLRenderer({canvas: #viewport}); main tick previously used requestAnimationFrame(tick) plus native updates, render throttling and resize. A distinct Model Atelier renderer exists with its own loop. This release replaces **only the main tick's scheduling** with renderer.setAnimationLoop(tick) (single driver in 2D and XR), stops WebGL canvas resize during XR presentation and renders each headset frame. Existing actor/game update code remains inside tick.

**Interaction:** WebXR immersive-vr local-floor session from explicit user gesture, headset view, two native controller target rays, raycast toward native actor roots, select via the existing selectActor only while editing, non-destructive hover indicator, in-scene EXIT VR sign and Quest-native exit. Supports session end event, cleanup, and restoration of saved editor camera, orbit state and transform helper. No separately created Three renderer or simulated browser pointer events.

**Deferrals:** Model Atelier renderer/session, sculpt brushes, actual grab/move/two-handed transformations and undo, locomotion, in-VR Chat/menu UI, account sync of controller settings and live Quest 2 usability acceptance. VR Controller Studio session diagnostics are connected, but its configurable mappings are not wired to actions here. An active Model Atelier blocks entry into the wrong scene.

**Evidence:** Branch-specific candidate CI and exact package/asset verifier; offline mocked WebXR lifecycle and controller object cleanup; previous 212 source patches preserved, new patch appended as #213, all 68 assets retained. The static HF deployment and host/device acceptance must be evidenced separately. Exact HTML 7,079,620 bytes, SHA-256 fb0732cc05fb4a4e5c5a8e114ffba9518c88be42a220c5d8908090262c20fd77.

**Risk note:** WebXR capabilities, session permissions and real physical controller profiles vary by headset/browser version. Only on-headset testing validates stereoscopy, spatial ray alignment, frame performance, exit accessibility and user comfort; mocked Node tests never establish those.
