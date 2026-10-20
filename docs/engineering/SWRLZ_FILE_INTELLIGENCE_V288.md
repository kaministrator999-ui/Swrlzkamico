# §wyrlz Chat v288 — File Intelligence Engine v1

**Owner:** HF Chat Stage-1 source specialist. **Source authority:** isolated feature branch based on the immutable, published v287 Chat source commit. **Permission class:** GitHub read only; no new OAuth scopes, editor rights, commits, or test execution granted to the end-user AI.

## Where it lives and how to use it

- Engine: hf_space/github_file_intelligence_v288.py
- Integrated route: hf_space/github_source_specialist_v241.py, function events
- Tests: hf_space/test_github_file_intelligence_v288.py
- CI: .github/workflows/chat-file-intelligence-v288.yml
- In §wyrlz Chat, first connect GitHub and select the repo. Ask: "Analyze the GitHub source file pkg/main.py and trace its dependencies" or "What breaks if I change this GitHub file pkg/main.py?".
- The existing Chat source specialist supplies source provenance; beneath it, a "File intelligence · static evidence" section shows chosen scenario, structures with source line numbers, verified same-repository dependency paths, related source inspected, unverified imports and coverage, before the Qwen Coder explanation.
- Source-file follow-ups can use the existing verified per-thread file context. This addition does **not** create an independent "analyze entire repository" command, editor, multi-file patch system or broad AI write permission.

## Decision and evidence model

The fixed, compact scenario registry chooses security, regression, impact, debug, architecture or explain from the current user's request. It maps to reusable analytical operations; none are mutation or deployment operations. This is a heuristic router, not weight training or autonomous task execution.

Python source is parsed via the standard-library AST (including functions/classes and imports with line numbers). Markdown uses headings, JSON uses validated top-level keys, JavaScript/TypeScript use a limited lexical declaration/import extractor with a reported limitation. Other supported text formats state that they lack a native parser.

Direct imports are turned into candidate paths, then **only exact matches in a complete, SHA-pinned Git tree** become graph edges; ambiguous imports remain ambiguous, and external/unresolved imports are not claimed broken. A maximum of four unique related source files (32 KB each, 96 KB aggregate) are retrieved by the existing authorized GitHub reader. Each retrieved blob is byte-verified against its Git blob SHA. The primary verified source is also rechecked. Hidden/sensitive paths, unknown/unreadable files, oversized texts, mismatches and directory traversal are excluded.

The structured graph and short evidence display are supplied as **untrusted data** to the existing read-only Qwen Coder specialist. The specialist still never receives GitHub credentials or write authority. Graph-unavailable states preserve the old source reader; graph source is not presented as proof of runtime execution, exhaustive architecture knowledge or test results.

## Validation and acceptance

1. Compile the engine and integrated source specialist.
2. Run deterministic scenarios, Python AST, import ambiguity, matched and mismatched Git blobs, hidden-source rejection, bounded reads, and an event-level source-specialist mock.
3. Validate CI on the exact candidate; integrate into the Chat source lane only with clean diff and passing checks.
4. Release using the repository's existing guarded HF Space flow, not a separate target, and distinguish successful publication from later signed-in Android acceptance.

## Deferred work

Full-repository traversal/task discovery, cross-language symbol call graphs, deep recursion, production observability, persisted SHA-based graph cache, structured redaction for non-hidden files, expanded Kotlin/Java parsers, and safe autonomous capability creation remain future phases. They are NOT claimed by v288.
