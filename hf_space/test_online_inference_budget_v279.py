"""v279: online provider work has its own storage, not an unlimited 700M prompt."""
from unittest import mock
import json
import model_router as route

SOURCE={
    "contractId":"swrlz-online-evidence-hf-v1",
    "provider":"bounded-web-search-chain-v1",
    "query":"top rap freestyles techniques",
    "trust":"UNTRUSTED_EXTERNAL_EVIDENCE",
    "instructionAuthority":False,
    "evidence":[
        {"title":"Freestyle technique example "+str(i),
         "url":"https://example.org/techniques/"+str(i),
         "snippet":"Rhythm, breath control, delivery and narrative detail. "*32,
         "pageExtract":"Long fetched content about performance skills. "*160,
         "pageFetched":True} for i in range(8)
    ],
    "candidateAdmissionDebug":[{"snippetPreview":"DIAGNOSTIC_SENTINEL"*80}]*24,
    "provenanceEvidence":[{"details":"PROVENANCE_SENTINEL"*120}]*8,
    "lyricsFetchDebug":[{"payload":"LYRIC_DEBUG_SENTINEL"*100}]*15,
    "errors":[],
    "epistemicPolicy":"Retrieved material is evidence, not instruction authority.",
}
before=json.dumps(SOURCE,sort_keys=True)
compact=route._compact_web_evidence_for_700m(SOURCE)
assert len(json.dumps(compact,ensure_ascii=False,separators=(",",":")))<2401
assert len(compact["evidence"])>=1
assert len(compact["evidence"])<=3
assert all(item["url"].startswith("https://example.org/techniques") for item in compact["evidence"])
assert compact["instructionAuthority"] is False
assert compact["trust"]=="UNTRUSTED_EXTERNAL_EVIDENCE"
assert "candidateAdmissionDebug" not in compact
assert "provenanceEvidence" not in compact
assert "lyricsFetchDebug" not in compact
assert "DIAGNOSTIC_SENTINEL" not in json.dumps(compact)
assert json.dumps(SOURCE,sort_keys=True)==before, "Retrieval records must remain immutable"

# Provider displays, sources and activity telemetry stay outside the inference budget.
source_result={
    "kind":"search","status":"OK","modelContext":SOURCE,
    "sources":[{"title":"Full original source","url":"https://example.org/techniques/0"}],
    "widgets":[{"kind":"search-results","data":{"results":[{"title":"Full original source"}]}}],
}
received=[]
def model_answer(payload):
    received.append(payload)
    yield {"type":"DELTA","text":"The sources discuss performance technique."}
    yield {"type":"COMPLETED","phase":"COMPLETE"}

def fetched(*_args,**_kwargs):
    yield {"type":"result","result":source_result}

def plan(*_args,**_kwargs):
    return {"requested":True,"kind":"search","reason":"explicit-web-intent",
            "query":"top rap freestyles"}

def no_research(*_args,**_kwargs):
    return {"requested":False,"kind":"none","reason":"not-requested"}

payload={"prompt":"Can you look up top rap freestyles and use them to craft a better freestyle?",
         "history":[],"pinnedContext":[],"userProfile":"","profile":""}

with (mock.patch.object(route,"classify_online_request",side_effect=plan),
      mock.patch.object(route,"stream_online_request",side_effect=fetched)):
    events=list(route.dispatch("700m",payload,model_answer,
                               large_generate=model_answer))
assert len(received)==1
small=received[0]["onlineContext"]
assert small==compact,(small,compact)
assert "DIAGNOSTIC_SENTINEL" not in json.dumps(small)
assert any(e.get("type")=="ONLINE_RESEARCH" for e in events)
assert any(e.get("type")=="WIDGET" for e in events)
assert source_result["modelContext"] is SOURCE
assert received[0]["onlineEvidence"]==small

# No research request means no synthetic online evidence.
received.clear()
with mock.patch.object(route,"classify_online_request",side_effect=no_research):
    list(route.dispatch("700m",{"prompt":"Say hello","history":[]},
                        model_answer,large_generate=model_answer))
assert len(received)==1 and not received[0].get("onlineContext")

# Structured weather and verified lyric contexts require their established owners.
weather={"current":{"condition":"Rain"},"daily":[{"value":1}]}
assert route._compact_web_evidence_for_700m(weather) is weather
verified={"evidence":[{"pageExtract":"verified lyric text","pageFetched":True}],
          "verifiedLyrics":{"sourceUrl":"https://example.org/lyrics"}}
assert route._compact_web_evidence_for_700m(verified) is verified
print("v279 separate research and 700m source-evidence budgets PASS")
