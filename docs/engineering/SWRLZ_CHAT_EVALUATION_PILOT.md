# §C Intent-Gated Conversation Evaluation — Two-User Pilot

Status: proposed test-only GitHub Actions workflow. **No Chat runtime or §E deployment changes.**

## Purpose and boundaries

One GitHub Actions job launches one Chromium browser with two isolated Playwright browser contexts (two separate dedicated evaluation accounts). The job runs two fixed, synthetic multi-turn conversations concurrently:

1. **Code repair** — §C must recognize that an existing Python add function needs fixing, not invent a different application. If the intent gate passes, request code and statically verify a literal a + b return in the expected function.
2. **§E Modeler intent** — §C must recognize a request for a cube model without creating/opening a game project. If the intent gate passes, request a planning response. This does **not** exercise actual §E tools, editor leases, model creation or geometry. Full modeler/game-engine integration is a future independent lane.

The worker saves bounded synthetic output excerpts and independent checks in an Actions artifact; it never saves personal account information, signed cookies, or full private conversation histories.

## Gating logic

- Step 1: present the request and ask §C to restate it.
- Step 2: conservatively check whether key intent/constraint evidence appears in the reply.
- If essential evidence is missing or a directly conflicting project action appears: mark IMPROVE_INTENT, stop that conversation and flag it for review. Missing keywords are evidence of an *unverified* intent, not proof the model misunderstood.
- Only after PASS does the worker send the next task. A correct intent paraphrase does not prove implementation quality.
- The code objective is validated with Python AST rather than running untrusted model-generated code. Modeler goal verifies planning language only.
- Synthetic users have separate account sessions, browser contexts, and fresh thread/request IDs. Preserve existing user-history boundaries.
- The run always has a bounded timeout; no unbounded retries.

## Running the pilot

Workflow: .github/workflows/chat-eval-pilot.yml

- Pull requests touching this evaluator run **smoke** mode automatically. This launches Chromium, checks two isolated page contexts, and checks sample good/bad intent and Python AST fixtures. It does not contact §C or use a model.
- From GitHub Actions, select the workflow → Run workflow → live to run the two real conversations.
- Before a live run, configure repository Actions secrets SWRLZ_EVAL_SESSION_A and SWRLZ_EVAL_SESSION_B with distinct valid swrlz_session cookie *values* belonging to separate, dedicated, empty test accounts on the canonical HF Chat site. Never use a personal account cookie. Session cookies expire; the pilot does not create or renew them.
- No GitHub OAuth, repository write, engine host lease, production deploy, or third-party website access is granted to either test account.
- Live mode with missing credentials fails closed and produces no fabricated model metrics.

The Space endpoint is https://kamiloki-swyrlz.hf.space. Authenticated /api/lalm_station/send and /api/lalm_station/sync endpoints are called from browser-context requests. The worker does not forge account identity.

## Results

Each run publishes:

- Browser startup and runner elapsed milliseconds.
- For live runs: chat page startup, acknowledgement latency, committed assistant response latency, scenario outcome, and short sanitized response excerpts.
- Outcomes: STOPPED_FOR_INTENT_IMPROVEMENT, PASS (coding AST), PLAN_EVIDENCE_ONLY (Modeler planning), REVIEW_EXECUTION, or BLOCKED.

An Actions summary and JSON artifact are created at reports/chat-eval-pilot/. **One live run is the baseline**. A progress comparison requires an additional run with the same scenarios and verified model/runtime revision. Smoke timings are not model speed.

## Follow-up after the first measured run

Review false-positive intent flags, timing variance, the authenticated-session path, and production inference capacity. Only then expand to more accounts/scenarios, semantic judges, and dedicated §E modeler/game-engine instrumented actions using temporary test-only projects. Keep evaluation independent from normal deploy/update workflows. No recurring schedule is configured in this pilot.
