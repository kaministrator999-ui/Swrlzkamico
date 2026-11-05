# §E v11.279 — Blank VR · Arcane Hands

## Native starter entry points
- **Starter Games → Blank VR · Arcane Hands**: `?project=blank-vr-hands`; an editable blank world with native ground but **no scenery, pawn, enemies or AI**.
- **Starter Models → Floating Hand · Arcane Glove (Left)**: `?project=arcane-glove-left`; separate native editable left-hand model project.
- Existing **Floating Hand · Arcane Glove** (`?project=floating-hand-glove`) remains the unchanged original right-hand reference and starter.

## Mirroring, skeletal animation and VR ownership
- The left model is generated from the canonical original, not rebuilt from primitives or a screenshot. Model parts, topology vertices, face winding, local transforms, mesh-group membership, finger/thumb anatomy, bone pivots and skinned joint weighting are reflected to the opposite hand.
- The same native 17-bone hierarchy is retained. Stored timeline keys and gesture presets use mirrored Y/Z Euler rotation signs, and thumb/wrist wave/poses are available on both sides in Model Atelier.
- The blank game attaches the original glove mesh to whichever Quest controller reports **right** handedness, and the mirrored model to **left**, using the existing WebXR controller objects. Missing/disconnected controllers do not show floating hands.
- On each side independently, **grip** bends the hand toward grasp/full fist and **trigger** bends toward precision pinch. Idle is the existing relaxed hand pose. The headset/controller pose drives hand location; this does **not** pretend to implement optical hand tracking, individual-finger capacitive sensing, or physics collisions.
- The renderer runs on the **existing XR frame loop**. Compatible source model meshes are combined into material batches, not a second renderer, and resources are cleaned up when leaving VR or changing projects. Other games, existing ray pointers, menu bindings and saved scenes retain their prior control paths.

## Source and verification
- Source runtime: `runtime/blank_vr_arcane_hands_v11_279.js`.
- Append-only patch: `patches/v11_279_blank_vr_arcane_hands.py`.
- Release verifier: `scripts/verify_v11_279_release.py`.
- Manifest: `§wyrl§ Engine v11.279`, **310 patches**, **69 assets**.
- Rebuilt HTML: **8,125,233 bytes**, SHA-256 `678667a1360fc495366cda34d0e7873042c6763baf92e1a6f766ae2de194f0ed` (GitHub Actions targeted source build + inline JS syntax succeeded).
- The owner must still assess controller offset/orientation, frame rate and thumb/gesture fidelity on physical Meta Quest 2. A successful source build is not a claim of visual acceptance.
