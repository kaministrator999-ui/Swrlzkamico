# §E v11.280 — Mage Spell Lab · Starter Particles and VR Arcane Gloves

## Native library
The already-existing **Starter Particles** tab and Particle Studio library sidebar expose the full **registered native preset catalog**:
- Original 10 built-in presets: Arcane motes, Flame, Smoke, Sparks, Snowfall, Rain, Healing wisps, Building magic, Portal shimmer, Confetti burst.
- Four existing Astral Vortex presets: Violet arm, Cyan arm, Radiant core, Flying sparks. The pre-existing four-emitter Astral Vortex starter remains available unchanged.
- Eighteen new editable Mage spell presets: **Ember Bolt, Inferno Breath, Frost Nova, Ice Lance, Storm Arc, Chain Storm, Arcane Missile, Runic Halo, Healing Bloom, Radiant Nova, Shadow Pulse, Void Orb, Gravity Well, Stone Burst, Meteor Rain, Wind Cyclone, Crystal Bloom, Thunder Ring**.

All 32 are normal `SE223_PRESETS` choices in the existing particle authoring schema, with standard editable rate, burst, spread, speed, color, life, gravity, drag, size, curves, undo, save and JSON export. Distinct motion for runic rings, spirals and lightning uses the same Particle Studio render loop, vertex buffers and particle budget.

**One-click Mage Spell Pack** adds eight complementary emitters as one undoable validated transaction, without clearing or overwriting existing emitters. Existing cap is 12 active authored emitters per project; load one at a time to test the whole catalog. Project library and built-in Particle Studio UI are still usable independently.

## Blank VR · Arcane Hands testing
- Existing `?project=blank-vr-hands` creates a native blank editable level. No game AI or extra pawn.
- The **left** and **right** gloves are the native rigged source and mirrored glove from v11.279.
- **Left trigger / right trigger:** cast the spell selected for that hand on a new press. Both sides are independently equipped and do not interfere with grip-driven glove gestures.
- **Left or right thumbstick click:** cycle that hand's spell through the quick-cast shortlist. This is scoped only to the blank VR hands project; Sheep Tag's left-stick Nerd Stats toggle and existing maps keep prior input bindings.
- The Particle Library also has **Left glove** and **Right glove** selectors, so any original or new native preset can be equipped before putting on the Quest. Settings persist locally in that browser.
- Small tracked labels display the equipped spell near each controller.

Casting uses the same preset data and native point cloud/materials as Particle Studio, but creates transient, bounded visual bursts tied to the controller's actual XR target ray. Maximum six effects are live at once; meshes and textures are disposed on leaving VR. The existing renderer's XR animation callback remains the only casting frame driver.

**Not yet implemented:** combat damage/hit detection, enemies, mana cost, spell cooldown trees, individual-finger optical tracking, audio effects, cooperative gameplay, or spell network replication. These can be added after the user's on-device tests.

## Source governance
- `runtime/mage_spell_lab_v11_280.js` and `.css`
- `patches/v11_280_mage_spell_lab.py`
- `scripts/verify_v11_280_release.py`
- 311 source patches, 69 packaged assets.
- Exact generated artifact bytes and SHA are stored in `source-manifest.json` and matched by the release verifier.

## Owner Quest 2 acceptance
1. Open `?project=blank-vr-hands` and enter Quest WebXR.
2. Confirm both gloves follow the correct controllers and gestures still animate.
3. Cast both hands at once, then switch left/right spells independently with thumbstick clicks.
4. Open **Projects → Starter Particles** from the normal browser view, add a new spell emitter or eight-pack, inspect the individual effects in Particle Studio, and confirm saved project/export behavior.
5. Compare render statistics before and after casting to detect VFX overhead on Quest 2.
