# §wyrlz Engine contributor instructions

Follow [RELEASE_PROCESS.md](./RELEASE_PROCESS.md) as the authoritative current owner delivery workflow (aka **§§§ = §uper §imple §wyrlz**).

For §E changes: implement and locally validate targeted modifications; commit cohesive changes to `main`; then trigger Hugging Face publishing via a **separate final commit changing only `DEPLOY_REQUEST.json`**. Confirm the hosted release before reporting success. Owner performs hands-on acceptance testing.

Do not initiate unrelated 22-case Sheep Tag/Maul/Anime/Storyboard CI while refining Model Atelier features. Historical engine verification workflows remain available for `workflow_dispatch` on demand. Do not disable or modify AI Chat/Core workflows. Never change the source manifest's integrity receipt without correctly building/resealing the actual changed artifact.

This instruction concerns only `projects/swrlz-forge-moba` and does not override security or integrity protections.
