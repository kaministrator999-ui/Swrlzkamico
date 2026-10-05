---
title: SWRLZ Forge Editor v5
emoji: 🌀
colorFrom: purple
colorTo: blue
sdk: static
app_file: index.html
fullWidth: true
header: mini
short_description: Browser game editor with project templates and agent tools.
---

# SWRLZ Forge · Editor v5

A browser-native 3D game editor and runtime.

v5 separates game examples from the engine itself. Forge now opens into a neutral **Starter World** project, while the original three-lane MOBA and a new **Dragon's Den** world are independent project templates that can be created, edited, saved, loaded, simulated, played, and exported.

### Built-in project templates

- **Starter World** — default general-purpose Forge sandbox.
- **MOBA Arena** — the original MOBA moved into an example-project lane.
- **Dragon's Den** — an arcane collaborative LALM world with dragon avatars, portals, council architecture, memory/inference anchors, and agent-role metadata.

The project JSON contract carries project identity, scene actors, paths, and editor state. The editor agent bridge is available at `window.SWRLZ_FORGE_AGENT`.

Source repository: `kaministrator999-ui/Swrlzkamico`  
Legacy project path: `projects/swrlz-forge-moba/`
