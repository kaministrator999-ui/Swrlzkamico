# §E v11.307 — Arcane VR glove orientation correction

## Owner-reported defect
On Meta Quest 2, the gloves in **Blank VR · Arcane Hands** (the Arcane Spell Casting VR starter) appeared upside down.

## Source diagnosis
The canonical editable glove model is authored with fingertips along local **+Y**, palm/sigil on **+Z**, and armored dorsal/backhand on **−Z**. The old controller mount rotated −90° around X, correctly pointing fingertips along WebXR's target-ray **−Z** but putting the palm **up** (+Y) and the armor **down** (−Y).

## Correction
The patch changes only `se279BuildGlove(side)` inside the assembled VR starter:
- Use `poseGroup.rotation.set(-Math.PI/2,Math.PI,0)`, directing fingertips forward (**−Z**), dorsal armor up (**+Y**) and palm down (**−Y**).
- That proper rotation also reverses the local X axis. Therefore the tracked left controller uses the original native source glove and the tracked right controller uses the physically mirrored glove, preserving inward-facing thumbs on both sides. The editable starter model definitions, rig metadata and saved poses themselves remain unchanged.
- Keep existing WebXR controllers, spell origin/aim, trigger/grip animations, thumbstick spell switching, text labels, and all other game/editor layouts unchanged.

## Verification and acceptance
Source checks must confirm the new geometry selection and controller quaternion, existing WebXR loop and Mage Spell Lab path, and unchanged reference starter model construction. The generated build must pass exact manifest SHA-256 and inline script syntax checks. This is a **source-based orientation fix**; actual visual alignment and comfort require the owner's Quest 2 test after confirmed deployment.

## Source files
- `patches/v11_307_arcane_vr_glove_orientation.py`
- `runtime/blank_vr_arcane_hands_v11_279.js` remains historical canonical source; v11.307 modifies the **assembled** runtime through an append-only patch.
- `source-manifest.json` and `scripts/verify_v11_307_release.py` seal exact output.
