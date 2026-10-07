# §wyrl§ Engine Roadmap

Canonical lane: §E / §wyrl§ Engine

This roadmap is mandatory release lineage for every governed §E GitHub update. Root §tart_§E.md defines the deployment contract.

## Release lineage

- v5.2 — first-person / twin-stick foundation; verified historical checkpoint.
- v5.3 — hierarchical groups + immersive Den; marker V5_3_GROUPS_IMMERSIVE_DEN.
- v5.4 — procedural Wisp visitor; marker V5_4_WISP_AVATAR.
- v5.5 — natural camera look + Dragon anatomy v2; marker V5_5_DRAGONS_NATURAL_LOOK.
- v5.6 — articulated wings + reusable surface foot contact; marker V5_6_DRAGON_GROUND_CONTACT.
- v5.7 — multi-sample sole contact + editor camera speed; marker V5_7_PRECISION_CONTACT_CAMERA_SPEED.
- v5.8 — Wisp alpha / foot-support iteration; patch retained in canonical chain.
- v5.9 — soft Wisp, planted feet, visible Undo/Redo/history; marker V5_9_WISP_SOFT_CONTACT_HISTORY.
- v6.0 — researched Glitch Dragon Den — Fracture Forge; marker V6_0_GLITCH_DRAGON_DEN.
- v6.1 — exposes Fracture Forge in Projects hub, fixes project routing, clarifies Seed Chamber version presentation; marker V6_1_GLITCH_DEN_STARTER.
- v7.0 — Glitch Den now builds directly from the regular Dragon Den source-of-truth layout, then applies its glitch theme in-place; marker V7_0_FRACTURE_FORGE_ASCENDANT.

## v6.0 — Glitch Dragon Den / Fracture Forge

v6.0 preserves the original Dragon's Den — Seed Chamber and adds a second glitch-dragons-den project. Major additions: oversized enclosed fractured megacavern; grouped shell, floor, buttresses and forge lighting; human-scale central forge and traversal circuit; chromatic fracture crystal veins, rune pylons, gates and perches; §wyrl§ Glitch Dragon, Frost Forge Dragon and Ember Glitch Dragon; agent surface advanced to v4.0.

Source authority:
- artifact: swyrl_engine_v6_0.html
- bytes: 170965
- SHA-256: 747076cbbd43b881887392bcf69a7721905564ffc155e3ab946831ed3a640569
- marker: SWYRL_ENGINE_DEPLOY_MARKER: V6_0_GLITCH_DRAGON_DEN
- verified v6.0 deployment source commit before governance sync: f02752e742d6a1656e5b7a81f6185a99a7d637bc
- deployment run #23: success


## v6.1 — Glitch Den starter exposure

v6.1 repairs the v6.0 reachability defect: the researched Fracture Forge existed in generated code but the Projects hub did not expose it and the project-creation router did not select it. The release adds the dedicated Glitch Dragon Den — Fracture Forge starter card, routes `glitch-dragons-den` through `buildGlitchDragonsDenProject()`, and changes the old Seed Chamber toast to distinguish its v5.3 architecture baseline from the current v6.1 engine.

Source authority:
- artifact: swyrl_engine_v6_1.html
- bytes: 171506
- SHA-256: 2cf327bebbe857e91ca1a82045427018737eaf5ccac0bbae785ddd82d486f15e
- marker: SWYRL_ENGINE_DEPLOY_MARKER: V6_1_GLITCH_DEN_STARTER
- validation: release-candidate reconstruction + JavaScript syntax + starter/card/router/label assertions PASS
- production deployment: pending final DEPLOY_REQUEST.json button press
- live verification: pending production deployment


## v7.0 — exact Dragon Den structural parity

The Glitch Den no longer maintains a separately invented megacavern layout. `buildGlitchDragonsDenProject()` now invokes `buildDragonsDenProject()` as its structural source of truth and rethemes the resulting scene in-place. This makes its architecture, floor plan, rooms, placements, groups, exits, collision layout, and camera framing exactly the regular Dragon Den while retaining a Glitch identity through palette/material treatment and themed names. Future regular-Den structural changes automatically propagate to the Glitch Den.

Source authority:
- artifact: swyrl_engine_v7_0.html
- bytes: 183813
- SHA-256: 4af05dc4d26819571c9e586703a36c5b5c7300a43611a3d2ec3d1499c917c6b7
- marker: SWYRL_ENGINE_DEPLOY_MARKER: V7_0_FRACTURE_FORGE_ASCENDANT
- validation: exact-base call, legacy megacavern removal, project-card parity description, reconstruction, and JavaScript syntax PASS
- production deployment: pending final DEPLOY_REQUEST.json button press
- live verification: pending production deployment

## v7.0 — Glitch Dragon Den II: Apex Nexus

Adds a second Glitch Den while preserving the original parity variant. Apex Nexus uses a dragon-scale layered cavern shell, central Nexus forge, crystal-vein clusters, throne vault, route gates, atmospheric point-light field, and three larger anatomy-v2 dragons: §wyrl§ Apex Glitch Dragon, Frost Nexus Dragon, and Ember Fracture Dragon.\n\nSource authority: swyrl_engine_v7_0.html · 183813 bytes · SHA-256 4af05dc4d26819571c9e586703a36c5b5c7300a43611a3d2ec3d1499c917c6b7 · marker V7_0_FRACTURE_FORGE_ASCENDANT. Candidate reconstruction and JavaScript syntax validation PASS.\n\n## v7.0 — single Glitch Den + Dragon Anatomy v3

Corrects the v6.3 duplicate-project mistake. There is one Glitch Dragon Den — Fracture Forge. The researched Apex environment ideas are folded into that project, while the extra Apex Nexus card/router/builder are removed. Dragons now use anatomy-v2 as the coherent skeletal base with v3 layered crown horns, overlapping dorsal armor, crystalline cheek/shoulder structures, fracture-energy halo and stronger material contrast. Validation explicitly asserts exactly one Glitch Den project card and absence of the accidental Apex template.\n\nSource authority: swyrl_engine_v7_0.html · 183813 bytes · SHA-256 4af05dc4d26819571c9e586703a36c5b5c7300a43611a3d2ec3d1499c917c6b7 · marker V7_0_FRACTURE_FORGE_ASCENDANT. Reconstruction + JavaScript syntax PASS.\n\n## v7.0 — Fracture Forge runtime parity + default\n\nGlitch Dragon Den — Fracture Forge now includes the Wisp Visitor / Creator player avatar used by the regular Dragon Den, therefore the existing first-person PIE/twin-stick runtime resolves a valid player hero in the redesigned den. The engine build default and startup project are now glitch-dragons-den. The v3 dragons and Fracture Forge environment remain unchanged. Validation asserts Wisp, first-person controls, default-project metadata, one Glitch Den card, and absence of the retired duplicate Apex template.\n\nSource authority: swyrl_engine_v7_0.html · 183813 bytes · SHA-256 4af05dc4d26819571c9e586703a36c5b5c7300a43611a3d2ec3d1499c917c6b7 · marker V7_0_FRACTURE_FORGE_ASCENDANT. Reconstruction + JavaScript syntax PASS.\n\n## v7.0 — Wisp hover collision + planted dragon idle rig\n\nThe Wisp retains its collider while gaining free hover altitude: horizontal movement still resolves the existing actor collision system, while Space/E rises and Shift/Q descends with a minimum terrain clearance. Glitch Dragon v3 paws are registered as contact points; lower-leg orientation is re-anchored toward the rear ankle of each paw instead of its center. Per-foot downward contact rays plant paws on terrain or solid scene objects. Procedural idle adds restrained breathing, head/neck motion, tail sway, wing settling and weight shift while foot contact remains solved.\n\nSource authority: swyrl_engine_v7_0.html · 183813 bytes · SHA-256 4af05dc4d26819571c9e586703a36c5b5c7300a43611a3d2ec3d1499c917c6b7 · marker V7_0_FRACTURE_FORGE_ASCENDANT. Reconstruction + JavaScript syntax PASS.\n\n## v7.0 — contact correction + organized mobile Tools\n\nCorrective pass driven by live mobile screenshots. Preserves the proven Wisp horizontal first-person controller while adding explicit mobile ▲/▼ hover controls so flight altitude no longer depends on keyboard input. Dragon contact solving now applies a bounded root-height correction from the lowest paw contact, then resolves each paw residual and rear-ankle lower-leg orientation, rather than moving isolated paw meshes. Mobile Tools are grouped at runtime into Project & History, Transform, World & Build, Play & Content, and File & View while preserving existing control IDs/handlers.\n\nSource authority: swyrl_engine_v7_0.html · 183813 bytes · SHA-256 4af05dc4d26819571c9e586703a36c5b5c7300a43611a3d2ec3d1499c917c6b7 · marker V7_0_FRACTURE_FORGE_ASCENDANT. Reconstruction + JavaScript syntax PASS.\n\n## v7.0 — Fracture Forge hard ground snap\n\nLive Den 2 inspection exposed three legacy construction offsets that deliberately raised the Fracture Forge dragons by +3.3, +2.05, and +1.9 units. Those offsets are removed. After each dragon receives its final yaw, snapDragonToSupport() finds the lowest world-space paw, resolves the support directly below it, and applies the full support delta to the dragon root immediately at project construction. The continuous contact solver now follows the lowest paw rather than the most-negative paw error.\n\nSource authority: swyrl_engine_v7_0.html · 183813 bytes · SHA-256 4af05dc4d26819571c9e586703a36c5b5c7300a43611a3d2ec3d1499c917c6b7 · marker V7_0_FRACTURE_FORGE_ASCENDANT. Reconstruction + JavaScript syntax PASS.\n\n## v7.0 — Fracture Forge Ascendant\n\nProduction-scale §E and flagship-den pass. The editor gains a compact Command Deck for Projects, Focus, Frame, Top, Play and Tools; live actor/selection status; searchable grouped mobile Tools; and faster scene navigation without replacing established handlers. Fracture Forge gains authored navigation landmarks, Creator Overlook, Fracture Spine Bridge, Ascendant Crown Gate, guardian-vault framing, wayfinder crystals, two additional traversal loops, and localized lighting composition. The single Glitch Den project boundary and v6.8 hard dragon support snap are preserved.\n\nSource authority: swyrl_engine_v7_0.html · 183813 bytes · SHA-256 4af05dc4d26819571c9e586703a36c5b5c7300a43611a3d2ec3d1499c917c6b7 · marker V7_0_FRACTURE_FORGE_ASCENDANT. Reconstruction + JavaScript syntax PASS.\n\n## Mandatory update protocol

Every §E GitHub mutation is a governed update. Each update must synchronize version surfaces when applicable, update this roadmap, use the dedicated DEPLOY_REQUEST.json final deploy-button mechanism, follow its resulting Actions run to terminal state, verify the live Hugging Face marker, and return both the deployment-run URL and live §wyrl§ Engine URL to the user. Documentation/governance-only changes may retain the current engine binary version, but still require a roadmap entry and deployment verification.

## Governance sync — 2026-10-06

- reconciled stale v5.7 documentation with current v6.0 source authority
- established this roadmap as mandatory per-update lineage
- codified version synchronization for versioned §E mutations
- codified manual deployment + terminal workflow + live marker verification for every §E update
- codified response requirement: exact deployment Actions link + live §wyrl§ Engine page link
- engine binary remains v6.0; this is governance/documentation synchronization
