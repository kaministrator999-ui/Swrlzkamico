# §wyrl§ Engine Roadmap

Canonical lane: §E / §wyrl§ Engine  
History audited through: **2026-10-07**  
Current governed engine release: **v7.9**

This roadmap is the mandatory release lineage for governed §E GitHub updates. Root `§tart_§E.md` defines the deployment contract.

## Audited release lineage

| Version | Date | What changed |
|---|---|---|
| v3 | 2026-10-05 | Unreal-inspired editor architecture: components, PIE/SIE, content drawer, undo/redo, snapping, viewport modes, validation, agent API. |
| v4 | 2026-10-05 | Solid terrain, locked authoring views, mobile tools, hardened physics/camera semantics, live-deploy proof. |
| v4.1 | 2026-10-05 | Grounded hero, clean PIE chrome, relocated jungle blockers, deterministic patch-layer verification. |
| v5 | 2026-10-05 | Project system; MOBA separated from engine core; Starter World and Dragon's Den became loadable templates. |
| v5.1 | 2026-10-05 | §wyrl§ Engine naming; Dragon's Den — Seed Chamber became default while other projects remained loadable. |
| v5.2 | 2026-10-05 | First-person PIE, camera-relative movement, mobile twin sticks, pointer-lock look, reticle/runtime cleanup. |
| v5.3 | 2026-10-05 | Hierarchical groups, multi-select, hierarchy persistence/grouped collisions, immersive Den redesign. |
| v5.4 | 2026-10-05 | Procedural Wisp visitor avatar replacing the default capsule while preserving controls and persistence. |
| v5.5 | 2026-10-06 | Natural camera look correction and Dragon anatomy v2. |
| v5.6 | 2026-10-06 | Detailed articulated wings/rear paws and reusable slope-aware surface foot grounding. |
| v5.7 | 2026-10-06 | Multi-sample precision paw contact, jaw/teeth correction, persistent editor camera-speed slider. |
| v5.8 | 2026-10-06 | Cleaner Wisp particles and bounded support correction for dragon paws on rocks/pedestals. |
| v5.9 | 2026-10-06 | Softer Wisp, stabilized planted feet, visible Undo/Redo/history. |
| v6.0 | 2026-10-06 | Researched Glitch Dragon Den / Fracture Forge introduced. |
| v6.1 | 2026-10-06 | Fracture Forge exposed in Projects hub; project router fixed; Seed Chamber version presentation clarified. |
| v6.2 | 2026-10-06 | Glitch Den made an exact structural variant of the regular Dragon Den. |
| v6.3 | 2026-10-06 | Apex Nexus experiment added as a second Glitch Den. |
| v6.4 | 2026-10-06 | Duplicate-project experiment removed; Apex ideas folded into one Fracture Forge; Dragon anatomy v3. |
| v6.5 | 2026-10-06 | Wisp first-person runtime restored in Fracture Forge; Glitch Den made default. |
| v6.6 | 2026-10-06 | Wisp hover/collision and planted dragon idle/contact rig. |
| v6.7 | 2026-10-06 | Wisp movement/contact correction, mobile hover controls, organized mobile Tools. |
| v6.8 | 2026-10-06 | Legacy Den-2 dragon lift offsets removed; hard ground snap to lowest-paw support. |
| v7.0 | 2026-10-07 | Fracture Forge Ascendant production pass plus Command Deck and navigation landmarks. |
| v7.1 | 2026-10-07 | Expanded Den breathing room and mobile viewport declutter. |
| v7.2 | 2026-10-07 | Wisp horizontal locomotion collision-deadlock repair. |
| v7.3 | 2026-10-07 | Unified Wisp flight controller and runtime diagnostics; historical lineage repair. |
| v7.4 | 2026-10-07 | Professional File/Edit/Create/View/Play/Tools/Window/Help menus and game-design workspace launcher. |
| v7.5 | 2026-10-07 | Mobile editor chrome consolidated behind one compact §E workspace trigger. |
| v7.6 | 2026-10-07 | Desktop editor chrome polish: dedicated menubar lane, duplicate Command Deck suppression, docked hints. |
| v7.7 | 2026-10-07 | Saved revision-142, 120-actor Moonfire Sanctum promoted to the sole canonical Glitch Dragon Den starter. |
| v7.8 | 2026-10-07 | Retractable desktop Outliner/Details docks plus persistent multi-object editor layers and visibility. |\n| v7.9 | 2026-10-07 | Editor-authored Sanctuary & Makers Grotto promoted to the canonical Dragon Den; project-local scripting namespace established. |

## Artifact authority

| Version | Artifact | Bytes | SHA-256 |
|---|---|---:|---|
| v3 | swrlz_forge_unreal_pass_v3.html | 89746 | 5459e050394a7cbab9bcf0cde16598975611dd0896273f9c04a21e45c309a2a9 |
| v4 | swrlz_forge_v4.html | 99591 | a8299fe89fbb98d15c6091751b7a66931a66efec8eec5cb464e1286f21895856 |
| v4.1 | swrlz_forge_v4_1.html | 100610 | 647a80a6a1062e8e4068c63593cca3c5566fe8ee9da5dcdcbc1810d42673132f |
| v5 | swrlz_forge_v5.html | 120501 | c5b44363460fc29ec3a119967c082c1fd95b035d781c50a4affa9d8ecd686593 |
| v5.1 | swyl_engine_v5_1.html | 129398 | a653064ce2be625d67d561a1db249a1bb4fa0637dc69377480cf6311e43fdf51 |
| v5.2 | swyrl_engine_v5_2.html | 135148 | e3ea58f80f83a2b001f087f5852b6ce7fa5a4dbf4af2f5d67c414eb46c196ad8 |
| v5.3 | swyrl_engine_v5_3.html | 146986 | ef68a0906430de83a5da464efe864eed26e757f03d6fdce5e81df6411c75f995 |
| v5.4 | swyrl_engine_v5_4.html | 151952 | add2c872e99097285a4ed68372aae3c6f7a42dff4cac4315771c56e8e9c0aea5 |
| v5.5 | swyrl_engine_v5_5.html | 155355 | 76410c2340664c0754ad2a50e7be858f7223787e89cb6f10c4360577cc27f4e2 |
| v5.6 | swyrl_engine_v5_6.html | 161347 | c4c0d88febfdfa2bf1c9b02925c6abd9ddafe05010ec5917dac2cd8eb05886e4 |
| v5.7 | swyrl_engine_v5_7.html | 163645 | 62fbe228f4ee412c17be53429239159a400bc02bd1f94b5c1b7760f85645c04a |
| v5.8 | swyrl_engine_v5_8.html | 164651 | 0fc3981d582c4ad5ddf07bd01c514463852a4774b3f81e1ff0518c3cb3456a7a |
| v5.9 | swyrl_engine_v5_9.html | 165545 | aafba38d59b520147aa0c625609db0c2e215e31c1f0a6cebaccc1c5faba51eef |
| v6.0 | swyrl_engine_v6_0.html | 170965 | 747076cbbd43b881887392bcf69a7721905564ffc155e3ab946831ed3a640569 |
| v6.1 | swyrl_engine_v6_1.html | 171506 | 2cf327bebbe857e91ca1a82045427018737eaf5ccac0bbae785ddd82d486f15e |
| v6.2 | swyrl_engine_v6_2.html | 168023 | 30504d0b7abeb6eefb7751f3a870d8006ed11966a5ee4f201208a70c0a72c8cd |
| v6.3 | swyrl_engine_v6_3.html | 172048 | 595552ab6f711d333866db9ffeea854f25799393a33463a346b67396774c2c8a |
| v6.4 | swyrl_engine_v6_4.html | 171486 | 98cd0c5a8d376a18ccbe2b958556b98cdc546bb6dc7f6930c4d4916b6d25704d |
| v6.5 | swyrl_engine_v6_5.html | 171694 | f0c3a048c2189a4b761c091971ee6737bcac06c12fb52125a5c2f31045e23a1f |
| v6.6 | swyrl_engine_v6_6.html | 174866 | 602a498245a01e9ddc87c44ca17390d0070b334996fa15c2817cbc5c5a4af72e |
| v6.7 | swyrl_engine_v6_7.html | 178252 | d71cc0f3c57692b1c78830d76ea73069804a9306838b29ae89ae0bafd91222d2 |
| v6.8 | swyrl_engine_v6_8.html | 178783 | 98e383e3795926c5375eace3b5db22dca92b498caeaa1935e51fc2bafd489613 |
| v7.0 | swyrl_engine_v7_0.html | 183813 | 4af05dc4d26819571c9e586703a36c5b5c7300a43611a3d2ec3d1499c917c6b7 |
| v7.1 | swyrl_engine_v7_1.html | 184471 | 35fedcc5decf0f00e4682315311470d9cc05f8c072d2c085daa40c4cacf1d053 |
| v7.2 | swyrl_engine_v7_2.html | 185212 | 3d03e66d04f26659f365d43a2da531692474f4bc5122e1ddffbe9dc515277132 |
| v7.3 | swyrl_engine_v7_3.html | 185760 | 4967a5b527223b8c3d5bfd7ea7ef9a413a6c8582351b2c317cf9c4bc9d0f0e3c |
| v7.4 | swyrl_engine_v7_4.html | 194122 | 822d4d58aad205a4710401c040cd954337585e6346bb337fe7866de73e02f25e |
| v7.5 | swyrl_engine_v7_5.html | 195495 | 0de92bd93af0e4a7d7b9ae22270ee964168e23cf049a11f780cd8563c1ce21e6 |
| v7.6 | swyrl_engine_v7_6.html | 197128 | 409f42adc579b8da5ade1a55c9d5d09d58ef67539ff6e9f0562b119de9ea7f80 |
| v7.7 | swyrl_engine_v7_7.html | 279207 | 75aef1f830dd7117c5675ac1666bdf70755c7be007c26f986c4acb169293bf25 |
| v7.8 | swyrl_engine_v7_8.html | 286002 | 1bf5d8d65f2e1a7af9c30311c119b2bed3fa5688a5ea6e0ff0995a87f38f38cc |

## Git push audit — 2026-10-05 through 2026-10-07

The §E project-path history was re-audited directly from GitHub on 2026-10-07. **174 commits** are accounted for from the initial scaffold (`32657c58`) through the current v7.8 deployment trigger (`9a529d94`). Versioned work is grouped below; counts include implementation, build-chain, validation/integrity, documentation synchronization, corrective and deployment-trigger commits carrying that version label.

| Release bucket | Commits | First versioned push | Last versioned push |
|---|---:|---|---|
| pre-version / governance / bootstrap | 18 | 32657c58 | a3faeb28 |
| v3 | 1 | 018b7351 | 018b7351 |
| v4 | 1 | 948489ba | 948489ba |
| v4.1 | 1 | 5d22b941 | 5d22b941 |
| v5 | 1 | e3dcc4b2 | e3dcc4b2 |
| v5.1 | 1 | f8e3b946 | f8e3b946 |
| v5.2 | 1 | c9c9e03d | c9c9e03d |
| v5.3 | 1 | 659e9b46 | 659e9b46 |
| v5.4 | 1 | afb098ba | afb098ba |
| v5.5 | 1 | e08e45fe | e08e45fe |
| v5.6 | 1 | 3b2f29aa | 3b2f29aa |
| v5.7 | 1 | a68a7f36 | a68a7f36 |
| v5.8 | 1 | 97985778 | 97985778 |
| v5.9 | 1 | 2bc743f9 | 2bc743f9 |
| v6.0 | 2 | 12680bb7 | f02752e7 |
| v6.1 | 9 | 08280e78 | 65f16d52 |
| v6.2 | 7 | d875b83d | fe43548e |
| v6.3 | 8 | 8c92aa0b | e2ed3a5f |
| v6.4 | 7 | 6c082b38 | 54ef0d86 |
| v6.5 | 7 | e3ad8f9e | 5e592b7a |
| v6.6 | 11 | f528b1b0 | c00fc940 |
| v6.7 | 12 | 336c389c | 8a9c1705 |
| v6.8 | 7 | 8902fecb | 27c43586 |
| v7.0 | 7 | e56c2186 | 89d0d64b |
| v7.1 | 7 | 322db34d | 368905b0 |
| v7.2 | 10 | 09dc077f | c5abb8f5 |
| v7.3 | 8 | 22790079 | 19343ce4 |
| v7.4 | 7 | dc4baec5 | 093905e1 |
| v7.5 | 7 | d513f0ae | 246889a6 |
| v7.6 | 7 | cebcaf82 | afebb830 |
| v7.7 | 8 | 73873d71 | 2798e4cc |
| v7.8 | 12 | 83eeeada | 9a529d94 |

### Audit corrections made

The 2026-10-07 audit repaired roadmap drift rather than rewriting Git history: v3/v4/v4.1/v5/v5.1 were added to the formal lineage; v7.4 and v7.5 were restored as distinct releases instead of being mislabeled v7.6; historical artifact authority was recovered from each release's own Git revision instead of inheriting later global replacements; literal escaped newline artifacts were removed; and the current v7.8 artifact remains the governing live release.

## v7.9 — Sanctuary & Makers Grotto becomes the canonical Dragon Den\n\nThe 120-actor editor-authored **§wyrl§ · Sanctuary & Makers Grotto** save is promoted directly into the canonical `dragon-den` project identity. It replaces Moonfire Sanctum as the default/original Dragon Den rather than becoming a second starter. The saved Code Studio, Archive Garden, World Forge, Prototype Court, Arrival and Guardian Alcove layout now opens through the normal project loader. A project-owned scripting namespace (`swyrl-project-scripts-v1`) is established on project metadata so future §wyrlz§cript/§form§cript assets remain project-local instead of engine-global.\n\nArtifact: `swyrl_engine_v7_9.html` · **285613 bytes** · SHA-256 `220a9e5cc7e54fd23e8edc084467101cfcc1c099b5033b1d0150fd2160065251` · marker `V7_9_SANCTUARY_CANONICAL_PROJECT`. Validation PASS.\n\n## Preserved v7.8 state

v7.8 preserves the canonical v7.7 Moonfire Sanctum starter and adds persistent editor layers plus retractable desktop docks. Layer membership is serialized with project state; layers can independently hide/show sets of objects without destroying hierarchy or transform groups. Outliner and Details can collapse to reclaim viewport space, especially useful on narrow desktop-mode displays.

v7.8 artifact authority: `swyrl_engine_v7_8.html` · **286002 bytes** · SHA-256 `1bf5d8d65f2e1a7af9c30311c119b2bed3fa5688a5ea6e0ff0995a87f38f38cc` · marker `V7_8_LAYERS_DESKTOP_DOCKS`.\n\nCurrent v7.9 artifact authority: `swyrl_engine_v7_9.html` · **285613 bytes** · SHA-256 `220a9e5cc7e54fd23e8edc084467101cfcc1c099b5033b1d0150fd2160065251` · marker `V7_9_SANCTUARY_CANONICAL_PROJECT`.

Current deployment trigger: `9a529d945f2e35e2427ebef18c6de6b31810eed6` · deployment run #45 succeeded.

## Mandatory update protocol

Every §E GitHub mutation is a governed update. Each versioned engine update must synchronize applicable version surfaces, update this roadmap, validate/reconstruct the exact artifact, and use the dedicated `DEPLOY_REQUEST.json` final deploy-button mechanism. The resulting Actions run must be followed to terminal state and the live Hugging Face marker verified before the release is reported complete.

Documentation-only historical/audit corrections do **not** create a new engine binary version. They must not silently rewrite historical artifact authority; corrections should identify their audit date and preserve the release SHAs they were recovered from.
