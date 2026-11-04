# §E v11.248 — Astral Vortex starter particle

## Owner request
Implement the purple/cyan particle-editor look and the swirling energy effect from the §E concept image as real editor tools, not a screenshot. Add a **Starter Particles** category next to Starter Games and Starter Models.

## Authored assets
**Astral Vortex** loads four native Particle Studio emitters in one undoable project transaction: violet spiral, cyan spiral, radiant center, and sparks. Each emitter uses the existing `swyrl-particle-studio-v1` schema and stays editable (rate, lifetime, size, colors, blend, location). Import/export, Undo/Redo, project persistence, preview, and Play remain owned by the existing Particle Studio.

The underlying model uses the existing render loop and THREE.Points budget (96 points per emitter, 576 total); a shared 64×64 generated radial glow texture is assigned once per emitter, with no extra renderer, animation loop, physics body, saved-world actor, or network message.

The isolated Particle Studio authoring chamber previews all four layers when a vortex component is selected, without changing the saved scene attachment position. The regular game renderer uses ordinary project particle flow.

## UI
- `Projects → Starter Projects → Starter Particles`: **Astral Vortex** card and Load.
- `Particle Studio`: purple/cyan chrome, desktop starter library plus project emitter list, existing inspector on the right, and top toolbar actions connected to real native controls.
- Phones/Quest browser-size view: Starter Particles toggles a bottom sheet; the real inspector remains accessible and its original Collapse control is preserved.

## Acceptance on owner devices
Open the Space on Moto G Power and Quest 2. Load from Projects, confirm four editable emitters and animated purple/cyan spiral in Particle Studio, check mobile drawer/inspector switching, minimize and restore controls, then return to Game Engine and verify no editor camera leak or changes to Sheep Tag world actors. Save/reload and test Undo/Redo on the new starter. Physical acceptance is owner-operated.
