# §C Online Lyric Extraction — production release receipt (2026-11-02)

## Scope
Owner-approved repair of the existing §C Chat's online song-lyric discovery, HTML extraction, line separation and verified-source admission only. No §E engine, game/model editor, model weights, Qwen programming, creative lyric generator, account/auth or Chat UI mutation.

## Source and candidate
- Exact guarded HF deployment source: `5d0333bc0737956f18d3e8f2f045ad7b922cccfa`
- Preserved accepted §C release source before repair: `c623d93670a493a573907451a4d59357d13337b1`
- Code propagated to current feature lineage through [PR #352](https://github.com/kaministrator999-ui/Swrlzkamico/pull/352), merged as `c656a267f883178ffb654f479948c3ba0934854f`.
- Changed behavior: `api/online_research.py` and `hf_space/online_tools.py`. Also added only a focused regression fixture and lyric-scoped workflow.
- Source differences from prior deployed commit: lyric HTML/parser code and lyric-specific tests/workflow; no unrelated app/runtime code.

## Validation and recovery history
- Focused online lyric extraction CI: [41540750437](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41540750437), SUCCESS; 6 targeted synthetic-fixture checks plus all 20 legacy full-lyrics scripts PASS.
- Earlier release attempt [41539817622](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41539817622) blocked before upload by a pre-existing short-snippet acceptance contract regression introduced by the first fix. Repaired with retained snippet-consistency and identity-bounded structured-body fallback.
- Second release attempt [41540456088](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41540456088) blocked before upload by site-copyright/footer text contamination. Added explicit song-page boundary and replay of the complete production lyric suite.
- Guarded release [41540837686](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41540837686), SUCCESS. Production lyric regressions, native R39 verification, real model reconstruction, 700M smoke and user/assistant identity acceptance PASS. No new R39/700M weights.

## HF deployment
- Existing Space: https://huggingface.co/spaces/kamiloki/Swyrlz
- Exact source uploaded: `5d0333bc0737956f18d3e8f2f045ad7b922cccfa`
- Prior Space revision / rollback target: `6cd79588edbddacf91881bd8d7de9f47b0eefb50`
- Uploaded Space revision: `d41771b5376ee927f7ed8c943b9c2a68ce374f46`
- Deployment triggered by `main:.deploy/HF_SPACE_REQUEST.txt`, Git commit `373b7bb283384959d74287e789e84033de28a43b`.
- Workflow captured the rollback checkpoint and HF release checkpoint as immutable artifacts.
- Release status: **UPLOAD_CONFIRMED / GITHUB_WORKFLOW_SUCCESS**. Provider runtime served-revision and real owner-device lyric lookup acceptance are **not independently verified by this receipt**. Do not claim a proven end-user lyric lookup until checked on §C.
