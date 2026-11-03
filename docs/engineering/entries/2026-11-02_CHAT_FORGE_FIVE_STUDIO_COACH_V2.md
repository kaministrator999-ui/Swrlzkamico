# §C ⇄ §E five-studio coaching · v2 candidate (2026-11-02)

**Scope:** Chat/LALM instructional context only; §E engine and native operation
permissions are unchanged. Source inspected on \`main\`: §E \`v11.231\`,
\`projects/swrlz-forge-moba/source-manifest.json\` (last patch
\`v11_231_sheep_house_camera_fit.py\`). This is **source information**, not proof
that a device or hosted runtime has that version.

## Canonical integration

The previously accepted Chat-side source hook remains in
\`hf_space/brain_forge.py\`, \`hf_space/lfm2_700m_engine.py\` and
\`hf_space/qwen_coder_engine.py\`. These continue to call the one existing
\`hf_space/forge_modeling_lessons.py::select_modeling_lesson\` selector.

The v2 selector extends that single owner rather than modifying model weights,
duplicating a Chat router, increasing the existing 1150-character context
limit, changing native schemas or adding another editor runtime.

| Topic | Canonical §E source and invariant |
| --- | --- |
| Game design / GUI | \`runtime/game_gui_menu_subtab_v11_228.js\`; \`currentProject.guiStudio\` is game UI, with editor-preview visibility separate from Show in Play |
| Model Atelier | \`runtime/model_atelier.js\`, \`model_atelier_components_v11_75.js\` and \`model_atelier_mesh_groups_v11_74.js\`; model parts, sculpt vertices and groups are not scene actors |
| Materials/textures | \`runtime/material_texture_core_v11_225.js\`; \`currentProject.materialStudio\` has up to 12 materials, editor paints and actor assignments; no direct individual Model Atelier part assignment |
| Rigging/animation | \`runtime/model_atelier_skeletal_core_v11_220.js\`, \`wolf_rig_motions_v11_224.js\`, \`sheep_tag_wolf_animation_v11_224.js\`; glove 17-bone versus wolf 14-bone, scene game pivot motion versus skinned authoring and sheep transform preview |
| Particles/VFX | \`runtime/particle_studio_core_v11_224.js\`; \`currentProject.particleStudio\` has bounded emitters, native preview/attachment and ephemeral GPU resources |
| Combined tasks | Source-anchored **plan → model → material → animation → particle → preview/save** vocabulary with no implied cross-editor transfer or automatic application |

## Guarded behavior

- The selector responds only to explicit §E/Forge context or a recognized
  connected-editor workspace **and** a related topic. Unrelated and generic
  prompts consume no extra model context.
- It provides one bounded topic lesson, not five full documents per turn.
  Inputs from native context remain hints, never authorization.
- Only the existing validated native operations can execute, under the
  existing trusted host lease, user approval, ID checks and host receipts.
  \`material.create\`, \`particle.create\`, \`rig.pose\`, direct keyframe
  and sculpt writes are **not** new Chat capabilities.
- Unsupported JSON planner requests must return
  \`disposition=clarify\` with no operations. No injected JavaScript,
  arbitrary scripts or implicit publish.
- Saved model/project data, generated materials, animation previews, particle
  previews and game simulation each have different ownership/receipts.

## Evidence and next acceptance

Local, isolated Python syntax compilation and **10/10** v2 selector checks passed
for game, modeling, materials, rig, animation, particles, cross-studio routing,
context relevance, the 1150-character bound and planner refusal. The same
test source is included as \`hf_space/test_forge_studio_coach_v2.py\`.

The original v1 integration hooks were not changed in this candidate.
The v1 Chat regression suite, hosted source checks, live 700M/Qwen outputs,
actual typed-host operations, GitHub CI, deployment and owner's Moto/Quest tests
were **not** executed by this v2 patch. A source commit is not a trained model
or live acceptance.

**Suggested owner evaluation after governed Chat release:** ask §C to design a
Sheep Tag building, explain the correct Model Atelier starter, create an
appropriate material in the Materials tab, identify the clip/rig pathway,
propose a construction particle effect and explicitly distinguish the steps
it merely described from any real native edits. A wrong engine capability claim
should be captured as an append-only lesson failure.
