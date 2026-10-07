---
title: §wyrl§ Engine v7.2
emoji: 🐉
colorFrom: purple
colorTo: blue
sdk: static
app_file: index.html
fullWidth: true
header: mini
short_description: Browser world engine maker with grouping and first-person.
---

# §wyrl§ Engine · Maker v7.2

A browser-native 3D world/game engine maker built around editable projects, first-person play, ghost → Bake authoring, hierarchical object groups, and a structured LALM/agent control surface.

v7.2 makes **Glitch Dragon Den — Fracture Forge** structurally identical to the regular Dragon Den by building the regular Den first and applying the glitch identity in-place.

v5.5 fixes look-stick horizontal direction so right means right by default and introduces Dragon anatomy v2: articulated low-poly wings, segmented neck/tail, four-joint legs, claws, horns, teeth, improved head silhouette, and less blocky shading.

v5.6 adds reusable dragon foot grounding, explicit rear paws/heels/claws, and a more detailed multi-finger wing membrane system.

v5.7 replaces single-point dragon foot contact with multi-sample sole raycasts, tucks dragon teeth back inside the mouth, and adds a top-bar camera speed slider for editor rotate/pan/scroll zoom.

## Default starter: Dragon's Den — Seed Chamber

The default visitor/player is now a luminous Wisp-style spirit: glowing core, additive aura, orbiting motes, trailing wisps, team glow, and subtle hover animation. It is specific to Dragon's Den; the other project templates retain their existing pawn models.

v5.3 improves the Den as an immersive cavern rather than a miniature open map:

- rocky cavern floor instead of grass/river presentation
- grouped stone floor assemblies
- grouped cavern shell
- grouped vaulted roof that stays out of the editor view and appears in runtime
- larger structural pillars and clearer room zoning
- Wake Nook, Council Chamber, Creator Alcove, Throne Side, Dragon Perch
- Portal Hall, Memory Vault, and Inference Core expansion exits
- first-person twin-stick mobile play from v5.2

## Hierarchical object grouping

Static/editor objects can be multi-selected and turned into one transformable group. Groups can be nested, saved, loaded, duplicated, moved, rotated, scaled, and ungrouped while preserving child transforms.

Dynamic gameplay/physics actors remain independent for runtime correctness.

Source repository: `kaministrator999-ui/Swrlzkamico`  
Legacy source path: `projects/swrlz-forge-moba/`
