# §C / §E — Progressive Analyze Workspace (2026-11-22)

## Scope and source of truth

The existing §E **Analyze workspace** action (`chat_workspace_analysis_v11_178.js`) sends a user-initiated read-only request through the integrated §Chat frame and the existing authenticated host lease. The current Space and session checks remain authoritative. This change does not alter §E source, native editor operations, project persistence, account login or model weights.

Previously, the §C native read route in `model_router.py` called `forge_chat_actions.generate_events()` which computed one entire deterministic `build_insight` explanation and returned it as a single `DELTA` before the usual `forge-workspace` widget. The new scoped route sends the verified project/level and editor-metadata observations **as they are checked**, emits the same original typed widget, and then streams a grounded conversational synthesis from the existing Qwen 9B backend. The model receives a **whitelisted, read-only** evidence summary, not the host session token.

## User-facing sequence

1. The authenticated snapshot identifies the project and whether the current workspace is **Model Studio** or **Scene**; Chat starts its first assistant text immediately.
2. The actual native snapshot supplies total meshes/actors and the bounded sample (normally at most 48). Chat states that coverage explicitly.
3. If an object is selected and included, Chat reports its recorded type, transform, and (for model parts) material/color. This is **not pixel/viewport vision**.
4. The original deterministic metadata analyzer reports type counts and possible duplicate labels/co-located object origins as *review hints*, never verified defects.
5. The original source-backed `forge-workspace` card remains unchanged. §Chat then streams a separate natural-language assessment and prioritized next checks using the locally hosted Qwen model. Failure/absence of inference uses deterministic recommendations from that card.
6. A final scope note confirms that no viewport pixels, animation, collision or gameplay were actually observed and no editor objects were changed.

The existing Station `STATUS`/NDJSON `DELTA` transport, Stop/cancel behavior and activity log remain in place. The milestones are **observable work**, not hidden model chain-of-thought.

## Files and safeguards

- Source release module: `scripts/releases/forge_progressive_review_v1.py`.
- Conditional routing and pinned HF deployment/rollback: `scripts/hf_forge_progressive_review_v1_release.py`.
- Regression: `tests/test_forge_progressive_review_v1.py`.
- Guarded workflow: `.github/workflows/hf-forge-progressive-review-v1.yml`.
- Latest verified original §C revision before update: `e55aa8736a4929d3587652f9894b5d3fb6e2db01`.
- The source-restricted update touches only `model_router.py` and adds `forge_progressive_review_v1.py` to the existing HF Chat Space.
- Native §E read classification, short-lived account lease, verified snapshot, mutation plan approvals, project ownership and source-evidence presentation are preserved.

## Acceptance criteria

On a real account, open §E with an existing project, enter Model Studio, select a model part, and click **Analyze workspace** in integrated Chat. The conversation should begin displaying verified project facts before the Qwen synthesis finishes, show the selected part's recorded attributes and sample coverage, then end with grounded modeling recommendations and a review card. With nothing selected or with a scene workspace, the response must report those differences without fabricating an object. No scene edit, save, screenshot or model write should occur. Test Stop, project change and inference failure on an actual device; automated tests do not establish device/browser acceptance.
