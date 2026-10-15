# v261 — Full-width AI workspace responses and widgets

Date: 2026-10-15
Space: `kamiloki/Swyrlz`

## User feedback and observed defect

The mobile screenshots show the verified v260 GitHub work receipt functioning correctly but starting noticeably inward from the viewport's left edge. Historical Chat CSS enforced a 38-pixel left indent on assistant widgets, activity/evidence and assistant body, plus a capped message-list width. The user explicitly requested an AI work platform layout in which all assistant responses and visualizations use the available Chat width rather than a person-to-person messaging gutter.

## Implementation

- [PR #186](https://github.com/kaministrator999-ui/Swrlzkamico/pull/186), merged.
- Add `hf_space/chat/§wyrlz/assets/assistant-fullwidth-v261.css`, included after the existing Chat and v260 GitHub widget CSS in the canonical Station response.
- Expand the Chat work column to available viewport width, remove only the AI-side 38–52px gutters, and make assistant prose, structured widgets, GitHub work dashboard, code/source panels, activity logs, source evidence, and actions stretch to full available width.
- Keep a minimal safe-area-aware viewport edge inset (6–16 CSS pixels), readable interior padding, text wrapping, no full-viewport horizontal overflow, and responsive phone / wide-screen treatment.
- Remove the duplicate outer title and border around the GitHub work receipt, which already has its own heading and verification frame.
- Preserve separately aligned user messages, account controls, permissions, code rendering semantics, model routing and GitHub create-only constraints. Previously saved AI response cards should reflow automatically after stylesheet load; no new repo write should be necessary.

## Acceptance evidence

- Source commit: `fc993799bc073e76ccd72fb857bdfa7332bda2cd`.
- Candidate offline CI [Actions #38817778350](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38817778350): **SUCCESS** (21 passing steps). Includes new `tests/test_assistant_fullwidth_v261.mjs` structural/cascade integrity checks and existing runtime/GitHub regressions.
- Guarded Hugging Face production deploy [Actions #38818035726](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38818035726): **SUCCESS**.
- New deployed Space revision `8a57553a14603cb0826e600c275e11b0c5afc7dc`.
- Rollback revision `bf5272aa205ac812b77f9690215716850c6e5199` snapshotted before upload.
- Version registry: repository-work `1.0.200`, server-runtime `2.3.412`, web-chat `1.5.143`.
- Release checkpoint: **DEPLOYED_UNVERIFIED**, `knownGood=false`, pending visual acceptance in the owner's logged-in phone browser.

## Pending live visual acceptance

Open the **existing** successful GitHub test-file Chat thread, refresh to load the v261 CSS, and confirm:
1. Assistant header remains legible and distinct;
2. GitHub statistics receipt, assistant text, work activity, and evidence share the same left/right Chat edges;
3. No 38px blank strip, doubled GitHub widget frame, overlapping metrics, or unwanted horizontal scroll;
4. Existing user message alignment remains distinct and legible; desktop content also uses the full Chat work area.

Offline structural validation and successful Hugging Face upload do not establish real phone visual acceptance. Do not mark known-good until observed.
