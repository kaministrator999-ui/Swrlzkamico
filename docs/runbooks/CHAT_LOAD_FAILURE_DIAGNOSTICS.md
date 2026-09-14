# Chat Load Failure Diagnostics

## Purpose

Use this runbook only when `/chat` stalls, freezes, partially hydrates, or appears to serve stale UI. Diagnostic UI and client logging are intentionally **not loaded during normal Chat operation**.

## First check: runtime revision/source alignment

Before debugging individual Chat helpers, verify that production `/chat` is actually requesting the current runtime loader revision.

1. Read `runtime_pages/manifest.json` on the `runtime` branch and note `version`.
2. Read `web/chat_runtime_loader_v3.js` and note `REV`.
3. Fetch production `/chat` and inspect the runtime/source headers and injected loader URL.
4. Confirm the production response identifies the expected runtime source/branch/path and that the injected `chat_runtime_loader_v3.js?v=<revision>` matches the current manifest/loader revision.
5. If production is still injecting an older revision, advance the runtime manifest revision and loader revision together, commit to `runtime`, reload `/chat`, and verify production again before changing any downstream helper.

### Incident that established this check

Chat appeared unable to load and the temporary diagnostic `LOG` probe never appeared. Stable APIs were healthy, but production `/chat` was still injecting `chat_runtime_loader_v3.js?v=57` while the diagnostic-aware loader was revision 61. Advancing `runtime_pages/manifest.json` from 57 to 61 caused Chat to load successfully immediately. The missing probe was therefore evidence that execution had not reached the new diagnostic loader; the fault boundary was runtime revision/source selection rather than a later Chat helper.

## Optional diagnostic instrumentation

The repository retains these dormant diagnostic assets for incident use:

- `web/chat_debug_log_v1.js` — persistent client boot/error logger and remote diagnostic sender.
- `web/chat_debug_ui_v1.js` — visible `LOG` probe/viewer.

They are intentionally absent from the normal `critical` loader list. Do not expose the `LOG` button or diagnostic access in ordinary production Chat.

When instrumentation is needed, temporarily place the logger first and the debug UI second in the `critical` array of `web/chat_runtime_loader_v3.js`, then advance the loader + manifest revision so production cannot reuse the previous asset revision. Verify that the `LOG` probe appears before interpreting downstream logs.

The useful trail is ordered execution: `script-start` followed by `script-load`, `script-error`, or `script-timeout`. A final `script-start` with no completion can identify the helper executing when the main thread stalls. Server-visible client diagnostics can then be inspected without requiring the user to extract logs from a frozen browser.

## Removal after incident

After the incident is resolved:

1. Remove `chat_debug_log_v1.js` and `chat_debug_ui_v1.js` from the normal critical loader list.
2. Advance loader + manifest revision again to invalidate the diagnostic boot chain.
3. Leave the diagnostic assets in the repository dormant for future incidents.
4. Verify `/chat` loads normally and no `LOG` control is visible.

## Guardrails

Do not clear browser storage as a first-line loading fix because Chat threads are browser-local. Do not change later helpers until runtime source/revision alignment is verified. Keep diagnostic payloads bounded and exclude conversation text, prompts, responses, tokens, cookies, secrets, and stored chat history.