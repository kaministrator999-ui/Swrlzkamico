# §C: private Aiven administration on live Hugging Face

**Target:** existing \`kamiloki/Swyrlz\` Space. **Do not** replace the
live Station with the historical bundled server or create a new Space.

## Admin identity

\`/admin/aiven\` is served only to the administrator's existing verified
Google login, recovered from \`swrlz_hf_account\` through the durable,
Redis-backed \`account_chat_store.load_login\`. It does **not** trust a
display name, browser flag, model output, or the broader Forge account adapter.

The allowlist is server-side and fail-closed:

- \`SWRLZ_ADMIN_GOOGLE_SUB\` (preferred stable Google subject); alternatively,
  the existing owner-only \`SWRLZ_SANDBOX_WRITE_GOOGLE_SUB\` if already configured.
- \`SWRLZ_ADMIN_GOOGLE_EMAIL\` (the owner's verified Google email).
  If both subject and email are configured, **both must match**.

Do not put an account email, subject, token, or any Aiven credential into
public HTML, commit messages, GitHub source, action inputs, or Chat.

## Monitoring

Private API \`GET /api/admin/aiven/metrics\` is authorized on each request.
It calls the Aiven provider only when the admin clicks **Check Aiven**.
The response is whitelisted, bounded, and no-store. Neither public §C Chat nor
other accounts poll the service. All provider requests are read-only
(\`GET service\` and \`POST service/metrics\`, where POST fetches time-series data).

Three additional **private** Aiven settings are needed:

- \`SWRLZ_AIVEN_API_TOKEN\` (Aiven API token with sufficient read permissions)
- \`SWRLZ_AIVEN_PROJECT\` (project name)
- \`SWRLZ_AIVEN_SERVICE\` (service name)

The Aiven Console remains the authority for alerts, quotas, billing, and
full-size charts. This endpoint is not a billing or free-credit meter.

## Guarded release

CI runs source syntax checks, Google-owner authorization regression tests,
unauthorized-route tests, and read-only exact live-source preflight.

The only target is the existing \`station.py\`, plus the new isolated
\`aiven_admin.py\`. The Python release patcher refuses unexpected Google
auth changes. It does not edit public Chat HTML, inference, model weights,
provider settings, or Space hardware.

**Only after private configuration has been provided** through GitHub
Actions repository secrets (not in workflow inputs), open:

\`https://github.com/kaministrator999-ui/Swrlzkamico/actions/workflows/manual-hf-aiven-admin.yml\`

Run once with \`mode=validate\`, \`approved=no\`, inspect the receipt. Then
\`mode=deploy\`, \`approved=yes\` performs a source-pinned commit to the
existing Space and verifies the uploaded bytes. On byte-verification failure,
it attempts rollback only if the published Space SHA is still current.
The workflow stores the predeploy \`station.py\` as a rollback artifact.

The GitHub workflow expects existing \`HF_TOKEN\` plus Google identity
(\`SWRLZ_ADMIN_GOOGLE_SUB\` or \`SWRLZ_ADMIN_GOOGLE_EMAIL\`) and all three
Aiven secrets. The release script refuses to deploy with missing configuration.

A successful HF source push remains **DEPLOYED_UNVERIFIED** until the
Space has restarted and the owner checks Google sign-in, owner-only access,
the Aiven read, and ordinary public Chat operation on their device.

## Current status

The isolated module and guarded release source are committed to the
\`Swrlzkamico\` GitHub repository. The active HF Space is **not**
changed by those commits, nor by the validation workflow. Running
the manual deployment and configuring private secrets are distinct steps.
