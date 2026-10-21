# §wyrlz Engine contributor instructions

Follow [RELEASE_PROCESS.md](./RELEASE_PROCESS.md) as the authoritative current owner delivery workflow (aka **§§§ = §uper §imple §wyrlz**).

For §E changes: implement and locally validate targeted modifications; commit cohesive changes to `main`; then trigger Hugging Face publishing via a **separate final commit changing only `DEPLOY_REQUEST.json`**. Confirm the hosted release before reporting success. Owner performs hands-on acceptance testing.

Every feature/fix changing shipped §E code must synchronize the source manifest's version, new patch lineage, actual HTML bytes/SHA-256, UI/runtime build identifier and deploy marker, release scripts and relevant docs. The final separate `DEPLOY_REQUEST.json` commit must identify that exact source version, SHA and source commit. See the full checklist in `RELEASE_PROCESS.md`. Do not bump runtime versions for documentation-only changes.

Do not initiate unrelated 22-case Sheep Tag/Maul/Anime/Storyboard CI while refining Model Atelier features. Historical engine verification workflows remain available for `workflow_dispatch` on demand. Do not disable or modify AI Chat/Core workflows. Never change the source manifest's integrity receipt without correctly building/resealing the actual changed artifact.

This instruction concerns only `projects/swrlz-forge-moba` and does not override security or integrity protections.
