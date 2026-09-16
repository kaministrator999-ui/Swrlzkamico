# Server 2.3.189 — Hot Online Research Foundation

Date: 2026-09-16

## Versions

- Server Runtime: 2.3.189
- LALM Engine: 2.1.61 / R39 v50
- Online Research: 1.0.0
- Stable Chat bridge: 1.4.1 after deployment
- Web Chat: unchanged

## Accomplishment

This event turns §wyrlz online research strategy and research-camera instrumentation into a runtime-hot evolvable capability while retaining a small stable server security/network boundary.

The Brain now owns a bounded semantic pre-retrieval planning pass. It resolves research intent, target, requested information, constraints, confidence, and search queries from meaning and active context. Quotation marks are evidence, not a requirement. Natural requests such as `look up hey`, `what does hey mean`, and `Hey, can you look up hay and its definition?` are intended to resolve semantically rather than through a quoted-token regex.

The hot research module owns query execution strategy over server-authorized capabilities, result normalization, bounded page-fetch selection, evidence packaging, and structured research Camera telemetry. The stable server retains network authority: public HTTP(S) only, ports 80/443, no URL credentials, DNS/private-address blocking, redirect revalidation, timeouts, and response byte limits.

Research Camera contract `swrlz_research_camera_v1` records absolute timestamps, request-relative timing, requestId, researchId, target resolution, query plan, provider/search lifecycle, discovered exact URLs, page-fetch lifecycle, final URL/status, bounded extraction size, evidence IDs, and bundle completion. Retrieved text remains untrusted evidence and never gains instruction authority.

The evidence contract advances to `swrlz_online_evidence_v2` and can carry exact source URLs, bounded page extracts, fetch metadata, research plan, researchId, and evidence IDs into R39 for evaluation and source-grounded synthesis.

## Hot-update architecture

After the stable foundation is deployed once, the server refreshes `runtime/runtime_hot/online_research_reasoner_v1.py` on a bounded interval. Future research-strategy and research-camera improvements can therefore normally ship through `runtime` without redeploying the stable server. Security/authorization/network-policy changes remain stable-infrastructure work and still require deliberate deployment.

R39 remains independently runtime-hot through its existing loader. Online Research is registered as its own module authority in `VERSION.txt` and `versions/online-research.txt`.

## Lineage

- Runtime PR: #13
- Runtime merge: `4f7019bebe880104f3f80bf6697806ddaaa5b054`
- Stable staging branch: `hot-online-research-foundation-v1`
- Stable files: `api/online_research.py`, `api/chat_extensions.py`

## Deployment / verification

- Runtime source: merged; no deployment/restart triggered.
- Stable source: staged for merge to `main` under current Git-deployment-disabled configuration.
- Production deployment: intentionally NOT performed by ChatGPT. User stated they will deploy after implementation is ready.
- Full production acceptance is pending that manual deployment. After deployment, verify `/api/chat/ops`, R39 v50 inspection, hot Online Research 1.0.0 inspection, one lexical lookup regression, one greeting-vs-target disambiguation regression, exact research-camera URL/timestamp records, evidence delivery, final source attribution, and absence of secret/auth-header logging.

## Rollback

The stable broker fails back to its bounded legacy search path when the hot reasoner cannot be fetched or loaded. Runtime R39 can be rolled back through its existing hot loader. No durable user data migration is introduced.
