from __future__ import annotations

import json
from pathlib import Path

from programming_telemetry import (
    buffered_chat_completion,
    candidate_attempt_receipt,
    generation_summary,
)


def check(condition, message):
    if not condition:
        raise AssertionError(message)


class FakeModel:
    def __init__(self, parts):
        self.parts=list(parts)

    def create_chat_completion(self, **kwargs):
        check(kwargs.get("stream") is True, kwargs)
        for part in self.parts:
            yield {"choices":[{"delta":{"content":part}}]}


candidate, timing=buffered_chat_completion(
    FakeModel(["alpha","-","candidate"]),
    [{"role":"user","content":"fixture"}],
    max_tokens=32,
    temperature=0.2,
)
check(candidate=="alpha-candidate",candidate)
check(timing["durationMs"]>=0,timing)
check(timing["firstTokenLatencyMs"] is not None,timing)
check(timing["deltaChunks"]==3,timing)

first=candidate_attempt_receipt(
    1,
    "initial",
    timing,
    {"status":"REJECT","reasons":["language-contract-mismatch:python"]},
    "fp-first",
)
second=candidate_attempt_receipt(
    2,
    "retry:contract-or-structural-rejection",
    {"durationMs":12.5,"firstTokenLatencyMs":2.5,"deltaChunks":4},
    {"status":"PASS","reasons":[]},
    "fp-second",
    previous_attempt_fingerprint="fp-first",
)
summary=generation_summary(
    [first,second],
    total_latency_ms=50.0,
    load_latency_ms=5.0,
    visible_first_delta_latency_ms=48.0,
    guarded_turn=True,
    repair_turn=False,
    strict_language=True,
)
check(summary["attemptCount"]==2,summary)
check(summary["regenerationCount"]==1,summary)
check(summary["firstCandidateRejected"] is True,summary)
check(summary["finalAcceptedAttempt"]==2,summary)
check(summary["finalCandidateStatus"]=="PASS",summary)
check(summary["attempts"][1]["changedFromPreviousAttempt"] is True,summary)
check(summary["engineTotalLatencyMs"]==50.0,summary)
check(summary["visibleFirstDeltaLatencyMs"]==48.0,summary)

serialized=json.dumps(summary,sort_keys=True)
check("alpha-candidate" not in serialized,serialized)
check("fixture" not in serialized,serialized)

root=Path(__file__).resolve().parent
station=(root/"station.py").read_text(encoding="utf-8")
qwen=(root/"qwen_coder_engine.py").read_text(encoding="utf-8")
large=(root/"lfm2_700m_engine.py").read_text(encoding="utf-8")
app=(root/"app.py").read_text(encoding="utf-8")

for owner in (qwen,large):
    check('"type":"CANDIDATE_ATTEMPT"' in owner,"candidate attempt event missing")
    check('"type":"GENERATION_TELEMETRY"' in owner,"generation telemetry event missing")
    check("buffered_chat_completion" in owner,"buffered attempt timing missing")

check("SWRLZ_DIAGNOSTIC_GITHUB_TOKEN" in station,"dedicated diagnostics token missing")
check("runtime-diagnostics/{category}/{safe_request}/{filename}" in station,"runtime diagnostics path missing")
check('"PROGRAMMING_GENERATION_TELEMETRY":("programming","candidate-attempt-telemetry.json"' in station,"programming log mapping missing")
check('g.setdefault("candidateAttempts",[])' in station,"Station candidate attempt persistence missing")
check('g["generationTelemetry"]' in station,"Station generation telemetry persistence missing")
check('"githubTelemetryPersistence"' in station,"GitHub persistence receipt missing")
check("persist_runtime_diagnostic" in app,"probe does not use Station persistence owner")

print("programming-telemetry-v118 PASS")
