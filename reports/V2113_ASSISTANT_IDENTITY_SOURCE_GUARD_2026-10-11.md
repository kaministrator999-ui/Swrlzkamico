# v211.3 — Direct §wyrlz application identity guard across model routes

Date: 2026-10-11 (US Central). Existing production Space `kamiloki/Swyrlz`.

## Owner-observed regression

A private native Chat JSON export demonstrated that the 700M route sometimes responded to a direct product-identity question as if it were ChatGPT, then contradicted itself about being §wyrlz. A generic greeting in the same thread was answered normally. Full private dialogue, child-specific personal context, account details and conversation history are **not included** in this repository report.

## Source-level diagnosis and resolution

`hf_space/lfm2_700m_engine.py:_direct_identity_answer` already resolves short questions like `Who are you?` or `What's your name?`, but did not cover direct yes/no and negated questions about whether the §wyrlz application is ChatGPT or §wyrlz. Those prompts flowed into uncontrolled GGUF response generation, which can imitate other AI product names.

At the common source-owned `hf_space/model_router.py:dispatch` ingress, v211.3 adds a bounded direct-application-identity response before online research and any model backend. It handles exact short yes/no app-name checks with both affirmative and negative forms, producing clear §wyrlz identity and distinguishing the application from OpenAI ChatGPT. It deliberately does **not** intercept broader questions about ChatGPT, comparative research, coding, creative requests, quoted speech or multi-part requests. The response is independent of the caller's Google account user-profile text, optional custom profile or GGUF route.

**Model routes covered:** 700M, R39, pinned stock and coder through the single shared dispatcher. No fake inference, model weights, account profile overwrite, historical message edit, OAuth grant or imported ChatGPT archive mutation. The browser/local Chat source stays `1.1.08`.

**Scope:** This protects only direct identity Q&A. It does not ensure the 700M model always maintains speaker-role boundaries in arbitrary conversation; nor does it infer the identity of the person typing from a shared Google account. The built-in generic assistant/persona and per-user identity/profile separation deserve an independent source review, never an ad hoc hardcoding of a household member.

## Candidate and test evidence

- Source: `fix/assistant-brand-identity-clarity-v2113@6c928770b16ae16fe4694f93d45d6af9a07f3fa5`, based on the previous published v211.2 `f81ffd43647a8796feb47ebd6c3c0ad80f5df545`, [draft PR #109](https://github.com/kaministrator999-ui/Swrlzkamico/pull/109).
- [GitHub account/integration CI #38190668607](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38190668607): **SUCCESS**.
- [HF offline candidate CI #38190672584](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38190672584): **SUCCESS**.
- Synthetic tests in `hf_space/test_assistant_app_identity_v2113.py` check direct affirmative/negated forms, unrelated negative controls, all four route handlers, no GGUF calls, no unnecessary online search, and optional-profile contradiction handling. No private export was uploaded to CI.

## Single guarded production release

- Canonical `main:.deploy/HF_SPACE_REQUEST.txt` request `2026-10-11-v2113-assistant-identity-source-guard-001` pinned exactly to source SHA `6c928770b16ae16fe4694f93d45d6af9a07f3fa5`, request commit `bb4b90281669efd376b150fff22310fecf3e893e`.
- [GitHub Actions Hugging Face deployment #38190793062](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38190793062) terminal **SUCCESS**. Existing Space source package, R39 rebuild/compatibility, 700M smoke test, production snapshot and publication succeeded.
- New Space revision **`64818d054d9b27e592bbcd963a8d9fbd4b602d0d`**.
- Preserved rollback Space revision **`a583a03912723c9f24200a14de0fcbd491b409f2`**.
- `hf-release-checkpoint` artifact ID **11721701444**: `knownGood=false`, `verificationState=DEPLOYED_UNVERIFIED`. Production publication is verified, live real-user interaction still pending.

## Runtime registry

Atomic runtime commit `59f638831822a71a641a95c37bc1c8ce54c961a3`, all affected modules reread:

| Registered module | Before | After |
|---|---|---|
| Repository Work | 1.0.153 | **1.0.154** |
| Server Runtime | 2.3.365 | **2.3.366** |
| LALM Engine | 2.1.189 | **2.1.190** |

Web Chat **1.5.104**, Google Account **1.0.14** and local Chat **1.1.08** remain unchanged. No Runtime Manifest, Stream Contract, Online Research, §E project version or native APK bump.

## Concurrent v212 source risk

A separate v212 GitHub Actions workflow workbench branch was in progress when this v211.3 patch shipped. It originally branched from v211.2. Before publishing any future v212 source, integrate/verify this v211.3 shared-router identity guard, with both CI suites passing on the integrated source. Do not silently replace production with a v212 tree that lacks this guard.

## User acceptance

On the existing Space, under a signed-in account, use short direct questions asking whether the assistant is ChatGPT or §wyrlz. Replies must identify §wyrlz consistently, and an ensuing contradictory user premise must not make the assistant deny its own name. Follow with a normal comparative question or creative task involving ChatGPT; those must remain normal model-driven tasks. Real-world browser checks remain pending, so do not promote `knownGood` yet.

**Status:** CODE/CI/PRODUCTION DEPLOYMENT/REGISTRY COMPLETE; LIVE CHAT ACCEPTANCE PENDING.
