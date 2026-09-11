# Server v2.3.36 — Ice Dragon Frozen Sanctum Upgrade

Date: 2026-09-11

## Module state

- Server Runtime: v2.3.36
- Web Chat: v1.4.31
- LALM Engine: unchanged
- LALM UI: unchanged
- Google Account architecture: unchanged
- Stream contract: unchanged

## Why this release exists

The Ice Dragon theme had become structurally solid after the mobile/desktop responsive fixes, but visually it still read mostly as a dark cyan skin with a dragon watermark. The user requested a stronger Ice Dragon identity while preserving the professional, relaxed Chat experience.

## Chat visual changes

- Reworked the Ice Dragon theme into a deeper frozen-sanctum presentation using layered arctic gradients, crystalline edge lighting, frost-line accents, and colder glass surfaces.
- Strengthened the sidebar identity with an icy illuminated edge, more pronounced dragon branding, colder active-thread treatment, and deeper arctic panel depth.
- Upgraded the top bar into a frosted command rail with a subtle luminous ice seam and more cohesive theme/status controls.
- Improved the conversation chamber with restrained crystalline texture and more deliberate assistant/user visual separation.
- Assistant messages now carry a stronger ice-breath identity through the illuminated left edge, crystal corner accent, colder glass, and deeper code/trace styling.
- User messages retain a distinct violet-blue glacial treatment so authorship remains obvious without breaking the theme.
- Upgraded the composer into an ice-altar treatment with a brighter focus rim, improved route/theme controls, and a more dimensional frozen send button.
- Reworked the large dragon sigil with rune-circle geometry, cardinal crystal markers, stronger icy gradient depth, and a brighter eye/halo detail.
- Kept effects primarily gradient/SVG/pseudo-element based to avoid introducing a continuous particle/canvas workload.
- Existing mobile drawer behavior, responsive geometry, account UI, streaming, Chat persistence, camera controls, and LALM behavior were intentionally left unchanged.

## Verification / deployment

- Theme source updated only on the `runtime` branch.
- No `main` infrastructure mutation was required.
- Production deployment: NONE.
- Server restart: NONE.
- Live source/asset verification follows this release record; final visual acceptance remains browser/screenshot driven.

## Relevant lineage

- Ice Dragon v2 theme stylesheet: `d9862e57514ce931c776baa0a9c1aa66ad688330`
- Ice Dragon sigil artwork: `b7decfaf3bce56aeeaf947d37bf2e5ef6911c616`
- Server runtime version authority: `bf6c271a75c30cc99914fb3a0dabe2c638971209`
- Web Chat version authority: `43cd432f5482abdeceaa3466a192a2e81933487d`

## Rollback

The theme remains isolated to the existing Ice Dragon stylesheet and local SVG asset. Rolling back those two files restores the previous Ice Dragon appearance without affecting the default theme or Chat runtime behavior.
