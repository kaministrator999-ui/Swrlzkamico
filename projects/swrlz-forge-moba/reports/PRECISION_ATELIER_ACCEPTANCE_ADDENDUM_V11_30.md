# §E Precision Model Atelier — v11.30 additive acceptance handoff
Date: 2026-10-18. Historical baseline and all previous accepted/pending requirements remain in [v11.29 acceptance ledger](PRECISION_ATELIER_ACCEPTANCE_LEDGER_V11_29.md).

**Status: tested stacked DRAFT candidate; NOT full specification completion, production merge, deployment, or character-art approval.**

## This slice: grouped 📌 surface boundary controls
- Existing polygonal and freehand surface lasso pins are unchanged in native schema and identity. New `LassoGroupPins` accepts 1–8 unique **one-based** pin numbers; group `LassoGroupDelta0/1/2` moves those pins together by signed object-local XYZ components ≤0.15.
- Every proposed boundary pin projects to actual mesh triangle attachment (local point, triangle index and barycentric coordinates). On invalid point/index/amount, failed surface projection, collapsed/self-intersecting boundary or invalid native schema, all proposals are rejected **atomically**; the original lasso pins and mesh remain untouched.
- One valid grouped motion records exactly one Undo checkpoint and is retained in the original native JSON serialization. It does not directly move a mesh vertex or add mesh topology. The existing region morph/refinement is a separate explicit action.

## Receipts
- [PR #235](https://github.com/kaministrator999-ui/Swrlzkamico/pull/235) stacked on v11.29 #234 → #233 → #232 → #231 → #230 → #229 → #219.
- [PASS — Actions run 39146901023](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39146901023), exact tested source `85ca96e5e25d8049a315c36681c38d7238d103cc`: source parse, sealed-base preview build, grouped pin input/projection/nonmutation unit test, advanced brush regression and real desktop/Android polygon region draw → grouped pin move → Undo → repeat → invalid rejection → morph → native save/import.
- [Initial failed run 39146833679](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39146833679) exposed binary floating-point equality in synthetic test (`-0.07500000000000001` vs `-0.075`). Corrected to tolerance and independently rerun; no hidden edits to production.

## Delta to v11.29 incomplete list
The v11.29 ledger's **group boundary pin transform** item is now implemented with bounded numeric translation and independently validated. It is NOT a visual rotation/scale gizmo for boundaries; full region Boolean operations, add/subtract/intersect, curve/segment interpolation, normal-offset boundary pins, arbitrary mesh-decimation/runtime LODs and freehand face cutting remain unimplemented. No claim of full-camera occlusion accuracy is made. Preserve the rest of the v11.29 ledger unchanged as historical evidence.

## Future release gate
Do not promote an unfinished design to main or press `projects/swrlz-forge-moba/DEPLOY_REQUEST.json`. Complete remaining selected slices, all dense-mobile cross-tool tests, original character likeness / independent visual review, release manifest and version sync, terminal dedicated deployment and live marker checks according to [§tart_§E.md](../../../%C2%A7tart_%C2%A7E.md). Production remains v11.20.
