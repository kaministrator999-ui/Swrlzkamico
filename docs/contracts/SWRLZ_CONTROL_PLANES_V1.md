# SWRLZ Control Planes V1

Server target: **2.1.3**

This revision treats Chat and Admin as two views over the same runtime evidence boundary.

## Chat control plane

Chat remains the conversational surface. Additive UI extensions provide response evidence drawers, retry and fork-from-message actions, thread search, bounded context inspection, bounded generation controls, a stream camera, response-trace export, deliberate Admin-authenticated "Send to Workbench" file creation, and a non-secret operations-status endpoint.

Truth Firewall remains unchanged: only `DELTA.text` is assistant prose. Status, route, trace, reason, timing and failure evidence remain operational UI.

## Admin control plane

Admin is the engineering/visual control surface. It adds health and release status, a capability registry, Live Web management for `/tmp/swrlz-admin/web`, runtime Chat-token set/change/generate/clear controls, instance-change warnings, web-workspace snapshots and rollback with secrets excluded, an activity timeline, and a promote manifest that describes tested live files without silently changing durable source.

## Secret precedence

Chat authentication resolves in this order:

1. `/tmp/swrlz-admin/runtime/web-chat-token.txt` when valid;
2. `SWRLZ_WEB_CHAT_TOKEN` from the deployment environment;
3. missing / fail closed.

Admin may create or replace the runtime override. A generated token is returned once to the authenticated Admin caller so it can be copied into Chat. Status never reads the secret value back.

## Storage boundary

`/tmp` is Vercel instance-local and ephemeral. Runtime Web, snapshots, activity logs and token overrides can disappear when the instance changes. The UI surfaces that explicitly. Durable promotion requires a separate source-control action; the promote manifest itself performs no durable mutation.
