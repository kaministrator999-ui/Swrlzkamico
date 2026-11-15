# Aiven: private §C service health

The existing bundled server workbench (`/api/admin`) has an **Aiven** section.
This does not modify the public §C Chat page. Its **Check Aiven** button invokes
`POST /api/admin?action=aiven-metrics`, which is inside the pre-existing
`SWRLZ_ADMIN_TOKEN` server-side authentication gate. The action is read-only
and makes no requests until the admin presses the button.

## Server-only configuration

Configure these as **server secrets**, never in HTML, JavaScript, a chat
message, GitHub source, or a client-accessible configuration endpoint:

- `SWRLZ_AIVEN_API_TOKEN`: a narrowly scoped Aiven API token with service
  read and service metrics read rights.
- `SWRLZ_AIVEN_PROJECT`: exact Aiven project name.
- `SWRLZ_AIVEN_SERVICE`: exact Aiven service name.

An absent credential produces a clear `AIVEN_NOT_CONFIGURED` response.
The provider is queried over the official HTTPS Aiven API and returns only
bounded service metadata plus numeric/chart metrics. The API token, service
URI and credentials are never returned. Remote errors use sanitized codes.

## Source and deployment boundaries

This implementation is in the legacy **bundled server admin plane**
(`api/server_v213.py` and `web/admin.html`) on GitHub. The active
`kamiloki/Swyrlz` Hugging Face Space is independently deployed; a GitHub
source commit does **not** establish that these admin routes are live there.
Do not deploy or replace the live HF Space from the historical server package,
or mistake an unrelated Vercel check for Hugging Face acceptance.

Integrating into the live Space requires inspecting its current `station.py`,
porting the private endpoint to that exact live revision, and running the
established guarded HF deployment/rollback procedure. Do not add Aiven API
traffic, metrics, or debugging receipts to the public Chat rendering path.

## Alerts and quotas

Aiven Console -> service -> Metrics shows CPU, disk, memory, I/O and network.
Use the provider's existing **notifications and alerts** for operational
warnings. This read-only bridge does not configure notification recipients,
service alerts, billing notifications or periodic background monitoring.

Aiven metrics are utilization readings, not automatically the same as
free-plan quotas or monthly billing. Do not infer remaining account credits
or API rate limits from the provisioned disk size.
