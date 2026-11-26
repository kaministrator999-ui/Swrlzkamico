# §X v0.4 — compatibility evidence and decision gate

Status: BLOCKED for candidate execution. Existing GitHub Actions browser backend remains unchanged.

## Observed evidence (user supplied live receipt, 2026-11-25)
- Runtime source SHA-256: 3f4e28a8e05f79949ef3e2f6da92363091b09fdc0be3ea4cf16cad2da1a063f0
- Source commit: 12ee05bb59771d36cd641afa7d5a46959b81b24c
- Landlock ABI 7, unprivileged execution, no_new_privs and synthetic workspace/outside file/TCP controls passed.
- Native Chromium sandbox unavailable; independent user, network, mount and PID namespace creation denied in earlier probes.
- Exact read-only OpenSSL config rule resolved Node initialization; Node and Playwright CLI pass.
- Debian launcher fails on /etc/chromium.d. Packaged Chromium ELF version, Playwright launch and context creation pass.
- Direct packaged fixture timed out with fatal proc_util.cc:39 (2 occurrences, errno 13) and crashpad directory_reader_posix.cc:43 (3 occurrences, /proc/self/fd).
- Playwright reaches renderer_page_creation, then fails NEW_PAGE. No rendered fixture, WebGL or screenshot verification.
- Chromium upstream source: https://chromium.googlesource.com/chromium/src/sandbox/+/c788b674274d7e0ccd9df920e3789f4b37dd6e17/linux/services/proc_util.cc — OpenDirectory requires a successful open; OpenProc opens /proc; fd inspection uses self/fd. Exact deployed Chromium revision not pinned in this receipt.

## Decision
Do not broaden /proc permissions, bypass Chromium security checks, or enable arbitrary candidate bytes based on these compatibility tests. Synthetic canaries are not a full credential or process boundary. Existing runtime read allowlist, TCP-only enforcement, process cleanup and shared UID need independent security review. Native sandbox remains absent.

Keep §X for fixed trusted diagnostics and preserve the existing §C browser backend. Evaluate a separately isolated browser runner with supported native sandbox or equivalent reviewed containment. Browser compatibility, isolation, and publication are separate gates. Do not treat a successful CI diagnostic collection as successful renderer execution.

Next investigation must have a new, explicit security-boundary design or hosting capability, not repeat the same allowlist guesses.
