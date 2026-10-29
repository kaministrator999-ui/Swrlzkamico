# §E v11.62 — scoped CI routing for Model Atelier and project starters

## Why this exists

The older native browser CI matrix launched **22 browser suites for every qualifying pull-request update**. Several historical anime workflows also listened to `source-manifest.json`, all patches, or all runtime scripts; even a pure Model Atelier layout adjustment would restart unrelated Sheep Tag, Maul, and storybook verifications.

These checks were valid **release integration tests**, but too expensive for routine local revisions.

## Routing contract

The source of truth is `scripts/route_ci_suites.py`. Every ordinary PR or `main` update uses the most recent commit's actual changed files (`git diff HEAD^ HEAD` on the checked-out commit SHA) to compute affected domains.

| Modified input | Focused browser checks |
|---|---|
| `patches/v11_*`, Model Atelier code, tests, scenes | `model_atelier`; desktop and mobile `model_reference` |
| `patches/v10_0`–`v10_5`, Sheep runtime, tests and scenes | Sheep Tag, Archive, Touch and Run |
| `patches/v10_6`–`v10_8`, Maul runtime, tests and scenes | Maul, Layout and Batch |
| Anime/cinematic patches, scenes, runtime and tests | Anime, storybook, character, episode suites |
| Shared runtime/build/payload/asset with cross-cutting risk | All 22 browser cases |
| Documentation or receipt notes alone | No unrelated browser suites; source-seal workflows remain authoritative |
| Manifest-only patch-order/build-recipe edit | Full suite (ambiguous runtime impact) |
| Deployment request / explicit `workflow_dispatch` | All 22 browser suites |

The `verify-swrlz-storybook-v8-8.yml` workflow's fast **Select affected §E starter suites** job performs `route_ci_suites.py --self-test` and emits a dynamic matrix. An empty selection skips the heavy browser job entirely. Historical anime, cel, cinematic and storybook camera workflows likewise use a cheap selection job and skip when the latest commit does not touch their domain. Their event path filters no longer use the manifest or every `v11_*` modeling patch as a reason to run.

### Safety, not silent omissions

- Unknown engine files, shared core, patch families outside the known domains, manifest edits without matching patch changes, missing history and malformed change lists **fail open** to the full integration suite.
- Packaging integrity, marker/asset preservation, HTML hash and the original canonical model remain in focused **source-seal** CI and are not relaxed.
- `workflow_dispatch` runs all 22 browser cases regardless of changed paths. A release candidate needs one explicit all-suites run at the final SHA **before promotion**; an update to `DEPLOY_REQUEST.json` also selects full integration.
- In a PR, diffing `HEAD^ HEAD` intentionally chooses *the latest revision*, not the cumulative PR file list, which otherwise restarts all components on every small correction. This is fast feedback, **not a substitute for the full final-SHA release sweep**.
- Classifier mapping is covered by deterministic self-tests for modeling, sheep, Maul, anime, unknown-shared, receipt-only and full-release cases. Changes to CI routing should be accompanied by changes to these scenarios.

## Local commands

```bash
python projects/swrlz-forge-moba/scripts/route_ci_suites.py --self-test
python projects/swrlz-forge-moba/scripts/route_ci_suites.py \
  --files-json '["projects/swrlz-forge-moba/patches/v11_63_sculpt.py"]'
python projects/swrlz-forge-moba/scripts/route_ci_suites.py \
  --files-json '["projects/swrlz-forge-moba/runtime/shared_renderer.js"]'
```

The first synthetic example chooses **three modeling suites**. The second chooses **all 22** because an unfamiliar shared renderer may affect every project. A manifest edit accompanied by an identifiable modeling patch still selects the modeling suites; a manifest-only build-recipe edit selects all 22.

## Explicit release gate

Trigger **Validate §E v11.62 native starter and animation studio** manually with `workflow_dispatch` on the exact candidate revision after code changes have stopped, and require all 22 suites to pass. Then complete the separate sealed v11.62 regression and source-receipt checks. Only after those gates pass should the release be merged and the one-file deployment request changed. Do not equate a fast PR route pass with live-release approval.
