# §wyrlz Clean Vercel SERVER Transplant

This package is for a **brand-new GitHub repository and brand-new Vercel project**.

It intentionally does **not** include the old `.git` history or the 226 MB R39 model. That avoids dragging the multi-GB repository history into the new deployment.

Included:
- FastAPI/Vercel routes
- `/api/health`
- `/api/admin` phone upload workbench
- `/api/lalm`
- exact repaired R39 size/SHA contract
- gzip -> raw verification

Deployment:
1. Create a new empty GitHub repository.
2. Extract this ZIP and put its contents directly at repository root.
3. Import that repo into a new Vercel project.
4. Set `SWRLZ_ADMIN_TOKEN` to a long random secret.
5. Deploy.
6. Open `/api/admin`.
7. Enter the same token and upload `SWYRLZ_LALM_R39_PHYSICAL_BASE_REPAIRED.§wyrlzx.gz`.
8. Open `/api/lalm` to verify/decompress R39.

Optional: set `SWRLZ_R39_URL` to a direct HTTPS URL serving the exact gzip for cold-start loading.

Important: Vercel `/tmp` is ephemeral and instance-local. For durable production cold-starts, keep R39 in external object storage or another direct artifact host rather than Git history.
