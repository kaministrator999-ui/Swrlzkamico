# §E v11.435 — Transform gizmos in the normal Model VR Grab state

## Reproduction and root cause
A native selection in immersive Model Studio auto-transitions from Inspect into Grab (v11.390), but the existing v11.372/v11.431 gizmo frame and ray contact only operated in Move, Rotate and Scale. This meant the normal first editing state hid the axis handles completely. The mobile viewport had independently working gizmos.

## Smallest compatible repair
The new v11.435 scoped VR helper reuses the v11.431 XYZ Move handle meshes, pivot frame, pointer tolerance and menu-priority picker while the active mode is Grab. It momentarily maps the helper's mode to Move solely during gizmo frame/picker calls, restores Grab synchronously and does not change the scene model or toolbar.

When Grip starts on the displayed X/Y/Z arrow, the v11.390 gesture path begins a native Move transaction with that axis, existing pose math, native constrain, preview, Finish/Cancel and Undo. Gripping elsewhere retains the original free-form Grab. Explicit Move, Rotate and uniform Scale modes behave as before. No new WebXR render loop, materials stored in project data, replacement selection store, model-root move or head-following UI.

## Verification and limits
- GitHub measurement: [successful run 43360329749](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43360329749); all 412 ordered patches reconstructed, both source syntax checks passed, real Three.js r169 five-group VR regression passed.
- Source artifact: 9,933,817 HTML bytes, SHA-256 `19d7464f80b572d6ace882ccac4a93cd8f9d96a370b13661d1b3c4ae9c7cdc84`.
- Regression covers Grab and explicit mode visibility; X/Y/Z controller ray contact; native constrained Move update without unintended rotation or scale; no-handle free-form Grab; menu priority; hidden selection state.
- Preservation: native mobile gesture and camera settings, saved character geometry/UV, mesh list, controller profiles and independent VR world-space menus remain unchanged.
- Physical Quest 2 comfort, actual controller feel, headset rendering and long-session performance need owner acceptance; automated Three.js checks do not prove those.

## Publication receipt

**Published / validated:** [sealed source commit 619dde2](https://github.com/kaministrator999-ui/Swrlzkamico/commit/619dde28a0b7b915f02832a0e8146a29358e7d0c); [full successful release verification 43361003457](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43361003457); [separate deployment request e5c9506](https://github.com/kaministrator999-ui/Swrlzkamico/commit/e5c9506666f5277a481db08f56619a876da13bd7); [successful Hugging Face upload 43361224731](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43361224731). The CI upload step confirmed publication to `kamiloki/swrlz-forge-moba`. Physical Quest 2 verification remains the owner's acceptance test; standalone public SOURCE.json was not separately fetched.

