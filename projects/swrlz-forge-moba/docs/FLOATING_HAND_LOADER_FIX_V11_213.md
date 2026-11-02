# Floating Hand · Arcane Glove — v11.213 loader repair

## Reproduction and root cause
The v11.212 starter was shipped with two invalid inherited/authoring details. A focused browser test loaded the static Model Atelier deep-link at modeler.html?project=floating-hand-glove, but its generated 39-part hand failed validation before loadProject could commit the scene, leaving the editor at 0 meshes.

1. The native cylinder named Wrist · dark floating sleeve used meshDensity {u:32,v:1}. Native checkPart requires meshDensity only for sphere/loft with v >= 4. The new v11.213 patch removes this unsupported field without removing the cylinder.
2. The new hand cloned the canonical Festival reference project envelope but retained modelAtelier.assemblies: a saved attachment-socket structure targeting legacy character parts. The new hand removed those parts and could not pass atelierValidateAssemblies. The fix deletes just this stale assemblies property before the native scene load.

## Scope and evidence
Fix: patches/v11_213_hand_loader_validation_fix.py, append-only after v11.212. No change to native validator, model parts, sculpt operations, saved user scenes or VR input mappings.

Regression: tests/ui_v11_212_hand_browser.mjs launches Chromium and loads the exact native modeler deep link from the generated HTML. The corrected candidate passed with no console/page error and status active/open/count=39. Browser evidence: GitHub Actions run #41399909619.

Native verifier: scripts/verify_v11_213_release.py ensures the corrected cylinder expression and legacy assembly deletion are present in the generated artifact. Deployed source must be independently sealed, built, and verified.

## Generated candidate SHA-256
- 7,478,295 HTML bytes
- SHA-256: 92785aeafddf55ec02535858b89b2b9e9a6c6f10cfcc149fcd8395ec2b01d8a4
- 245 ordered patch modules; 68 packaged assets

The proof is a Chromium browser test, not a physical Quest 2 acceptance. Owner visual/VR editing checks remain pending.
