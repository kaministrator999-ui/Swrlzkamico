# Unreal Engine Study → SWRLZ Forge v3

**Purpose:** record the Unreal Engine editor concepts studied for the Forge v3 improvement pass, the design principle extracted from each, and how Forge adapts it to a browser-native engine.

**Reference baseline:** Epic Games Unreal Engine 5.8 documentation.

---

## 1. Level Editor composition

Epic's Level Editor centers the workflow around a Main Toolbar, Viewport Toolbar, Level Viewport, hierarchical Outliner, Details panel, Content Drawer/Browser, and Bottom Toolbar/Output Log.

Reference:
- https://dev.epicgames.com/documentation/unreal-engine/unreal-editor-interface
- https://dev.epicgames.com/documentation/en-us/unreal-engine/unreal-engine-interface-and-navigation

### Forge adaptation

Forge v3 now mirrors the *responsibility split*, not Unreal's implementation:

```text
Top toolbar
  -> transform mode / space / snap / camera / view / play

Viewport
  -> direct spatial editing + selection feedback

World Outliner
  -> hierarchy / folders / search / visibility / selection

Details
  -> Transform / Components / Gameplay / Physics

Content Drawer
  -> asset/prefab discovery + Output Log

Bottom/status surfaces
  -> engine state / validation / transaction feedback
```

This keeps the editor understandable as it grows instead of accumulating controls directly over the viewport.

---

## 2. Transform spaces, snapping, and viewport modes

Unreal supports World and Local transform spaces, snapping for translation/rotation/scale, Perspective and orthographic views, and multiple visualization modes.

References:
- https://dev.epicgames.com/documentation/en-us/unreal-engine/coordinate-system-and-spaces-in-unreal-engine
- https://dev.epicgames.com/documentation/en-us/unreal-engine/using-editor-viewports-in-unreal-engine

### Forge adaptation

v3 adds:

- World / Local transform-space toggle;
- translation snap;
- rotation snap;
- scale snap;
- Perspective / Top / Front / Right views;
- Lit / Unlit / Wireframe display modes;
- editor camera-speed selection;
- selection bounds.

**Principle:** camera and transform controls are authoring tools, not gameplay controls. The default editor remains precision-oriented rather than becoming an FPS-style builder.

---

## 3. Actor + Component composition

In Unreal, Actors are containers whose reusable functionality is composed from Components. Actor Components model abstract behavior, Scene Components add transforms/hierarchy, and Primitive Components add geometric/collision representation.

References:
- https://dev.epicgames.com/documentation/unreal-engine/components-in-unreal-engine?application_version=5.8
- https://dev.epicgames.com/documentation/unreal-engine/actors-in-unreal-engine?application_version=5.8

### Forge adaptation

Forge v3 begins separating actor identity from reusable behavior through component metadata.

Current reusable components:

```text
RotatingMovement
BobMovement
PhysicsBody
LaunchPad
```

The editor can add/remove components through Details and runtime systems execute them during simulation/play.

**Direction:** continue moving behavior out of giant actor-type conditionals and into registered components with lifecycle hooks:

```text
onCreate
onEditorUpdate
onBeginPlay
onTick
onCollision
onDestroy
serialize
```

This is the architectural path toward a real engine rather than an increasingly large MOBA-specific script.

---

## 4. Blueprints as reusable classes/prefabs

Unreal Blueprint Classes combine Components, variables, node graphs, events, and Construction Scripts. Editing a Blueprint Class updates its instances, and Epic explicitly describes Blueprints as a powerful prefab-like class system.

References:
- https://dev.epicgames.com/documentation/en-us/unreal-engine/introduction-to-blueprints-visual-scripting-in-unreal-engine
- https://dev.epicgames.com/documentation/en-us/unreal-engine/technical-guide-for-blueprints-visual-scripting-in-unreal-engine
- https://dev.epicgames.com/documentation/en-us/unreal-engine/construction-script-in-unreal-engine

### Forge adaptation

v3 does not pretend to have a complete Blueprint compiler yet. Instead, it establishes the correct lower rung:

1. actor;
2. components;
3. reusable prefab identity;
4. editor-time behavior;
5. runtime behavior;
6. serialized component data.

The default scene now contains Blueprint-like reusable examples such as:

- `BP_JumpPad`;
- `BP_Rotator`;
- physics-enabled prop.

### Next rung

A future visual graph should compile into the same component/event runtime rather than creating a second behavior system.

Target:

```text
Blueprint asset
├── Components
├── Variables
├── Construction graph
└── Event graph
        ↓ compile
Forge behavior IR
        ↓
same runtime used by authored scripts + agents
```

---

## 5. PIE / SIE and safe editor-world separation

Unreal distinguishes Play In Editor (PIE) from Simulate In Editor (SIE). PIE provides player control. SIE runs game logic while preserving editor tools. Unreal duplicates the editor world for preview, and selected simulation changes can be deliberately kept.

References:
- https://dev.epicgames.com/documentation/unreal-engine/playing-and-simulating-in-unreal-engine
- https://dev.epicgames.com/documentation/unreal-engine/ineditor-testing-play-and-simulate-in-unreal-engine

### Forge adaptation

v3 adds:

- Play In Editor;
- Simulate In Editor;
- Pause / Resume;
- Keep Simulation Changes;
- Play From Here;
- explicit editor-state snapshot/restore.

This is particularly important for Forge's collaboration model:

```text
authoritative baked editor world
        ↓
simulation/play copy
        ↓
experiment
        ↓
discard OR Keep Simulation Changes
```

That same boundary can later protect multiplayer ghost edits and AI-agent proposals.

---

## 6. Outliner, Details, Content Browser, and Output Log

Unreal's Outliner is searchable/filterable and hierarchical; Details reflects selected Actor/components; Content Browser owns assets; Output Log belongs to the editor/tooling surface.

References:
- https://dev.epicgames.com/documentation/unreal-engine/outliner-in-unreal-engine
- https://dev.epicgames.com/documentation/en-us/unreal-engine/content-browser-in-unreal-engine
- https://dev.epicgames.com/documentation/unreal-engine/unreal-editor-interface

### Forge adaptation

v3 adds:

- Outliner search;
- folders;
- actor visibility;
- synchronized viewport/outliner selection;
- collapsible Details sections;
- component management;
- Content Drawer asset search;
- Output Log;
- Build Validation.

**Principle:** project assets, scene instances, selected-object properties, and diagnostics are different data domains and should remain visibly separate.

---

## 7. Editor automation → future §wyrlz orb tunnel

Unreal exposes editor automation via Blueprints and Python. Epic's editor scripting documentation explicitly supports automating content placement/layout, asset pipelines, reusable tools, and custom editor UIs.

References:
- https://dev.epicgames.com/documentation/unreal-engine/scripting-and-automating-the-unreal-editor
- https://dev.epicgames.com/documentation/unreal-engine/scripting-the-unreal-editor-using-blueprints

### Forge adaptation

Forge v3 now exposes a bounded browser command surface:

```javascript
window.SWRLZ_FORGE_AGENT
```

Current operations include:

- inspect scene;
- list actors;
- spawn actor/prefab;
- set transform;
- add component;
- bake ghost changes;
- validate map.

This implements the important architectural idea from the user's collaboration concept:

```text
AI inference
   ↓
structured editor commands
   ↓
visible orb / proposal workspace
   ↓
ghost changes
   ↓
validation
   ↓
authorized Bake
```

The AI should command editor semantics, not imitate mouse movement.

---

## 8. What Forge intentionally does not copy

Forge is not attempting to clone Unreal's source code, UI artwork, proprietary systems, or feature count.

The useful target is **workflow architecture**:

- clear ownership of editor surfaces;
- composable behavior;
- safe edit/play separation;
- reusable assets/classes;
- deterministic transactions;
- inspectable automation;
- scalable scene organization.

Forge remains browser-native, lightweight, collaborative-first, and designed around ghost → Bake.

---

## 9. Next high-value Unreal-derived rungs

Recommended future order:

1. **Real asset registry/import pipeline**
   - GLB/GLTF models;
   - textures/material assets;
   - stable asset IDs;
   - drag/drop from Content Drawer.

2. **Prefab / Blueprint Class assets**
   - class defaults;
   - instance overrides;
   - Construction Script equivalent;
   - propagate class edits to instances.

3. **Visual behavior graph**
   - typed pins;
   - events;
   - variables;
   - functions/macros;
   - compile to shared behavior IR.

4. **Component hierarchy**
   - root SceneComponent;
   - child transforms;
   - attach/detach;
   - cameras/lights/colliders as components.

5. **Physics world**
   - broadphase;
   - rigid bodies;
   - collision shapes;
   - triggers;
   - constraints;
   - deterministic editor simulation boundary.

6. **Project/level asset model**
   - multiple maps;
   - scenes as assets;
   - prefab assets;
   - autosave/recovery;
   - revision history.

7. **Collaborative transaction layer**
   - per-user orb/presence;
   - independent ghost workspaces;
   - conflict visualization;
   - Bake as revision commit;
   - revertable scene transactions.

8. **Agent editor protocol**
   - schema-versioned command API;
   - read/query tools;
   - proposal transactions;
   - validation/test receipts;
   - permissioned Bake.

---

## Bottom line

The v3 pass uses Unreal Engine as a **design teacher**, not a skin to copy. The most important transplant is the separation of concerns:

```text
Assets
→ Actors
→ Components
→ Editor transactions
→ Simulation copy
→ Runtime
→ Automation API
```

That structure gives SWRLZ Forge room to evolve from a clever single-file MOBA editor into a genuine browser-native game creation environment without sacrificing the ghost → Bake collaboration model.
